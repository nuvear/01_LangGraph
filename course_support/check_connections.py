"""Run real service checks without printing credentials.

Usage: python -m course_support.check_connections --service all
A successful telemetry check means ingestion was acknowledged, not UI inspection.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / ".work" / "validation"


def values() -> dict[str, str]:
    """Read configuration in place; never put the entire .env in a trace."""
    return {key: value or "" for key, value in dotenv_values(ROOT / ".env").items()}


def safe_endpoint(value: str, default: str, allowed_hosts: set[str]) -> str:
    endpoint = value.strip() or default
    parsed = urlsplit(endpoint)
    if (parsed.scheme != "https" or parsed.hostname not in allowed_hosts
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in ("", "/") or parsed.port not in (None, 443)):
        raise ValueError("Use a supported official HTTPS API endpoint without a path or credentials.")
    return endpoint.rstrip("/")


def test_anthropic(config: dict[str, str]) -> dict:
    import anthropic

    key = config.get("ANTHROPIC_API_KEY")
    model = config.get("ANTHROPIC_MODEL", "")
    if not key or not re.fullmatch(r"claude-[A-Za-z0-9_.:-]+", model):
        return {"status": "configuration_error", "detail": "A key and valid Claude model ID are required."}
    with anthropic.Anthropic(api_key=key, base_url="https://api.anthropic.com", timeout=45, max_retries=0) as client:
        response = client.messages.create(
            model=model, max_tokens=64,
            messages=[{"role": "user", "content": "Reply with exactly ANTHROPIC_CONNECTION_OK and nothing else."}],
        )
    text = "".join(block.text for block in response.content if block.type == "text").strip()
    return {"status": "passed" if text == "ANTHROPIC_CONNECTION_OK" else "unexpected_response",
            "configured_model": model, "response_model": response.model, "response_text": text,
            "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens,
            "request_id": getattr(response, "_request_id", None)}


def test_langsmith(config: dict[str, str]) -> dict:
    from langsmith import Client

    key = config.get("LANGSMITH_API_KEY") or config.get("LANGCHAIN_API_KEY")
    if not key:
        return {"status": "configuration_error", "detail": "LANGSMITH_API_KEY is required."}
    endpoint = safe_endpoint(config.get("LANGSMITH_ENDPOINT") or config.get("LANGCHAIN_ENDPOINT", ""),
                             "https://api.smith.langchain.com",
                             {"api.smith.langchain.com", "eu.api.smith.langchain.com",
                              "apac.api.smith.langchain.com", "aws.api.smith.langchain.com"})
    project = config.get("LANGSMITH_PROJECT") or config.get("LANGCHAIN_PROJECT") or "langgraph-course"
    run_id = uuid4()
    now = datetime.now(timezone.utc)
    client = Client(api_url=endpoint, api_key=key, auto_batch_tracing=False, timeout_ms=15000,
                    workspace_id=config.get("LANGSMITH_WORKSPACE_ID") or None,
                    omit_traced_runtime_info=True)
    try:
        client.create_run(name="LangGraph Course Connection Check", id=run_id, run_type="chain",
                          project_name=project, inputs={"synthetic_value": 2}, outputs={"result": 3},
                          start_time=now, end_time=now, extra={"metadata": {"synthetic": True}})
        # Reading back distinguishes actual persistence from an SDK call merely returning.
        async def retrieve():
            for attempt in range(4):
                try:
                    project_record = await client.aread_project(project_name=project)
                    return await client.runs.retrieve(
                        run_id=str(run_id), project_id=str(project_record.id),
                        start_time=now.isoformat(), selects=["ID", "INPUTS", "OUTPUTS"],
                    )
                except Exception:
                    if attempt == 3:
                        raise
                    await asyncio.sleep(1)

        stored = asyncio.run(retrieve())
        if stored.outputs != {"result": 3} or stored.inputs != {"synthetic_value": 2}:
            raise ValueError("The stored trace did not contain the expected synthetic input/output.")
        return {"status": "passed", "endpoint": endpoint, "run_id": str(stored.id),
                "ingestion_acknowledged": True, "readback_verified": True,
                "dashboard_visually_verified": False}
    finally:
        client.close()


def test_langwatch(config: dict[str, str]) -> dict:
    import requests
    from langwatch.utils.auth import build_auth_headers
    from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans
    from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceResponse
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    key = config.get("LANGWATCH_API_KEY")
    if not key:
        return {"status": "configuration_error", "detail": "LANGWATCH_API_KEY is required."}
    endpoint = safe_endpoint(config.get("LANGWATCH_ENDPOINT", ""), "https://app.langwatch.ai",
                             {"app.langwatch.ai"})

    memory = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(memory))
    with provider.get_tracer("langgraph-course").start_as_current_span("LangGraph Course Connection Check") as span:
        span.set_attribute("course.synthetic", True)
        span.set_attribute("course.result", 3)
        trace_id = format(span.get_span_context().trace_id, "032x")
    headers = build_auth_headers(key, config.get("LANGWATCH_PROJECT_ID") or None)
    headers["Content-Type"] = "application/x-protobuf"
    payload = encode_spans(memory.get_finished_spans()).SerializeToString()
    try:
        # A direct OTLP POST makes the server acknowledgment visible. A successful
        # batch-processor flush alone does not establish remote ingestion.
        with requests.Session() as session:
            response = session.post(endpoint + "/api/otel/v1/traces", data=payload,
                                    headers=headers, timeout=15, allow_redirects=False)
        rejected_spans = None
        acknowledgment_format = None
        if response.status_code == 200:
            if "json" in response.headers.get("Content-Type", "").lower():
                acknowledgment = response.json()
                acknowledgment_format = "json"
                # LangWatch's OTLP receiver may return a JSON success envelope.
                rejected_spans = int(acknowledgment.get("partialSuccess", {}).get("rejectedSpans", 0))
                if acknowledgment.get("error") or acknowledgment.get("success") is False:
                    rejected_spans = 1
            else:
                acknowledgment = ExportTraceServiceResponse.FromString(response.content)
                acknowledgment_format = "protobuf"
                rejected_spans = acknowledgment.partial_success.rejected_spans
        passed = response.status_code == 200 and rejected_spans == 0
        return {"status": "passed" if passed else "export_failed",
                "endpoint": endpoint, "http_status": response.status_code,
                "ingestion_acknowledged": passed, "rejected_spans": rejected_spans,
                "acknowledgment_format": acknowledgment_format,
                "trace_id": trace_id, "dashboard_visually_verified": False}
    finally:
        provider.shutdown()


def run(service: str, config: dict[str, str]) -> dict:
    report = {"service": service, "checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "credential_values_logged": False, "synthetic_data_only": True}
    try:
        report.update({"anthropic": test_anthropic, "langsmith": test_langsmith,
                       "langwatch": test_langwatch}[service](config))
    except Exception as exc:
        # Never log arbitrary exception content: it can include headers or tokens.
        report.update(status="failed", error_type=type(exc).__name__)
        status = getattr(exc, "status_code", None)
        response = getattr(exc, "response", None)
        if status is None and response is not None:
            status = getattr(response, "status_code", None)
        if status is not None:
            report["http_status"] = status
        if service == "anthropic":
            report["request_id"] = getattr(exc, "request_id", None)
        report["detail"] = "Check the API key, endpoint region, project/workspace scope, and permissions."
    serialized = json.dumps(report, indent=2)
    for name, value in config.items():
        if value and any(word in name.upper() for word in ("KEY", "TOKEN", "SECRET", "PASSWORD")):
            serialized = serialized.replace(value, "[REDACTED]")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / f"{service}_connection.json").write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--service", choices=("all", "anthropic", "langsmith", "langwatch"), default="all")
    args = parser.parse_args()
    # Suppress SDK logs: only the allowlisted report above is printed.
    logging.disable(logging.CRITICAL)
    config = values()
    services = ("anthropic", "langsmith", "langwatch") if args.service == "all" else (args.service,)
    results = [run(service, config) for service in services]
    return 0 if all(result["status"] == "passed" for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
