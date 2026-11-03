"""Offline L09 tests: all model responses are explicitly named test doubles."""
from __future__ import annotations

import json

import pytest
from langchain_core.messages import (
    AIMessage, HumanMessage, SystemMessage, ToolMessage,
)
from langgraph.graph import END
from langgraph.graph.message import add_messages

from course_lessons import l09 as demo
from exercises.solutions import l09 as solution
from exercises.starters import l09 as starter


class ScriptedArithmeticModelDouble:
    """A finite scripted response source; never contacts an API."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.inputs = []
        self.configs = []
        self.bound_names = []

    def bind_tools(self, tools):
        self.bound_names = [item.name for item in tools]
        return self

    def invoke(self, messages, config=None):
        self.inputs.append(list(messages))
        self.configs.append(config)
        if not self.responses:
            raise AssertionError("The explicit offline script was exhausted.")
        return self.responses.pop(0)


class RepeatingArithmeticModelDouble(ScriptedArithmeticModelDouble):
    """Intentionally never finishes, to verify an explicit call budget."""

    def __init__(self):
        super().__init__([])

    def invoke(self, messages, config=None):
        self.inputs.append(list(messages))
        return request("add", 1, 1, f"repeat-{len(self.inputs)}")


def request(name, a, b, identifier):
    return AIMessage(content="", tool_calls=[{
        "name": name, "args": {"a": a, "b": b}, "id": identifier,
        "type": "tool_call",
    }])


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    # Disable automatic tracing even if the parent enabled it in their shell.
    # No .env file is loaded and no model or tracing client is constructed.
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "false")
    monkeypatch.setenv("LANGCHAIN_TRACING", "false")


@pytest.fixture(params=["demo", "solution"])
def implementation(request):
    if request.param == "demo":
        return demo, demo.build_graph, demo.inspect_transcript, demo.ToolLoopLimit
    return solution, solution.make_agent, solution.collect_audit, solution.AuditLimit


def observations(report):
    return report.get("observations", report.get("audit"))


def test_sequential_loop_preserves_messages_and_runtime_config(
    implementation, monkeypatch,
):
    module, build, inspect, _ = implementation
    fake = ScriptedArithmeticModelDouble([
        request("add", 40, 12, "first"),
        request("multiply", 52, 6, "second"),
        AIMessage(content="The result is 312."),
    ])
    monkeypatch.setattr(module, "execution_config", lambda: {
        "recursion_limit": 40, "tags": ["l09-offline-double"],
    })
    report = module.run_request(build(fake), "Calculate the dependent result.")
    assert fake.bound_names == ["add", "subtract", "multiply"]
    assert report["model_calls"] == 3
    assert [row["result"] for row in observations(report)] == ["52", "312"]
    assert [len(messages) for messages in fake.inputs] == [2, 4, 6]
    assert all(isinstance(messages[0], SystemMessage) for messages in fake.inputs)
    assert all(isinstance(messages[1], HumanMessage) for messages in fake.inputs)
    assert all("l09-offline-double" in c["tags"] for c in fake.configs)
    assert all(c["recursion_limit"] == 40 for c in fake.configs)
    json.dumps(report)  # The parent can safely serialize this small summary.


def test_parallel_requests_are_all_executed(implementation):
    module, build, _, _ = implementation
    first = request("add", 34, 21, "a")
    second = request("add", 3, 4, "b")
    fake = ScriptedArithmeticModelDouble([
        AIMessage(content="", tool_calls=first.tool_calls + second.tool_calls),
        AIMessage(content="55 and 7"),
    ])
    report = module.run_request(build(fake), "Two independent additions.")
    assert report["model_calls"] == 2
    assert sorted(row["result"] for row in observations(report)) == ["55", "7"]
    results = [m for m in fake.inputs[1] if isinstance(m, ToolMessage)]
    assert {message.tool_call_id for message in results} == {"a", "b"}


def test_no_tool_route_ends_after_one_model_call(implementation):
    module, build, _, _ = implementation
    fake = ScriptedArithmeticModelDouble([AIMessage(content="Hello!")])
    report = module.run_request(build(fake), "Greet me.")
    assert report["model_calls"] == 1
    assert report["tool_calls"] == 0
    assert observations(report) == []


@pytest.mark.parametrize("tool_name,a,b,result", [
    ("add", -4, 4, 0), ("subtract", 3, 8, -5), ("multiply", -3, 4, -12),
])
def test_actual_python_tool_edge_cases(implementation, tool_name, a, b, result):
    module, build, _, _ = implementation
    tool = next(item for item in module.TOOLS if item.name == tool_name)
    assert tool.description and tool.invoke({"a": a, "b": b}) == result
    fake = ScriptedArithmeticModelDouble([
        request(tool_name, a, b, "edge"), AIMessage(content=str(result)),
    ])
    report = module.run_request(build(fake), "Check signed integer arithmetic.")
    assert observations(report)[0]["result"] == str(result)


@pytest.mark.parametrize("name,args", [
    ("divide", {"a": 9, "b": 0}),
    ("add", {"a": "not-an-integer", "b": 3}),
    ("multiply", {"a": 2}),
])
def test_invalid_call_returns_error_observation_then_model_can_exit(
    implementation, name, args,
):
    module, build, _, _ = implementation
    fake = ScriptedArithmeticModelDouble([
        AIMessage(content="", tool_calls=[{
            "name": name, "args": args, "id": "bad", "type": "tool_call",
        }]),
        AIMessage(content="That tool request was invalid."),
    ])
    report = module.run_request(build(fake), "An intentionally invalid call.")
    assert report["model_calls"] == 2
    assert observations(report)[0]["status"] == "error"
    assert observations(report)[0]["result"]
    assert any(isinstance(m, ToolMessage) for m in fake.inputs[1])


def test_invalid_arguments_can_be_corrected(implementation):
    module, build, _, _ = implementation
    fake = ScriptedArithmeticModelDouble([
        request("add", "bad", 3, "bad-input"),
        request("add", 2, 3, "corrected"),
        AIMessage(content="5"),
    ])
    report = module.run_request(build(fake), "Recover from an argument error.")
    assert [r["status"] for r in observations(report)] == ["error", "success"]
    assert observations(report)[1]["result"] == "5"


def test_infinite_model_is_stopped_before_extra_invocation(implementation):
    module, build, _, limit = implementation
    fake = RepeatingArithmeticModelDouble()
    with pytest.raises(limit, match="budget exhausted"):
        module.run_request(build(fake, max_model_calls=2), "Never stop.")
    assert len(fake.inputs) == 2


@pytest.mark.parametrize("budget", [0, 11])
def test_bad_budget_is_rejected(implementation, budget):
    _, build, _, _ = implementation
    with pytest.raises(ValueError, match="between 1 and 10"):
        build(ScriptedArithmeticModelDouble([]), max_model_calls=budget)


def test_oversized_batch_is_rejected_before_execution(implementation):
    module, build, _, limit = implementation
    batch = [request("add", 1, 2, f"id-{i}").tool_calls[0] for i in range(5)]
    fake = ScriptedArithmeticModelDouble([AIMessage(content="", tool_calls=batch)])
    with pytest.raises(limit, match="batch"):
        module.run_request(build(fake), "Too many calls.")
    assert len(fake.inputs) == 1


def test_malformed_json_is_not_treated_as_a_final_answer(implementation):
    module, build, _, _ = implementation
    fake = ScriptedArithmeticModelDouble([AIMessage(
        content="", invalid_tool_calls=[{
            "name": "add", "args": "{", "id": "invalid", "error": "bad json",
            "type": "invalid_tool_call",
        }],
    )])
    with pytest.raises(ValueError, match="[Mm]alformed"):
        module.run_request(build(fake), "Bad serialization.")


def test_audit_pairs_reversed_batch_results_by_id(implementation):
    _, _, inspect, _ = implementation
    a = request("subtract", 10, 3, "a").tool_calls[0]
    b = request("multiply", 2, 4, "b").tool_calls[0]
    report = inspect({"model_calls": 2, "messages": [
        HumanMessage(content="Two operations"),
        AIMessage(content="", tool_calls=[a, b]),
        ToolMessage(content="8", tool_call_id="b"),
        ToolMessage(content="7", tool_call_id="a"),
        AIMessage(content="7 and 8"),
    ]})
    rows = observations(report)
    assert [(r["tool"], r["result"]) for r in rows] == [
        ("multiply", "8"), ("subtract", "7"),
    ]


@pytest.mark.parametrize("fault", [
    "orphan", "missing", "duplicate", "empty_id", "interrupted", "empty_final",
])
def test_audit_rejects_broken_transcripts(implementation, fault):
    _, _, inspect, _ = implementation
    call = request("add", 2, 3, "a")
    result = ToolMessage(content="5", tool_call_id="a")
    final = AIMessage(content="5")
    broken = {
        "orphan": [ToolMessage(content="5", tool_call_id="unknown"), final],
        "missing": [call],
        "duplicate": [call, result, call, result, final],
        "empty_id": [request("add", 2, 3, ""), final],
        "interrupted": [call, HumanMessage(content="Oops"), result, final],
        "empty_final": [call, result, AIMessage(content="")],
    }[fault]
    with pytest.raises((ValueError, AssertionError)):
        inspect({"messages": broken, "model_calls": 2})


def test_message_reducer_updates_ids_not_just_blind_append():
    old = [HumanMessage(content="original", id="same")]
    updated = add_messages(old, [HumanMessage(content="corrected", id="same")])
    assert len(updated) == 1 and updated[0].content == "corrected"
    assert len(add_messages(updated, [AIMessage(content="new", id="new")])) == 2


def test_routes_reject_non_ai_messages(implementation):
    module, _, _, _ = implementation
    route = getattr(module, "route_after_model", None) or module.route_next
    with pytest.raises(TypeError):
        route({"messages": [HumanMessage(content="not a model")], "model_calls": 0})
    assert route({"messages": [AIMessage(content="done")], "model_calls": 1}) == END


def test_live_entrypoints_refuse_offline_without_constructing_real_models(
    implementation, monkeypatch,
):
    module, _, _, _ = implementation

    def explicit_live_gate(*, live, max_tokens):
        assert live is False
        raise ValueError("Offline test: real model construction forbidden.")

    monkeypatch.setattr(module, "get_model", explicit_live_gate)
    with pytest.raises(ValueError, match="forbidden"):
        module.run_demo()


def test_starter_is_honestly_unfinished():
    with pytest.raises(NotImplementedError, match="TODO 1"):
        starter.check_started()


def test_solution_live_harness_with_explicit_offline_double(monkeypatch):
    # Exercises the real acceptance harness, not an actual paid model call.
    fake = ScriptedArithmeticModelDouble([
        request("subtract", 18, 5, "s1"),
        request("multiply", 13, 4, "s2"),
        AIMessage(content="52"),
        AIMessage(content="", tool_calls=[
            request("add", 9, 6, "s3").tool_calls[0],
            request("multiply", 8, 3, "s4").tool_calls[0],
        ]),
        AIMessage(content="15 and 24"),
        AIMessage(content="Hello!"),
    ])
    monkeypatch.setattr(solution, "get_model", lambda **kwargs: fake)
    report = solution.run_demo(live=False)
    assert report["compound"]["tool_calls"] == 2
    assert report["independent"]["tool_calls"] == 2
    assert report["greeting"]["tool_calls"] == 0


def test_demo_live_harness_with_explicit_offline_double(monkeypatch):
    fake = ScriptedArithmeticModelDouble([
        request("add", 3, 4, "d1"), AIMessage(content="7"),
        request("add", 34, 21, "d2"), AIMessage(content="55"),
        AIMessage(content="", tool_calls=[
            request("add", 34, 21, "d3").tool_calls[0],
            request("add", 3, 4, "d4").tool_calls[0],
        ]), AIMessage(content="55 and 7"),
        request("add", 40, 12, "d5"),
        request("multiply", 52, 6, "d6"), AIMessage(content="312"),
        request("subtract", 29, 12, "d7"), AIMessage(content="17"),
        request("add", 9, 9, "d8"), AIMessage(content="18. A clean joke."),
        AIMessage(content="Hello!"),
    ])
    monkeypatch.setattr(demo, "get_model", lambda **kwargs: fake)
    report = demo.run_demo(live=False)
    assert len(report["checked_cases"]) == 7
    assert report["checked_cases"]["sequential"]["tool_calls"] == 2
