"""S2: a real Anthropic/tool round trip, observable through runtime callbacks.

Only CLI --live constructs a model. Tests inject explicitly named test doubles.
The shared CLI defaults S2 to LangWatch and owns the parent trace and flushing.
"""
from __future__ import annotations

import json
import operator
from pathlib import Path
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from course_support.runtime import (
    execution_config,
    get_model,
    message_text,
    output_directory,
    run_cli,
    safe_write_text,
)


class TraceState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    events: Annotated[list[str], operator.add]
    model_calls: int
    tool_results: list[str]
    answer: str


@tool
def add_numbers(a: int, b: int) -> int:
    """Add two synthetic classroom integers; do not access external services."""
    return a + b


def build_graph(model):
    """Accept a real chat model or an explicit offline test double.

    Request one first-turn tool call and reject a missing call explicitly.
    The second turn uses the unbound model. Reject unexpected further tool calls
    rather than permit an unbounded agent loop.
    """
    tool_model = model.bind_tools(
        [add_numbers], tool_choice="auto", parallel_tool_calls=False
    )

    def prepare(state: TraceState) -> dict:
        return {"events": ["prepare"]}

    def agent(state: TraceState, config: RunnableConfig) -> dict:
        calls = state["model_calls"]
        if calls >= 2:
            raise RuntimeError("Model call budget exhausted.")
        selected = tool_model if calls == 0 else model
        response = selected.invoke(
            [SystemMessage(content=(
                "Use add_numbers once with a=18 and b=24, then explain its result "
                "in one short sentence. These are synthetic classroom data."
            ))] + state["messages"],
            config=config,
        )
        if not isinstance(response, AIMessage):
            raise TypeError("The chat model must return an AIMessage.")
        if calls == 0 and len(response.tool_calls) != 1:
            raise ValueError("Expected exactly one first-turn tool call.")
        if calls == 1 and response.tool_calls:
            raise RuntimeError("Tool round budget exhausted.")
        return {
            "messages": [response], "model_calls": calls + 1,
            "events": ["agent"],
        }

    def tools(state: TraceState, config: RunnableConfig) -> dict:
        call = state["messages"][-1].tool_calls[0]
        if call["name"] != add_numbers.name:
            raise ValueError("Unknown tool requested.")
        # Passing the entire call preserves the model's tool_call_id.
        observation = add_numbers.invoke(call, config=config)
        return {
            "messages": [observation],
            "tool_results": [str(observation.content)],
            "events": ["tools"],
        }

    def route(state: TraceState) -> str:
        return "tools" if state["messages"][-1].tool_calls else "finish"

    def finish(state: TraceState) -> dict:
        answer = message_text(state["messages"][-1]).strip()
        if not answer:
            raise ValueError("Expected a nonempty final model response.")
        return {"answer": answer, "events": ["finish"]}

    builder = StateGraph(TraceState)
    for name, node in (
        ("prepare", prepare), ("agent", agent),
        ("tools", tools), ("finish", finish),
    ):
        builder.add_node(name, node)
    builder.add_edge(START, "prepare")
    builder.add_edge("prepare", "agent")
    builder.add_conditional_edges(
        "agent", route, {"tools": "tools", "finish": "finish"}
    )
    builder.add_edge("tools", "agent")
    builder.add_edge("finish", END)
    return builder.compile()


def initial_state() -> TraceState:
    return {
        "messages": [HumanMessage(content="Please add 18 and 24 using the tool.")],
        "events": [], "model_calls": 0, "tool_results": [], "answer": "",
    }


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    model = get_model(live=live, max_tokens=256)
    result = build_graph(model).invoke(initial_state(), config=execution_config())
    assert result["tool_results"] == ["42"]
    assert result["model_calls"] == 2
    assert result["events"] == ["prepare", "agent", "tools", "agent", "finish"]
    assert result["answer"]
    summary = {
        "scenario": "synthetic-add-18-24",
        "tool_results": result["tool_results"],
        "model_calls": result["model_calls"],
        "events": result["events"],
        "answer": result["answer"],
        "ingestion_acknowledged": "not_checked",
        "dashboard_visually_verified": False,
        "flush_owner": "CLI tracing context after run_demo returns",
    }
    directory = output_directory(workdir, "s2")
    report = safe_write_text(
        directory, "s2-demo.txt", json.dumps(summary, indent=2) + "\n"
    )
    return {**summary, "report": str(report)}


if __name__ == "__main__":
    run_cli("S2", run_demo)
