"""U1 exercise solution: three isolated travel notebooks in one SQLite file.

This is independent of course_lessons.u1 and requires five calls with --live.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, MessagesState, StateGraph

from course_support.runtime import (
    execution_config,
    get_model,
    message_text,
    output_directory,
    run_cli,
)

NOTEBOOK_RULE = (
    "You are a synthetic classroom travel notebook. Remember destinations only "
    "from this conversation. When asked for the destination, include its exact "
    "spelling if supplied; otherwise reply UNKNOWN without inventing a city. "
    "Use one short sentence."
)


def build_notebook(model: Any, checkpointer: Any):
    """Build one response node; MessagesState merges only the returned delta."""
    def answer(state: MessagesState, config: RunnableConfig) -> dict:
        reply = model.invoke(
            [SystemMessage(content=NOTEBOOK_RULE), *state["messages"]],
            config=config,
        )
        if not isinstance(reply, AIMessage):
            raise TypeError("The chat model must return an AIMessage.")
        return {"messages": [reply]}

    builder = StateGraph(MessagesState)
    builder.add_node("answer", answer)
    builder.add_edge(START, "answer")
    builder.add_edge("answer", END)
    return builder.compile(checkpointer=checkpointer)


def ask(graph: Any, thread_id: str, text: str) -> dict:
    """Reject blank inputs and invoke with only the new human message."""
    if not isinstance(thread_id, str) or not thread_id.strip():
        raise ValueError("thread_id must be a nonblank string.")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a nonblank string.")
    return graph.invoke(
        {"messages": [HumanMessage(content=text)]},
        config=execution_config(thread_id),
    )


def run_lab(model: Any, database: Path) -> dict:
    """Seed two threads, close/reopen the file, recall, and check a fresh third."""
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError as error:
        raise RuntimeError(
            "U1 requires langgraph-checkpoint-sqlite in the course environment."
        ) from error
    database = Path(database).resolve()
    if database.exists():
        raise FileExistsError("Choose a new database for a clean exercise run.")
    database.parent.mkdir(parents=True, exist_ok=True)
    seeds = {
        "trip-a": "My destination is Kyoto. Remember it.",
        "trip-b": "My destination is Oslo. Remember it.",
    }
    saved_ids = {}
    with SqliteSaver.from_conn_string(str(database)) as saver:
        graph = build_notebook(model, saver)
        for thread_id, text in seeds.items():
            result = ask(graph, thread_id, text)
            assert len(result["messages"]) == 2
            snapshot = graph.get_state(execution_config(thread_id))
            assert snapshot.next == ()
            saved_ids[thread_id] = snapshot.config["configurable"]["checkpoint_id"]

    # Do not use the old graph here: its SQLite connection is closed.
    assert database.is_file() and database.stat().st_size > 0
    answers = {}
    question = "What is my destination?"
    with SqliteSaver.from_conn_string(str(database)) as reopened:
        graph = build_notebook(model, reopened)
        # Complete restoration inspection for BOTH threads before any model call.
        for thread_id in seeds:
            restored = graph.get_state(execution_config(thread_id))
            assert len(restored.values["messages"]) == 2
            assert restored.next == ()
            assert restored.config["configurable"]["checkpoint_id"] == (
                saved_ids[thread_id]
            )
        for thread_id, expected, forbidden in (
            ("trip-a", "Kyoto", "Oslo"),
            ("trip-b", "Oslo", "Kyoto"),
        ):
            result = ask(graph, thread_id, question)
            assert len(result["messages"]) == 4
            human_texts = [
                message_text(item) for item in result["messages"]
                if isinstance(item, HumanMessage)
            ]
            assert human_texts == [seeds[thread_id], question]
            answer = message_text(result["messages"][-1])
            assert expected.casefold() in answer.casefold()
            assert forbidden.casefold() not in answer.casefold()
            answers[thread_id] = answer

        assert not graph.get_state(execution_config("trip-c")).values
        fresh = ask(graph, "trip-c", question)
        assert len(fresh["messages"]) == 2
        assert message_text(fresh["messages"][0]) == question
        unknown = message_text(fresh["messages"][-1])
        assert "UNKNOWN" in unknown.upper()
        assert "kyoto" not in unknown.casefold()
        assert "oslo" not in unknown.casefold()
        answers["trip-c"] = unknown
        counts = {
            thread_id: len(
                graph.get_state(execution_config(thread_id)).values["messages"]
            ) for thread_id in ("trip-a", "trip-b", "trip-c")
        }
        assert counts == {"trip-a": 4, "trip-b": 4, "trip-c": 2}

    return {
        "database": str(database),
        "closed_and_reopened": True,
        "recovered_checkpoint_ids_match": True,
        "thread_isolation": True,
        "message_counts": counts,
        "answers": answers,
        "model_calls": 5,
    }


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Run the complete independent exercise using real Anthropic with --live."""
    model = get_model(live=live, max_tokens=128)
    directory = output_directory(workdir, "U1")
    return run_lab(model, directory / f"u1-solution-{uuid4().hex}.sqlite3")


if __name__ == "__main__":
    run_cli("U1", run_demo)
