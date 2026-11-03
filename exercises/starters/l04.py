"""L04 student starter: complete the three TODO functions, not the solution.

Run from the repository root: python -m exercises.starters.l04
Until all three nodes work, this command exits successfully with the explicit
STARTER_NOT_COMPLETED message. That message is not an assessment pass.
"""
from __future__ import annotations

from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.observability import graph_tracing
from course_support.runtime import execution_config


class ProfileState(TypedDict):
    name: str
    age: int
    skills: list[str]
    result: NotRequired[str]
    visited: NotRequired[list[str]]


def make_input(name: str, age: int, skills: list[str]) -> ProfileState:
    """Entry validation is supplied; keep this separate from node ordering."""
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
    # TODO 1: Return result '<name> welcome to the system.' and visited
    # ['welcome']. Begin afresh, even if an old result/visited value exists.
    # Return only those two updates; do not mutate state or its lists.
    raise NotImplementedError("Complete welcome")


def describe_age(state: ProfileState) -> dict:
    # TODO 2: Preserve result, append ' You are <age> years old', and extend
    # visited with 'age'. Use 'year' for age 1. Do not append a period here.
    raise NotImplementedError("Complete describe_age")


def describe_skills(state: ProfileState) -> dict:
    # TODO 3: Preserve result and finish the sentence. Empty list:
    # ' and you have no listed skills.' Nonempty list:
    # ' and you have skills in <formatted skills>.' Use the sole item for one
    # skill; for two or more use commas between earlier items and ' and '
    # before the last item. Keep input order and extend visited with 'skills'.
    raise NotImplementedError("Complete describe_skills")


def build_graph():
    """Topology is supplied: explain each of these four edges in the workbook."""
    builder = StateGraph(ProfileState)
    builder.add_node("welcome", welcome)
    builder.add_node("age", describe_age)
    builder.add_node("skills", describe_skills)
    builder.add_edge(START, "welcome")
    builder.add_edge("welcome", "age")
    builder.add_edge("age", "skills")
    builder.add_edge("skills", END)
    return builder.compile()


def main() -> None:
    with graph_tracing("none"):
        graph = build_graph()
        initial = make_input(
            "Linda", 31, ["Python", "machine learning", "LangGraph"]
        )
        try:
            final = graph.invoke(initial, config=execution_config())
            assert final["result"] == (
                "Linda welcome to the system. You are 31 years old and you have "
                "skills in Python, machine learning and LangGraph."
            )
            assert final["visited"] == ["welcome", "age", "skills"]
            for name, age, skills, ending in (
                ("Ari", 0, [], "0 years old and you have no listed skills."),
                ("Jo", 1, ["Python"], "1 year old and you have skills in Python."),
                ("Bo", 2, ["Python", "SQL"],
                 "2 years old and you have skills in Python and SQL."),
            ):
                sample = make_input(name, age, skills)
                output = graph.invoke(sample, config=execution_config())
                assert output["result"] == (
                    f"{name} welcome to the system. You are {ending}"
                )
                assert output["visited"] == ["welcome", "age", "skills"]
                assert all(output[key] == sample[key]
                           for key in ("name", "age", "skills"))
                assert "result" not in sample and "visited" not in sample
        except NotImplementedError as exc:
            print(
                f"STARTER_NOT_COMPLETED: {exc}. "
                "Follow course/chapters/l04/workbook.md"
            )
            return
        print("STARTER_CHECKS_PASSED: compare your reasoning with the workbook.")
        print(final["result"])


if __name__ == "__main__":
    main()
