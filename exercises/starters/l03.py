"""L03 starter: implement the three TODO functions, then run this module."""
from math import prod
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config


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
    """TODO 1: raise ValueError for every invalid required input.

    Require a list containing only actual integers (no bool), a nonblank name,
    and operation '+' or '*'. Empty lists are valid. Missing fields are invalid.
    Do not alter the supplied state or normalize the supplied name.
    """
    raise NotImplementedError("TODO 1: validate_inputs")


def process_values(state: ArithmeticState) -> ArithmeticUpdate:
    """TODO 2: validate, then use an if inside this single processing node.

    Return only answer and result. The exact format is:
    Hi {name}, your answer is {answer}.
    Empty addition returns 0; empty multiplication returns 1.
    sum and prod are available. Do not mutate state or its values list.
    """
    raise NotImplementedError("TODO 2: process_values")


def build_graph():
    """TODO 3: compile START -> calculator -> END using process_values.

    Register exactly one work-performing node, named 'calculator'. Do not add
    conditional edges or separate operation nodes. Return the compiled graph.
    """
    raise NotImplementedError("TODO 3: build_graph")


def check_work() -> None:
    """Local checks run only when the learner has implemented the TODOs."""
    graph = build_graph()
    assert set(graph.get_graph().nodes) == {START, "calculator", END}
    for values, operation, expected in (
        ([1, 2, 3, 4], "+", 10),
        ([1, 2, 3, 4], "*", 24),
        ([-3, 0, 5], "+", 2),
        ([-3, 0, 5], "*", 0),
        ([], "+", 0),
        ([], "*", 1),
        ([-2, 3], "*", -6),
        ([7], "+", 7),
    ):
        initial: ArithmeticState = {
            "values": values.copy(), "name": "Jack Sparrow", "operation": operation
        }
        before = {**initial, "values": initial["values"].copy()}
        update = process_values(initial)
        assert set(update) == {"answer", "result"}
        assert initial == before
        final = graph.invoke(initial, config=execution_config())
        assert final == {
            **before,
            "answer": expected,
            "result": f"Hi Jack Sparrow, your answer is {expected}.",
        }
        assert initial == before
    invalid_cases = [
        {"values": [2, 3], "name": "Ari", "operation": "/"},
        {"values": [True], "name": "Ari", "operation": "+"},
        {"values": [2.5], "name": "Ari", "operation": "*"},
        {"values": (2, 3), "name": "Ari", "operation": "+"},
        {"values": [2, 3], "name": " ", "operation": "+"},
        {"values": [2, 3], "name": "Ari"},
        {"name": "Ari", "operation": "+"},
        {"values": [2, 3], "operation": "+"},
    ]
    for invalid in invalid_cases:
        try:
            graph.invoke(invalid, config=execution_config())
        except ValueError:
            continue
        raise AssertionError("An invalid request was accepted")


def main() -> None:
    # Explicitly disable ambient tracing; this starter never loads an .env file.
    from langsmith import tracing_context

    with tracing_context(enabled=False):
        try:
            check_work()
        except NotImplementedError as error:
            print(f"STARTER_NOT_COMPLETED: {error}")
            return
    print("STARTER_CHECKS_PASSED: arithmetic and rejection checks completed.")


if __name__ == "__main__":
    main()
