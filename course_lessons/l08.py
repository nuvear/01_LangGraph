"""L08: manual process-local history and a readable, non-restoring text log."""
from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from course_support.runtime import (
    execution_config,
    get_model,
    message_text,
    output_directory,
    run_cli,
    safe_write_text,
)


class ConversationState(TypedDict):
    # No reducer: this channel is replaced by each returned list.
    messages: list[BaseMessage]


def build_graph(model):
    """Accept a real chat model, or an explicitly named offline test double."""
    def respond(state: ConversationState, config: RunnableConfig) -> dict:
        history = state["messages"]
        if not history or not isinstance(history[-1], HumanMessage):
            raise ValueError("A turn must end with a HumanMessage.")
        response = model.invoke(list(history), config=config)
        if not isinstance(response, AIMessage) or response.tool_calls:
            raise TypeError("This text-only lesson requires an AIMessage, no tools.")
        if not message_text(response).strip():
            raise ValueError("The model returned no visible text.")
        # Preserve the AIMessage itself, including its ID and usage metadata.
        return {"messages": [*history, response]}

    builder = StateGraph(ConversationState)
    builder.add_node("respond", respond)
    builder.add_edge(START, "respond")
    builder.add_edge("respond", END)
    return builder.compile()  # Deliberately no checkpointer in L08.


def run_turn(graph, history: list[BaseMessage], text: str) -> list[BaseMessage]:
    """Send prior turns plus one new human message without mutating the caller."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Enter nonblank text.")
    result = graph.invoke(
        {"messages": [*history, HumanMessage(content=text)]},
        config=execution_config(),
    )
    return result["messages"]


def format_transcript(history: list[BaseMessage]) -> str:
    """Readable text only, not an unambiguous reload format or a checkpoint."""
    entries = []
    for message in history:
        if isinstance(message, HumanMessage):
            role = "Human"
        elif isinstance(message, AIMessage):
            role = "AI"
        else:
            raise TypeError("Only human and AI messages belong in this log.")
        entries.append(f"{role}:\n{message_text(message)}\n")
    return "\n".join(entries)


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Make three real Anthropic calls; never silently substitute canned replies."""
    model = get_model(live=live, max_tokens=192)
    graph = build_graph(model)
    first = "Hi, my name is Steve. Please acknowledge briefly."
    second = "gud morning! What name did I give you?"
    history = run_turn(graph, [], first)
    assert len(history) == 2
    history = run_turn(graph, history, second)
    assert len(history) == 4
    assert [message.type for message in history] == ["human", "ai"] * 2
    assert history[0].content == first and history[2].content == second
    recall_answer = message_text(history[-1])
    assert "steve" in recall_answer.casefold(), "Inspect the live recall response."

    # Same compiled graph, new list: no state is retained by this graph itself.
    fresh = run_turn(
        graph, [],
        "What name did I give you? If absent here, say you don't know.",
    )
    assert len(fresh) == 2
    assert not any(message is history[0] for message in fresh)
    directory = output_directory(workdir, "L08")
    transcript = format_transcript(history)
    path = safe_write_text(directory, "conversation.txt", transcript)
    assert path.read_text(encoding="utf-8") == transcript
    assert f"Human:\n{second}\n" in transcript
    return {
        "history_messages": len(history),
        "roles": [message.type for message in history],
        "recall_answer": recall_answer,
        "fresh_history_messages": len(fresh),
        "fresh_answer": message_text(fresh[-1]),
        "fresh_history_is_reset_simulation": True,
        "log_path": str(path),
        "raw_input_preserved": True,
        "automatic_log_reload": False,
        "model_calls": 3,
    }


if __name__ == "__main__":
    run_cli("L08", run_demo)
