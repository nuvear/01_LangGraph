"""L07: a real Anthropic call in a stateless, single-node graph.

The CLI scripts two turns and exit so it does not wait for classroom input.
For an interactive terminal, call terminal_chat(build_bot(get_model(live=True)))
from a Python shell. Each submitted turn is a fresh one-message request.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from course_support.runtime import (
    execution_config,
    get_model,
    message_text,
    run_cli,
)


class BotState(TypedDict, total=False):
    messages: list[HumanMessage]
    reply: str
    usage: dict
    sent_messages: list[str]


def build_bot(model):
    """Inject a real chat model, or an explicitly named offline test double."""
    def call_model(state: BotState, config: RunnableConfig) -> dict:
        messages = state.get("messages", [])
        if len(messages) != 1 or not isinstance(messages[0], HumanMessage):
            raise ValueError("Supply exactly one fresh HumanMessage.")
        if not isinstance(messages[0].content, str) or not messages[0].content.strip():
            raise ValueError("Supply nonblank text.")
        # This is the entire request: no saved earlier turns or system memory.
        response = model.invoke(messages, config=config)
        if not isinstance(response, AIMessage):
            raise TypeError("The chat model must return an AIMessage.")
        reply = message_text(response)
        if not reply.strip():
            raise ValueError("The model returned no displayable text.")
        return {
            "reply": reply,
            "usage": dict(response.usage_metadata or {}),
            "sent_messages": [message.content for message in messages],
        }

    builder = StateGraph(BotState)
    builder.add_node("call_model", call_model)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", END)
    return builder.compile()  # Intentionally no checkpointer.


def ask(graph, prompt: str) -> dict:
    """Never feed a previous result back into the next graph invocation."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Supply nonblank text.")
    return graph.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        config=execution_config(),
    )


def terminal_chat(
    graph,
    *,
    read: Callable[[str], str] = input,
    write: Callable[[str], None] = print,
    max_entries: int = 10,
) -> dict:
    """A bounded Python input loop, not a loop edge or conversation memory."""
    if type(max_entries) is not int or max_entries < 1:
        raise ValueError("max_entries must be a positive integer.")
    turns = []
    skipped = 0
    stop_reason = "limit"
    for _ in range(max_entries):
        try:
            raw = read("You (exit to stop): ")
        except EOFError:
            stop_reason = "eof"
            break
        if raw.strip().casefold() == "exit":
            stop_reason = "exit"
            break
        if not raw.strip():
            skipped += 1
            write("Blank input skipped; no model call.")
            continue
        result = ask(graph, raw)
        turns.append(result)
        write(result["reply"])
    return {"turns": turns, "skipped": skipped, "stop_reason": stop_reason}


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Two real requests when opted in; no canned response fallback."""
    if not live:
        raise ValueError("L07 requires --live; use offline pytest for test doubles.")
    model = get_model(live=live, max_tokens=256)
    graph = build_bot(model)
    prompts = ["Hello, my name is Bob.", "What is my name?"]
    entries = iter([*prompts, "exit"])
    session = terminal_chat(graph, read=lambda _: next(entries))
    turns = session["turns"]
    assert session["stop_reason"] == "exit"
    assert len(turns) == 2
    assert [turn["sent_messages"] for turn in turns] == [[p] for p in prompts]
    assert all(len(turn["messages"]) == 1 for turn in turns)
    assert all(turn["reply"].strip() for turn in turns)
    return {
        "checked_turns": len(turns),
        "messages_per_request": [len(t["sent_messages"]) for t in turns],
        "prior_turns_forwarded": False,
        "stop_reason": session["stop_reason"],
        "replies": [turn["reply"] for turn in turns],
        "usage": [turn["usage"] for turn in turns],
        "evidence": "Actual request construction; not exact name-recall wording.",
    }


if __name__ == "__main__":
    run_cli("L07", run_demo)
