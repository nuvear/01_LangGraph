"""Independent reference solution: typed workshop badges, not the movie demo."""
from __future__ import annotations

from pathlib import Path
from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config, run_cli


class BadgeState(TypedDict):
    name: str | None
    sessions: int
    badge: NotRequired[str]


class NameUpdate(TypedDict):
    name: str


class BadgeUpdate(TypedDict):
    badge: str


def normalize_name(state: BadgeState) -> NameUpdate:
    """None/blank becomes Visitor; nonblank strings lose surrounding space."""
    name = state["name"]
    if name is not None and not isinstance(name, str):
        raise TypeError("name must be a string or None")
    clean = name.strip() if name is not None else ""
    return {"name": clean or "Visitor"}


def make_badge(state: BadgeState) -> BadgeUpdate:
    """Validate the count and return a new badge update, not a mutated state."""
    sessions = state["sessions"]
    if type(sessions) is not int:
        raise TypeError("sessions must be an integer, not a boolean")
    if sessions < 0:
        raise ValueError("sessions must be nonnegative")
    unit = "session" if sessions == 1 else "sessions"
    return {"badge": f"{state['name']}: {sessions} {unit}"}


def build_graph():
    """Both nodes execute even when sessions is zero; routing is a paper preview."""
    builder = StateGraph(BadgeState)
    builder.add_node("normalize_name", normalize_name)
    builder.add_node("make_badge", make_badge)
    builder.add_edge(START, "normalize_name")
    builder.add_edge("normalize_name", "make_badge")
    builder.add_edge("make_badge", END)
    return builder.compile()


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Run all three acceptance cases plus an explicit invalid-input check."""
    graph = build_graph()
    cases: list[tuple[BadgeState, str, str]] = [
        ({"name": "  Ada  ", "sessions": 2}, "Ada", "Ada: 2 sessions"),
        ({"name": None, "sessions": 0}, "Visitor", "Visitor: 0 sessions"),
        ({"name": "   ", "sessions": 1}, "Visitor", "Visitor: 1 session"),
    ]
    results = []
    for source, name, badge in cases:
        before = dict(source)
        result = graph.invoke(source, config=execution_config())
        assert result == {
            "name": name, "sessions": source["sessions"], "badge": badge,
        }
        assert source == before
        results.append(result)
    try:
        graph.invoke({"name": "Ada", "sessions": -1}, config=execution_config())
    except ValueError as error:
        assert str(error) == "sessions must be nonnegative"
    else:
        raise AssertionError("negative sessions must be rejected")
    return {
        "mode": "deterministic_no_model", "badges": results,
        "negative_sessions_rejected": True, "inputs_unchanged": True,
    }


if __name__ == "__main__":
    run_cli("L01", run_demo)
