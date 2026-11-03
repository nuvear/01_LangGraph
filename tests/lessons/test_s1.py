"""Offline S1 tests. Every model here is an explicitly named test double.

No credentials, configuration files, API calls, or tracing ingestion are used.
Run only this file: python -m pytest tests/lessons/test_s1.py -q
"""
from __future__ import annotations

import json
from pathlib import Path
import socket
from typing import Any
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langsmith import tracing_context
import pytest

from course_lessons import s1 as demo
from course_support import check_connections, observability, runtime
from exercises.solutions import s1 as solution
from exercises.starters import s1 as starter


class ReceiptEchoChatModel(BaseChatModel):
    """Explicit OFFLINE double; no provider/client is instantiated."""
    behavior: str = "echo"
    calls: int = 0

    @property
    def _llm_type(self) -> str:
        return "explicit-offline-s1-receipt-double"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.calls += 1
        if self.behavior == "raise":
            raise RuntimeError("Synthetic offline model failure")
        receipt = json.loads(messages[-1].content)
        assert set(receipt) == {"total", "unit", "source"}
        if self.behavior == "always_bad":
            text = "not JSON"
        elif self.behavior == "bad_once" and self.calls == 1:
            text = "```json\n{}\n```"
        else:
            if self.behavior == "wrong_amount":
                receipt["total"] += 1
            if self.behavior == "wrong_source":
                receipt["source"] = "untrusted-policy"
            text = json.dumps(receipt)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])


class RecordingCallbacks(BaseCallbackHandler):
    """Record local LangChain callback ancestry, never export telemetry."""
    def __init__(self):
        self.events: list[dict] = []

    def on_chain_start(self, serialized, inputs, *, run_id, parent_run_id=None,
                       **kwargs):
        self.events.append({"kind": "chain", "run_id": run_id,
                            "parent": parent_run_id, "inputs": inputs})

    def on_chat_model_start(self, serialized, messages, *, run_id,
                            parent_run_id=None, **kwargs):
        self.events.append({"kind": "model", "run_id": run_id,
                            "parent": parent_run_id})

    def on_tool_start(self, serialized, input_str, *, run_id,
                      parent_run_id=None, **kwargs):
        self.events.append({"kind": "tool", "run_id": run_id,
                            "parent": parent_run_id})


@pytest.fixture(autouse=True)
def forbid_network_and_settings(monkeypatch):
    def forbidden(*args: Any, **kwargs: Any):
        raise AssertionError("S1 offline tests must not access settings/network")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(check_connections, "values", forbidden)
    monkeypatch.setattr(runtime, "values", forbidden)
    monkeypatch.setattr(observability, "values", forbidden)
    with tracing_context(enabled=False):
        yield


def parse(module, text):
    decoder = demo.parse_receipt if module is demo else module.decode_receipt
    return decoder(text)


@pytest.mark.parametrize("module", [demo, solution], ids=["demo", "solution"])
def test_evaluation_reports_and_callback_ancestry(module, tmp_path, monkeypatch):
    recorder = RecordingCallbacks()
    monkeypatch.setattr(module, "execution_config", lambda: {
        "callbacks": [recorder], "recursion_limit": 40, "tags": ["offline-test"],
    })
    model = ReceiptEchoChatModel()
    summary = module.run_evaluation(model, workdir=tmp_path)
    report = json.loads(Path(summary["report_path"]).read_text())
    assert summary["passed"] == summary["examples"] == 3
    assert summary["model_calls"] == model.calls == 3
    assert report["langsmith_experiment_created"] is False
    assert report["dashboard_visually_verified"] is False
    for row in report["rows"]:
        assert row["path"] == ["quote", "format", "check"]
        assert all(row["checks"].values())
        assert row["elapsed_ms"] >= 0
        UUID(row["run_id"])
    roots = [event for event in recorder.events
             if event["kind"] == "chain" and event["parent"] is None]
    assert {str(event["run_id"]) for event in roots} == {
        row["run_id"] for row in report["rows"]
    }
    for root in roots:
        assert "reference_outputs" not in root["inputs"]
    for kind in ["tool", "model"]:
        children = [event for event in recorder.events if event["kind"] == kind]
        assert len(children) == 3
        assert all(event["parent"] is not None for event in children)
        chain_ids = {event["run_id"] for event in recorder.events
                     if event["kind"] == "chain"}
        assert all(event["parent"] in chain_ids for event in children)


@pytest.mark.parametrize("module", [demo, solution], ids=["demo", "solution"])
def test_malformed_then_valid_retries_once_without_repeating_tool(module):
    model = ReceiptEchoChatModel(behavior="bad_once")
    outputs = module.build_graph(model).invoke(
        {**module.EXAMPLES[0]["inputs"], "attempts": 0, "trace_log": []},
        config={"callbacks": [], "recursion_limit": 40},
    )
    assert outputs["attempts"] == model.calls == 2
    assert outputs["trace_log"] == ["quote", "format", "check", "format", "check"]
    assert outputs["format_ok"]
    assert all(module.evaluate_receipt(
        outputs, module.EXAMPLES[0]["reference_outputs"]
    ).values())


@pytest.mark.parametrize("module", [demo, solution], ids=["demo", "solution"])
def test_bad_format_terminates_at_two_and_persists_failed_report(module, tmp_path):
    model = ReceiptEchoChatModel(behavior="always_bad")
    with pytest.raises(AssertionError, match="Evaluation failed"):
        module.run_evaluation(model, workdir=tmp_path)
    reports = list(tmp_path.glob("*.txt"))
    assert len(reports) == 1
    report = json.loads(reports[0].read_text())
    assert report["passed"] == 0
    assert model.calls == 6
    assert all(row["attempts"] == 2 for row in report["rows"])
    assert all(not row["checks"]["schema_ok"] for row in report["rows"])
    assert all(row["path"].count("quote") == 1 for row in report["rows"])


@pytest.mark.parametrize("module", [demo, solution], ids=["demo", "solution"])
@pytest.mark.parametrize("behavior,metric", [
    ("wrong_amount", "amount_ok"), ("wrong_source", "source_ok"),
])
def test_valid_json_is_not_automatically_correct(module, behavior, metric, tmp_path):
    model = ReceiptEchoChatModel(behavior=behavior)
    with pytest.raises(AssertionError, match="Evaluation failed"):
        module.run_evaluation(model, workdir=tmp_path)
    report = json.loads(next(tmp_path.glob("*.txt")).read_text())
    assert model.calls == 3  # Schema-valid factual errors do not trigger repair.
    assert all(row["checks"]["schema_ok"] for row in report["rows"])
    assert all(not row["checks"][metric] for row in report["rows"])


@pytest.mark.parametrize("module", [demo, solution], ids=["demo", "solution"])
@pytest.mark.parametrize("raw", [
    "not JSON", "[]", "null", "{}",
    '{"total":true,"unit":"credits","source":"policy"}',
    '{"total":2.0,"unit":"credits","source":"policy"}',
    '{"total":2,"unit":"money","source":"policy"}',
    '{"total":2,"unit":"credits","source":"  "}',
    '{"total":2,"unit":"credits","source":"policy","extra":1}',
    '```json\n{"total":2,"unit":"credits","source":"policy"}\n```',
])
def test_strict_schema_rejects_invalid_receipts(module, raw):
    assert parse(module, raw) == {}


@pytest.mark.parametrize("module", [demo, solution], ids=["demo", "solution"])
def test_whitespace_and_key_order_are_not_semantic_errors(module):
    text = ' { "source": "policy", "unit": "credits", "total": 12 } '
    assert parse(module, text) == {
        "total": 12, "unit": "credits", "source": "policy",
    }


@pytest.mark.parametrize("weight", [0, -1, 11, True, 2.0, "2"])
def test_shipping_quote_rejects_bad_weights(weight):
    with pytest.raises(ValueError):
        solution.shipping_quote("local", weight)


def test_shipping_quote_boundaries_and_regions():
    assert solution.shipping_quote("local", 1)["total"] == 5
    assert solution.shipping_quote("regional", 10)["total"] == 35
    with pytest.raises(ValueError):
        solution.shipping_quote("overseas", 2)


@pytest.mark.parametrize("module", [demo, solution], ids=["demo", "solution"])
def test_model_error_propagates_without_fake_report(module, tmp_path):
    with pytest.raises(RuntimeError, match="Synthetic offline model failure"):
        module.run_evaluation(
            ReceiptEchoChatModel(behavior="raise"), workdir=tmp_path
        )
    assert not list(tmp_path.glob("*.txt"))


@pytest.mark.parametrize("module", [demo, solution], ids=["demo", "solution"])
def test_invalid_tool_input_fails_before_model_call(module):
    inputs = ({"plan": "unknown", "seats": 1} if module is demo
              else {"region": "overseas", "weight": 1})
    model = ReceiptEchoChatModel()
    with pytest.raises(ValueError):
        module.build_graph(model).invoke(
            {**inputs, "attempts": 0, "trace_log": []},
            config={"callbacks": [], "recursion_limit": 40},
        )
    assert model.calls == 0


@pytest.mark.parametrize("module", [demo, solution], ids=["demo", "solution"])
def test_missing_evidence_fails_even_with_correct_model_json(module):
    reference = module.EXAMPLES[0]["reference_outputs"]
    outputs = {"raw": json.dumps({**reference, "unit": "credits"}), "attempts": 3}
    checks = module.evaluate_receipt(outputs, reference)
    assert checks["schema_ok"] and checks["amount_ok"] and checks["source_ok"]
    assert not checks["bounded_attempts"]
    assert not checks["tool_evidence"]
    assert not any(module.evaluate_receipt({}, reference).values())


@pytest.mark.parametrize("module", [demo, solution], ids=["demo", "solution"])
def test_run_demo_requires_explicit_live_opt_in_without_settings(module, tmp_path):
    with pytest.raises(ValueError, match="needs --live"):
        module.run_demo(live=False, workdir=tmp_path)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("module", [demo, solution], ids=["demo", "solution"])
def test_live_entry_wiring_uses_injected_double_not_real_service(
    module, tmp_path, monkeypatch
):
    requested = []

    def explicit_model_factory(*, live, max_tokens):
        requested.append((live, max_tokens))
        return ReceiptEchoChatModel()

    monkeypatch.setattr(module, "get_model", explicit_model_factory)
    assert module.run_demo(live=True, workdir=tmp_path)["passed"] == 3
    assert requested == [(True, 192)]


@pytest.mark.parametrize("module", [demo, solution], ids=["demo", "solution"])
def test_report_does_not_overwrite_previous_evidence(module, tmp_path):
    summary = module.run_evaluation(ReceiptEchoChatModel(), workdir=tmp_path)
    path = Path(summary["report_path"])
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        module.run_evaluation(ReceiptEchoChatModel(), workdir=tmp_path)
    assert path.read_bytes() == before


def test_starter_reports_incomplete_without_model_or_configuration(
    capsys, monkeypatch
):
    def unfinished_quote(*args, **kwargs):
        raise NotImplementedError("TODO 1: simulated unfinished learner function")

    monkeypatch.setattr(starter, "shipping_quote", unfinished_quote)
    starter.main()
    text = capsys.readouterr().out
    assert "STARTER_NOT_COMPLETED" in text
    assert "passed" not in text.lower()


def test_completed_starter_contract_when_implemented(tmp_path):
    try:
        quote = starter.shipping_quote("local", 2)
        starter.decode_receipt("{}")
        starter.evaluate_receipt({}, {"total": 7, "source": starter.SOURCE})
    except NotImplementedError:
        pytest.skip("STARTER_NOT_COMPLETED: implement the three S1 TODOs first")
    assert quote == {"total": 7, "unit": "credits", "source": starter.SOURCE}
    assert starter.shipping_quote("regional", 3)["total"] == 14
    assert starter.shipping_quote("local", 1)["total"] == 5
    for weight in (0, 11, True, 2.0, "2"):
        with pytest.raises(ValueError):
            starter.shipping_quote("local", weight)
    with pytest.raises(ValueError):
        starter.shipping_quote("overseas", 1)
    for raw in ("not JSON", "[]", "null", "{}", "```json\n{}\n```",
                '{"total":true,"unit":"credits","source":"policy"}',
                '{"total":5,"unit":"credits","source":"  "}'):
        assert starter.decode_receipt(raw) == {}
    good = json.dumps({"total": 7, "unit": "credits", "source": starter.SOURCE})
    assert starter.decode_receipt(good)["total"] == 7
    actual = {"raw": good, "attempts": 1, "tool_result": quote,
              "trace_log": ["quote", "format", "check"]}
    reference = {"total": 7, "source": starter.SOURCE}
    checks = starter.evaluate_receipt(actual, reference)
    assert set(checks) == {"schema_ok", "amount_ok", "source_ok",
                           "bounded_attempts", "tool_evidence"}
    assert all(type(value) is bool and value for value in checks.values())
    wrong = {**actual, "raw": good.replace('"total": 7', '"total": 8')}
    assert not starter.evaluate_receipt(wrong, reference)["amount_ok"]
    missing = starter.evaluate_receipt({}, reference)
    assert not any(missing.values())
    summary = starter.run_evaluation(ReceiptEchoChatModel(), workdir=tmp_path)
    assert summary["passed"] == 3


@pytest.mark.parametrize("module", [demo, solution], ids=["demo", "solution"])
@pytest.mark.parametrize("value", [True, 2.0, "2"])
def test_raw_graph_input_rejects_coercion_before_tool_or_model(module, value):
    inputs = ({"plan": "basic", "seats": value} if module is demo
              else {"region": "local", "weight": value})
    model = ReceiptEchoChatModel()
    with pytest.raises(ValueError, match="must be an integer"):
        module.build_graph(model).invoke(
            {**inputs, "attempts": 0, "trace_log": []},
            config={"callbacks": [], "recursion_limit": 40},
        )
    assert model.calls == 0


def test_starter_scaffolding_accepts_matching_reference_functions(
    tmp_path, monkeypatch
):
    # Validate supplied starter plumbing without filling in the learner's file.
    for name in ("shipping_quote", "decode_receipt", "evaluate_receipt"):
        monkeypatch.setattr(starter, name, getattr(solution, name))
    test_completed_starter_contract_when_implemented(tmp_path)
