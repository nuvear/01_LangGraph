"""Offline P00 tests: no model, environment-file access or network is permitted."""
from __future__ import annotations

import builtins
from importlib import metadata
import io
import json
from pathlib import Path
import runpy
import socket
import sys

import pytest

from course_lessons import p00 as demo
from exercises.solutions import p00 as solution
from exercises.starters import p00 as starter


@pytest.fixture(autouse=True)
def forbid_environment_files_and_network(monkeypatch):
    """Fail, rather than silently skip, on accidental secret/network access."""
    import dotenv
    from course_support import check_connections, observability, runtime

    def forbidden(*args, **kwargs):
        raise AssertionError("P00 must not load configuration or contact a service.")

    for module in (check_connections, observability, runtime):
        monkeypatch.setattr(module, "values", forbidden)
    monkeypatch.setattr(check_connections, "dotenv_values", forbidden)
    monkeypatch.setattr(dotenv, "dotenv_values", forbidden)
    monkeypatch.setattr(dotenv, "load_dotenv", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden)
    original_open = builtins.open
    original_io_open = io.open

    def guarded_open(file, *args, **kwargs):
        if isinstance(file, (str, bytes, Path)):
            name = Path(file.decode() if isinstance(file, bytes) else file).name
            if name == ".env" or name.startswith(".env."):
                raise AssertionError("P00 must not access environment files.")
        return original_open(file, *args, **kwargs)

    def guarded_io_open(file, *args, **kwargs):
        if isinstance(file, (str, bytes, Path)):
            name = Path(file.decode() if isinstance(file, bytes) else file).name
            if name == ".env" or name.startswith(".env."):
                raise AssertionError("P00 must not access environment files.")
        return original_io_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(io, "open", guarded_io_open)


class InstalledPackageInventory:
    """Named local metadata double, not a model or service response."""
    def __init__(self, missing=()):
        self.missing = missing

    def __call__(self, name):
        if name in self.missing:
            raise metadata.PackageNotFoundError(name)
        return "1.0.0-test"


def test_environment_inventory_and_missing_package():
    report = demo.inspect_environment(
        python_version=(3, 12), prefixes=("venv", "base"),
        version_reader=InstalledPackageInventory(),
    )
    assert report["ready"] is True
    assert set(report["packages"]) == set(demo.PACKAGES)
    broken = demo.inspect_environment(
        python_version=(3, 11), prefixes=("base", "base"),
        version_reader=InstalledPackageInventory(missing=("pytest",)),
    )
    assert broken["ready"] is False
    assert broken["python_supported"] is False
    assert broken["virtual_environment"] is False
    assert broken["missing_packages"] == ["pytest"]
    assert broken["packages"]["pytest"] == "not_installed"


@pytest.mark.parametrize("module", [demo, solution])
@pytest.mark.parametrize("service,endpoint,expected", [
    ("anthropic", "", "https://api.anthropic.com"),
    ("langwatch", " ", "https://app.langwatch.ai"),
    ("langsmith", "", "https://api.smith.langchain.com"),
    ("langsmith", " https://eu.api.smith.langchain.com:443/ ",
     "https://eu.api.smith.langchain.com"),
    ("langsmith", "https://apac.api.smith.langchain.com",
     "https://apac.api.smith.langchain.com"),
    ("langsmith", "https://aws.api.smith.langchain.com/",
     "https://aws.api.smith.langchain.com"),
    ("langwatch", "HTTPS://APP.LANGWATCH.AI", "https://app.langwatch.ai"),
])
def test_supported_endpoints(module, service, endpoint, expected):
    assert module.validate_endpoint(service, endpoint) == expected


@pytest.mark.parametrize("module", [demo, solution])
@pytest.mark.parametrize("endpoint", [
    "http://app.langwatch.ai", "https://app.langwatch.ai.attacker.invalid",
    "https://app.langwatch.ai@attacker.invalid", "https://token@app.langwatch.ai",
    "https://user:password@app.langwatch.ai", "https://app.langwatch.ai/api",
    "https://app.langwatch.ai?token=SYNTHETIC_SECRET", "https://app.langwatch.ai?",
    "https://app.langwatch.ai#", "https://app.langwatch.ai:80",
    "https://app.langwatch.ai:invalid", "https://app.langwatch.ai:",
    "https://app.langwatch.ai:0443", "https://app.langwatch.ai//",
    "https://app.langwatch.ai\\", "https://app.langwatch.ai/\npath",
    "https://app.\tlangwatch.ai", "https://[malformed",
])
def test_unsafe_endpoints_never_echo_inputs(module, endpoint):
    with pytest.raises(ValueError) as error:
        module.validate_endpoint("langwatch", endpoint)
    assert endpoint not in str(error.value)
    assert "SYNTHETIC_SECRET" not in str(error.value)


@pytest.mark.parametrize("module", [demo, solution])
def test_wrong_service_and_dashboard_host(module):
    with pytest.raises(ValueError, match="Unsupported service"):
        module.validate_endpoint("unknown")
    with pytest.raises(ValueError):
        module.validate_endpoint("langsmith", "https://smith.langchain.com")
    with pytest.raises(ValueError):
        module.validate_endpoint("anthropic", "https://api.anthropic.com/v1/messages")


def test_demo_graph_updates_and_independent_invocations():
    graph = demo.build_graph()
    for label in (" first ", "second"):
        result = graph.invoke({"label": label}, config=demo.execution_config())
        assert result["label"] == label.strip()
        assert result["checks"] == ["label_checked", "graph_completed"]
    state = {"label": " spaced "}
    assert demo.check_label(state)["label"] == "spaced"
    assert state == {"label": " spaced "}
    with pytest.raises(ValueError, match="nonempty"):
        graph.invoke({"label": "  "}, config=demo.execution_config())


def test_exact_workbook_ready_and_repair_profiles():
    before = dict(solution.READY_PROFILE)
    ready = solution.run_profile(solution.READY_PROFILE)
    repair = solution.run_profile(solution.REPAIR_PROFILE)
    assert solution.READY_PROFILE == before
    assert ready["status"] == "ready" and ready["issues"] == []
    assert ready["remote_checked"] is False
    assert ready["message"] == "Local profile ready."
    assert repair["issues"] == [
        "model_invalid", "langsmith_endpoint_invalid", "langwatch_project_required",
    ]
    assert repair["endpoints"] == {"langwatch": "https://app.langwatch.ai"}
    assert repair["message"] == "Repair public settings."


@pytest.mark.parametrize("kind,project,issues", [
    ("project", "", []), ("service", "id", []), ("personal", "id", []),
    ("service", "  ", ["langwatch_project_required"]),
    ("personal", "", ["langwatch_project_required"]),
    ("unknown", "", ["langwatch_key_kind_invalid"]),
])
def test_langwatch_scope_policy(kind, project, issues):
    profile = {**solution.READY_PROFILE, "langwatch_key_kind": kind,
               "langwatch_project_id": project}
    assert solution.check_profile(profile)["issues"] == issues


def test_profile_defaults_backend_and_always_checked_origins():
    minimal = solution.check_profile({"model": "claude-course-example"})
    assert minimal["status"] == "ready"
    assert len(minimal["endpoints"]) == 2
    report = solution.check_profile({
        "model": "bad", "backend": "invalid",
        "langsmith_endpoint": "http://api.smith.langchain.com",
        "langwatch_endpoint": "https://app.langwatch.ai?",
    })
    assert report["issues"] == [
        "model_invalid", "backend_invalid", "langsmith_endpoint_invalid",
        "langwatch_endpoint_invalid",
    ]
    report = solution.check_profile({
        "model": "claude-course-example", "backend": "none",
        "langwatch_endpoint": "http://app.langwatch.ai",
        "langwatch_key_kind": "unknown",
    })
    assert report["issues"] == ["langwatch_endpoint_invalid"]


@pytest.mark.parametrize("profile,issue", [
    ({"api_key": "SYNTHETIC_SECRET"}, "unsupported_fields"),
    ({"model": None}, "invalid_value_type"),
])
def test_unexpected_profile_fields_never_enter_graph_state(monkeypatch, profile, issue):
    captured = []

    class CapturingLocalGraph:
        def invoke(self, state, config):
            captured.append(state)
            assert config["recursion_limit"] == 40
            return {**state, "message": "Repair public settings."}

    monkeypatch.setattr(solution, "build_graph", CapturingLocalGraph)
    result = solution.run_profile(profile)
    assert result["issues"] == [issue]
    assert result["endpoints"] == {}
    assert "SYNTHETIC_SECRET" not in json.dumps(captured)
    assert "SYNTHETIC_SECRET" not in json.dumps(result)


@pytest.mark.parametrize("status,action", [
    (None, "Check network, DNS, proxy and TLS; never disable certificate checks."),
    (401, "Verify or rotate the key privately; do not print it."),
    (403, "Check organization/workspace permissions and model access."),
    (404, "Check the configured model ID and API resource path."),
    (429, "Check rate and spend limits; honor Retry-After when present."),
    (529, "Wait and retry within a bounded backoff budget."),
    (418, "Record a sanitized status and request ID; consult official errors."),
])
def test_exact_offline_triage(status, action):
    assert solution.classify_failure(status) == action


@pytest.mark.parametrize("module", [demo, solution])
def test_both_run_demo_interfaces(module, tmp_path):
    result = module.run_demo(workdir=tmp_path)
    json.dumps(result)
    assert result["remote_checked"] is False
    assert result["environment_file_read"] is False
    assert list(tmp_path.iterdir()) == []
    with pytest.raises(ValueError, match="live"):
        module.run_demo(live=True, workdir=tmp_path)


@pytest.mark.parametrize("module_name", ["course_lessons.p00", "exercises.solutions.p00"])
def test_default_cli_uses_no_environment_or_network(module_name, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [module_name, "--backend", "none",
                                     "--output-dir", str(tmp_path)])
    # Importing the module earlier allows direct unit tests; runpy's warning
    # here is expected, not an execution or network failure.
    with pytest.warns(RuntimeWarning, match="found in sys.modules"):
        runpy.run_module(module_name, run_name="__main__")
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "passed"
    assert output["live_api_enabled"] is False
    assert output["backend"] == "none"
    assert output["result"]["remote_checked"] is False


@pytest.mark.parametrize("module_name", ["course_lessons.p00", "exercises.solutions.p00"])
@pytest.mark.parametrize("arguments", [
    ["--live"], ["--backend", "langsmith"], ["--backend=both"],
    ["--backend", "langwatch"], ["--back=langsmith"], ["--li"],
])
def test_cli_rejects_remote_options_before_shared_runtime(module_name, arguments, monkeypatch):
    monkeypatch.setattr(sys, "argv", [module_name, *arguments])
    with pytest.warns(RuntimeWarning, match="found in sys.modules"):
        with pytest.raises(SystemExit):
            runpy.run_module(module_name, run_name="__main__")


def test_unfinished_starter_is_honest(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["p00"])
    starter.main()
    output = capsys.readouterr().out
    assert "STARTER_NOT_COMPLETED" in output
    assert "CHECKS_PASSED" not in output


def test_starter_scaffolding_matches_reference_task(monkeypatch):
    # Inject completed pure functions solely to check the supplied scaffolding.
    for name in ("validate_endpoint", "check_profile", "classify_failure"):
        monkeypatch.setattr(starter, name, getattr(solution, name))
    starter.verify_work()
