"""Explicit tracing backends; credentials are never part of graph state or metadata.

Only pass synthetic classroom data to the traced examples. Both services receive
inputs and outputs when backend='both'; this is intentional, not a privacy filter.
"""
from __future__ import annotations

import os
from contextlib import ExitStack, contextmanager
from typing import Iterator

from course_support.check_connections import safe_endpoint, values

BACKENDS = ("none", "langsmith", "langwatch", "both")


@contextmanager
def graph_tracing(backend: str = "none", *, name: str = "LangGraph Course Demo") -> Iterator[dict]:
    """Yield invocation configuration and flush selected callbacks before exit.

    A flush means submission was attempted, not that a dashboard was inspected.
    Use check_connections to verify remote ingestion independently.
    """
    if backend not in BACKENDS:
        raise ValueError(f"Tracing backend must be one of {BACKENDS}.")
    from langsmith import tracing_context

    with ExitStack() as stack:
        # Prevent ambient environment flags from enabling unrequested tracing.
        stack.enter_context(tracing_context(enabled=False))
        if backend == "none":
            yield {"callbacks": []}
            return
        config = values()
        callbacks = []
        smith_client = None
        watch_client = None
        if backend in ("langsmith", "both"):
            from langsmith import Client
            from langchain_core.tracers.langchain import LangChainTracer, wait_for_all_tracers

            key = config.get("LANGSMITH_API_KEY") or config.get("LANGCHAIN_API_KEY")
            if not key:
                raise ValueError("LANGSMITH_API_KEY is required for this tracing backend.")
            endpoint = safe_endpoint(config.get("LANGSMITH_ENDPOINT") or config.get("LANGCHAIN_ENDPOINT", ""),
                                     "https://api.smith.langchain.com",
                                     {"api.smith.langchain.com", "eu.api.smith.langchain.com",
                                      "apac.api.smith.langchain.com", "aws.api.smith.langchain.com"})
            smith_client = Client(api_url=endpoint, api_key=key, timeout_ms=15000,
                                  workspace_id=config.get("LANGSMITH_WORKSPACE_ID") or None,
                                  omit_traced_runtime_info=True)
            callbacks.append(LangChainTracer(
                project_name=config.get("LANGSMITH_PROJECT") or config.get("LANGCHAIN_PROJECT") or "langgraph-course",
                client=smith_client))
            stack.callback(smith_client.close)
            stack.callback(smith_client.flush)
            stack.callback(wait_for_all_tracers)
        if backend in ("langwatch", "both"):
            import langwatch
            from opentelemetry.sdk.trace import TracerProvider

            key = config.get("LANGWATCH_API_KEY")
            if not key:
                raise ValueError("LANGWATCH_API_KEY is required for this tracing backend.")
            endpoint = safe_endpoint(config.get("LANGWATCH_ENDPOINT", ""), "https://app.langwatch.ai", {"app.langwatch.ai"})
            # A dedicated provider keeps this course's spans out of unrelated
            # telemetry pipelines configured by the host process.
            provider = TracerProvider()
            previous_project = os.environ.get("LANGWATCH_PROJECT_ID")
            try:
                if config.get("LANGWATCH_PROJECT_ID"):
                    os.environ["LANGWATCH_PROJECT_ID"] = config["LANGWATCH_PROJECT_ID"]
                watch_client = langwatch.setup(api_key=key, endpoint_url=endpoint,
                                               tracer_provider=provider, instrumentors=[])
            finally:
                if previous_project is None:
                    os.environ.pop("LANGWATCH_PROJECT_ID", None)
                else:
                    os.environ["LANGWATCH_PROJECT_ID"] = previous_project
            # Registered first so the trace context exits before flush/shutdown.
            stack.callback(provider.shutdown)
            stack.callback(provider.force_flush, timeout_millis=15000)
            trace = stack.enter_context(langwatch.trace(name=name, capture_input=False, capture_output=False,
                                                        tracer_provider=provider))
            callbacks.append(trace.get_langchain_callback())
        yield {"callbacks": callbacks, "run_name": name, "tags": ["langgraph-course", "synthetic-data"]}
