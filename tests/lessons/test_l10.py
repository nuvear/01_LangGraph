"""Offline L10 tests: scripted doubles are NOT evidence of Anthropic behavior."""
from __future__ import annotations

from pathlib import Path
import socket

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langsmith import tracing_context

import course_support.check_connections as connections
import course_support.observability as observability
import course_support.runtime as runtime
from course_lessons import l10 as demonstration
from exercises.solutions import l10 as solution
from exercises.starters import l10 as starter


class ScriptedOfflineChatModel:
    """Named test double; returns only test-authored AIMessage objects."""

    def __init__(self, responses: list[AIMessage]):
        self.responses = list(responses)
        self.invocations = []
        self.bindings = []

    def bind_tools(self, tools, **kwargs):
        self.bindings.append(([item.name for item in tools], kwargs))
        return self

    def invoke(self, messages, config=None):
        self.invocations.append((list(messages), dict(config or {})))
        assert self.responses, "Unexpected extra model invocation"
        return self.responses.pop(0)


def tool_request(name: str, args: dict, call_id: str = "offline-call") -> AIMessage:
    return AIMessage(content="", tool_calls=[
        {"name": name, "args": args, "id": call_id, "type": "tool_call"},
    ])


@pytest.fixture(autouse=True)
def no_network_or_settings(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Offline tests must not use network or settings")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(connections, "dotenv_values", forbidden)
    monkeypatch.setattr(connections, "values", forbidden)
    monkeypatch.setattr(runtime, "values", forbidden)
    monkeypatch.setattr(observability, "values", forbidden)
    with tracing_context(enabled=False):
        yield


@pytest.fixture(params=[demonstration, solution], ids=["demo", "reference"])
def lesson(request):
    return request.param


def test_update_revise_save_keeps_history_and_stops_without_extra_model_call(
        lesson, tmp_path, monkeypatch):
    initial = "Dear Tom,\nMeeting cancelled.\n\nMaya"
    final = "Dear Tom,\n12:00 New York time tomorrow.\n\nPriya"
    model = ScriptedOfflineChatModel([
        tool_request("update", {"content": initial}, "u1"),
        AIMessage(content=initial),
        tool_request("update", {"content": final}, "u2"),
        AIMessage(content=final),
        tool_request("save", {"filename": "approved.txt"}, "s1"),
    ])
    monkeypatch.setattr(lesson, "execution_config", lambda: {
        "callbacks": [], "tags": ["offline-l10"], "recursion_limit": 40,
    })
    session = lesson.DraftSession()
    graph = lesson.build_graph(model, tmp_path, session)
    first = lesson.take_turn(graph, session, [], "Draft the cancellation.")
    assert session.content == initial and session.saved_path is None
    revised = lesson.take_turn(graph, session, first["messages"], "Revise it.")
    saved = lesson.take_turn(
        graph, session, revised["messages"], "Save approved.txt",
        save_requested=True,
    )
    assert session.revision_count == 2
    assert session.saved_path.read_bytes() == final.encode("utf-8")
    assert session.saved_path == tmp_path / "approved.txt"
    assert isinstance(saved["messages"][-1], ToolMessage)
    assert saved["messages"][-1].tool_call_id == "s1"
    assert saved["messages"][-1].status == "success"
    assert len(saved["messages"]) == 11
    assert sum(isinstance(item, HumanMessage)
               for item in saved["messages"]) == 3
    assert len(model.invocations) == 5 and not model.responses
    assert all("offline-l10" in config["tags"]
               for _, config in model.invocations)
    assert model.bindings == [(["update", "save"], {"parallel_tool_calls": False})]
    assert not session.save_requested
    with pytest.raises(ValueError, match="ended after saving"):
        lesson.take_turn(graph, session, saved["messages"], "One more change")


def test_underspecified_request_ends_turn_without_executing_tools(lesson, tmp_path):
    model = ScriptedOfflineChatModel([
        AIMessage(content="Who is the recipient, and what is the email about?"),
    ])
    session = lesson.DraftSession()
    result = lesson.take_turn(
        lesson.build_graph(model, tmp_path, session), session, [], "write an email",
    )
    assert len(result["messages"]) == 2 and result["model_calls"] == 1
    assert not any(isinstance(item, ToolMessage) for item in result["messages"])
    assert session.content == "" and session.revision_count == 0
    assert session.saved_path is None and list(tmp_path.iterdir()) == []


def test_collision_is_an_error_and_a_later_human_turn_recovers(lesson, tmp_path):
    occupied = tmp_path / "taken.txt"
    occupied.write_text("DO NOT OVERWRITE", encoding="utf-8")
    model = ScriptedOfflineChatModel([
        tool_request("save", {"filename": "taken.txt"}, "failed"),
        AIMessage(content="The file exists. Please choose another filename."),
        tool_request("save", {"filename": "recovered.txt"}, "recovered"),
    ])
    session = lesson.DraftSession(content="Latest reviewed email", revision_count=2)
    graph = lesson.build_graph(model, tmp_path, session)
    failed = lesson.take_turn(
        graph, session, [], "Save taken.txt", save_requested=True,
    )
    error = next(item for item in failed["messages"]
                 if isinstance(item, ToolMessage))
    assert error.tool_call_id == "failed" and error.status == "error"
    assert "FileExistsError" in error.content
    assert session.saved_path is None and session.revision_count == 2
    assert occupied.read_text(encoding="utf-8") == "DO NOT OVERWRITE"
    assert session.content == "Latest reviewed email"
    lesson.take_turn(
        graph, session, failed["messages"], "Save recovered.txt",
        save_requested=True,
    )
    assert session.saved_path.read_text(encoding="utf-8") == session.content
    assert occupied.read_text(encoding="utf-8") == "DO NOT OVERWRITE"
    assert not session.save_requested


@pytest.mark.parametrize("requested,content,expected", [
    (False, "Reviewed draft", "not requested"),
    (True, "", "no draft"),
])
def test_save_guard_blocks_unrequested_or_empty_save(
        lesson, tmp_path, requested, content, expected):
    model = ScriptedOfflineChatModel([
        tool_request("save", {"filename": "blocked.txt"}),
        AIMessage(content="Please provide the missing human input."),
    ])
    session = lesson.DraftSession(content=content)
    result = lesson.take_turn(
        lesson.build_graph(model, tmp_path, session), session, [], "Feedback",
        save_requested=requested,
    )
    error = next(item for item in result["messages"]
                 if isinstance(item, ToolMessage))
    assert error.status == "error" and expected in error.content
    assert session.saved_path is None and not session.save_requested
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("filename", [
    "../escape.txt", "/absolute.txt", "nested/draft.txt", "draft.pdf",
    "draft..txt",
])
def test_unsafe_filename_does_not_write_or_mark_success(lesson, tmp_path, filename):
    session = lesson.DraftSession(content="Private classroom draft", save_requested=True)
    save = {item.name: item for item in lesson.make_tools(session, tmp_path)}["save"]
    with pytest.raises(ValueError):
        save.invoke({"filename": filename})
    assert session.saved_path is None and list(tmp_path.iterdir()) == []


def test_symlink_target_cannot_be_overwritten(lesson, tmp_path):
    target = tmp_path / "real.txt"
    target.write_text("Existing", encoding="utf-8")
    (tmp_path / "link.txt").symlink_to(target)
    session = lesson.DraftSession(content="Do not write", save_requested=True)
    save = {item.name: item for item in lesson.make_tools(session, tmp_path)}["save"]
    with pytest.raises(ValueError):
        save.invoke({"filename": "link.txt"})
    assert session.saved_path is None
    assert target.read_text(encoding="utf-8") == "Existing"


def test_blank_or_invalid_update_does_not_increment_revision(lesson, tmp_path):
    session = lesson.DraftSession(content="Original", revision_count=1)
    update = {item.name: item for item in lesson.make_tools(session, tmp_path)}["update"]
    for args in ({"content": "  \n"}, {}):
        with pytest.raises(ValueError):
            update.invoke(args)
    assert session.content == "Original" and session.revision_count == 1


def test_ambiguous_batch_rejects_all_calls_and_answers_every_id(lesson, tmp_path):
    batch = AIMessage(content="", tool_calls=[
        {"name": "update", "args": {"content": "Unexpected"}, "id": "one"},
        {"name": "save", "args": {"filename": "bad.txt"}, "id": "two"},
    ])
    model = ScriptedOfflineChatModel([batch, AIMessage(content="One at a time.")])
    session = lesson.DraftSession(content="Original")
    result = lesson.take_turn(
        lesson.build_graph(model, tmp_path, session), session, [], "Save",
        save_requested=True,
    )
    results = [item for item in result["messages"] if isinstance(item, ToolMessage)]
    assert [item.tool_call_id for item in results] == ["one", "two"]
    assert all(item.status == "error" for item in results)
    assert session.content == "Original" and session.revision_count == 0
    assert session.saved_path is None and list(tmp_path.iterdir()) == []


def test_unknown_tool_loop_is_bounded_and_permission_resets(lesson, tmp_path):
    model = ScriptedOfflineChatModel([
        tool_request("unknown", {}, f"bad-{index}")
        for index in range(lesson.MAX_MODEL_CALLS)
    ])
    session = lesson.DraftSession(content="Still intact")
    with pytest.raises(RuntimeError, match="budget exhausted"):
        lesson.take_turn(
            lesson.build_graph(model, tmp_path, session), session, [], "Save",
            save_requested=True,
        )
    assert len(model.invocations) == lesson.MAX_MODEL_CALLS
    assert session.content == "Still intact" and session.saved_path is None
    assert not session.save_requested


def test_assistant_claim_of_saving_is_not_file_evidence(lesson, tmp_path):
    model = ScriptedOfflineChatModel([AIMessage(content="I saved your document.")])
    session = lesson.DraftSession(content="Draft")
    lesson.take_turn(
        lesson.build_graph(model, tmp_path, session), session, [], "Save it",
        save_requested=True,
    )
    assert session.saved_path is None and list(tmp_path.iterdir()) == []
    state = {"messages": [], "model_calls": 1}
    assert lesson.after_tools(state, session) == "agent"


def test_empty_feedback_rejected_before_model_call(lesson, tmp_path):
    model = ScriptedOfflineChatModel([])
    session = lesson.DraftSession()
    with pytest.raises(ValueError, match="must not be empty"):
        lesson.take_turn(lesson.build_graph(model, tmp_path, session), session, [], " ")
    assert not model.invocations


def test_real_entrypoint_requires_explicit_live_opt_in(lesson, tmp_path):
    with pytest.raises(ValueError, match="needs --live"):
        lesson.run_demo(workdir=tmp_path)


def test_demonstration_run_demo_acceptance_with_explicit_offline_double(
        tmp_path, monkeypatch):
    initial = "Dear Tom,\nI cannot attend the 10 a.m. meeting.\n\nMaya"
    final = "Dear Tom,\nCould we meet at 12:00 New York time tomorrow?\n\nPriya"
    double = ScriptedOfflineChatModel([
        tool_request("update", {"content": initial}, "u1"), AIMessage(content=initial),
        tool_request("update", {"content": final}, "u2"), AIMessage(content=final),
        tool_request("save", {"filename": "meeting_email.txt"}, "s1"),
        AIMessage(content="Who is the recipient and what is the purpose?"),
    ])

    def offline_factory(*, live, max_tokens):
        assert live is False and max_tokens == 1100
        return double

    monkeypatch.setattr(demonstration, "get_model", offline_factory)
    result = demonstration.run_demo(workdir=tmp_path)
    assert result["saved_matches_latest_draft"] and result["ended_on_successful_save"]
    assert result["clarification_without_tools"] and result["revision_count"] == 2
    assert Path(result["saved_path"]).read_text(encoding="utf-8") == final
    assert not double.responses


def test_solution_run_demo_acceptance_with_explicit_offline_double(
        tmp_path, monkeypatch):
    initial = "Dear Elena,\nWorkshop: 17 November at 09:00 Singapore time.\n\nArun"
    final = "Dear Elena,\nWorkshop: 18 November at 14:30 Singapore time.\n\nArun"
    double = ScriptedOfflineChatModel([
        tool_request("update", {"content": initial}, "u1"), AIMessage(content=initial),
        tool_request("update", {"content": final}, "u2"), AIMessage(content=final),
        tool_request("save", {"filename": "workshop_taken.txt"}, "failed"),
        AIMessage(content="The file exists; please choose another filename."),
        tool_request("save", {"filename": "workshop_notice.txt"}, "s1"),
        AIMessage(content="Who is the recipient and what is the purpose?"),
    ])

    def offline_factory(*, live, max_tokens):
        assert live is False and max_tokens == 1100
        return double

    monkeypatch.setattr(solution, "get_model", offline_factory)
    result = solution.run_demo(workdir=tmp_path)
    assert result["collision_preserved_existing_file"]
    assert result["failed_save_did_not_finish"]
    assert result["recovery_saved_latest_draft"]
    assert result["ended_on_successful_save"] and result["clarification_without_tools"]
    assert Path(result["saved_path"]).read_text(encoding="utf-8") == final
    assert not double.responses


def test_starter_is_a_separate_honest_incomplete_program(tmp_path):
    with pytest.raises(NotImplementedError, match="TODO 1"):
        starter.run_demo(workdir=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_partially_completed_starter_reports_remaining_todos_without_calls(
        monkeypatch, capsys):
    starter.main()
    initial = capsys.readouterr().out
    assert "STARTER_NOT_COMPLETED" in initial
    assert all(name in initial for name in
               ("make_tools", "after_tools", "build_graph"))
    monkeypatch.setattr(starter, "make_tools", lambda session, directory: [])
    monkeypatch.setattr(starter, "after_tools", lambda state, session: "agent")
    starter.main()
    partial = capsys.readouterr().out
    assert partial == "STARTER_NOT_COMPLETED: implement build_graph\n"
