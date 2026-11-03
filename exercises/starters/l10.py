"""L10 starter: implement exactly the three TODO functions below.

Run with python -m exercises.starters.l10. Until implemented, this prints
STARTER_NOT_COMPLETED and exits successfully, without making a model request.
Once completed, use --live to run the supplied workshop acceptance scenario.
Do not import the reference solution or the demonstration to fill the TODOs.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, TypedDict

from langchain_core.messages import (
    AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage,
)
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from course_support.runtime import (
    execution_config, get_model, message_text, output_directory, run_cli,
    safe_write_text,
)

MAX_MODEL_CALLS = 4
SYSTEM = """You are a collaborative workshop-email drafter using synthetic data.
When recipient or purpose is missing, ask for clarification WITHOUT tools.
For complete drafting or revision requests, call update with the ENTIRE email,
not a patch. Keep it under 140 words. Then show the current draft and wait for
human feedback. Preserve requested literal names, dates, and time strings.
Use no more than one tool per response. Only call save when the latest human
feedback requests it, using the exact filename. A save must not revise content.
On any tool ERROR, explain the failure and wait for new human feedback; do not
retry or select a new filename yourself. A successful save ends the workflow.
"""


class DraftState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    model_calls: int


@dataclass
class DraftSession:
    content: str = ""
    revision_count: int = 0
    saved_path: Path | None = None
    save_requested: bool = False


def make_tools(session: DraftSession, directory: Path) -> list:
    """TODO 1: return @tool update(content: str) and save(filename: str).

    update must reject blank content and finished sessions, replace the whole
    buffer, and increment revision_count once per successful update.
    save must require save_requested, reject empty/finished sessions, and call
    safe_write_text. Set saved_path ONLY after the writer returns successfully.
    Let validation and filesystem exceptions reach the tools node.
    """
    raise NotImplementedError("TODO 1: implement update and save tools")


def after_tools(state: DraftState, session: DraftSession) -> str:
    """TODO 2: return 'end' on successful saved_path or exhausted call budget.

    Otherwise return 'agent'. Never search text for the word 'saved'. An error
    result is not evidence that a file was written.
    """
    raise NotImplementedError("TODO 2: implement the tools router")


def build_graph(model, directory: Path, session: DraftSession):
    """TODO 3: compile a two-node agent/tools graph.

    Bind make_tools with parallel_tool_calls=False. agent invokes the bound
    model with SYSTEM plus state messages, forwards RunnableConfig, and returns
    ONLY the new AIMessage plus incremented model_calls. Reject non-AIMessages.
    The tools node must execute only a single known call, pass config to tool
    invocation, and create a ToolMessage with the matching ID and name. Convert
    ValueError/OSError/TypeError to status='error'; never claim a failed save.
    Reject a multi-call batch WITHOUT executing any member, but answer every ID.
    START -> agent; agent -> tools only when tool_calls exist, otherwise END.
    tools -> agent/END through after_tools. Do not add unconditional outgoing
    edges alongside conditional ones. Compile with no checkpointer for L10.
    """
    raise NotImplementedError("TODO 3: implement and compile the graph")


def take_turn(app, session: DraftSession, history: list, prompt: str, *,
              save_requested: bool = False) -> dict:
    """Supplied host driver: retain history explicitly between graph runs."""
    if session.saved_path is not None:
        raise ValueError("The workflow ended after saving; start a new session.")
    if not prompt.strip():
        raise ValueError("Human feedback must not be empty.")
    session.save_requested = save_requested
    try:
        result = app.invoke(
            {"messages": [*history, HumanMessage(content=prompt)],
             "model_calls": 0},
            config=execution_config(),
        )
    finally:
        session.save_requested = False
    if (result["model_calls"] >= MAX_MODEL_CALLS
            and isinstance(result["messages"][-1], ToolMessage)
            and session.saved_path is None):
        raise RuntimeError("Turn budget exhausted; inspect the last tool error.")
    return result


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    # Unimplemented tools are detected BEFORE loading model configuration.
    make_tools(DraftSession(), Path("."))
    after_tools({"messages": [], "model_calls": 0}, DraftSession())
    model = get_model(live=live, max_tokens=1100)
    directory = output_directory(workdir, "L10")
    session = DraftSession()
    app = build_graph(model, directory, session)
    first = take_turn(
        app, session, [],
        "Draft an email to Elena postponing our training workshop. Propose "
        "17 November at 09:00 Singapore time and sign Arun. Call update "
        "with the whole draft. Do not save yet.",
    )
    assert session.content.strip() and session.revision_count >= 1
    initial = session.content
    for fact in ("Elena", "Arun", "17 November at 09:00 Singapore time"):
        assert fact in initial, f"Missing initial fact: {fact}"
    revised = take_turn(
        app, session, first["messages"],
        "Change the proposed schedule to the literal phrase '18 November at "
        "14:30 Singapore time'. Keep Elena and Arun, remove the old schedule, "
        "and put a blank line before the closing. Call update with the ENTIRE "
        "revised email. Do not save.",
    )
    final_draft = session.content
    assert final_draft != initial and session.revision_count >= 2
    for fact in ("Elena", "Arun", "18 November at 14:30 Singapore time"):
        assert fact in final_draft, f"Missing requested fact: {fact}"
    assert "17 November" not in final_draft and "09:00" not in final_draft
    assert "\n\n" in final_draft and session.saved_path is None
    revisions_before_save = session.revision_count
    original = "Existing classroom file: preserve me.\n"
    occupied = safe_write_text(directory, "workshop_taken.txt", original)
    failed = take_turn(
        app, session, revised["messages"],
        "Save the unchanged draft as workshop_taken.txt. If this fails, "
        "explain the error and wait; do not retry or invent a new filename.",
        save_requested=True,
    )
    new_messages = failed["messages"][len(revised["messages"]):]
    assert any(isinstance(item, ToolMessage) and item.status == "error"
               for item in new_messages)
    assert session.saved_path is None and session.content == final_draft
    assert session.revision_count == revisions_before_save
    assert occupied.read_text(encoding="utf-8") == original
    saved = take_turn(
        app, session, failed["messages"],
        "I approve recovery. Save the unchanged draft as workshop_notice.txt.",
        save_requested=True,
    )
    assert session.saved_path == directory / "workshop_notice.txt"
    assert session.saved_path.read_text(encoding="utf-8") == final_draft
    assert session.revision_count == revisions_before_save
    assert isinstance(saved["messages"][-1], ToolMessage)
    assert saved["messages"][-1].name == "save"
    assert saved["messages"][-1].status == "success"
    unclear = DraftSession()
    clarification = take_turn(
        build_graph(model, directory, unclear), unclear, [], "write an email",
    )
    assert unclear.content == "" and unclear.revision_count == 0
    assert not any(isinstance(item, ToolMessage)
                   for item in clarification["messages"])
    question = message_text(clarification["messages"][-1])
    assert question.strip() and unclear.saved_path is None
    return {
        "saved_path": str(session.saved_path),
        "revision_count": session.revision_count,
        "collision_preserved_existing_file": True,
        "failed_save_did_not_finish": True,
        "recovery_saved_latest_draft": True,
        "ended_on_successful_save": True,
        "clarification_without_tools": True,
        "clarifying_response": question,
        "final_document": final_draft,
    }


def main() -> None:
    # A construction check: identify remaining placeholder raises, not a test
    # of correctness. Removing them does not bypass the scenario's assertions.
    pending = [function.__name__ for function in
               (make_tools, after_tools, build_graph)
               if "NotImplementedError" in function.__code__.co_names]
    if pending:
        print("STARTER_NOT_COMPLETED: implement " + ", ".join(pending))
        return
    try:
        run_cli("L10", run_demo)
    except NotImplementedError as error:
        print(f"STARTER_NOT_COMPLETED: {error}")


if __name__ == "__main__":
    main()
