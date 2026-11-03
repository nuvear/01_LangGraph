"""U2 starter: finish the three TODO functions; no solution imports."""
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
    return sha256(text.encode("utf-8")).hexdigest()


def initial_state(session: str, brief: str, filename: str) -> ReviewState:
    return {
        "session": session, "brief": brief, "filename": filename, "draft": "",
        "draft_hash": "", "approved_hash": "", "status": "new",
        "saved_path": "", "error": "", "repairs": 0,
    }


def approval_update(state: ReviewState, decision: object, *, repair=False) -> dict:
    """TODO 1: approve only exact True + current hash; validate repair filename.

    Return status, approved_hash, saved_path='', error=''. Reject malformed,
    stale, or negative decisions. On repair increment repairs by one and copy
    a nonblank string filename only when approved. Never edit draft content.
    """
    raise NotImplementedError("TODO 1: validate approval and optional repair")


def attempt_save(state: ReviewState, directory: Path) -> dict:
    """TODO 2: guard approved status/hash, then call safe_write_text.

    Raise ValueError for missing or stale approval. Return saved + actual path
    only after success. Catch OSError/ValueError from the writer and return
    save_failed, saved_path='', and a nonempty error. Never overwrite files.
    """
    raise NotImplementedError("TODO 2: implement honest, guarded file saving")


def make_nodes(model, directory: Path) -> dict:
    """Supplied node bodies keep the exercise focused on policy and topology."""
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

    return {
        "generate": generate, "review": review, "save": save,
        "repair": repair, "retry_save": save,
    }


def build_graph(model, directory: Path, *, checkpointer=None):
    """TODO 3: register make_nodes, wire bounded routes, compile with a saver.

    START -> generate -> review. Approved review -> save, rejection -> END.
    Saved -> END; first save_failed -> repair. Approved repair -> retry_save;
    rejection -> END. retry_save -> END even on failure. No back edges.
    Use the supplied checkpointer or a new InMemorySaver.
    """
    raise NotImplementedError("TODO 3: build the bounded approval/repair graph")


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    model = get_model(live=live)
    directory = output_directory(workdir, "u2")
    graph = build_graph(model, directory)
    configs = {name: execution_config(f"u2-starter-{name}-{uuid4().hex}")
               for name in ("cedar", "orchid")}
    cedar = graph.invoke(initial_state(
        "cedar", "A fictional Cedar robotics workshop on Tuesday at 10:00.",
        "../unsafe.txt",
    ), configs["cedar"])
    orchid = graph.invoke(initial_state(
        "orchid", "A fictional Orchid painting workshop on Friday at 14:00.",
        "orchid-starter.txt",
    ), configs["orchid"])
    assert cedar["__interrupt__"] and orchid["__interrupt__"]
    assert not (directory / "recovered.txt").exists()
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
    assert not (directory / "orchid-starter.txt").exists()
    return {"status": saved["status"], "repairs": saved["repairs"],
            "isolation_checked": True, "saved_path": saved["saved_path"]}


def main() -> None:
    # Probe TODOs with NO model invocation and NO filesystem write.
    state = initial_state("probe", "synthetic", "probe.txt")
    try:
        approval_update(state, {"approve": False})
        try:
            attempt_save(state, Path("."))
        except ValueError:
            pass  # Correct: unapproved state is forbidden.
        build_graph(None, Path("."))
    except NotImplementedError as exc:
        print(f"STARTER_NOT_COMPLETED: {exc}")
        print("Finish all three TODOs, then rerun with --live for real validation.")
        return
    run_cli("U2", run_demo)


if __name__ == "__main__":
    main()
