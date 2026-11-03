"""U2 workbook extension: approve exact content, then allow ONE filename repair."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import TypedDict
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from course_support.runtime import (
    execution_config,
    get_model,
    message_text,
    output_directory,
    run_cli,
    safe_write_text,
)


class ReviewState(TypedDict):
    session: str
    brief: str
    filename: str
    draft: str
    draft_hash: str
    approved_hash: str
    status: str
    saved_path: str
    error: str
    repairs: int


def draft_digest(text: str) -> str:
    """Hash the exact UTF-8 bytes, including whitespace; do not normalize."""
    return sha256(text.encode("utf-8")).hexdigest()


def initial_state(session: str, brief: str, filename: str) -> ReviewState:
    return {
        "session": session, "brief": brief, "filename": filename, "draft": "",
        "draft_hash": "", "approved_hash": "", "status": "new",
        "saved_path": "", "error": "", "repairs": 0,
    }


def approval_update(state: ReviewState, decision: object, *, repair=False) -> dict:
    """Validate a human response; a repair may change the filename, never content."""
    valid = (
        isinstance(decision, dict)
        and decision.get("approve") is True
        and decision.get("draft_hash") == draft_digest(state["draft"])
        and state["draft_hash"] == draft_digest(state["draft"])
    )
    if repair:
        valid = valid and isinstance(decision.get("filename"), str)
        valid = valid and bool(decision.get("filename", "").strip())
    update = {
        "status": "approved" if valid else "rejected",
        "approved_hash": state["draft_hash"] if valid else "",
        "saved_path": "", "error": "",
    }
    if repair:
        update["repairs"] = state["repairs"] + 1
        if valid:
            update["filename"] = decision["filename"]
    return update


def attempt_save(state: ReviewState, directory: Path) -> dict:
    """Refuse unapproved/stale content; filesystem errors must never look saved."""
    if (state["status"] != "approved"
            or state["approved_hash"] != draft_digest(state["draft"])):
        raise ValueError("The exact current draft must be approved before saving.")
    try:
        path = safe_write_text(directory, state["filename"], state["draft"])
    except (OSError, ValueError) as exc:
        return {
            "status": "save_failed", "saved_path": "",
            "error": f"{type(exc).__name__}: {exc}",
        }
    return {"status": "saved", "saved_path": str(path), "error": ""}


def build_graph(model, directory: Path, *, checkpointer=None):
    """Fixed, acyclic workflow: generate once, review, save, optional repair/save."""
    def generate(state: ReviewState, config) -> dict:
        response = model.invoke([
            SystemMessage(content=(
                "Write a short fictional workshop notice from the brief. "
                "Return only text. Never claim to save or send anything."
            )),
            HumanMessage(content=state["brief"]),
        ], config=config)
        text = message_text(response)
        if not text.strip():
            raise ValueError("The model returned an empty draft.")
        return {
            "draft": text, "draft_hash": draft_digest(text),
            "approved_hash": "", "status": "awaiting_approval",
            "saved_path": "", "error": "",
        }

    def review(state: ReviewState) -> dict:
        decision = interrupt({
            "action": "approve_exact_draft", "session": state["session"],
            "filename": state["filename"], "draft": state["draft"],
            "draft_hash": state["draft_hash"],
        })
        return approval_update(state, decision)

    def repair(state: ReviewState) -> dict:
        decision = interrupt({
            "action": "repair_filename_once", "session": state["session"],
            "draft": state["draft"], "draft_hash": state["draft_hash"],
            "failed_filename": state["filename"], "error": state["error"],
            "repairs_remaining": 1,
        })
        return approval_update(state, decision, repair=True)

    def save(state: ReviewState) -> dict:
        return attempt_save(state, directory)

    builder = StateGraph(ReviewState)
    for name, node in (
        ("generate", generate), ("review", review), ("save", save),
        ("repair", repair), ("retry_save", save),
    ):
        builder.add_node(name, node)
    builder.add_edge(START, "generate")
    builder.add_edge("generate", "review")
    builder.add_conditional_edges(
        "review", lambda state: state["status"],
        {"approved": "save", "rejected": END},
    )
    builder.add_conditional_edges(
        "save", lambda state: state["status"],
        {"saved": END, "save_failed": "repair"},
    )
    builder.add_conditional_edges(
        "repair", lambda state: state["status"],
        {"approved": "retry_save", "rejected": END},
    )
    builder.add_edge("retry_save", END)
    saver = checkpointer if checkpointer is not None else InMemorySaver()
    return builder.compile(checkpointer=saver)


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    model = get_model(live=live)
    directory = output_directory(workdir, "u2")
    graph = build_graph(model, directory)
    configs = {name: execution_config(f"u2-solution-{name}-{uuid4().hex}")
               for name in ("cedar", "orchid")}
    cedar = graph.invoke(initial_state(
        "cedar", "A fictional Cedar robotics workshop on Tuesday at 10:00.",
        "../unsafe.txt",
    ), configs["cedar"])
    orchid = graph.invoke(initial_state(
        "orchid", "A fictional Orchid painting workshop on Friday at 14:00.",
        "orchid-solution.txt",
    ), configs["orchid"])
    assert cedar["__interrupt__"] and orchid["__interrupt__"]
    assert not (directory / "recovered.txt").exists()
    assert not (directory / "orchid-solution.txt").exists()
    failed = graph.invoke(Command(resume={
        "approve": True, "draft_hash": cedar["draft_hash"],
    }), configs["cedar"])
    assert failed["status"] == "save_failed" and not failed["saved_path"]
    assert failed["__interrupt__"][0].value["action"] == "repair_filename_once"
    saved = graph.invoke(Command(resume={
        "approve": True, "draft_hash": cedar["draft_hash"],
        "filename": "recovered.txt",
    }), configs["cedar"])
    assert saved["status"] == "saved" and saved["repairs"] == 1
    assert saved["draft"] == cedar["draft"]
    assert Path(saved["saved_path"]).read_text(encoding="utf-8") == cedar["draft"]
    other = graph.get_state(configs["orchid"])
    assert other.values["draft"] == orchid["draft"] and other.next == ("review",)
    rejected = graph.invoke(Command(resume={"approve": False}), configs["orchid"])
    assert rejected["status"] == "rejected"
    assert not (directory / "orchid-solution.txt").exists()
    collision = attempt_save({**saved, "status": "approved"}, directory)
    assert collision["status"] == "save_failed" and not collision["saved_path"]
    stale = approval_update(cedar, {"approve": True, "draft_hash": "stale"})
    assert stale["status"] == "rejected"
    assert Path(saved["saved_path"]).read_text(encoding="utf-8") == cedar["draft"]
    return {
        "paused_sessions": 2, "isolation_checked": True,
        "first_save_status": failed["status"], "final_status": saved["status"],
        "repairs": saved["repairs"], "unchanged_draft": True,
        "stale_approval_status": stale["status"],
        "overwrite_status": collision["status"], "saved_path": saved["saved_path"],
    }


if __name__ == "__main__":
    run_cli("U2", run_demo)
