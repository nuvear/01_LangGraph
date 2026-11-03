"""L01 learner starter: implement the three TODO functions, then run this module."""
from __future__ import annotations

import json
from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config


class BadgeState(TypedDict):
    name: str | None
    sessions: int
    badge: NotRequired[str]


class NameUpdate(TypedDict):
    name: str


class BadgeUpdate(TypedDict):
    badge: str


def normalize_name(state: BadgeState) -> NameUpdate:
    """TODO 1: Return only name; trim strings; None/blank becomes Visitor.

    Raise TypeError for names other than strings or None. Do not mutate state.
    """
    raise NotImplementedError("TODO 1: implement normalize_name")


def make_badge(state: BadgeState) -> BadgeUpdate:
    """TODO 2: Return only badge: '<name>: <sessions> session[s]'.

    Exactly 1 uses 'session'. Reject non-int counts (including bool) with
    TypeError and negative counts with ValueError. Zero is valid.
    """
    raise NotImplementedError("TODO 2: implement make_badge")


def build_graph():
    """TODO 3: Compile START -> normalize_name -> make_badge -> END.

    Register both Python functions using these exact node names. Use
    StateGraph(BadgeState), add_node, add_edge and compile. Do not import
    either the demonstration or reference solution.
    """
    raise NotImplementedError("TODO 3: implement build_graph")


def check_work() -> dict:
    """Small learner checks; the independent pytest file has more edge cases."""
    graph = build_graph()
    cases = [
        ({"name": "  Ada  ", "sessions": 2}, "Ada", "Ada: 2 sessions"),
        ({"name": None, "sessions": 0}, "Visitor", "Visitor: 0 sessions"),
        ({"name": "   ", "sessions": 1}, "Visitor", "Visitor: 1 session"),
    ]
    for source, name, badge in cases:
        before = dict(source)
        result = graph.invoke(source, config=execution_config())
        assert result == {
            "name": name, "sessions": source["sessions"], "badge": badge,
        }
        assert source == before, "Nodes must return updates, not mutate inputs."
    for invalid, expected_error in [
        (-1, ValueError), ("2", TypeError), (True, TypeError),
    ]:
        try:
            graph.invoke(
                {"name": "Ada", "sessions": invalid}, config=execution_config(),
            )
        except expected_error:
            pass
        else:
            raise AssertionError(f"sessions={invalid!r} must be rejected")
    try:
        normalize_name({"name": 42, "sessions": 1})
    except TypeError:
        pass
    else:
        raise AssertionError("non-string/non-None names must be rejected")
    return {"status": "STARTER_CHECKS_PASSED", "checked_cases": len(cases)}


if __name__ == "__main__":
    try:
        summary = check_work()
    except NotImplementedError as error:
        print(f"STARTER_NOT_COMPLETED: {error}")
    else:
        print(json.dumps(summary, indent=2))
