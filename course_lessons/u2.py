"""U2 baseline: session-scoped drafts and approval BEFORE a file side effect."""
from __future__ import annotations

from pathlib import Path
from typing import Annotated, TypedDict
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, ToolRuntime
from langgraph.types import Command, interrupt

from course_support.runtime import (
    execution_config,
    get_model,
    message_text,
    output_directory,
    run_cli,
    safe_write_text,
)


class DraftState(TypedDict):
    session: str
    brief: str
    filename: str
    draft: str
    messages: Annotated[list, add_messages]
    status: str
    saved_path: str
    error: str


@tool
def update_draft(content: str, runtime: ToolRuntime) -> Command:
    """Replace only this thread's draft; do not write any files."""
    if not content.strip():
        raise ValueError("A draft must contain text.")
    return Command(update={
        "draft": content,
        "status": "awaiting_approval",
        "saved_path": "",
        "error": "",
        "messages": [ToolMessage(
            content=f"Draft updated for {runtime.state['session']}.",
            tool_call_id=runtime.tool_call_id,
        )],
    })


def initial_state(session: str, brief: str, filename: str) -> DraftState:
    """Initialize every field so an earlier save cannot leak into a new request."""
    return {
        "session": session, "brief": brief, "filename": filename, "draft": "",
        "messages": [], "status": "new", "saved_path": "", "error": "",
    }


def approval_update(decision: object) -> dict:
    """Only the boolean True authorizes a write; strings are not approval."""
    approved = decision is True
    return {
        "status": "approved" if approved else "rejected",
        "saved_path": "", "error": "",
    }


def save_draft(state: DraftState, directory: Path) -> dict:
    """Report success only after exclusive creation of the requested file."""
    if state["status"] != "approved":
        raise ValueError("Saving requires explicit approval.")
    try:
        path = safe_write_text(directory, state["filename"], state["draft"])
    except (OSError, ValueError) as exc:
        return {
            "status": "save_failed", "saved_path": "",
            "error": f"{type(exc).__name__}: {exc}",
        }
    return {"status": "saved", "saved_path": str(path), "error": ""}


def build_graph(model, directory: Path, *, checkpointer=None):
    """Inject a real model at the CLI, or an explicitly named test double in tests."""
    def generate(state: DraftState, config) -> dict:
        response = model.invoke([
            SystemMessage(content=(
                "Write a short fictional workshop notice from the supplied brief. "
                "Return only the notice text. Do not claim to save or send anything."
            )),
            HumanMessage(content=state["brief"]),
        ], config=config)
        text = message_text(response)
        if not text.strip():
            raise ValueError("The model returned an empty draft.")
        # The coordinator, NOT the model, selects this fixed tool handoff.
        # A valid call/result pair lets ToolNode demonstrate runtime injection.
        call = AIMessage(content="", tool_calls=[{
            "name": "update_draft", "args": {"content": text},
            "id": f"draft-{uuid4().hex}", "type": "tool_call",
        }])
        return {"messages": [call]}

    def review(state: DraftState) -> dict:
        # No writes/model calls before this interrupt: this node replays on resume.
        decision = interrupt({
            "action": "approve_save", "session": state["session"],
            "filename": state["filename"], "draft": state["draft"],
        })
        return approval_update(decision)

    def save(state: DraftState) -> dict:
        return save_draft(state, directory)

    builder = StateGraph(DraftState)
    builder.add_node("generate", generate)
    builder.add_node("update", ToolNode([update_draft], handle_tool_errors=False))
    builder.add_node("review", review)
    builder.add_node("save", save)
    builder.add_edge(START, "generate")
    builder.add_edge("generate", "update")
    builder.add_edge("update", "review")
    builder.add_conditional_edges(
        "review", lambda state: state["status"],
        {"approved": "save", "rejected": END},
    )
    builder.add_edge("save", END)
    saver = checkpointer if checkpointer is not None else InMemorySaver()
    return builder.compile(checkpointer=saver)


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    model = get_model(live=live)
    directory = output_directory(workdir, "u2")
    graph = build_graph(model, directory)
    configs = {name: execution_config(f"u2-{name}-{uuid4().hex}")
               for name in ("cedar", "orchid")}
    cedar = graph.invoke(initial_state(
        "cedar", "A fictional Cedar Python workshop on Tuesday at 10:00.",
        "cedar.txt",
    ), configs["cedar"])
    orchid = graph.invoke(initial_state(
        "orchid", "A fictional Orchid gardening workshop on Friday at 14:00.",
        "orchid.txt",
    ), configs["orchid"])
    assert cedar["__interrupt__"] and orchid["__interrupt__"]
    assert not (directory / "cedar.txt").exists()
    assert not (directory / "orchid.txt").exists()
    assert cedar["draft"].strip() and orchid["draft"].strip()
    assert graph.get_state(configs["cedar"]).values["draft"] == cedar["draft"]
    saved = graph.invoke(Command(resume=True), configs["cedar"])
    assert saved["status"] == "saved"
    assert Path(saved["saved_path"]).read_text(encoding="utf-8") == cedar["draft"]
    other = graph.get_state(configs["orchid"])
    assert other.values["draft"] == orchid["draft"] and other.next == ("review",)
    rejected = graph.invoke(Command(resume=False), configs["orchid"])
    assert rejected["status"] == "rejected"
    assert not (directory / "orchid.txt").exists()
    approved = {**saved, "status": "approved"}
    collision = save_draft(approved, directory)
    assert collision["status"] == "save_failed" and not collision["saved_path"]
    traversal = save_draft({**approved, "filename": "../escape.txt"}, directory)
    assert traversal["status"] == "save_failed" and not traversal["saved_path"]
    assert Path(saved["saved_path"]).read_text(encoding="utf-8") == cedar["draft"]
    return {
        "paused_sessions": 2, "isolation_checked": True,
        "approved_status": saved["status"], "rejected_status": rejected["status"],
        "overwrite_status": collision["status"],
        "traversal_status": traversal["status"], "saved_path": saved["saved_path"],
    }


if __name__ == "__main__":
    run_cli("U2", run_demo)
