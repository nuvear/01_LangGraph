"""L05 offline checks: real deterministic graphs, never model or telemetry calls."""
from __future__ import annotations

from copy import deepcopy
import json
import socket

import pytest

from course_lessons import l05 as demonstration
from course_support import check_connections, runtime
from course_support.observability import graph_tracing
from exercises.solutions import l05 as solution
from exercises.starters import l05 as starter


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    """Fail loudly if this lesson attempts networking or credential loading."""
    def forbidden_network(*args, **kwargs):
        raise AssertionError("L05 tests must not open a network connection.")

    def forbidden_credentials(*args, **kwargs):
        raise AssertionError("L05 tests must not read credentials or call models.")

    monkeypatch.setattr(socket.socket, "connect", forbidden_network)
    monkeypatch.setattr(socket, "create_connection", forbidden_network)
    monkeypatch.setattr(check_connections, "dotenv_values", forbidden_credentials)
    monkeypatch.setattr(runtime, "get_model", forbidden_credentials)
    with graph_tracing("none"):
        yield


@pytest.fixture
def pair_input():
    return {
        "number1": 10, "number2": 5, "number3": 7, "number4": 2,
        "operation1": "-", "operation2": "+",
    }


@pytest.mark.parametrize("operation,expected,node", [
    ("+", 15, "add"), ("-", 5, "subtract"),
])
def test_demo_both_routes_and_actual_executed_nodes(operation, expected, node):
    graph = demonstration.build_graph()
    initial = {"number1": 10, "number2": 5, "operation": operation}
    final = graph.invoke(initial, config=runtime.execution_config())
    assert final["result"] == expected
    assert final["selected_node"] == node
    updates = list(graph.stream(
        initial, config=runtime.execution_config(), stream_mode="updates",
    ))
    assert [name for update in updates for name in update] == ["router", node]
    assert "result" not in initial


@pytest.mark.parametrize("left,op,right,expected", [
    (0, "+", 0, 0), (-5, "+", 2, -3), (0, "-", 7, -7),
    (-5, "-", -2, -3),
])
def test_demo_zero_and_negative_operands(left, op, right, expected):
    final = demonstration.build_graph().invoke(
        {"number1": left, "number2": right, "operation": op},
        config=runtime.execution_config(),
    )
    assert final["result"] == expected


@pytest.mark.parametrize("bad", ["*", "/", "", "add", None])
def test_demo_unsupported_operation_is_not_subtraction(bad):
    with pytest.raises(ValueError, match="operation must"):
        demonstration.build_graph().invoke(
            {"number1": 10, "number2": 5, "operation": bad},
            config=runtime.execution_config(),
        )


@pytest.mark.parametrize("key", ["number1", "number2"])
@pytest.mark.parametrize("bad", [True, "5", 1.5, None])
def test_demo_requires_actual_integers(key, bad):
    state = {"number1": 10, "number2": 5, "operation": "+", key: bad}
    with pytest.raises(TypeError, match=key):
        demonstration.build_graph().invoke(state, config=runtime.execution_config())


def test_route_callable_is_not_a_node_update():
    state = {"number1": 10, "number2": 5, "operation": "+"}
    before = deepcopy(state)
    assert demonstration.validate_inputs(state) == {}
    assert demonstration.choose_route(state) == "addition"
    assert demonstration.add_numbers(state) == {
        "result": 15, "selected_node": "add",
    }
    assert state == before


@pytest.mark.parametrize("op1,op2,answer1,answer2,node1,node2", [
    ("+", "+", 15, 9, "add1", "add2"),
    ("+", "-", 15, 5, "add1", "subtract2"),
    ("-", "+", 5, 9, "subtract1", "add2"),
    ("-", "-", 5, 5, "subtract1", "subtract2"),
])
def test_solution_all_four_combinations(
    pair_input, op1, op2, answer1, answer2, node1, node2,
):
    graph = solution.build_graph()
    initial = {**pair_input, "operation1": op1, "operation2": op2}
    before = deepcopy(initial)
    final = graph.invoke(initial, config=runtime.execution_config())
    assert (final["result1"], final["result2"]) == (answer1, answer2)
    expected_nodes = ["router1", node1, "router2", node2]
    assert final["visited"] == expected_nodes
    updates = graph.stream(
        initial, config=runtime.execution_config(), stream_mode="updates",
    )
    assert [name for update in updates for name in update] == expected_nodes
    assert initial == before
    assert all(final[key] == value for key, value in initial.items())


def test_solution_second_pair_never_uses_first_result(pair_input):
    graph = solution.build_graph()
    changed_first = graph.invoke(
        {**pair_input, "number1": 100}, config=runtime.execution_config(),
    )
    changed_second = graph.invoke(
        {**pair_input, "number3": -7}, config=runtime.execution_config(),
    )
    assert (changed_first["result1"], changed_first["result2"]) == (95, 9)
    assert (changed_second["result1"], changed_second["result2"]) == (5, -5)


def test_solution_zero_negative_and_repeated_run_isolation(pair_input):
    graph = solution.build_graph()
    first = graph.invoke(
        {**pair_input, "number1": 0, "number3": -7, "number4": 0},
        config=runtime.execution_config(),
    )
    assert (first["result1"], first["result2"]) == (-5, -7)
    second = graph.invoke(pair_input, config=runtime.execution_config())
    assert (second["result1"], second["result2"]) == (5, 9)
    assert len(second["visited"]) == 4
    assert first["visited"] is not second["visited"]


@pytest.mark.parametrize("key", ["operation1", "operation2"])
@pytest.mark.parametrize("bad", ["*", "/", "", None])
def test_solution_rejects_bad_operation_before_arithmetic(
    monkeypatch, pair_input, key, bad,
):
    def arithmetic_must_not_run(state):
        raise AssertionError("Validation must precede all arithmetic.")

    monkeypatch.setattr(solution, "add_first", arithmetic_must_not_run)
    monkeypatch.setattr(solution, "subtract_first", arithmetic_must_not_run)
    with pytest.raises(ValueError, match=key):
        solution.build_graph().invoke(
            {**pair_input, key: bad}, config=runtime.execution_config(),
        )


@pytest.mark.parametrize("key", ["number1", "number2", "number3", "number4"])
@pytest.mark.parametrize("bad", [True, "7", 2.5, None])
def test_solution_validates_all_four_operands(pair_input, key, bad):
    with pytest.raises(TypeError, match=key):
        solution.build_graph().invoke(
            {**pair_input, key: bad}, config=runtime.execution_config(),
        )


@pytest.mark.parametrize("key", ["number4", "operation2"])
def test_solution_missing_required_input_has_clear_error(pair_input, key):
    del pair_input[key]
    error_type = TypeError if key == "number4" else ValueError
    with pytest.raises(error_type, match=key):
        solution.build_graph().invoke(pair_input, config=runtime.execution_config())


def test_solution_nodes_preserve_previous_results_and_input_lists(pair_input):
    state = {**pair_input, "result1": 5, "visited": ["router1", "subtract1"]}
    before = deepcopy(state)
    update = solution.start_second(state)
    assert state == before
    second_state = {**state, **update}
    arithmetic_update = solution.add_second(second_state)
    assert "result1" not in arithmetic_update
    assert arithmetic_update["result2"] == 9
    assert second_state["visited"] == ["router1", "subtract1", "router2"]


@pytest.mark.parametrize("module", [demonstration, solution])
def test_run_demo_returns_checked_serializable_summary(module, tmp_path):
    result = module.run_demo(live=False, workdir=tmp_path)
    assert result["model_calls"] == 0
    assert len(result["cases"]) == 4
    json.dumps(result)
    assert list(tmp_path.iterdir()) == []


def test_starter_reports_unfinished_todo(monkeypatch, capsys):
    def unfinished_graph():
        raise NotImplementedError("Complete the remaining graph connections.")

    monkeypatch.setattr(starter, "build_graph", unfinished_graph)
    starter.main()
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "STARTER_NOT_COMPLETED"
    assert "passed" not in result.values()
    assert "TODO" in result["instructions"]
