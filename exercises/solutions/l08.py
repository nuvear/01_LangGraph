"""L08 reference solution: bounded model input, complete process-local transcript."""
from __future__ import annotations

from pathlib import Path

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, MessagesState, StateGraph

from course_support.runtime import (
    execution_config,
    get_model,
    message_text,
    output_directory,
    run_cli,
    safe_write_text,
)


def select_prompt(
    history: list[BaseMessage], max_pairs: int = 1,
) -> list[BaseMessage]:
    """Keep recent complete human/AI pairs and the pending human message.

    This intentionally handles only alternating text-chat turns, not system or
    tool messages. It bounds message count, NOT tokens, and never trims state.
    """
    if isinstance(max_pairs, bool) or not isinstance(max_pairs, int):
        raise ValueError("max_pairs must be a nonnegative integer.")
    if max_pairs < 0:
        raise ValueError("max_pairs must be a nonnegative integer.")
    if not history or len(history) % 2 != 1:
        raise ValueError("Expected complete pairs followed by one human message.")
    for index, message in enumerate(history):
        expected = HumanMessage if index % 2 == 0 else AIMessage
        if not isinstance(message, expected):
            raise ValueError("Expected alternating human/AI messages.")
        if isinstance(message, AIMessage) and message.tool_calls:
            raise ValueError("Tool conversations need a different trimming policy.")
    return list(history[-(2 * max_pairs + 1):])


def build_graph(model, max_pairs: int = 1):
    """Use MessagesState; return only the new AI delta to its reducer."""
    # Validate even when no graph invocation has happened yet.
    select_prompt([HumanMessage(content="validation")], max_pairs)

    def respond(state: MessagesState, config: RunnableConfig) -> dict:
        prompt = select_prompt(state["messages"], max_pairs)
        response = model.invoke(prompt, config=config)
        if not isinstance(response, AIMessage) or response.tool_calls:
            raise TypeError("This text-only lesson requires an AIMessage, no tools.")
        if not message_text(response).strip():
            raise ValueError("The model returned no visible text.")
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("respond", respond)
    builder.add_edge(START, "respond")
    builder.add_edge("respond", END)
    return builder.compile()  # No checkpoint: caller must carry the full history.


def format_transcript(history: list[BaseMessage]) -> str:
    """Preserve raw human text while labeling both roles in a readable log."""
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


def run_turn(graph, history: list[BaseMessage], text: str) -> list[BaseMessage]:
    """A new invocation has no saved state, so supply the caller's history."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Enter nonblank text.")
    result = graph.invoke(
        {"messages": [*history, HumanMessage(content=text)]},
        config=execution_config(),
    )
    return result["messages"]


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Four real calls: three carried turns and a separate fresh-history turn."""
    model = get_model(live=live, max_tokens=192)
    graph = build_graph(model, max_pairs=1)
    inputs = [
        "Hi, my name is Mira. Please acknowledge briefly.",
        "gud morning!\nWhat name did I give you?",
        "Reply with one short greeting.",
    ]
    history: list[BaseMessage] = []
    prompt_counts = []
    state_counts = []
    for text in inputs:
        pending = [*history, HumanMessage(content=text)]
        prompt_counts.append(len(select_prompt(pending, max_pairs=1)))
        history = run_turn(graph, history, text)
        state_counts.append(len(history))
    assert prompt_counts == [1, 3, 3]
    assert state_counts == [2, 4, 6]
    assert [message.type for message in history] == ["human", "ai"] * 3
    assert [message.content for message in history[::2]] == inputs
    assert "mira" in message_text(history[3]).casefold(), "Inspect live recall."
    third_prompt = select_prompt(history[:-1], max_pairs=1)
    assert third_prompt[0].id == history[2].id
    assert history[0].id not in [message.id for message in third_prompt]

    fresh = run_turn(
        graph, [],
        "What name did I give you? If absent here, say you don't know.",
    )
    assert len(fresh) == 2
    directory = output_directory(workdir, "L08")
    transcript = format_transcript(history)
    path = safe_write_text(directory, "bounded-conversation.txt", transcript)
    assert path.read_text(encoding="utf-8") == transcript
    assert f"Human:\n{inputs[1]}\n" in transcript
    return {
        "max_pairs": 1,
        "prompt_message_counts": prompt_counts,
        "full_history_counts": state_counts,
        "recall_answer": message_text(history[3]),
        "third_answer": message_text(history[-1]),
        "oldest_human_excluded_from_third_prompt": True,
        "full_transcript_messages": len(history),
        "raw_input_preserved": True,
        "fresh_history_messages": len(fresh),
        "fresh_answer": message_text(fresh[-1]),
        "fresh_history_is_reset_simulation": True,
        "log_path": str(path),
        "automatic_log_reload": False,
        "model_calls": 4,
    }


if __name__ == "__main__":
    run_cli("L08", run_demo)
