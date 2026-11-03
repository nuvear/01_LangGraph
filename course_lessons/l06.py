"""L06: a bounded graph back-edge, with repeatable local random draws.

Run from the project root: python -m course_lessons.l06 --backend none
No model, network, environment loading, or file output is needed by this lesson.
"""
from __future__ import annotations

from pathlib import Path
from random import Random
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config, run_cli

GENERATIONS = 5


class LoopState(TypedDict):
    name: str
    numbers: list[int]
    counter: int
    greeting: NotRequired[str]


def reset_loop(state: LoopState) -> dict:
    """Begin a fresh run, even if the caller supplies a stale counter or list."""
    if not isinstance(state["name"], str) or not state["name"].strip():
        raise ValueError("name must be a nonblank string")
    return {
        "greeting": f"Hi there, {state['name']}!",
        "numbers": [],
        "counter": 0,
    }


def loop_route(state: LoopState) -> Literal["again", "done"]:
    """Read the updated counter; do not mutate it in the routing function."""
    return "again" if state["counter"] < GENERATIONS else "done"


def build_graph(*, seed: int = 23):
    """Compile a repeatable graph; no mutable random generator is shared.

    Each visit uses seed + counter for a local Random instance. This is an
    explicit reproducibility policy for repeatable execution and debugging.
    """
    if type(seed) is not int:
        raise ValueError("seed must be an integer")

    def generate_number(state: LoopState) -> dict:
        number = Random(seed + state["counter"]).randint(0, 10)
        return {
            "numbers": [*state["numbers"], number],
            "counter": state["counter"] + 1,
        }

    builder = StateGraph(LoopState)
    builder.add_node("greeting", reset_loop)
    builder.add_node("generate", generate_number)
    builder.add_edge(START, "greeting")
    builder.add_edge("greeting", "generate")
    builder.add_conditional_edges(
        "generate", loop_route, {"again": "generate", "done": END}
    )
    return builder.compile()


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Check actual offline runs and return a small JSON-compatible summary."""
    # live/workdir are accepted for the shared CLI, not used for models or files.
    graph = build_graph()
    dirty: LoopState = {"name": "Student", "numbers": [999], "counter": -12}
    first = graph.invoke(dirty, config=execution_config())
    second = graph.invoke(
        {"name": "Student", "numbers": [], "counter": 90},
        config=execution_config(),
    )
    assert first["counter"] == GENERATIONS
    assert len(first["numbers"]) == GENERATIONS
    assert all(0 <= number <= 10 for number in first["numbers"])
    assert first["numbers"] == second["numbers"]
    assert first["name"] == "Student"
    assert first["greeting"] == "Hi there, Student!"
    assert dirty == {"name": "Student", "numbers": [999], "counter": -12}
    return {
        "counter": first["counter"],
        "numbers": first["numbers"],
        "greeting": first["greeting"],
        "repeatable": first["numbers"] == second["numbers"],
        "stale_state_reset": True,
        "model_used": False,
    }


if __name__ == "__main__":
    run_cli("L06", run_demo)
