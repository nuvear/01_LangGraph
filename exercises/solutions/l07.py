"""L07 reference solution: stateless help-desk session (added practice).

Independent of course_lessons.l07. This is an answer to the workbook task,
not an alternate entry point that imports the demonstration.
"""
from __future__ import annotations

from itertools import islice
from pathlib import Path
from typing import Iterable, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from course_support.runtime import (
    execution_config,
    get_model,
    message_text,
    run_cli,
)


class RequestState(TypedDict, total=False):
    prompt: str
    reply: str
    sent_messages: list[str]
    usage: dict


def classify_entry(raw: str) -> str:
    """Normalize only for control decisions; keep submitted text unchanged."""
    if not isinstance(raw, str):
        raise TypeError("Each entry must be a string.")
    if raw.strip().casefold() == "exit":
        return "exit"
    if not raw.strip():
        return "skip"
    return "send"


def build_bot(model):
    """Construct exactly START -> respond -> END, without history storage."""
    def respond(state: RequestState, config: RunnableConfig) -> dict:
        prompt = state.get("prompt", "")
        if classify_entry(prompt) != "send":
            raise ValueError("The graph accepts only nonblank, non-exit prompts.")
        messages = [HumanMessage(content=prompt)]
        response = model.invoke(messages, config=config)
        if not isinstance(response, AIMessage):
            raise TypeError("The chat model must return an AIMessage.")
        reply = message_text(response)
        if not reply.strip():
            raise ValueError("The model returned no displayable text.")
        return {
            "reply": reply,
            "sent_messages": [message.content for message in messages],
            "usage": dict(response.usage_metadata or {}),
        }

    builder = StateGraph(RequestState)
    builder.add_node("respond", respond)
    builder.add_edge(START, "respond")
    builder.add_edge("respond", END)
    return builder.compile()


def run_session(graph, entries: Iterable[str], *, max_entries: int = 6) -> dict:
    """Process at most max_entries raw entries, counting blanks and exit too."""
    if type(max_entries) is not int or max_entries < 1:
        raise ValueError("max_entries must be a positive integer.")
    turns = []
    skipped = 0
    inspected = 0
    stop_reason = "exhausted"
    for raw in islice(entries, max_entries):
        inspected += 1
        action = classify_entry(raw)
        if action == "exit":
            stop_reason = "exit"
            break
        if action == "skip":
            skipped += 1
            continue
        result = graph.invoke({"prompt": raw}, config=execution_config())
        assert result["sent_messages"] == [raw]
        turns.append(result)
    else:
        if inspected == max_entries:
            stop_reason = "limit"
    return {
        "turns": turns,
        "skipped": skipped,
        "inspected": inspected,
        "stop_reason": stop_reason,
    }


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    if not live:
        raise ValueError("L07 solution requires --live; offline tests use doubles.")
    graph = build_bot(get_model(live=live, max_tokens=256))
    entries = [
        "  ",
        "My name is Mira. Say hello briefly.",
        "What is my name?",
        " ExIt ",
        "This must never be sent.",
    ]
    session = run_session(graph, entries)
    turns = session["turns"]
    assert session["inspected"] == 4
    assert session["skipped"] == 1
    assert session["stop_reason"] == "exit"
    assert len(turns) == 2
    assert [t["sent_messages"] for t in turns] == [[p] for p in entries[1:3]]
    assert all(turn["reply"].strip() for turn in turns)
    return {
        "checked_turns": len(turns),
        "skipped": session["skipped"],
        "inspected": session["inspected"],
        "stop_reason": session["stop_reason"],
        "messages_per_request": [len(t["sent_messages"]) for t in turns],
        "prior_turns_forwarded": False,
        "replies": [t["reply"] for t in turns],
        "usage": [t["usage"] for t in turns],
    }


if __name__ == "__main__":
    run_cli("L07", run_demo)
