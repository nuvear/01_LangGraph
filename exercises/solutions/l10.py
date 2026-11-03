"""Independent L10 exercise solution: revise a workshop notice, recover a save.

This file does not import course_lessons.l10. The human drives turns from Python;
it is deliberately not a checkpointed interrupt/resume implementation.
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
    """Tools own only this single process-local session's document buffer."""
    @tool
    def update(content: str) -> str:
        """Replace the complete current workshop email with nonempty content."""
        if not content.strip():
            raise ValueError("The draft must not be empty.")
        if session.saved_path is not None:
            raise ValueError("This session has already finished saving.")
        session.content = content
        session.revision_count += 1
        return "UPDATED; current document:\n" + content

    @tool
    def save(filename: str) -> str:
        """Write the current draft to a NEW simple .txt file after human request."""
        if not session.save_requested:
            raise ValueError("The human has not requested saving this turn.")
        if session.saved_path is not None:
            raise ValueError("This session has already finished saving.")
        if not session.content.strip():
            raise ValueError("There is no draft to save.")
        written = safe_write_text(directory, filename, session.content)
        session.saved_path = written
        return "SAVED: " + written.name

    return [update, save]


def after_agent(state: DraftState) -> str:
    response = state["messages"][-1]
    if isinstance(response, AIMessage) and response.tool_calls:
        return "tools"
    return "end"


def after_tools(state: DraftState, session: DraftSession) -> str:
    """Use actual saved state, never a substring in an assistant's prose."""
    if session.saved_path is not None:
        return "end"
    if state["model_calls"] >= MAX_MODEL_CALLS:
        return "end"
    return "agent"


def build_graph(model, directory: Path, session: DraftSession):
    available = {item.name: item for item in make_tools(session, directory)}
    chat = model.bind_tools(list(available.values()), parallel_tool_calls=False)

    def agent(state: DraftState, config: RunnableConfig) -> dict:
        response = chat.invoke(
            [SystemMessage(content=SYSTEM), *state["messages"]], config=config,
        )
        if not isinstance(response, AIMessage):
            raise TypeError("The chat model must return an AIMessage.")
        return {
            "messages": [response], "model_calls": state["model_calls"] + 1,
        }

    def tools(state: DraftState, config: RunnableConfig) -> dict:
        calls = state["messages"][-1].tool_calls
        replies = []
        for call in calls:
            try:
                if len(calls) != 1:
                    raise ValueError("Request one tool at a time; no batch executed.")
                if call["name"] not in available:
                    raise ValueError("Unknown tool: " + call["name"])
                result = available[call["name"]].invoke(
                    call["args"], config=config,
                )
                status = "success"
            except (ValueError, OSError, TypeError) as error:
                result = f"ERROR: {type(error).__name__}: {error}"
                status = "error"
            replies.append(ToolMessage(
                content=result, tool_call_id=call["id"], name=call["name"],
                status=status,
            ))
        return {"messages": replies}

    graph = StateGraph(DraftState)
    graph.add_node("agent", agent)
    graph.add_node("tools", tools)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent", after_agent, {"tools": "tools", "end": END},
    )
    graph.add_conditional_edges(
        "tools", lambda state: after_tools(state, session),
        {"agent": "agent", "end": END},
    )
    return graph.compile()


def take_turn(app, session: DraftSession, history: list, prompt: str, *,
              save_requested: bool = False) -> dict:
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
    model = get_model(live=live, max_tokens=1100)
    directory = output_directory(workdir, "L10")
    session = DraftSession()
    app = build_graph(model, directory, session)
    drafted = take_turn(
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
        app, session, drafted["messages"],
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


if __name__ == "__main__":
    run_cli("L10", run_demo)
