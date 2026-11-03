"""Offline L03 tests: real deterministic graphs, no model or service calls."""
from copy import deepcopy
import json
import socket

import pytest
from langgraph.graph import END, START
from langsmith import tracing_context

from course_lessons import l03 as demo
from course_support import check_connections, runtime
from exercises.solutions import l03 as solution
from exercises.starters import l03 as starter


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    """Fail on accidental network/config loading and disable ambient tracing."""
    def forbidden_network(*args, **kwargs):
        raise AssertionError("L03 must not use the network")

    def forbidden_configuration(*args, **kwargs):
        raise AssertionError("L03 must not load environment configuration or models")

    monkeypatch.setattr(socket.socket, "connect", forbidden_network)
    monkeypatch.setattr(socket, "create_connection", forbidden_network)
    monkeypatch.setattr(check_connections, "values", forbidden_configuration)
    monkeypatch.setattr(runtime, "values", forbidden_configuration)
    monkeypatch.setattr(runtime, "get_model", forbidden_configuration)
    with tracing_context(enabled=False):
        yield


@pytest.mark.parametrize(
    "values, expected", [([1, 2, 3, 4], 10), ([], 0), ([-3, 0, 5], 2), ([7], 7)]
)
def test_demo_node_returns_only_derived_fields_without_mutation(values, expected):
    initial = {"values": values, "name": "Steve"}
    before = deepcopy(initial)
    assert demo.process_values(initial) == {
        "total": expected,
        "result": f"Hi there Steve! Your sum = {expected}.",
    }
    assert initial == before


@pytest.mark.parametrize(
    "module, node", [(demo, "processor"), (solution, "calculator")]
)
def test_compiled_graph_has_exactly_one_work_node_and_two_edges(module, node):
    view = module.build_graph().get_graph()
    assert set(view.nodes) == {START, node, END}
    assert {(edge.source, edge.target) for edge in view.edges} == {
        (START, node), (node, END)
    }
    assert not any(edge.conditional for edge in view.edges)


def test_demo_graph_merges_update_and_replaces_stale_outputs():
    initial = {
        "values": [1, 2, 3, 4], "name": "Steve", "total": -1, "result": "stale"
    }
    before = deepcopy(initial)
    final = demo.build_graph().invoke(initial, config=runtime.execution_config())
    assert final == {
        "values": [1, 2, 3, 4], "name": "Steve", "total": 10,
        "result": "Hi there Steve! Your sum = 10.",
    }
    assert initial == before


@pytest.mark.parametrize(
    "values, operation, expected",
    [
        ([1, 2, 3, 4], "+", 10),
        ([1, 2, 3, 4], "*", 24),
        ([-3, 0, 5], "+", 2),
        ([-3, 0, 5], "*", 0),
        ([], "+", 0),
        ([], "*", 1),
        ([-2, 3], "*", -6),
        ([7], "+", 7),
        ([7], "*", 7),
        ([0], "+", 0),
        ([0], "*", 0),
    ],
)
def test_solution_both_paths_and_edge_cases(values, operation, expected):
    initial = {"values": values, "name": "Jack Sparrow", "operation": operation}
    before = deepcopy(initial)
    update = solution.process_values(initial)
    assert update == {
        "answer": expected,
        "result": f"Hi Jack Sparrow, your answer is {expected}.",
    }
    final = solution.build_graph().invoke(initial, config=runtime.execution_config())
    assert final == {**before, **update}
    assert initial == before


@pytest.mark.parametrize("module", [demo, solution])
@pytest.mark.parametrize(
    "changes",
    [
        {"values": None}, {"values": "123"}, {"values": (1, 2)},
        {"values": [1, True]}, {"values": [1, 2.5]}, {"values": [1, "2"]},
        {"values": [[1]]}, {"name": ""}, {"name": " \t"}, {"name": None},
        {"name": 12},
    ],
)
def test_invalid_input_types_are_rejected_by_node_and_graph(module, changes):
    state = {"values": [1, 2], "name": "Ari", "operation": "+", **changes}
    before = deepcopy(state)
    with pytest.raises(ValueError):
        module.process_values(state)
    with pytest.raises(ValueError):
        module.build_graph().invoke(state, config=runtime.execution_config())
    assert state == before


@pytest.mark.parametrize("operation", ["/", "add", "x", "+ ", "", None, 1, ["+"]])
def test_solution_rejects_unsupported_operation_including_nonstring(operation):
    state = {"values": [2, 3], "name": "Ari", "operation": operation}
    with pytest.raises(ValueError, match="operation must be"):
        solution.build_graph().invoke(state, config=runtime.execution_config())


@pytest.mark.parametrize(
    "module, missing",
    [(demo, "values"), (demo, "name"), (solution, "values"),
     (solution, "name"), (solution, "operation")],
)
def test_missing_required_inputs_raise_valueerror_not_assumed_none(module, missing):
    initial = {"values": [2, 3], "name": "Ari", "operation": "+"}
    del initial[missing]
    with pytest.raises(ValueError):
        module.build_graph().invoke(initial, config=runtime.execution_config())


def test_solution_replaces_stale_outputs_and_keeps_supplied_name():
    initial = {
        "values": [2, 3], "name": "  Mei  ", "operation": "*",
        "answer": 999, "result": "old",
    }
    before = deepcopy(initial)
    final = solution.build_graph().invoke(initial, config=runtime.execution_config())
    assert final == {
        **before, "answer": 6, "result": "Hi   Mei  , your answer is 6."
    }
    assert initial == before


@pytest.mark.parametrize("module, calls", [(demo, 3), (solution, 9)])
def test_run_demo_asserts_real_graph_outcomes_and_uses_execution_config(
    module, calls, monkeypatch, tmp_path
):
    configurations = []

    def recorded_execution_config():
        config = {"callbacks": [], "recursion_limit": 40, "tags": ["l03-offline"]}
        configurations.append(config)
        return config

    monkeypatch.setattr(module, "execution_config", recorded_execution_config)
    summary = module.run_demo(live=False, workdir=tmp_path)
    assert summary["model_used"] is False
    assert summary["inputs_unchanged"] is True
    assert len(configurations) == calls
    assert json.loads(json.dumps(summary)) == summary
    assert not list(tmp_path.iterdir())
    if module is solution:
        assert summary["case_count"] == 8
        assert summary["unsupported_operation_rejected"] is True
    else:
        assert summary["final_state"]["total"] == 10
        assert summary["empty_sum"] == 0


def test_starter_main_reports_unfinished_without_claiming_pass(monkeypatch, capsys):
    def unfinished_builder():
        raise NotImplementedError("TODO 3: build_graph")

    monkeypatch.setattr(starter, "build_graph", unfinished_builder)
    assert starter.main() is None
    output = capsys.readouterr().out
    assert "STARTER_NOT_COMPLETED" in output
    assert "STARTER_CHECKS_PASSED" not in output


def test_starter_checks_agree_with_complete_independent_solution(
    monkeypatch, capsys
):
    # Test-only injection verifies the checker; the starter never imports solutions.
    monkeypatch.setattr(starter, "validate_inputs", solution.validate_inputs)
    monkeypatch.setattr(starter, "process_values", solution.process_values)
    monkeypatch.setattr(starter, "build_graph", solution.build_graph)
    starter.main()
    assert "STARTER_CHECKS_PASSED" in capsys.readouterr().out
