"""L02: a single ordinary Python node, with no model or network requirement.

Run from the project root: python -m course_lessons.l02 --backend none
"""
from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config, run_cli


class MessageState(TypedDict):
    """The message begins as a name and becomes the formatted greeting."""

    message: str


def read_name(state: MessageState) -> str:
    """Reject absent, non-string, or blank names without changing valid text."""
    name = state.get("message")
    if not isinstance(name, str):
        raise TypeError("message must be a string.")
    if not name.strip():
        raise ValueError("message must not be blank.")
    return name


def greeting_node(state: MessageState) -> MessageState:
    """Read the incoming name and return a new dictionary containing its update."""
    name = read_name(state)
    return {"message": f"Hello, {name}! How is your day going?"}


def build_graph():
    """Register one node, connect its boundaries, and return the compiled graph."""
    builder = StateGraph(MessageState)
    builder.add_node("greeter", greeting_node)
    builder.add_edge(START, "greeter")
    builder.add_edge("greeter", END)
    return builder.compile()


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Check real graph behavior locally; live/workdir are shared CLI parameters.

    This deterministic lesson never creates a model, even when live=True.
    It writes no artifacts. The CLI itself manages its own output directory.
    """
    graph = build_graph()
    names = ("Bob", "Ada Lovelace", "Zoë", "  Bob  ")
    results = []
    for name in names:
        original: MessageState = {"message": name}
        before = original.copy()
        result = graph.invoke(original, config=execution_config())
        assert original == before, "The caller's input must not be mutated."
        assert result == {"message": f"Hello, {name}! How is your day going?"}
        results.append(result["message"])

    repeated = graph.invoke({"message": "Bob"}, config=execution_config())
    assert repeated["message"] == results[0], "Fresh runs must be deterministic."
    edge_pairs = {(edge.source, edge.target) for edge in graph.get_graph().edges}
    assert edge_pairs == {(START, "greeter"), ("greeter", END)}
    return {
        "input_name": names[0],
        "message": results[0],
        "checked_names": list(names),
        "input_unchanged": True,
        "deterministic": True,
        "graph_node": "greeter",
        "model_used": False,
    }


if __name__ == "__main__":
    run_cli("L02", run_demo)
