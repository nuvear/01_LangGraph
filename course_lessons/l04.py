"""L04: two sequential nodes, an overwrite bug, and explicit preservation.

Run from the repository root: python -m course_lessons.l04 --backend none
This is ordinary Python in a LangGraph workflow, not an LLM application.
"""
from __future__ import annotations

from pathlib import Path
from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config, run_cli


class GreetingState(TypedDict):
    name: str
    age: int
    final: NotRequired[str]
    visited: NotRequired[list[str]]


def make_input(name: str, age: int) -> GreetingState:
    """Validate deliberately: TypedDict annotations alone do not check values."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a nonblank string")
    if type(age) is not int or age < 0:
        raise ValueError("age must be a nonnegative integer, not a boolean")
    return {"name": name, "age": age}


def greet(state: GreetingState) -> dict:
    """Start this run's message; do not mutate the dictionary passed in."""
    return {"final": f"Hi {state['name']}.", "visited": ["greet"]}


def append_age(state: GreetingState) -> dict:
    """Read the earlier message and return a replacement that preserves it."""
    unit = "year" if state["age"] == 1 else "years"
    sentence = f"You are {state['age']} {unit} old."
    return {
        "final": f"{state['final']} {sentence}",
        "visited": state["visited"] + ["age"],
    }


def overwrite_age(state: GreetingState) -> dict:
    """Intentional counterexample: the new final value drops the greeting."""
    unit = "year" if state["age"] == 1 else "years"
    return {
        "final": f"You are {state['age']} {unit} old.",
        "visited": state["visited"] + ["age"],
    }


def build_graph(*, demonstrate_overwrite: bool = False):
    """Build the same topology with either a broken or corrected age node."""
    builder = StateGraph(GreetingState)
    builder.add_node("greet", greet)
    age_node = overwrite_age if demonstrate_overwrite else append_age
    builder.add_node("age", age_node)
    builder.add_edge(START, "greet")
    builder.add_edge("greet", "age")
    builder.add_edge("age", END)
    return builder.compile()


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Assert real graph outcomes; live/workdir are standard course arguments.

    Neither argument activates a model call or file write in this lesson.
    """
    initial = make_input("Charlie", 20)
    broken = build_graph(demonstrate_overwrite=True).invoke(
        initial, config=execution_config()
    )
    fixed = build_graph().invoke(initial, config=execution_config())
    assert broken["final"] == "You are 20 years old."
    assert fixed["final"] == "Hi Charlie. You are 20 years old."
    assert broken["visited"] == fixed["visited"] == ["greet", "age"]
    assert fixed["name"] == initial["name"]
    assert fixed["age"] == initial["age"]
    assert initial == {"name": "Charlie", "age": 20}

    updates = list(build_graph().stream(
        initial, config=execution_config(), stream_mode="updates"
    ))
    assert [next(iter(update)) for update in updates] == ["greet", "age"]
    assert set(updates[0]["greet"]) == {"final", "visited"}
    assert updates[-1]["age"]["final"] == fixed["final"]
    return {
        "broken_final": broken["final"],
        "corrected_final": fixed["final"],
        "node_order": fixed["visited"],
        "updates": updates,
        "inputs_unchanged": True,
        "model_calls": 0,
    }


if __name__ == "__main__":
    run_cli("L04", run_demo)
