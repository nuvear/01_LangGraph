"""U1: durable thread memory, not a global conversation list.

Run with --live for four real Anthropic requests. Tests inject named doubles.
SQLite is imported lazily so a missing optional package has a clear diagnosis.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
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

INSTRUCTION = (
    "You are a synthetic classroom project notebook. Use only this conversation "
    "when recalling its project code. If no project code was supplied in this "
    "conversation, reply UNKNOWN and do not guess. When recalling a supplied "
    "code, include its exact spelling. Keep answers to one short sentence."
)


def sqlite_saver():
    """Return the real optional backend; never substitute an in-memory saver."""
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError as error:
        raise RuntimeError(
            "U1 requires langgraph-checkpoint-sqlite in the course environment."
        ) from error
    return SqliteSaver


def build_graph(model: Any, checkpointer: Any):
    """Inject a ChatAnthropic-compatible model for live or explicit offline use."""
    def reply(state: MessagesState, config: RunnableConfig) -> dict:
        response = model.invoke(
            [SystemMessage(content=INSTRUCTION), *state["messages"]],
            config=config,
        )
        if not isinstance(response, AIMessage):
            raise TypeError("The chat model must return an AIMessage.")
        # MessagesState applies add_messages; return ONLY the new response.
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("reply", reply)
    builder.add_edge(START, "reply")
    builder.add_edge("reply", END)
    return builder.compile(checkpointer=checkpointer)


def send_turn(graph: Any, thread_id: str, text: str) -> dict:
    """Send one new human message; the saver supplies the prior thread state."""
    if not isinstance(thread_id, str) or not thread_id.strip():
        raise ValueError("thread_id must be a nonblank string.")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a nonblank string.")
    return graph.invoke(
        {"messages": [HumanMessage(content=text)]},
        config=execution_config(thread_id),
    )


def inspect_checkpoint(database: Path, thread_id: str) -> dict:
    """Read a saved checkpoint without invoking any model or loading settings."""
    database = Path(database).resolve()
    if not database.is_file():
        raise FileNotFoundError(database)
    with sqlite_saver().from_conn_string(str(database)) as saver:
        saved = saver.get_tuple(execution_config(thread_id))
        if saved is None:
            return {"exists": False, "message_count": 0, "human_texts": []}
        messages = saved.checkpoint["channel_values"].get("messages", [])
        return {
            "exists": True,
            "message_count": len(messages),
            "human_texts": [
                message_text(item) for item in messages
                if isinstance(item, HumanMessage)
            ],
        }


def fresh_process_view(database: Path, thread_id: str) -> dict:
    """Start a fresh interpreter: no inherited model, graph, or Python history."""
    program = (
        "import json, sys; from pathlib import Path; "
        "from course_lessons.u1 import inspect_checkpoint; "
        "print(json.dumps(inspect_checkpoint(Path(sys.argv[1]), sys.argv[2])))"
    )
    completed = subprocess.run(
        [sys.executable, "-c", program, str(Path(database).resolve()), thread_id],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return json.loads(completed.stdout)


def run_checkpoint_lab(model: Any, directory: Path) -> dict:
    """Four model calls, two isolated threads, and actual disk recovery checks."""
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    database = directory / f"u1-demo-{uuid4().hex}.sqlite3"
    primary = "project-a"
    other = "project-b"
    introduction = "My project code is ORCHID-42. Remember it."
    question = "What is my project code?"

    with sqlite_saver().from_conn_string(str(database)) as saver:
        graph = build_graph(model, saver)
        first = send_turn(graph, primary, introduction)
        second = send_turn(graph, primary, question)
        isolated = send_turn(graph, other, question)
        assert len(first["messages"]) == 2
        assert len(second["messages"]) == 4
        assert len(isolated["messages"]) == 2
        assert "ORCHID-42" in message_text(second["messages"][-1])
        isolated_reply = message_text(isolated["messages"][-1])
        assert "UNKNOWN" in isolated_reply.upper()
        assert "ORCHID-42" not in isolated_reply
        assert all(
            "ORCHID-42" not in message_text(item)
            for item in isolated["messages"]
        )
        snapshot = graph.get_state(execution_config(primary))
        assert snapshot.next == ()
        assert len(snapshot.values["messages"]) == 4
        checkpoint_id = snapshot.config["configurable"]["checkpoint_id"]
    # The first SQLite connection is CLOSED before any recovery assertion.
    assert database.is_file() and database.stat().st_size > 0
    restarted = fresh_process_view(database, primary)
    assert restarted == {
        "exists": True,
        "message_count": 4,
        "human_texts": [introduction, question],
    }

    with sqlite_saver().from_conn_string(str(database)) as reopened:
        # A new compiled graph and a new saver load the same thread from disk.
        restored_graph = build_graph(model, reopened)
        restored = restored_graph.get_state(execution_config(primary))
        assert restored.next == ()
        assert len(restored.values["messages"]) == 4
        assert restored.config["configurable"]["checkpoint_id"] == checkpoint_id
        final = send_turn(restored_graph, primary, question)
        assert len(final["messages"]) == 6
        assert "ORCHID-42" in message_text(final["messages"][-1])
        untouched = restored_graph.get_state(execution_config(other))
        assert len(untouched.values["messages"]) == 2

    return {
        "database": str(database),
        "same_thread_recall": True,
        "separate_thread_isolation": True,
        "closed_and_reopened": True,
        "fresh_process_checkpoint_read": True,
        "primary_message_count": 6,
        "other_message_count": 2,
        "model_calls": 4,
        "recovered_answer": message_text(final["messages"][-1]),
    }


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Only --live constructs the real Anthropic model; tests inject their own."""
    model = get_model(live=live, max_tokens=128)
    return run_checkpoint_lab(model, output_directory(workdir, "U1"))


if __name__ == "__main__":
    run_cli("U1", run_demo)
