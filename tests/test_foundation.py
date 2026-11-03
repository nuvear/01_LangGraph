"""Offline checks; no .env reads or paid API calls are needed."""
from pathlib import Path

import pytest

from course_support import check_connections as checks
from course_support.observability import graph_tracing
from examples.observability_demo import build_graph


@pytest.mark.parametrize("value,expected", [(2, 3), (0, 1), (-2, -1), (100, 101)])
def test_two_node_graph(value, expected):
    result = build_graph().invoke({"value": value})
    assert result == {"value": value, "result": expected, "label": f"Result: {expected}"}


def test_tracing_disabled_does_not_read_credentials(monkeypatch):
    def forbidden():
        raise AssertionError("No credentials should be read for backend=none")
    monkeypatch.setattr("course_support.observability.values", forbidden)
    with graph_tracing("none") as config:
        assert config == {"callbacks": []}
        assert build_graph().invoke({"value": 2}, config=config)["result"] == 3


def test_invalid_backend():
    with pytest.raises(ValueError):
        with graph_tracing("unknown"):
            pass


@pytest.mark.parametrize("endpoint", [
    "http://app.langwatch.ai", "https://evil.example", "https://app.langwatch.ai@evil.example",
    "https://user:password@app.langwatch.ai", "https://app.langwatch.ai/?token=secret",
    "https://app.langwatch.ai/unexpected", "https://app.langwatch.ai:8443",
])
def test_endpoint_rejects_untrusted_or_credential_bearing_urls(endpoint):
    with pytest.raises(ValueError):
        checks.safe_endpoint(endpoint, "https://app.langwatch.ai", {"app.langwatch.ai"})


def test_endpoint_default():
    assert checks.safe_endpoint("", "https://app.langwatch.ai", {"app.langwatch.ai"}) == "https://app.langwatch.ai"


@pytest.mark.parametrize("service", ["anthropic", "langsmith", "langwatch"])
def test_missing_keys_fail_before_network(service):
    result = {"anthropic": checks.test_anthropic, "langsmith": checks.test_langsmith,
              "langwatch": checks.test_langwatch}[service]({})
    assert result["status"] == "configuration_error"


def test_error_output_never_contains_a_key(monkeypatch, tmp_path, capsys):
    secret = "synthetic-secret-never-a-real-api-key"
    def fail(config):
        raise RuntimeError("An unsafe upstream exception contains " + config["ANTHROPIC_API_KEY"])
    monkeypatch.setattr(checks, "test_anthropic", fail)
    monkeypatch.setattr(checks, "REPORT_DIR", tmp_path)
    report = checks.run("anthropic", {"ANTHROPIC_API_KEY": secret})
    assert report["status"] == "failed"
    assert secret not in capsys.readouterr().out
    assert secret not in (tmp_path / "anthropic_connection.json").read_text()


def test_success_output_redacts_accidental_key(monkeypatch, tmp_path, capsys):
    secret = "synthetic-secret-never-a-real-api-key"
    monkeypatch.setattr(checks, "test_anthropic", lambda config: {"status": "passed", "response_text": secret})
    monkeypatch.setattr(checks, "REPORT_DIR", tmp_path)
    checks.run("anthropic", {"ANTHROPIC_API_KEY": secret})
    assert secret not in capsys.readouterr().out
    assert secret not in (tmp_path / "anthropic_connection.json").read_text()
