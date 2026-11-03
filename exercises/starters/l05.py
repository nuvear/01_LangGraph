"""L05 starter: complete ONLY route_first, route_second, and build_graph.

Run: python -m exercises.starters.l05
Until the TODOs are implemented, the command exits normally and reports
STARTER_NOT_COMPLETED. That is not a passing exercise result.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.observability import graph_tracing
from course_support.runtime import execution_config


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
    for key in ("number1", "number2", "number3", "number4"):
        if key not in state or type(state[key]) is not int:
            raise TypeError(f"{key} must be an integer, not a boolean or string.")
    for key in ("operation1", "operation2"):
        if state.get(key) not in ("+", "-"):
            raise ValueError(f"{key} must be '+' or '-'.")
    return {"visited": ["router1"]}


def route_first(state: PairState) -> Literal["addition", "subtraction"]:
    # TODO 1: Read operation1. Return the matching label; reject other values.
    raise NotImplementedError("Complete route_first using operation1.")


def route_second(state: PairState) -> Literal["addition", "subtraction"]:
    # TODO 2: Read operation2, NOT operation1 or result1.
    raise NotImplementedError("Complete route_second using operation2.")


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
    # TODO 3: Add boundary edges, both conditional edges with path maps,
    # and edges from BOTH first arithmetic branches into router2.
    # Finish both second arithmetic branches at END; return builder.compile().
    # Do not add ordinary outgoing edges from router1 or router2.
    raise NotImplementedError("Connect and compile the two-section graph.")


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Local acceptance checks become active when the TODOs are complete."""
    graph = build_graph()
    base: PairState = {
        "number1": 10, "number2": 5, "number3": 7, "number4": 2,
        "operation1": "-", "operation2": "+",
    }
    cases = [
        ("+", "+", 15, 9, "add1", "add2"),
        ("+", "-", 15, 5, "add1", "subtract2"),
        ("-", "+", 5, 9, "subtract1", "add2"),
        ("-", "-", 5, 5, "subtract1", "subtract2"),
    ]
    for op1, op2, answer1, answer2, node1, node2 in cases:
        initial = {**base, "operation1": op1, "operation2": op2}
        final = graph.invoke(initial, config=execution_config())
        assert (final["result1"], final["result2"]) == (answer1, answer2)
        assert final["visited"] == ["router1", node1, "router2", node2]
        assert all(final[key] == value for key, value in initial.items())
    for key in ("operation1", "operation2"):
        try:
            graph.invoke({**base, key: "*"}, config=execution_config())
        except ValueError as error:
            assert str(error) == f"{key} must be '+' or '-'."
        else:
            raise AssertionError(f"Unsupported {key} was silently accepted.")
    changed = graph.invoke({**base, "number1": 100}, config=execution_config())
    assert (changed["result1"], changed["result2"]) == (95, 9)
    changed = graph.invoke({**base, "number3": -7}, config=execution_config())
    assert (changed["result1"], changed["result2"]) == (5, -5)
    edge = graph.invoke(
        {**base, "number1": 0, "number2": 5, "number3": -7, "number4": 0},
        config=execution_config(),
    )
    assert (edge["result1"], edge["result2"]) == (-5, -7)
    return {
        "status": "COMPLETED", "operation_combinations_checked": 4,
        "independence_checked": True, "invalid_operations_rejected": True,
        "zero_and_negative_checked": True, "model_calls": 0,
    }


def main() -> None:
    with graph_tracing("none"):
        try:
            result = run_demo()
        except NotImplementedError as error:
            result = {
                "status": "STARTER_NOT_COMPLETED",
                "next_step": str(error),
                "instructions": "Implement the three TODO functions, then rerun.",
            }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
