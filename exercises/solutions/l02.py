"""L02 reference solution: one-node personalized compliment, implemented independently.

Run from the project root: python -m exercises.solutions.l02 --backend none
"""
from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config, run_cli


class MessageState(TypedDict):
    """One channel: incoming name, then outgoing personalized compliment."""

    message: str


def read_name(state: MessageState) -> str:
    """Validate the input while preserving every character of a valid name."""
    name = state.get("message")
    if not isinstance(name, str):
        raise TypeError("message must be a string.")
    if not name.strip():
        raise ValueError("message must not be blank.")
    return name


def compliment_node(state: MessageState) -> MessageState:
    """Return the message update, without assigning into the supplied state."""
    name = read_name(state)
    return {"message": f"{name}, you're doing an amazing job learning LangGraph."}


def build_graph():
    """Build exactly START -> compliment -> END and compile it for invocation."""
    builder = StateGraph(MessageState)
    builder.add_node("compliment", compliment_node)
    builder.add_edge(START, "compliment")
    builder.add_edge("compliment", END)
    return builder.compile()


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Execute the actual solution graph and assert the workbook acceptance cases.

    Neither parameter enables a model in this deterministic lesson. No files are
    written by this function; run_cli owns CLI output-directory setup.
    """
    graph = build_graph()
    names = ("Bob", "Ada Lovelace", "Zoë", "  Bob  ")
    outputs = []
    for name in names:
        original: MessageState = {"message": name}
        before = original.copy()
        update = compliment_node(original)
        assert original == before and update is not original
        expected = f"{name}, you're doing an amazing job learning LangGraph."
        result = graph.invoke(original, config=execution_config())
        assert result == {"message": expected}
        assert original == before
        outputs.append(result["message"])

    # These errors come from explicit Python checks, not from TypedDict itself.
    rejected = 0
    invalid_cases = (
        ({"message": ""}, ValueError),
        ({"message": " \t\n"}, ValueError),
        ({"message": 7}, TypeError),
        ({}, TypeError),
    )
    for bad_state, expected_error in invalid_cases:
        try:
            graph.invoke(bad_state, config=execution_config())
        except expected_error:
            rejected += 1
        else:
            raise AssertionError("The solution accepted an invalid name.")
    assert rejected == len(invalid_cases)
    repeat = graph.invoke({"message": "Bob"}, config=execution_config())
    assert repeat["message"] == outputs[0]
    edges = {(edge.source, edge.target) for edge in graph.get_graph().edges}
    assert edges == {(START, "compliment"), ("compliment", END)}
    return {
        "input_name": names[0],
        "message": outputs[0],
        "checked_names": list(names),
        "input_unchanged": True,
        "deterministic": True,
        "invalid_inputs_rejected": rejected,
        "graph_node": "compliment",
        "model_used": False,
    }


if __name__ == "__main__":
    run_cli("L02", run_demo)
