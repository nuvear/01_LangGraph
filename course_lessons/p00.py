"""P00: inspect local readiness and run a graph without a model or .env."""
from __future__ import annotations

from importlib import metadata
from pathlib import Path
import sys
from typing import Callable, TypedDict
from urllib.parse import urlsplit

from langgraph.graph import END, START, StateGraph
from langsmith import tracing_context

from course_support.runtime import execution_config, run_cli

PACKAGES = (
    "langgraph", "langchain-core", "langchain-anthropic", "anthropic",
    "python-dotenv", "langsmith", "langwatch", "pytest",
)
ORIGINS = {
    "anthropic": ("api.anthropic.com",),
    "langsmith": (
        "api.smith.langchain.com", "eu.api.smith.langchain.com",
        "apac.api.smith.langchain.com", "aws.api.smith.langchain.com",
    ),
    "langwatch": ("app.langwatch.ai",),
}


def inspect_environment(
    *,
    python_version: tuple[int, int] | None = None,
    prefixes: tuple[str, str] | None = None,
    version_reader: Callable[[str], str] = metadata.version,
) -> dict:
    """Read installed distribution metadata, never configuration or credentials."""
    version = python_version if python_version is not None else sys.version_info[:2]
    current, base = prefixes if prefixes is not None else (sys.prefix, sys.base_prefix)
    installed = {}
    missing = []
    for package in PACKAGES:
        try:
            installed[package] = version_reader(package)
        except metadata.PackageNotFoundError:
            installed[package] = "not_installed"
            missing.append(package)
    supported = tuple(version) == (3, 12)
    isolated = current != base
    return {
        "python": ".".join(map(str, version)),
        "python_supported": supported,
        "virtual_environment": isolated,
        "packages": installed,
        "missing_packages": missing,
        "ready": supported and isolated and not missing,
    }


def validate_endpoint(service: str, value: str = "") -> str:
    """Accept a supported HTTPS origin, not arbitrary URLs or dashboard paths."""
    if service not in ORIGINS:
        raise ValueError("Unsupported service name.")
    endpoint = value.strip() or f"https://{ORIGINS[service][0]}"
    error = "Use a supported HTTPS origin without credentials, paths or query data."
    # Reject URL parser cleanup of control characters and empty ?/# components.
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


class SetupState(TypedDict, total=False):
    label: str
    checks: list[str]
    message: str


def check_label(state: SetupState) -> dict:
    """A plain Python node returns only the state fields it changes."""
    label = state["label"].strip()
    if not label:
        raise ValueError("Supply a nonempty synthetic learner label.")
    return {"label": label, "checks": ["label_checked"]}


def finish_setup(state: SetupState) -> dict:
    return {
        "checks": [*state["checks"], "graph_completed"],
        "message": f"Offline setup graph ready for {state['label']}.",
    }


def build_graph():
    builder = StateGraph(SetupState)
    builder.add_node("check_label", check_label)
    builder.add_node("finish_setup", finish_setup)
    builder.add_edge(START, "check_label")
    builder.add_edge("check_label", "finish_setup")
    builder.add_edge("finish_setup", END)
    return builder.compile()


def reject_remote_options(arguments: list[str]) -> None:
    """Fail before the shared CLI could initialize a remote tracing backend."""
    for index, argument in enumerate(arguments):
        if argument == "--live":
            raise SystemExit("P00 is offline only: omit --live.")
        if argument.startswith("--backend="):
            if argument.split("=", 1)[1] != "none":
                raise SystemExit("P00 requires --backend none.")
        if argument == "--backend" and index + 1 < len(arguments):
            if arguments[index + 1] != "none":
                raise SystemExit("P00 requires --backend none.")
        # argparse accepts long-option abbreviations; disallow them here so
        # --back=langsmith cannot bypass this pre-initialization guard.
        name = argument.split("=", 1)[0]
        if name.startswith("--") and name not in (
            "--live", "--backend", "--output-dir", "--help",
        ):
            raise SystemExit("Use full option names; P00 supports offline options only.")


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Local checks only; workdir is accepted for the common course interface."""
    if live:
        raise ValueError("P00 does not perform live calls.")
    del workdir  # No report files or environment files are needed by this module.
    inventory = inspect_environment()
    with tracing_context(enabled=False):
        result = build_graph().invoke(
            {"label": " learner "}, config=execution_config(),
        )
    assert result["label"] == "learner"
    assert result["checks"] == ["label_checked", "graph_completed"]
    assert result["message"] == "Offline setup graph ready for learner."
    endpoints = {service: validate_endpoint(service) for service in ORIGINS}
    assert validate_endpoint(
        "langsmith", " https://eu.api.smith.langchain.com:443/ ",
    ) == "https://eu.api.smith.langchain.com"
    rejected = 0
    for service, endpoint in (
        ("langsmith", "https://smith.langchain.com"),
        ("langwatch", "http://app.langwatch.ai"),
        ("anthropic", "https://api.anthropic.com/v1/messages"),
    ):
        try:
            validate_endpoint(service, endpoint)
        except ValueError:
            rejected += 1
    assert rejected == 3
    return {
        "environment": inventory,
        "graph_checks": result["checks"],
        "message": result["message"],
        "supported_endpoints": endpoints,
        "unsafe_examples_rejected": rejected,
        "remote_checked": False,
        "environment_file_read": False,
    }


if __name__ == "__main__":
    reject_remote_options(sys.argv[1:])
    run_cli("P00", run_demo)
