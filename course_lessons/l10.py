"""L10: a bounded Drafter graph, with human feedback between invocations.

The buffer is deliberately process-local, not checkpointed state. U2 replaces
this teaching compromise with explicit state and durable approval/resume.
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
SYSTEM = """You are Drafter, collaborating on synthetic classroom emails.
If the recipient or purpose is missing, ask a short clarifying question and do
not call a tool. Never invent missing facts. For a complete drafting or revision
request, call update with the ENTIRE revised email, not a patch. Keep drafts
under 140 words. After an update, show the complete current draft for review and
wait for human feedback. Call at most one tool per response. Never save unless
the latest human feedback explicitly requests it. On a save request call save
with the exact requested .txt filename; do not update again unless requested.
A tool ERROR is a failure, not success: explain or correct it. A successful save
ends the workflow. Preserve literal names and time strings requested by the user.
"""


class DraftState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    model_calls: int


@dataclass
class DraftSession:
    """One buffer per graph; do not share it between users or concurrent turns."""

    content: str = ""
    revision_count: int = 0
    saved_path: Path | None = None
    save_requested: bool = False


def make_tools(session: DraftSession, directory: Path) -> list:
    """Bind two local functions to this buffer, not a module-global document."""
    @tool
    def update(content: str) -> str:
        """Replace the entire current email with nonempty revised content."""
        if not content.strip():
            raise ValueError("The draft must not be empty.")
        if session.saved_path is not None:
            raise ValueError("This session has already finished saving.")
        session.content = content
        session.revision_count += 1
        return "UPDATED; current document:\n" + session.content

    @tool
    def save(filename: str) -> str:
        """Save the current email as a NEW simple .txt file after human request."""
        if not session.save_requested:
            raise ValueError("The human has not requested saving this turn.")
        if session.saved_path is not None:
            raise ValueError("This session has already finished saving.")
        if not session.content.strip():
            raise ValueError("There is no draft to save.")
        # Assign success only AFTER the exclusive file write succeeds.
        path = safe_write_text(directory, filename, session.content)
        session.saved_path = path
        return "SAVED: " + path.name

    return [update, save]


def after_agent(state: DraftState) -> str:
    last = state["messages"][-1]
    return "tools" if isinstance(last, AIMessage) and last.tool_calls else "end"


def after_tools(state: DraftState, session: DraftSession) -> str:
    if session.saved_path is not None:
        return "end"
    return "end" if state["model_calls"] >= MAX_MODEL_CALLS else "agent"


def build_graph(model, directory: Path, session: DraftSession):
    """Accept an injected chat model; tests supply named offline doubles."""
    tools = make_tools(session, directory)
    by_name = {item.name: item for item in tools}
    bound = model.bind_tools(tools, parallel_tool_calls=False)

    def agent(state: DraftState, config: RunnableConfig) -> dict:
        reply = bound.invoke(
            [SystemMessage(content=SYSTEM), *state["messages"]], config=config,
        )
        if not isinstance(reply, AIMessage):
            raise TypeError("The chat model must return an AIMessage.")
        return {"messages": [reply], "model_calls": state["model_calls"] + 1}

    def execute_tools(state: DraftState, config: RunnableConfig) -> dict:
        calls = state["messages"][-1].tool_calls
        results = []
        for call in calls:
            try:
                # Reject a whole batch rather than ambiguously update AND save.
                if len(calls) != 1:
                    raise ValueError("Request one tool at a time; no batch executed.")
                if call["name"] not in by_name:
                    raise ValueError("Unknown tool: " + call["name"])
                text = by_name[call["name"]].invoke(call["args"], config=config)
                status = "success"
            except (ValueError, OSError, TypeError) as error:
                text = f"ERROR: {type(error).__name__}: {error}"
                status = "error"
            results.append(ToolMessage(
                content=text, tool_call_id=call["id"], name=call["name"],
                status=status,
            ))
        return {"messages": results}

    builder = StateGraph(DraftState)
    builder.add_node("agent", agent)
    builder.add_node("tools", execute_tools)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent", after_agent, {"tools": "tools", "end": END},
    )
    builder.add_conditional_edges(
        "tools", lambda state: after_tools(state, session),
        {"agent": "agent", "end": END},
    )
    return builder.compile()


def take_turn(app, session: DraftSession, history: list, prompt: str, *,
              save_requested: bool = False) -> dict:
    """The human supplies feedback OUTSIDE the graph; this is not interrupt()."""
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
    first = take_turn(
        app, session, [],
        "Draft a polite email to Tom: I cannot attend the 10 a.m. meeting. "
        "Sign it Maya. Use update with the complete draft; do not save.",
    )
    assert session.content.strip() and session.revision_count >= 1
    assert session.saved_path is None
    initial = session.content
    revised = take_turn(
        app, session, first["messages"],
        "Revise the current email. Offer 12:00 New York time tomorrow instead. "
        "Replace the sender Maya with Priya and put a blank line before the "
        "closing. Preserve Tom. Include the literal phrase '12:00 New York "
        "time tomorrow'. Call update with the whole revised email; do not save.",
    )
    final_draft = session.content
    assert final_draft != initial and session.revision_count >= 2
    for fact in ("Tom", "Priya", "12:00 New York time tomorrow"):
        assert fact in final_draft, f"Missing requested fact: {fact}"
    assert "Maya" not in final_draft and "\n\n" in final_draft
    saved = take_turn(
        app, session, revised["messages"],
        "I approve this draft. Save it now as meeting_email.txt, unchanged.",
        save_requested=True,
    )
    assert session.saved_path == directory / "meeting_email.txt"
    assert session.saved_path.read_text(encoding="utf-8") == final_draft
    assert isinstance(saved["messages"][-1], ToolMessage)
    assert saved["messages"][-1].name == "save"
    assert saved["messages"][-1].status == "success"

    unclear = DraftSession()
    clarification = take_turn(
        build_graph(model, directory, unclear), unclear, [], "write an email",
    )
    assert not unclear.content and unclear.revision_count == 0
    assert not any(isinstance(item, ToolMessage)
                   for item in clarification["messages"])
    question = message_text(clarification["messages"][-1])
    assert question.strip() and unclear.saved_path is None
    return {
        "saved_path": str(session.saved_path),
        "revision_count": session.revision_count,
        "saved_matches_latest_draft": True,
        "ended_on_successful_save": True,
        "clarification_without_tools": True,
        "clarifying_response": question,
        "final_document": final_draft,
    }


if __name__ == "__main__":
    run_cli("L10", run_demo)
