"""L05 baseline: route one integer pair to exactly one arithmetic node.

Run from the repository root: python -m course_lessons.l05 --backend none
No model, credential loading, network access, or output files are needed.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config, run_cli


class ArithmeticState(TypedDict):
    number1: int
    number2: int
    operation: str
    result: NotRequired[int]
    selected_node: NotRequired[str]


def validate_inputs(state: ArithmeticState) -> dict:
    """A real graph node returns an update, even when it changes no fields."""
    for key in ("number1", "number2"):
        if key not in state or type(state[key]) is not int:
            raise TypeError(f"{key} must be an integer, not a boolean or string.")
    if state.get("operation") not in ("+", "-"):
        raise ValueError("operation must be '+' or '-'.")
    return {}


def choose_route(state: ArithmeticState) -> Literal["addition", "subtraction"]:
    """A routing callable returns a label, not a state-update dictionary."""
    if state["operation"] == "+":
        return "addition"
    if state["operation"] == "-":
        return "subtraction"
    raise ValueError("operation must be '+' or '-'.")


def add_numbers(state: ArithmeticState) -> dict:
    return {
        "result": state["number1"] + state["number2"],
        "selected_node": "add",
    }


def subtract_numbers(state: ArithmeticState) -> dict:
    return {
        "result": state["number1"] - state["number2"],
        "selected_node": "subtract",
    }


def build_graph():
    """Register work nodes, attach a route map, then compile the graph."""
    builder = StateGraph(ArithmeticState)
    builder.add_node("router", validate_inputs)
    builder.add_node("add", add_numbers)
    builder.add_node("subtract", subtract_numbers)
    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        "router", choose_route,
        {"addition": "add", "subtraction": "subtract"},
    )
    builder.add_edge("add", END)
    builder.add_edge("subtract", END)
    return builder.compile()


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Check both branches and a rejected operation; never call a model.

    live/workdir keep the shared lesson interface. Neither is needed here.
    """
    graph = build_graph()
    cases = [
        (10, "-", 5, 5, "subtract"),
        (7, "+", 2, 9, "add"),
        (0, "-", 7, -7, "subtract"),
        (-3, "+", 0, -3, "add"),
    ]
    checked = []
    for left, operation, right, expected, node in cases:
        initial: ArithmeticState = {
            "number1": left, "number2": right, "operation": operation,
        }
        before = dict(initial)
        final = graph.invoke(initial, config=execution_config())
        assert final["result"] == expected
        assert final["selected_node"] == node
        assert initial == before
        assert all(final[key] == value for key, value in initial.items())
        checked.append({
            "number1": left, "operation": operation, "number2": right,
            "result": final["result"], "selected_node": final["selected_node"],
        })
    try:
        graph.invoke(
            {"number1": 10, "number2": 5, "operation": "*"},
            config=execution_config(),
        )
    except ValueError as error:
        assert str(error) == "operation must be '+' or '-'."
    else:
        raise AssertionError("An unsupported operation was silently accepted.")
    return {
        "cases": checked,
        "unsupported_operation_rejected": True,
        "model_calls": 0,
    }


if __name__ == "__main__":
    run_cli("L05", run_demo)
