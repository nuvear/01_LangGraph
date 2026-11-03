"""P00 workbook starter. Run from the project root; no keys or network needed."""
from __future__ import annotations

import argparse
import re
from typing import Mapping, TypedDict
from urllib.parse import urlsplit

from langgraph.graph import END, START, StateGraph
from langsmith import tracing_context

from course_support.runtime import execution_config

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
    "model": "claude-course-example",  # Syntax fixture only, not a real model ID.
    "backend": "both",  # A proposed configuration, NOT an enabled backend.
    "langsmith_endpoint": " https://eu.api.smith.langchain.com:443/ ",
    "langwatch_endpoint": "",
    "langwatch_key_kind": "service",
    "langwatch_project_id": "course-synthetic",
}
REPAIR_PROFILE = {
    **READY_PROFILE, "model": "",
    "langsmith_endpoint": "https://smith.langchain.com",
    "langwatch_project_id": "",
}


def validate_endpoint(service: str, value: str = "") -> str:
    """TODO 1: validate an allowlisted origin and return its canonical form.

    Strip outside whitespace; blank uses the service's first ORIGINS host.
    Permit HTTPS, no port or literal :443, and no path or a single slash.
    Reject credentials, unknown/lookalike hosts, control characters, backslash,
    any ? or # (even empty), malformed ports and unsupported service names.
    Raise ValueError with a FIXED message; never echo the supplied URL.
    Return https://HOST with no port or slash. urlsplit is imported for you.
    """
    raise NotImplementedError("Implement validate_endpoint (TODO 1).")


def check_profile(profile: Mapping[str, str]) -> dict:
    """TODO 2: return a safe report, never the original profile.

    Report keys: status, issues, endpoints, remote_checked (always False).
    Unknown keys -> only unsupported_fields; otherwise a non-string value ->
    only invalid_value_type. For those early exits, endpoints must be {}.
    Otherwise append issues in this order:
    * model_invalid unless fullmatch(r'claude-[A-Za-z0-9_.:-]+', model).
    * backend_invalid unless none/langsmith/langwatch/both; default is none.
    * langsmith_endpoint_invalid, then langwatch_endpoint_invalid, if their
      validators fail; validate BOTH even when backend is none. Keep only
      valid canonical origins in endpoints. Missing endpoints default blank.
    * For langwatch/both only: langwatch_key_kind_invalid unless kind is
      project/service/personal (missing defaults project); otherwise append
      langwatch_project_required for service/personal with a blank project ID.
    Status is ready only when issues == []; otherwise needs_attention.
    Do not modify profile. Do not read files or environment variables.
    """
    raise NotImplementedError("Implement check_profile (TODO 2).")


def classify_failure(status_code: int | None) -> str:
    """TODO 3: return exactly the fixed action for each workbook scenario.

    None: Check network, DNS, proxy and TLS; never disable certificate checks.
    401: Verify or rotate the key privately; do not print it.
    403: Check organization/workspace permissions and model access.
    404: Check the configured model ID and API resource path.
    429: Check rate and spend limits; honor Retry-After when present.
    529: Wait and retry within a bounded backoff budget.
    Other: Record a sanitized status and request ID; consult official errors.
    These are simulated status inputs, not responses from actual requests.
    """
    raise NotImplementedError("Implement classify_failure (TODO 3).")


class ReadinessState(TypedDict, total=False):
    report: dict
    message: str


def build_graph():
    """Provided graph wiring: only the sanitized report enters state."""
    def summarize(state: ReadinessState) -> dict:
        ready = state["report"]["status"] == "ready"
        return {"message": "Local profile ready." if ready else "Repair public settings."}

    builder = StateGraph(ReadinessState)
    builder.add_node("summarize", summarize)
    builder.add_edge(START, "summarize")
    builder.add_edge("summarize", END)
    return builder.compile()


def run_profile(profile: Mapping[str, str]) -> dict:
    report = check_profile(profile)
    with tracing_context(enabled=False):
        result = build_graph().invoke({"report": report}, config=execution_config())
    return {**result["report"], "message": result["message"]}


def verify_work() -> None:
    """Focused self-checks; instructor tests cover more endpoint edge cases."""
    assert validate_endpoint("langwatch") == "https://app.langwatch.ai"
    assert validate_endpoint("langsmith", READY_PROFILE["langsmith_endpoint"]) == (
        "https://eu.api.smith.langchain.com"
    )
    for bad in ("http://app.langwatch.ai", "https://app.langwatch.ai?token=sample"):
        try:
            validate_endpoint("langwatch", bad)
        except ValueError:
            pass
        else:
            raise AssertionError("An unsafe URL was accepted.")
    ready = run_profile(READY_PROFILE)
    repair = run_profile(REPAIR_PROFILE)
    assert ready["status"] == "ready" and ready["issues"] == []
    assert ready["message"] == "Local profile ready."
    assert ready["remote_checked"] is False
    assert repair["issues"] == [
        "model_invalid", "langsmith_endpoint_invalid", "langwatch_project_required",
    ]
    assert repair["status"] == "needs_attention"
    assert repair["message"] == "Repair public settings."
    assert check_profile({"api_key": "synthetic-do-not-echo"}) == {
        "status": "needs_attention", "issues": ["unsupported_fields"],
        "endpoints": {}, "remote_checked": False,
    }
    expected = {
        None: "Check network, DNS, proxy and TLS; never disable certificate checks.",
        401: "Verify or rotate the key privately; do not print it.",
        403: "Check organization/workspace permissions and model access.",
        404: "Check the configured model ID and API resource path.",
        429: "Check rate and spend limits; honor Retry-After when present.",
        529: "Wait and retry within a bounded backoff budget.",
        418: "Record a sanitized status and request ID; consult official errors.",
    }
    for status, action in expected.items():
        assert classify_failure(status) == action


def main() -> None:
    argparse.ArgumentParser(description=__doc__, allow_abbrev=False).parse_args()
    try:
        verify_work()
    except NotImplementedError as exc:
        print(f"STARTER_NOT_COMPLETED: {exc}")
        return
    print("LOCAL_EXERCISE_CHECKS_PASSED: offline checks only; no remote service checked.")


if __name__ == "__main__":
    main()
