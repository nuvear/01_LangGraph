"""L08 starter: implement three TODOs; this is not a fake successful exercise."""
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
    """TODO 1: validate alternating text-chat input and return a new window list.

    Accept a nonnegative integer max_pairs (not bool). Input must contain zero
    or more HumanMessage/AIMessage pairs, followed by one HumanMessage. Reject
    tool calls. Retain the newest max_pairs complete pairs plus that human.
    Empty/even/nonalternating input and invalid limits must raise ValueError.
    Do not mutate history; max_pairs=0 keeps only the pending human message.
    """
    raise NotImplementedError("TODO 1: select_prompt")


def build_graph(model, max_pairs: int = 1):
    """TODO 2: compile START -> respond -> END using MessagesState.

    Validate max_pairs at build time. In respond(state, config), send only
    select_prompt(state['messages'], max_pairs) to model.invoke(..., config=config).
    Require a nonempty visible-text AIMessage without tools. Return ONLY the new
    AI message as {'messages': [response]}; do not append/mutate full state.
    Use no checkpointer. This function must compile with model=None for the
    readiness check, because model.invoke belongs inside respond, not here.
    """
    raise NotImplementedError("TODO 2: build_graph")


def format_transcript(history: list[BaseMessage]) -> str:
    """TODO 3: format every full-history message without rewriting its content.

    Each entry is '<role>:\n<text>\n', with Human or AI as the role, joined by
    one additional newline. Use message_text; reject other roles with TypeError.
    Empty history produces ''. Keep spelling, case, spaces and newlines intact.
    Do not open files here: the provided runner handles safe writing.
    """
    raise NotImplementedError("TODO 3: format_transcript")


def run_turn(graph, history: list[BaseMessage], text: str) -> list[BaseMessage]:
    """Provided orchestration: carry state because this graph has no checkpoint."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Enter nonblank text.")
    result = graph.invoke(
        {"messages": [*history, HumanMessage(content=text)]},
        config=execution_config(),
    )
    return result["messages"]


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Provided acceptance scenario; do not weaken assertions to pass."""
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


def main() -> None:
    """No model construction or credentials needed until all TODOs exist."""
    try:
        select_prompt([HumanMessage(content="readiness check")])
        build_graph(None)
        format_transcript([])
    except NotImplementedError as error:
        print(f"STARTER_NOT_COMPLETED: {error}. Complete all three TODOs.")
        return
    print("TODO functions are present; live acceptance checks will now run.")
    run_cli("L08", run_demo)


if __name__ == "__main__":
    main()
