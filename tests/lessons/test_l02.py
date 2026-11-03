"""Offline L02 tests: real deterministic graphs, no model doubles or live calls."""
from __future__ import annotations

import json
import socket

from langchain_core.callbacks import BaseCallbackHandler
from langgraph.graph import END, START
from langsmith import tracing_context
import pytest

from course_lessons import l02 as demonstration
from course_support import check_connections, observability, runtime
from exercises.solutions import l02 as solution
from exercises.starters import l02 as starter


@pytest.fixture(autouse=True)
def offline_boundary(monkeypatch):
    """Fail on network, environment-file loading, or model creation in this file."""
    def forbidden(*args, **kwargs):
        raise AssertionError("L02 must not use network, credentials, or a model.")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(check_connections, "dotenv_values", forbidden)
    monkeypatch.setattr(check_connections, "values", forbidden)
    monkeypatch.setattr(observability, "values", forbidden)
    monkeypatch.setattr(runtime, "values", forbidden)
    monkeypatch.setattr(runtime, "get_model", forbidden)
    with tracing_context(enabled=False):
        yield


IMPLEMENTATIONS = (
    (demonstration, "greeting_node", "greeter",
     "Hello, {name}! How is your day going?"),
    (solution, "compliment_node", "compliment",
     "{name}, you're doing an amazing job learning LangGraph."),
)


@pytest.mark.parametrize("module,node_function,node_name,template", IMPLEMENTATIONS)
@pytest.mark.parametrize("name", ["Bob", "Ada Lovelace", "Zoë", "  Bob  "])
def test_node_formats_the_actual_name_without_mutation(
    module, node_function, node_name, template, name
):
    incoming = {"message": name}
    before = incoming.copy()
    update = getattr(module, node_function)(incoming)
    assert incoming == before
    assert update is not incoming
    assert update == {"message": template.format(name=name)}


@pytest.mark.parametrize("module,node_function,node_name,template", IMPLEMENTATIONS)
def test_real_graph_topology_and_fresh_invocations(
    module, node_function, node_name, template
):
    graph = module.build_graph()
    drawable = graph.get_graph()
    assert set(drawable.nodes) == {START, node_name, END}
    assert {(edge.source, edge.target) for edge in drawable.edges} == {
        (START, node_name), (node_name, END)
    }
    for name in ("Bob", "Ada Lovelace", "Zoë", "  Bob  ", "Bob"):
        incoming = {"message": name}
        result = graph.invoke(incoming, config=runtime.execution_config())
        assert result == {"message": template.format(name=name)}
        assert incoming == {"message": name}


@pytest.mark.parametrize("module,node_function,node_name,template", IMPLEMENTATIONS)
@pytest.mark.parametrize(
    "bad_state,error_type,error_message",
    [
        ({"message": ""}, ValueError, "message must not be blank."),
        ({"message": " \t\n"}, ValueError, "message must not be blank."),
        ({"message": 7}, TypeError, "message must be a string."),
        ({"message": None}, TypeError, "message must be a string."),
        ({}, TypeError, "message must be a string."),
    ],
)
def test_explicit_validation_in_node_and_graph(
    module, node_function, node_name, template, bad_state, error_type, error_message
):
    before = bad_state.copy()
    with pytest.raises(error_type) as node_error:
        getattr(module, node_function)(bad_state)
    assert str(node_error.value) == error_message
    with pytest.raises(error_type) as graph_error:
        module.build_graph().invoke(bad_state, config=runtime.execution_config())
    assert str(graph_error.value) == error_message
    assert bad_state == before


class NodeRecordingCallback(BaseCallbackHandler):
    """Named local callback, not a remote tracer and not a model test double."""

    def __init__(self):
        self.started_nodes = []

    def on_chain_start(self, serialized, inputs, **kwargs):
        node = (kwargs.get("metadata") or {}).get("langgraph_node")
        if node is not None:
            self.started_nodes.append(node)


@pytest.mark.parametrize("module,node_function,node_name,template", IMPLEMENTATIONS)
def test_run_demo_forwards_execution_config_to_actual_graph(
    monkeypatch, tmp_path, module, node_function, node_name, template
):
    callback = NodeRecordingCallback()
    config_calls = []

    def local_execution_config():
        config_calls.append(True)
        return {"callbacks": [callback], "recursion_limit": 40}

    monkeypatch.setattr(module, "execution_config", local_execution_config)
    summary = module.run_demo(workdir=tmp_path)
    assert summary["message"] == template.format(name="Bob")
    assert summary["graph_node"] == node_name
    assert summary["input_unchanged"] is True
    assert summary["deterministic"] is True
    assert summary["model_used"] is False
    assert summary["checked_names"] == ["Bob", "Ada Lovelace", "Zoë", "  Bob  "]
    assert len(config_calls) >= 5
    assert callback.started_nodes
    assert set(callback.started_nodes) == {node_name}
    assert list(tmp_path.iterdir()) == []
    json.dumps(summary)


@pytest.mark.parametrize("module", [demonstration, solution])
def test_live_flag_does_not_change_deterministic_lesson(module, tmp_path):
    assert module.run_demo(live=True, workdir=tmp_path)["model_used"] is False


def test_solution_exercises_all_required_rejections(tmp_path):
    summary = solution.run_demo(workdir=tmp_path)
    assert summary["invalid_inputs_rejected"] == 4
    assert summary["message"] == (
        "Bob, you're doing an amazing job learning LangGraph."
    )
    assert solution.build_graph is not demonstration.build_graph
    assert solution.read_name is not demonstration.read_name


def test_incomplete_starter_does_not_claim_a_pass(monkeypatch, capsys):
    def unfinished_graph():
        raise NotImplementedError("TODO 3: implement build_graph.")

    monkeypatch.setattr(starter, "build_graph", unfinished_graph)
    starter.main()
    printed = capsys.readouterr().out
    assert "STARTER_NOT_COMPLETED" in printed
    assert "TODO 3" in printed
    assert '"status": "passed"' not in printed
    assert '"status": "completed"' not in printed


def test_starter_acceptance_harness_can_complete_with_matching_implementations(
    monkeypatch, capsys
):
    # Only this in-memory test substitutes the completed functions. The starter
    # on disk remains separate and imports neither solution nor demonstration.
    monkeypatch.setattr(starter, "read_name", solution.read_name)
    monkeypatch.setattr(starter, "compliment_node", solution.compliment_node)
    monkeypatch.setattr(starter, "build_graph", solution.build_graph)
    starter.main()
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "completed"
    assert output["result"]["model_used"] is False
