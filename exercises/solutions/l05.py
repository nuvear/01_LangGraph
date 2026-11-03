"""L05 reference solution: two sequential sections, independent operand pairs.

Run: python -m exercises.solutions.l05 --backend none
This module deliberately does not import the lesson demonstration or starter.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config, run_cli


class PairState(TypedDict):
    number1: int
    number2: int
    number3: int
    number4: int
    operation1: str
    operation2: str
    result1: NotRequired[int]
    result2: NotRequired[int]
    visited: NotRequired[list[str]]


def validate_and_start(state: PairState) -> dict:
    """Validate the entire request before either arithmetic section runs."""
    for key in ("number1", "number2", "number3", "number4"):
        if key not in state or type(state[key]) is not int:
            raise TypeError(f"{key} must be an integer, not a boolean or string.")
    for key in ("operation1", "operation2"):
        if state.get(key) not in ("+", "-"):
            raise ValueError(f"{key} must be '+' or '-'.")
    return {"visited": ["router1"]}


def route_first(state: PairState) -> Literal["addition", "subtraction"]:
    if state["operation1"] == "+":
        return "addition"
    if state["operation1"] == "-":
        return "subtraction"
    raise ValueError("operation1 must be '+' or '-'.")


def route_second(state: PairState) -> Literal["addition", "subtraction"]:
    if state["operation2"] == "+":
        return "addition"
    if state["operation2"] == "-":
        return "subtraction"
    raise ValueError("operation2 must be '+' or '-'.")


def add_first(state: PairState) -> dict:
    return {
        "result1": state["number1"] + state["number2"],
        "visited": state["visited"] + ["add1"],
    }


def subtract_first(state: PairState) -> dict:
    return {
        "result1": state["number1"] - state["number2"],
        "visited": state["visited"] + ["subtract1"],
    }


def start_second(state: PairState) -> dict:
    return {"visited": state["visited"] + ["router2"]}


def add_second(state: PairState) -> dict:
    return {
        "result2": state["number3"] + state["number4"],
        "visited": state["visited"] + ["add2"],
    }


def subtract_second(state: PairState) -> dict:
    return {
        "result2": state["number3"] - state["number4"],
        "visited": state["visited"] + ["subtract2"],
    }


def build_graph():
    builder = StateGraph(PairState)
    builder.add_node("router1", validate_and_start)
    builder.add_node("add1", add_first)
    builder.add_node("subtract1", subtract_first)
    builder.add_node("router2", start_second)
    builder.add_node("add2", add_second)
    builder.add_node("subtract2", subtract_second)
    builder.add_edge(START, "router1")
    builder.add_conditional_edges(
        "router1", route_first,
        {"addition": "add1", "subtraction": "subtract1"},
    )
    builder.add_edge("add1", "router2")
    builder.add_edge("subtract1", "router2")
    builder.add_conditional_edges(
        "router2", route_second,
        {"addition": "add2", "subtraction": "subtract2"},
    )
    builder.add_edge("add2", END)
    builder.add_edge("subtract2", END)
    return builder.compile()


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Prove all four combinations, independence, and fail-fast validation."""
    graph = build_graph()
    checked = []
    combinations = [
        ("+", "+", 15, 9, "add1", "add2"),
        ("+", "-", 15, 5, "add1", "subtract2"),
        ("-", "+", 5, 9, "subtract1", "add2"),
        ("-", "-", 5, 5, "subtract1", "subtract2"),
    ]
    for op1, op2, answer1, answer2, node1, node2 in combinations:
        initial: PairState = {
            "number1": 10, "number2": 5, "number3": 7, "number4": 2,
            "operation1": op1, "operation2": op2,
        }
        before = dict(initial)
        final = graph.invoke(initial, config=execution_config())
        assert (final["result1"], final["result2"]) == (answer1, answer2)
        assert final["visited"] == ["router1", node1, "router2", node2]
        assert initial == before
        assert all(final[key] == value for key, value in initial.items())
        checked.append({
            "operation1": op1, "operation2": op2,
            "result1": final["result1"], "result2": final["result2"],
            "visited": final["visited"],
        })

    # Changing pair one must not affect pair two, and vice versa.
    base: PairState = {
        "number1": 10, "number2": 5, "number3": 7, "number4": 2,
        "operation1": "-", "operation2": "+",
    }
    changed_first = graph.invoke(
        {**base, "number1": 100}, config=execution_config(),
    )
    changed_second = graph.invoke(
        {**base, "number3": -7}, config=execution_config(),
    )
    assert (changed_first["result1"], changed_first["result2"]) == (95, 9)
    assert (changed_second["result1"], changed_second["result2"]) == (5, -5)

    for key in ("operation1", "operation2"):
        try:
            graph.invoke({**base, key: "*"}, config=execution_config())
        except ValueError as error:
            assert str(error) == f"{key} must be '+' or '-'."
        else:
            raise AssertionError(f"Unsupported {key} was silently accepted.")
    return {
        "cases": checked,
        "independent_pairs_checked": True,
        "both_invalid_operations_rejected": True,
        "model_calls": 0,
    }


if __name__ == "__main__":
    run_cli("L05", run_demo)
