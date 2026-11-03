"""L03 exercise reference: add or multiply inside exactly one graph node."""
from math import prod
from pathlib import Path
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config, run_cli


class ArithmeticState(TypedDict):
    values: list[int]
    name: str
    operation: Literal["+", "*"]
    answer: NotRequired[int]
    result: NotRequired[str]


class ArithmeticUpdate(TypedDict):
    answer: int
    result: str


def validate_inputs(state: ArithmeticState) -> None:
    """Reject malformed/missing inputs rather than relying on annotations."""
    values = state.get("values")
    name = state.get("name")
    operation = state.get("operation")
    if not isinstance(values, list) or any(type(item) is not int for item in values):
        raise ValueError("values must be a list of integers, not booleans")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a nonblank string")
    if not isinstance(operation, str) or operation not in ("+", "*"):
        raise ValueError("operation must be '+' or '*'")


def process_values(state: ArithmeticState) -> ArithmeticUpdate:
    """Select arithmetic with Python logic, not graph-level conditional edges."""
    validate_inputs(state)
    if state["operation"] == "+":
        answer = sum(state["values"])
    else:
        answer = prod(state["values"])
    return {
        "answer": answer,
        "result": f"Hi {state['name']}, your answer is {answer}.",
    }


def build_graph():
    """Register only one work-performing node and compile the builder."""
    builder = StateGraph(ArithmeticState)
    builder.add_node("calculator", process_values)
    builder.add_edge(START, "calculator")
    builder.add_edge("calculator", END)
    return builder.compile()


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Exercise both operations, identities, state preservation, and rejection."""
    graph = build_graph()
    cases = [
        ("Jack Sparrow", [1, 2, 3, 4], "*", 24),
        ("Steve", [1, 2, 3, 4], "+", 10),
        ("Mei", [-3, 0, 5], "+", 2),
        ("Mei", [-3, 0, 5], "*", 0),
        ("Ari", [], "+", 0),
        ("Ari", [], "*", 1),
        ("Sam", [-2, 3], "*", -6),
        ("Sam", [7], "+", 7),
    ]
    checked = []
    for name, values, operation, expected in cases:
        initial: ArithmeticState = {
            "values": values.copy(), "name": name, "operation": operation
        }
        before = {**initial, "values": initial["values"].copy()}
        final = graph.invoke(initial, config=execution_config())
        assert final["answer"] == expected
        assert final["result"] == f"Hi {name}, your answer is {expected}."
        for key in ("values", "name", "operation"):
            assert final[key] == before[key]
        assert initial == before
        checked.append({"operation": operation, "answer": final["answer"]})
    unsupported = {"values": [2, 3], "name": "Ari", "operation": "/"}
    try:
        graph.invoke(unsupported, config=execution_config())
    except ValueError as error:
        assert str(error) == "operation must be '+' or '*'"
    else:
        raise AssertionError("Unsupported operations must raise ValueError")
    return {
        "node": "calculator",
        "checked_cases": checked,
        "case_count": len(checked),
        "jack_sparrow_result": "Hi Jack Sparrow, your answer is 24.",
        "unsupported_operation_rejected": True,
        "inputs_unchanged": True,
        "model_used": False,
    }


if __name__ == "__main__":
    run_cli("L03", run_demo)
