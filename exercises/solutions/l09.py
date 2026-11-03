"""L09 reference solution: a bounded arithmetic runner with an observable audit."""
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
    """A request reached the exercise's model-call or batch limit."""


@tool
def add(a: int, b: int) -> int:
    """Return the sum of two integers a and b."""
    return a + b


@tool
def subtract(a: int, b: int) -> int:
    """Return integer a minus integer b, preserving their order."""
    return a - b


@tool
def multiply(a: int, b: int) -> int:
    """Return the product of two integers a and b."""
    return a * b


TOOLS = [add, subtract, multiply]
INSTRUCTIONS = (
    "Use the arithmetic tools for every requested calculation. For a dependent "
    "calculation, wait for the previous tool result before making the next call. "
    "You may batch independent calls. Do not use tools for a plain greeting. "
    "If a tool reports an error, do not repeat the same invalid call; explain "
    "the problem or correct its arguments. State final results as decimal digits."
)


def validation_observation(error: ToolException) -> str:
    """Only expected argument failures become safe, model-visible observations."""
    return "Invalid arithmetic arguments. Supply integer a and b."


def route_next(state: AuditState) -> str:
    """Exit on final text; reject malformed calls or a batch above three."""
    reply = state["messages"][-1]
    if not isinstance(reply, AIMessage):
        raise TypeError("Expected an AIMessage from the model node.")
    if reply.invalid_tool_calls:
        raise ValueError("Malformed tool-call arguments cannot be executed.")
    if len(reply.tool_calls) > 3:
        raise AuditLimit("At most three tool calls are allowed per batch.")
    return "tools" if reply.tool_calls else END


def make_agent(model, *, max_model_calls: int = 4):
    """Build the exercise graph independently of the demonstration module."""
    if not 1 <= max_model_calls <= 10:
        raise ValueError("max_model_calls must be between 1 and 10.")
    bound = model.bind_tools(TOOLS)

    def ask(state: AuditState, config: RunnableConfig) -> dict:
        if state["model_calls"] >= max_model_calls:
            raise AuditLimit("Model-call budget exhausted; no answer claimed.")
        response = bound.invoke(
            [SystemMessage(content=INSTRUCTIONS), *state["messages"]],
            config=config,
        )
        return {
            "messages": [response],
            "model_calls": state["model_calls"] + 1,
        }

    graph = StateGraph(AuditState)
    graph.add_node("model", ask)
    graph.add_node("tools", ToolNode(TOOLS, handle_tool_errors=validation_observation))
    graph.add_edge(START, "model")
    graph.add_conditional_edges("model", route_next, {"tools": "tools", END: END})
    graph.add_edge("tools", "model")
    return graph.compile()


def collect_audit(state: AuditState) -> dict:
    """Match results by call ID, never by parallel execution order."""
    pending = {}
    used_ids = set()
    rows = []
    for message in state["messages"]:
        if isinstance(message, AIMessage):
            if pending:
                raise ValueError("Missing tool results before the next AI message.")
            for call in message.tool_calls:
                identifier = call["id"]
                if not identifier or identifier in used_ids:
                    raise ValueError("Tool-call IDs must be nonempty and unique.")
                used_ids.add(identifier)
                pending[identifier] = call
        elif isinstance(message, ToolMessage):
            call = pending.pop(message.tool_call_id, None)
            if call is None:
                raise ValueError("Tool result has no matching pending call ID.")
            rows.append({
                "call_id": message.tool_call_id,
                "tool": call["name"],
                "args": call["args"],
                "result": message_text(message),
                "status": message.status,
            })
        elif pending:
            raise ValueError("A non-tool message interrupted pending tool results.")
    if pending:
        raise ValueError("The transcript ends with missing tool results.")
    messages = state["messages"]
    if not messages or not isinstance(messages[-1], AIMessage):
        raise ValueError("A completed transcript ends with an AIMessage.")
    final = messages[-1]
    if final.tool_calls or not message_text(final).strip():
        raise ValueError("A completed transcript needs a nonempty final answer.")
    return {
        "model_calls": state["model_calls"],
        "tool_calls": len(rows),
        "audit": rows,
        "final_text": message_text(final),
    }


def run_request(graph, prompt: str) -> dict:
    """Invoke a fresh state and retain selected runtime callbacks."""
    return collect_audit(graph.invoke(
        {"messages": [HumanMessage(content=prompt)], "model_calls": 0},
        config=execution_config(),
    ))


def check_case(report: dict, expected: list[int]) -> None:
    """Check actual tool observations plus final numbers; ignore model phrasing."""
    successful = [r for r in report["audit"] if r["status"] == "success"]
    assert len(successful) == report["tool_calls"]
    assert sorted(int(r["result"]) for r in successful) == sorted(expected)
    assert report["model_calls"] <= 4


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Validate the exact workbook cases with real, explicitly enabled Anthropic."""
    graph = make_agent(get_model(live=live, max_tokens=768))
    compound = run_request(
        graph,
        "Subtract 5 from 18. After seeing the result, multiply that result by 4.",
    )
    check_case(compound, [13, 52])
    assert [r["tool"] for r in compound["audit"]] == ["subtract", "multiply"]
    assert compound["audit"][0]["args"] == {"a": 18, "b": 5}
    assert sorted(compound["audit"][1]["args"].values()) == [4, 13]
    assert compound["model_calls"] >= 3
    assert "52" in re.findall(r"(?<![\w.])-?\d+(?!\w|\.\d)", compound["final_text"])
    independent = run_request(graph, "Compute 9 + 6 and separately 8 * 3.")
    check_case(independent, [15, 24])
    assert {r["tool"] for r in independent["audit"]} == {"add", "multiply"}
    for value in ("15", "24"):
        assert value in re.findall(
            r"(?<![\w.])-?\d+(?!\w|\.\d)", independent["final_text"],
        )
    greeting = run_request(graph, "Say a friendly hello. Do not calculate anything.")
    check_case(greeting, [])
    assert greeting["model_calls"] == 1
    return {
        "compound": compound,
        "independent": independent,
        "greeting": greeting,
        "audit_is_observable_messages_not_private_reasoning": True,
    }


if __name__ == "__main__":
    run_cli("L09", run_demo)
