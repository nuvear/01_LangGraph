"""L09: observable ReAct arithmetic, with real models only in live runs."""
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


class ArithmeticState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    model_calls: int


class ToolLoopLimit(RuntimeError):
    """The classroom request exceeded its explicit execution budget."""


@tool
def add(a: int, b: int) -> int:
    """Add two integers a and b; return their exact sum."""
    return a + b


@tool
def subtract(a: int, b: int) -> int:
    """Subtract integer b from integer a; argument order matters."""
    return a - b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers a and b; return their exact product."""
    return a * b


TOOLS = [add, subtract, multiply]
SYSTEM = (
    "You are an integer arithmetic tutor. Use the supplied tools for every "
    "requested arithmetic operation, even easy ones. For dependent operations, "
    "wait for the earlier tool result before requesting the next operation. "
    "Independent operations may share one batch. Do not call arithmetic tools "
    "for greetings, explanations, or jokes. Do not retry an identical invalid "
    "call. Answer concisely, writing final numerical answers as decimal digits."
)


def arithmetic_error(error: ToolException) -> str:
    """Return a safe validation observation without echoing exception internals."""
    return "Invalid arithmetic arguments. Supply integer a and b."


def route_after_model(state: ArithmeticState) -> str:
    """A tool request means execute tools, not that a result already exists."""
    last = state["messages"][-1]
    if not isinstance(last, AIMessage):
        raise TypeError("The model node must return an AIMessage.")
    if last.invalid_tool_calls:
        raise ValueError("The model returned malformed tool-call arguments.")
    if len(last.tool_calls) > 4:
        raise ToolLoopLimit("At most four tool calls are allowed in one batch.")
    return "tools" if last.tool_calls else END


def build_graph(model, *, max_model_calls: int = 6):
    """Bind an injected chat model and build the bounded, explicit tool loop."""
    if not 1 <= max_model_calls <= 10:
        raise ValueError("max_model_calls must be between 1 and 10.")
    bound_model = model.bind_tools(TOOLS)

    def call_model(state: ArithmeticState, config: RunnableConfig) -> dict:
        count = state["model_calls"]
        if count >= max_model_calls:
            raise ToolLoopLimit("Model-call budget exhausted; no answer claimed.")
        reply = bound_model.invoke(
            [SystemMessage(content=SYSTEM), *state["messages"]], config=config,
        )
        return {"messages": [reply], "model_calls": count + 1}

    builder = StateGraph(ArithmeticState)
    builder.add_node("model", call_model)
    builder.add_node("tools", ToolNode(TOOLS, handle_tool_errors=arithmetic_error))
    builder.add_edge(START, "model")
    builder.add_conditional_edges(
        "model", route_after_model, {"tools": "tools", END: END},
    )
    builder.add_edge("tools", "model")
    return builder.compile()


def inspect_transcript(state: ArithmeticState) -> dict:
    """Validate call/result pairing and expose only observable messages."""
    pending: dict[str, dict] = {}
    seen: set[str] = set()
    observations = []
    messages = state["messages"]
    for message in messages:
        if isinstance(message, AIMessage):
            assert not pending, "A model reply arrived before all tool results."
            for call in message.tool_calls:
                identifier = call["id"]
                assert identifier and identifier not in seen, "Duplicate call ID."
                seen.add(identifier)
                pending[identifier] = call
        elif isinstance(message, ToolMessage):
            assert message.tool_call_id in pending, "Unmatched tool result."
            call = pending.pop(message.tool_call_id)
            observations.append({
                "id": message.tool_call_id,
                "tool": call["name"],
                "args": call["args"],
                "result": message_text(message),
                "status": message.status,
            })
        else:
            assert not pending, "Non-tool message interrupted a tool-result batch."
    assert not pending, "Tool calls are still awaiting results."
    assert messages and isinstance(messages[-1], AIMessage)
    assert not messages[-1].tool_calls, "No final answer yet."
    final = message_text(messages[-1])
    assert final.strip(), "Final answer must contain text."
    return {
        "model_calls": state["model_calls"],
        "tool_calls": len(observations),
        "observations": observations,
        "final_text": final,
    }


def run_request(graph, prompt: str) -> dict:
    """Start a fresh request; this lesson does not persist conversation memory."""
    state = graph.invoke(
        {"messages": [HumanMessage(content=prompt)], "model_calls": 0},
        config=execution_config(),
    )
    return inspect_transcript(state)


def assert_numbers(text: str, expected: list[int]) -> None:
    """Check complete decimal tokens, not a brittle exact model sentence."""
    tokens = re.findall(r"(?<![\w.])-?\d+(?!\w|\.\d)", text)
    assert all(str(value) in tokens for value in expected), text


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Run source-backed examples using REAL Anthropic, never a fallback fake."""
    graph = build_graph(get_model(live=live, max_tokens=768))
    cases = [
        ("single", "Use add for 3 + 4.", [7], {"add"}),
        ("larger", "Use add for 34 + 21.", [55], {"add"}),
        ("multiple", "Compute 34 + 21 and separately 3 + 4.", [55, 7], {"add"}),
        (
            "sequential",
            "Add 40 + 12. After observing that result, multiply it by 6.",
            [52, 312], {"add", "multiply"},
        ),
        ("subtract", "Use subtract for 29 - 12.", [17], {"subtract"}),
        (
            "mixed", "Compute 9 + 9 with a tool, then tell one short clean joke.",
            [18], {"add"},
        ),
        ("no_tool", "Say a short friendly hello. Do not do arithmetic.", [], set()),
    ]
    checked = {}
    for name, prompt, results, names in cases:
        report = run_request(graph, prompt)
        rows = report["observations"]
        assert all(row["status"] == "success" for row in rows)
        assert names == {row["tool"] for row in rows}
        assert all(str(value) in [r["result"] for r in rows] for value in results)
        final_numbers = [312] if name == "sequential" else results
        assert_numbers(report["final_text"], final_numbers)
        if name == "no_tool":
            assert report["model_calls"] == 1 and not rows
        if name == "sequential":
            assert report["model_calls"] >= 3
            assert [r["tool"] for r in rows] == ["add", "multiply"]
            assert sorted(rows[1]["args"].values()) == [6, 52]
        checked[name] = report
    return {"checked_cases": checked, "persistent_memory": False}


if __name__ == "__main__":
    run_cli("L09", run_demo)
