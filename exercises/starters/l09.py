"""L09 starter: implement the three TODO functions, then request a live run.

Run unchanged: python -m exercises.starters.l09
It exits successfully with STARTER_NOT_COMPLETED, not a fake passing result.
"""
from __future__ import annotations

from pathlib import Path
import re
from typing import Annotated, TypedDict

from langchain_core.messages import (
    AIMessage, AnyMessage, HumanMessage, SystemMessage, ToolMessage,
)
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import ToolException, tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from course_support.runtime import (
    execution_config, get_model, message_text, run_cli,
)


class AuditState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    model_calls: int


class AuditLimit(RuntimeError):
    """Raise when the model-call budget or tool batch limit is exceeded."""


@tool
def add(a: int, b: int) -> int:
    """Return the sum of integers a and b."""
    return a + b


@tool
def subtract(a: int, b: int) -> int:
    """Return integer a minus integer b, in that order."""
    return a - b


@tool
def multiply(a: int, b: int) -> int:
    """Return the product of integers a and b."""
    return a * b


TOOLS = [add, subtract, multiply]
INSTRUCTIONS = (
    "Use tools for every calculation, wait for results before dependent calls, "
    "and answer final numbers as decimal digits. Independent calls may share a "
    "batch. Do not use arithmetic tools for greetings. If arguments are invalid, "
    "correct them or explain the error; do not repeat the identical failed call."
)


def validation_observation(error: ToolException) -> str:
    return "Invalid arithmetic arguments. Supply integer a and b."


def route_next(state: AuditState) -> str:
    """TODO 1: return 'tools' or END after validating the last AI message.

    Reject non-AI messages with TypeError, invalid_tool_calls with ValueError,
    and batches above three calls with AuditLimit. Do not execute tools here.
    """
    raise NotImplementedError("TODO 1: route_next")


def make_agent(model, *, max_model_calls: int = 4):
    """TODO 2: bind TOOLS and compile START -> model -> tools -> model/END.

    Accept budgets 1..10. The model node prepends SystemMessage(INSTRUCTIONS),
    includes every state message, forwards its RunnableConfig, returns only the
    new AI message and incremented count, and raises AuditLimit BEFORE an
    invocation beyond the budget. Use ToolNode with validation_observation.
    Pass route_next to add_conditional_edges and add tools -> model.
    """
    raise NotImplementedError("TODO 2: make_agent")


def collect_audit(state: AuditState) -> dict:
    """TODO 3: pair every ToolMessage with its pending AI call by ID.

    Return model_calls, tool_calls, audit, final_text. Each audit row contains
    call_id, tool, args, result (text), status. Keep error rows as error rows.
    Raise ValueError for duplicate/empty IDs, orphan/missing results, interrupted
    batches, or a missing/nontext/pending-call final AI answer. Do not assume
    parallel tool messages arrive in call order. Never invent missing results.
    """
    raise NotImplementedError("TODO 3: collect_audit")


def run_request(graph, prompt: str) -> dict:
    return collect_audit(graph.invoke(
        {"messages": [HumanMessage(content=prompt)], "model_calls": 0},
        config=execution_config(),
    ))


def check_case(report: dict, expected: list[int]) -> None:
    rows = report["audit"]
    assert all(row["status"] == "success" for row in rows)
    assert sorted(int(row["result"]) for row in rows) == sorted(expected)
    assert report["tool_calls"] == len(rows)
    assert report["model_calls"] <= 4


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """The supplied acceptance harness; do not replace it with fixed answers."""
    graph = make_agent(get_model(live=live, max_tokens=768))
    compound = run_request(
        graph,
        "Subtract 5 from 18. After seeing the result, multiply that result by 4.",
    )
    check_case(compound, [13, 52])
    assert [row["tool"] for row in compound["audit"]] == ["subtract", "multiply"]
    assert compound["audit"][0]["args"] == {"a": 18, "b": 5}
    assert sorted(compound["audit"][1]["args"].values()) == [4, 13]
    assert compound["model_calls"] >= 3
    assert "52" in re.findall(r"(?<![\w.])-?\d+(?!\w|\.\d)", compound["final_text"])
    independent = run_request(graph, "Compute 9 + 6 and separately 8 * 3.")
    check_case(independent, [15, 24])
    assert {row["tool"] for row in independent["audit"]} == {"add", "multiply"}
    for value in ("15", "24"):
        assert value in re.findall(
            r"(?<![\w.])-?\d+(?!\w|\.\d)", independent["final_text"],
        )
    greeting = run_request(graph, "Say a friendly hello. Do not calculate anything.")
    check_case(greeting, [])
    assert greeting["model_calls"] == 1
    return {"compound": compound, "independent": independent, "greeting": greeting}


class BindingOnlyProbe:
    """An explicit offline readiness probe, NOT an AI response or live model.

    Building a graph binds schemas but must not invoke the model. This probe
    only locates remaining TODOs; readiness is not proof of a correct solution.
    """

    def bind_tools(self, tools):
        return self

    def invoke(self, messages, config=None):
        raise AssertionError("The readiness probe must never invoke a model.")


def check_started() -> None:
    state = {"messages": [AIMessage(content="Ready")], "model_calls": 1}
    route_next(state)
    make_agent(BindingOnlyProbe())
    collect_audit(state)


if __name__ == "__main__":
    try:
        check_started()
    except NotImplementedError as error:
        print(f"STARTER_NOT_COMPLETED: {error}. Implement all three TODOs.")
    else:
        run_cli("L09", run_demo)
