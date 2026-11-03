"""L04 reference solution: welcome -> age -> skills, retaining all components.

Run: python -m exercises.solutions.l04 --backend none
Independent of the demonstration and starter; no LLM or network is needed.
"""
from __future__ import annotations

from pathlib import Path
from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config, run_cli


class ProfileState(TypedDict):
    name: str
    age: int
    skills: list[str]
    result: NotRequired[str]
    visited: NotRequired[list[str]]


def make_input(name: str, age: int, skills: list[str]) -> ProfileState:
    """Validate entry data and copy the list so callers retain their own list."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a nonblank string")
    if type(age) is not int or age < 0:
        raise ValueError("age must be a nonnegative integer, not a boolean")
    if not isinstance(skills, list) or any(
        not isinstance(skill, str) or not skill.strip() for skill in skills
    ):
        raise ValueError("skills must be a list of nonblank strings")
    return {"name": name, "age": age, "skills": list(skills)}


def welcome(state: ProfileState) -> dict:
    """Begin a fresh profile; an old result must not leak into this one."""
    return {
        "result": f"{state['name']} welcome to the system.",
        "visited": ["welcome"],
    }


def describe_age(state: ProfileState) -> dict:
    """Retain the welcome and add age without closing the second sentence."""
    unit = "year" if state["age"] == 1 else "years"
    return {
        "result": f"{state['result']} You are {state['age']} {unit} old",
        "visited": state["visited"] + ["age"],
    }


def describe_skills(state: ProfileState) -> dict:
    """Preserve input order and use a readable final 'and' without an Oxford comma."""
    skills = state["skills"]
    if not skills:
        ending = " and you have no listed skills."
    else:
        if len(skills) == 1:
            formatted = skills[0]
        else:
            formatted = ", ".join(skills[:-1]) + " and " + skills[-1]
        ending = f" and you have skills in {formatted}."
    return {
        "result": state["result"] + ending,
        "visited": state["visited"] + ["skills"],
    }


def build_graph():
    """Use exactly three work nodes and two node-to-node directed edges."""
    builder = StateGraph(ProfileState)
    builder.add_node("welcome", welcome)
    builder.add_node("age", describe_age)
    builder.add_node("skills", describe_skills)
    builder.add_edge(START, "welcome")
    builder.add_edge("welcome", "age")
    builder.add_edge("age", "skills")
    builder.add_edge("skills", END)
    return builder.compile()


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Check the workbook acceptance cases with independent invocations."""
    graph = build_graph()
    initial = make_input("Linda", 31, ["Python", "machine learning", "LangGraph"])
    final = graph.invoke(initial, config=execution_config())
    expected = (
        "Linda welcome to the system. You are 31 years old and you have skills "
        "in Python, machine learning and LangGraph."
    )
    assert final["result"] == expected
    assert final["visited"] == ["welcome", "age", "skills"]
    for key in ("name", "age", "skills"):
        assert final[key] == initial[key]
    assert "result" not in initial and "visited" not in initial

    empty = graph.invoke(make_input("Ari", 0, []), config=execution_config())
    assert empty["result"] == (
        "Ari welcome to the system. You are 0 years old and you have no listed "
        "skills."
    )
    single = graph.invoke(
        make_input("Jo", 1, ["Python"]), config=execution_config()
    )
    assert single["result"] == (
        "Jo welcome to the system. You are 1 year old and you have skills in "
        "Python."
    )
    assert empty["visited"] == single["visited"] == final["visited"]
    return {
        "result": final["result"],
        "node_order": final["visited"],
        "empty_skills_result": empty["result"],
        "single_skill_result": single["result"],
        "inputs_unchanged": True,
        "model_calls": 0,
    }


if __name__ == "__main__":
    run_cli("L04", run_demo)
