"""L02 learner starter; implement only the three TODO functions below.

Run: python -m exercises.starters.l02
The untouched starter exits successfully with STARTER_NOT_COMPLETED, not a pass.
Do not import the reference solution or replace the acceptance checks.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.observability import graph_tracing
from course_support.runtime import execution_config


class MessageState(TypedDict):
    """The single message channel holds the incoming name, then the compliment."""

    message: str


def read_name(state: MessageState) -> str:
    """TODO 1: check type and blankness, then return the original name string.

    Missing message or a non-string: raise TypeError.
    Empty or whitespace-only string: raise ValueError.
    Valid names: preserve every character; do not return a stripped version.
    """
    raise NotImplementedError("TODO 1: implement read_name.")


def compliment_node(state: MessageState) -> MessageState:
    """TODO 2: use read_name and return a NEW one-key message update.

    For Bob, the exact text is:
    Bob, you're doing an amazing job learning LangGraph.
    Do not assign into state; do not hard-code the supplied person's name.
    """
    raise NotImplementedError("TODO 2: implement compliment_node.")


def build_graph():
    """TODO 3: register compliment_node as 'compliment', connect, and compile.

    The only path must be START -> compliment -> END.
    Return the compiled graph, not the StateGraph builder.
    """
    raise NotImplementedError("TODO 3: implement build_graph.")


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Acceptance checks supplied for the learner; no model or file output."""
    graph = build_graph()
    names = ("Bob", "Ada Lovelace", "Zoë", "  Bob  ")
    for name in names:
        original: MessageState = {"message": name}
        before = original.copy()
        update = compliment_node(original)
        assert update is not original and original == before
        expected = f"{name}, you're doing an amazing job learning LangGraph."
        assert update == {"message": expected}
        result = graph.invoke(original, config=execution_config())
        assert result == {"message": expected}
        assert original == before
        assert graph.invoke(original, config=execution_config()) == result

    for bad_state, error_type in (
        ({"message": ""}, ValueError),
        ({"message": " \t\n"}, ValueError),
        ({"message": 7}, TypeError),
        ({}, TypeError),
    ):
        try:
            graph.invoke(bad_state, config=execution_config())
        except error_type:
            pass
        else:
            raise AssertionError(f"Expected {error_type.__name__} for invalid input.")

    edges = {(edge.source, edge.target) for edge in graph.get_graph().edges}
    assert edges == {(START, "compliment"), ("compliment", END)}
    return {"checked_names": list(names), "model_used": False}


def main() -> None:
    try:
        with graph_tracing("none"):
            result = run_demo()
    except NotImplementedError as error:
        print(f"STARTER_NOT_COMPLETED: {error}")
        print("Complete the three TODO functions, then run this module again.")
        return
    print(json.dumps({"lesson": "L02", "status": "completed", "result": result},
                     indent=2))


if __name__ == "__main__":
    main()
