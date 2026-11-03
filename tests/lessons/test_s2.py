"""Offline tests only: named model doubles, local callbacks, no service traffic."""
from __future__ import annotations

from contextlib import contextmanager
import json
import socket
import sys

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langsmith import tracing_context
from pydantic import Field
import pytest

from course_lessons import s2 as demo
from course_support import check_connections, runtime
from exercises.solutions import s2 as solution
from exercises.starters import s2 as starter


class ScriptedChatModelDouble(BaseChatModel):
    """Explicit offline double that emits real LangChain local callback events."""

    responses: list[AIMessage]
    seen_messages: list[list] = Field(default_factory=list)
    binding: dict = Field(default_factory=dict)

    @property
    def _llm_type(self) -> str:
        return "s2-offline-scripted-test-double"

    def bind_tools(self, tools, **kwargs):
        self.binding = {"names": [item.name for item in tools], **kwargs}
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.seen_messages.append(list(messages))
        if not self.responses:
            raise AssertionError("The explicit offline double ran out of messages.")
        return ChatResult(generations=[ChatGeneration(
            message=self.responses.pop(0)
        )])


class LocalEventRecorder(BaseCallbackHandler):
    """Record local events; this is not an exporter and proves no ingestion."""

    def __init__(self):
        self.nodes = []
        self.tools = []
        self.models = 0
        self.retrievals = []

    def on_chain_start(self, serialized, inputs, **kwargs):
        self.nodes.append(kwargs.get("name"))

    def on_chat_model_start(self, serialized, messages, **kwargs):
        self.models += 1

    def on_tool_start(self, serialized, input_str, **kwargs):
        self.tools.append(serialized.get("name"))

    def on_retriever_start(self, serialized, query, **kwargs):
        self.retrievals.append(query)


def tool_request(name, arguments, call_id="offline-call-1"):
    return AIMessage(content="", tool_calls=[{
        "name": name, "args": arguments, "id": call_id, "type": "tool_call",
    }])


def demo_double():
    return ScriptedChatModelDouble(responses=[
        tool_request("add_numbers", {"a": 18, "b": 24}),
        AIMessage(content="The synthetic sum is 42."),
    ])


def solution_double(document_ids=("TRACE-101",)):
    messages = []
    for document_id in document_ids:
        messages.extend([
            tool_request("lookup_handout", {"document_id": document_id}),
            AIMessage(content="Offline double final response; not a live result."),
        ])
    return ScriptedChatModelDouble(responses=messages)


@pytest.fixture(autouse=True)
def prevent_configuration_and_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("S2 offline tests must not load .env or use network.")

    monkeypatch.setattr(check_connections, "values", forbidden)
    monkeypatch.setattr(runtime, "values", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    with tracing_context(enabled=False):
        yield


def test_demo_real_local_callback_tree_and_tool_id():
    model = demo_double()
    recorder = LocalEventRecorder()
    result = demo.build_graph(model).invoke(
        demo.initial_state(), {"callbacks": [recorder], "recursion_limit": 40}
    )
    assert result["tool_results"] == ["42"]
    assert result["events"] == ["prepare", "agent", "tools", "agent", "finish"]
    assert result["model_calls"] == recorder.models == 2
    assert {"prepare", "agent", "tools", "finish"} <= set(recorder.nodes)
    assert recorder.tools == ["add_numbers"]
    assert model.binding["tool_choice"] == "auto"
    assert model.binding["parallel_tool_calls"] is False
    observation = next(m for m in model.seen_messages[1] if isinstance(m, ToolMessage))
    assert observation.tool_call_id == "offline-call-1"
    assert observation.content == "42"


@pytest.mark.parametrize("document_id,status,count", [
    ("TRACE-101", "supported", 1), ("MISSING-999", "no_evidence", 0),
])
def test_solution_found_and_empty_retriever_paths(document_id, status, count):
    model = solution_double((document_id,))
    recorder = LocalEventRecorder()
    result = solution.build_graph(model).invoke(
        solution.initial_state(document_id),
        {"callbacks": [recorder], "recursion_limit": 40},
    )
    assert result["status"] == status
    assert len(result["evidence"]["documents"]) == count
    assert result["model_calls"] == recorder.models == 2
    assert recorder.tools == ["lookup_handout"]
    assert recorder.retrievals == [document_id]
    assert result["events"] == ["prepare", "agent", "tools", "agent", "finish"]
    observation = next(m for m in model.seen_messages[1] if isinstance(m, ToolMessage))
    assert observation.tool_call_id == "offline-call-1"
    if count:
        item = result["evidence"]["documents"][0]
        assert item == {
            "id": "TRACE-101", "source": "synthetic-s2-handout", "page": 1,
            "text": solution.DOCUMENT_TEXT,
        }


@pytest.mark.parametrize("module,tool_name,args", [
    (demo, "add_numbers", {"a": 18, "b": 24}),
    (solution, "lookup_handout", {"document_id": "TRACE-101"}),
])
@pytest.mark.parametrize("failure", ["absent", "multiple", "unknown", "repeat", "empty"])
def test_bounded_failure_paths(module, tool_name, args, failure):
    first = tool_request(tool_name, args)
    second = AIMessage(content="Done.")
    error = ValueError
    if failure == "absent":
        first = AIMessage(content="I skipped the required tool.")
    elif failure == "multiple":
        first = AIMessage(content="", tool_calls=[
            {"name": tool_name, "args": args, "id": str(i), "type": "tool_call"}
            for i in range(2)
        ])
    elif failure == "unknown":
        first = tool_request("unapproved_tool", args)
    elif failure == "repeat":
        second = tool_request(tool_name, args, "offline-call-2")
        error = RuntimeError
    elif failure == "empty":
        second = AIMessage(content="  ")
    model = ScriptedChatModelDouble(responses=[first, second])
    state = demo.initial_state() if module is demo else solution.initial_state("TRACE-101")
    with pytest.raises(error):
        module.build_graph(model).invoke(state, {"callbacks": [], "recursion_limit": 40})
    assert len(model.seen_messages) <= 2


@pytest.mark.parametrize("module", [demo, solution])
def test_model_budget_prevents_extra_call(module):
    model = ScriptedChatModelDouble(responses=[])
    state = demo.initial_state() if module is demo else solution.initial_state("TRACE-101")
    state["model_calls"] = 2
    with pytest.raises(RuntimeError, match="Model call budget"):
        module.build_graph(model).invoke(state, {"callbacks": []})
    assert model.seen_messages == []


def test_solution_rejects_changed_id_and_blank_input():
    model = solution_double(("OTHER",))
    with pytest.raises(ValueError, match="changed"):
        solution.build_graph(model).invoke(solution.initial_state("TRACE-101"))
    model = solution_double()
    with pytest.raises(ValueError, match="blank"):
        solution.build_graph(model).invoke(solution.initial_state(" "))
    assert model.seen_messages == []


@pytest.mark.parametrize("backend,recipients", [
    ("none", []), ("langsmith", ["LangSmith"]),
    ("langwatch", ["LangWatch"]), ("both", ["LangSmith", "LangWatch"]),
])
def test_privacy_plans_do_not_claim_redaction(backend, recipients):
    plan = solution.privacy_plan(backend)
    assert plan["telemetry_recipients"] == recipients
    assert plan["model_recipient"] == "Anthropic when --live is used"
    assert plan["root_capture_is_child_redaction"] is False
    assert plan["plan_only"] is True


def test_privacy_plan_rejects_unknown_backend():
    with pytest.raises(ValueError):
        solution.privacy_plan("mystery")


def checker_fixture():
    return {
        "service": "langwatch", "status": "passed", "http_status": 200,
        "ingestion_acknowledged": True, "rejected_spans": 0,
        "dashboard_visually_verified": False,
    }


def test_ingestion_ack_does_not_prove_lesson_ingestion_or_ui():
    evidence = solution.classify_ingestion(checker_fixture())
    assert evidence == {
        "checker_ingestion": "acknowledged", "lesson_trace_ingestion": "not_checked",
        "dashboard_visibility": "not_checked",
    }


@pytest.mark.parametrize("change", [
    {"rejected_spans": 1}, {"rejected_spans": "0"}, {"rejected_spans": False},
    {"http_status": 401}, {"status": "failed"}, {"service": "langsmith"},
    {"ingestion_acknowledged": False}, {"ingestion_acknowledged": "true"},
])
def test_partial_or_failed_checker_does_not_pass(change):
    evidence = solution.classify_ingestion({**checker_fixture(), **change})
    assert evidence["checker_ingestion"] == "not_established"
    assert evidence["dashboard_visibility"] == "not_checked"


def test_missing_checker_fields_do_not_pass():
    assert solution.classify_ingestion({})["checker_ingestion"] == "not_established"
    report = checker_fixture()
    del report["rejected_spans"]
    assert solution.classify_ingestion(report)["checker_ingestion"] == "not_established"


@pytest.mark.parametrize("module", [demo, solution])
def test_run_demo_writes_real_checked_local_report_using_offline_double(
    module, monkeypatch, tmp_path
):
    factory = demo_double if module is demo else lambda: solution_double(
        ("TRACE-101", "MISSING-999")
    )
    monkeypatch.setattr(module, "get_model", lambda **kwargs: factory())
    monkeypatch.setattr(module, "execution_config", lambda: {"callbacks": []})
    result = module.run_demo(workdir=tmp_path)
    report = tmp_path / ("s2-demo.txt" if module is demo else "s2-solution.txt")
    stored = json.loads(report.read_text())
    assert result["report"] == str(report)
    if module is demo:
        assert stored["tool_results"] == ["42"]
        assert stored["ingestion_acknowledged"] == "not_checked"
    else:
        assert [item["status"] for item in stored["cases"]] == [
            "supported", "no_evidence"
        ]
        assert stored["remote_evidence"]["checker_ingestion"] == "not_established"
    with pytest.raises(FileExistsError):
        module.run_demo(workdir=tmp_path)


@pytest.mark.parametrize("module", [demo, solution])
def test_live_opt_in_required_without_any_configuration_access(module, tmp_path):
    with pytest.raises(ValueError, match="needs --live"):
        module.run_demo(workdir=tmp_path)


@pytest.mark.parametrize("module", [demo, solution])
def test_s2_cli_default_and_callback_scope_without_exporters(
    module, monkeypatch, tmp_path, capsys
):
    recorder = LocalEventRecorder()
    lifecycle = []

    @contextmanager
    def offline_tracing_context_double(backend, *, name):
        # A context double is not an actual exporter or flush implementation.
        lifecycle.append(("enter", backend, name))
        try:
            yield {"callbacks": [recorder], "run_name": name}
        finally:
            assert capsys.readouterr().out == ""
            lifecycle.append(("exit", backend, name))

    factory = demo_double if module is demo else lambda: solution_double(
        ("TRACE-101", "MISSING-999")
    )
    monkeypatch.setattr(runtime, "graph_tracing", offline_tracing_context_double)
    monkeypatch.setattr(module, "get_model", lambda **kwargs: factory())
    monkeypatch.setattr(sys, "argv", [
        "s2-offline-cli-check", "--output-dir", str(tmp_path)
    ])
    runtime.run_cli("S2", module.run_demo)
    output = json.loads(capsys.readouterr().out)
    assert output["backend"] == "langwatch"
    assert output["live_api_enabled"] is False
    assert lifecycle == [
        ("enter", "langwatch", "LangGraph Course S2"),
        ("exit", "langwatch", "LangGraph Course S2"),
    ]
    assert recorder.models == (2 if module is demo else 4)
    assert runtime.execution_config().get("callbacks") is None


def test_starter_is_explicitly_incomplete_and_independent(capsys):
    starter.main()
    assert "STARTER_NOT_COMPLETED" in capsys.readouterr().out
    for function, argument in (
        (starter.privacy_plan, "none"), (starter.classify_ingestion, {}),
        (starter.build_graph, None),
    ):
        with pytest.raises(NotImplementedError):
            function(argument)
