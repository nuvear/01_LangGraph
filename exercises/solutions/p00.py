"""Independent P00 solution: a public-profile readiness check, never authentication."""
from __future__ import annotations

from pathlib import Path
import re
import sys
from typing import Mapping, TypedDict
from urllib.parse import urlsplit

from langgraph.graph import END, START, StateGraph
from langsmith import tracing_context

from course_support.runtime import execution_config, run_cli

ORIGINS = {
    "anthropic": ("api.anthropic.com",),
    "langsmith": (
        "api.smith.langchain.com", "eu.api.smith.langchain.com",
        "apac.api.smith.langchain.com", "aws.api.smith.langchain.com",
    ),
    "langwatch": ("app.langwatch.ai",),
}
PUBLIC_FIELDS = {
    "model", "backend", "langsmith_endpoint", "langwatch_endpoint",
    "langwatch_key_kind", "langwatch_project_id",
}
READY_PROFILE = {
    "model": "claude-course-example",  # Synthetic syntax example, not a real model.
    "backend": "both",  # Describes a future plan; it does not enable tracing.
    "langsmith_endpoint": " https://eu.api.smith.langchain.com:443/ ",
    "langwatch_endpoint": "",
    "langwatch_key_kind": "service",
    "langwatch_project_id": "course-synthetic",
}
REPAIR_PROFILE = {
    **READY_PROFILE,
    "model": "",
    "langsmith_endpoint": "https://smith.langchain.com",
    "langwatch_project_id": "",
}


def validate_endpoint(service: str, value: str = "") -> str:
    if service not in ORIGINS:
        raise ValueError("Unsupported service name.")
    endpoint = value.strip() or f"https://{ORIGINS[service][0]}"
    error = "Use a supported HTTPS origin without credentials, paths or query data."
    if any(ord(char) < 33 or ord(char) == 127 for char in endpoint):
        raise ValueError(error)
    if any(char in endpoint for char in ("\\", "?", "#")):
        raise ValueError(error)
    try:
        parsed = urlsplit(endpoint)
        host = parsed.hostname
        port = parsed.port
    except ValueError:
        raise ValueError(error) from None
    if (
        parsed.scheme != "https"
        or host not in ORIGINS[service]
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or port not in (None, 443)
        or parsed.netloc.lower() not in (host, f"{host}:443")
    ):
        raise ValueError(error)
    return f"https://{host}"


def check_profile(profile: Mapping[str, str]) -> dict:
    """Return allowlisted results only; never return the original profile."""
    issues = []
    endpoints = {}
    if set(profile) - PUBLIC_FIELDS:
        issues.append("unsupported_fields")
    elif any(not isinstance(value, str) for value in profile.values()):
        issues.append("invalid_value_type")
    else:
        if not re.fullmatch(r"claude-[A-Za-z0-9_.:-]+", profile.get("model", "")):
            issues.append("model_invalid")
        backend = profile.get("backend", "none")
        if backend not in ("none", "langsmith", "langwatch", "both"):
            issues.append("backend_invalid")
        # Check BOTH origins even for a future backend plan of 'none'.
        for service in ("langsmith", "langwatch"):
            try:
                endpoints[service] = validate_endpoint(
                    service, profile.get(f"{service}_endpoint", ""),
                )
            except ValueError:
                issues.append(f"{service}_endpoint_invalid")
        if backend in ("langwatch", "both"):
            key_kind = profile.get("langwatch_key_kind", "project")
            if key_kind not in ("project", "service", "personal"):
                issues.append("langwatch_key_kind_invalid")
            elif key_kind in ("service", "personal"):
                if not profile.get("langwatch_project_id", "").strip():
                    issues.append("langwatch_project_required")
    return {
        "status": "needs_attention" if issues else "ready",
        "issues": issues,
        "endpoints": endpoints,
        "remote_checked": False,
    }


def classify_failure(status_code: int | None) -> str:
    """Offline triage recommendations, not a claim that a request was made."""
    actions = {
        None: "Check network, DNS, proxy and TLS; never disable certificate checks.",
        401: "Verify or rotate the key privately; do not print it.",
        403: "Check organization/workspace permissions and model access.",
        404: "Check the configured model ID and API resource path.",
        429: "Check rate and spend limits; honor Retry-After when present.",
        529: "Wait and retry within a bounded backoff budget.",
    }
    return actions.get(
        status_code,
        "Record a sanitized status and request ID; consult official errors.",
    )


class ReadinessState(TypedDict, total=False):
    report: dict
    message: str


def build_graph():
    """Only a sanitized report, not a credential-bearing profile, enters state."""
    def summarize(state: ReadinessState) -> dict:
        ready = state["report"]["status"] == "ready"
        return {"message": "Local profile ready." if ready else "Repair public settings."}

    builder = StateGraph(ReadinessState)
    builder.add_node("summarize", summarize)
    builder.add_edge(START, "summarize")
    builder.add_edge("summarize", END)
    return builder.compile()


def run_profile(profile: Mapping[str, str]) -> dict:
    # Validate before invocation so even an unknown credential field cannot
    # enter graph state. Only fixed issue names and supported origins are kept.
    report = check_profile(profile)
    with tracing_context(enabled=False):
        result = build_graph().invoke({"report": report}, config=execution_config())
    return {**result["report"], "message": result["message"]}


def reject_remote_options(arguments: list[str]) -> None:
    for index, argument in enumerate(arguments):
        if argument == "--live":
            raise SystemExit("P00 is offline only: omit --live.")
        if argument.startswith("--backend="):
            if argument.split("=", 1)[1] != "none":
                raise SystemExit("P00 requires --backend none.")
        if argument == "--backend" and index + 1 < len(arguments):
            if arguments[index + 1] != "none":
                raise SystemExit("P00 requires --backend none.")
        name = argument.split("=", 1)[0]
        if name.startswith("--") and name not in (
            "--live", "--backend", "--output-dir", "--help",
        ):
            raise SystemExit("Use full option names; P00 supports offline options only.")


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    if live:
        raise ValueError("P00 does not perform live calls.")
    del workdir
    ready = run_profile(READY_PROFILE)
    repair = run_profile(REPAIR_PROFILE)
    assert ready["status"] == "ready" and ready["issues"] == []
    assert ready["endpoints"]["langsmith"] == "https://eu.api.smith.langchain.com"
    assert ready["remote_checked"] is False
    assert ready["message"] == "Local profile ready."
    assert repair["status"] == "needs_attention"
    assert repair["issues"] == [
        "model_invalid", "langsmith_endpoint_invalid", "langwatch_project_required",
    ]
    assert repair["message"] == "Repair public settings."
    codes = (None, 401, 403, 404, 429, 529, 418)
    advice = {"network" if code is None else str(code): classify_failure(code)
              for code in codes}
    assert "privately" in advice["401"]
    assert "Retry-After" in advice["429"]
    return {"ready_case": ready, "repair_case": repair, "triage": advice,
            "remote_checked": False, "environment_file_read": False}


if __name__ == "__main__":
    reject_remote_options(sys.argv[1:])
    run_cli("P00", run_demo)
