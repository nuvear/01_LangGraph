"""Offline L07 checks: these doubles are NOT live Anthropic validation."""
from __future__ import annotations

import json
import runpy
import socket

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from course_lessons import l07 as demo
from course_support import runtime
from exercises.solutions import l07 as solution


class RecordingChatModelDouble:
    """Record exact inputs/config; return explicit synthetic test text."""

    def __init__(self, response=None):
        self.calls = []
        self.response = response if response is not None else AIMessage(
            content="OFFLINE TEST DOUBLE reply",
            usage_metadata={"input_tokens": 7, "output_tokens": 3, "total_tokens": 10},
        )

    def invoke(self, messages, config=None):
        self.calls.append({"messages": list(messages), "config": config})
        return self.response


class FailingChatModelDouble:
    """A simulated provider failure must propagate, not become a fake answer."""

    def invoke(self, messages, config=None):
        raise RuntimeError("OFFLINE simulated provider failure")


@pytest.fixture(autouse=True)
def prevent_network_and_credentials(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Offline L07 tests must not use network or credentials.")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(runtime, "values", forbidden)
    for module in (demo, solution):
        monkeypatch.setattr(
            module, "execution_config",
            lambda: {"recursion_limit": 40, "tags": ["l07-offline-test"]},
        )


def test_demo_fresh_human_message_each_time_and_config_forwarding():
    model = RecordingChatModelDouble()
    graph = demo.build_bot(model)
    first = demo.ask(graph, "My name is Bob.")
    second = demo.ask(graph, "What is my name?")
    assert first["sent_messages"] == ["My name is Bob."]
    assert second["sent_messages"] == ["What is my name?"]
    assert len(first["messages"]) == len(second["messages"]) == 1
    assert first["messages"] is not second["messages"]
    assert [c["messages"][0].content for c in model.calls] == [
        "My name is Bob.", "What is my name?",
    ]
    assert all(len(c["messages"]) == 1 for c in model.calls)
    assert all(isinstance(c["messages"][0], HumanMessage) for c in model.calls)
    assert all(c["config"]["recursion_limit"] == 40 for c in model.calls)
    assert all("l07-offline-test" in c["config"]["tags"] for c in model.calls)
    assert second["usage"]["total_tokens"] == 10


@pytest.mark.parametrize("prompt", ["", " \n", None, 42])
def test_demo_rejects_invalid_prompt_before_model_call(prompt):
    model = RecordingChatModelDouble()
    with pytest.raises(ValueError, match="nonblank"):
        demo.ask(demo.build_bot(model), prompt)
    assert model.calls == []


@pytest.mark.parametrize("messages", [[], [AIMessage(content="wrong role")],
                                       [HumanMessage(content="a"),
                                        HumanMessage(content="b")]])
def test_demo_graph_rejects_history_or_wrong_role(messages):
    model = RecordingChatModelDouble()
    with pytest.raises(ValueError, match="exactly one"):
        demo.build_bot(model).invoke(
            {"messages": messages}, config=demo.execution_config(),
        )
    assert model.calls == []


def test_terminal_loop_skips_blank_preserves_text_and_stops_before_exit():
    model = RecordingChatModelDouble()
    entries = iter(["  ", "  Hello there  ", " ExIt ", "never send"])
    displayed = []
    report = demo.terminal_chat(
        demo.build_bot(model), read=lambda _: next(entries), write=displayed.append,
    )
    assert report["skipped"] == 1
    assert report["stop_reason"] == "exit"
    assert len(report["turns"]) == len(model.calls) == 1
    assert model.calls[0]["messages"][0].content == "  Hello there  "
    assert next(entries) == "never send"
    assert "no model call" in displayed[0]


def test_terminal_limit_counts_blank_entries_and_handles_eof():
    model = RecordingChatModelDouble()
    graph = demo.build_bot(model)
    report = demo.terminal_chat(
        graph, read=lambda _: "  ", write=lambda _: None, max_entries=2,
    )
    assert report == {"turns": [], "skipped": 2, "stop_reason": "limit"}

    def eof(_):
        raise EOFError

    assert demo.terminal_chat(graph, read=eof)["stop_reason"] == "eof"
    assert model.calls == []


@pytest.mark.parametrize("raw,expected", [
    ("exit", "exit"), (" ExIt \n", "exit"), ("  ", "skip"),
    ("", "skip"), (" exiting ", "send"), ("  Hi  ", "send"),
])
def test_solution_control_policy(raw, expected):
    assert solution.classify_entry(raw) == expected


def test_solution_control_rejects_nonstring():
    with pytest.raises(TypeError, match="string"):
        solution.classify_entry(None)


def test_solution_exact_workbook_session_and_no_history():
    model = RecordingChatModelDouble()
    entries = ["  ", "My name is Mira. Say hello briefly.",
               "What is my name?", " ExIt ", "This must never be sent."]
    original = entries.copy()
    report = solution.run_session(solution.build_bot(model), entries)
    assert report["skipped"] == 1
    assert report["inspected"] == 4
    assert report["stop_reason"] == "exit"
    assert len(report["turns"]) == len(model.calls) == 2
    assert [c["messages"][0].content for c in model.calls] == entries[1:3]
    assert all(len(c["messages"]) == 1 for c in model.calls)
    assert all(c["config"]["recursion_limit"] == 40 for c in model.calls)
    assert all("l07-offline-test" in c["config"]["tags"] for c in model.calls)
    assert [t["sent_messages"] for t in report["turns"]] == [
        [entries[1]], [entries[2]],
    ]
    assert entries == original
    assert json.loads(json.dumps(report))["stop_reason"] == "exit"


def test_solution_limit_exhaustion_and_unconsumed_tail():
    model = RecordingChatModelDouble()
    graph = solution.build_bot(model)
    source = iter(["one", " ", "three"])
    report = solution.run_session(graph, source, max_entries=2)
    assert report["stop_reason"] == "limit"
    assert report["inspected"] == 2 and report["skipped"] == 1
    assert next(source) == "three"
    empty = solution.run_session(graph, [])
    assert empty == {"turns": [], "skipped": 0, "inspected": 0,
                     "stop_reason": "exhausted"}
    assert solution.run_session(graph, ["short"])["stop_reason"] == "exhausted"


@pytest.mark.parametrize("limit", [0, -1, 1.5, True])
def test_both_loops_reject_invalid_limits_without_model_call(limit):
    model = RecordingChatModelDouble()
    with pytest.raises(ValueError, match="positive integer"):
        solution.run_session(solution.build_bot(model), ["hello"], max_entries=limit)
    with pytest.raises(ValueError, match="positive integer"):
        demo.terminal_chat(demo.build_bot(model), max_entries=limit)
    assert model.calls == []


@pytest.mark.parametrize("prompt", ["", " ", " ExIt "])
def test_solution_direct_graph_rejects_control_entries(prompt):
    model = RecordingChatModelDouble()
    with pytest.raises(ValueError, match="nonblank, non-exit"):
        solution.build_bot(model).invoke(
            {"prompt": prompt}, config=solution.execution_config(),
        )
    assert model.calls == []


@pytest.mark.parametrize("module", [demo, solution])
def test_content_blocks_and_missing_usage_are_supported(module):
    response = AIMessage(content=[
        {"type": "text", "text": "First."},
        {"type": "thinking", "thinking": "not display text"},
        {"type": "text", "text": "Second."},
    ])
    model = RecordingChatModelDouble(response)
    graph = module.build_bot(model)
    result = (demo.ask(graph, "Hello") if module is demo else
              solution.run_session(graph, ["Hello"])["turns"][0])
    assert result["reply"] == "First.Second."
    assert result["usage"] == {}


@pytest.mark.parametrize("module", [demo, solution])
@pytest.mark.parametrize("response,error", [
    (AIMessage(content="  "), ValueError), ("not an AIMessage", TypeError),
])
def test_both_graphs_reject_unusable_responses(module, response, error):
    graph = module.build_bot(RecordingChatModelDouble(response))
    with pytest.raises(error):
        if module is demo:
            demo.ask(graph, "Hello")
        else:
            solution.run_session(graph, ["Hello"])


@pytest.mark.parametrize("module", [demo, solution])
def test_provider_failure_is_not_replaced_with_canned_success(module):
    graph = module.build_bot(FailingChatModelDouble())
    with pytest.raises(RuntimeError, match="simulated provider failure"):
        if module is demo:
            demo.ask(graph, "Hello")
        else:
            solution.run_session(graph, ["Hello"])


@pytest.mark.parametrize("module", [demo, solution])
def test_run_demo_refuses_without_live_before_accessing_model(module, monkeypatch):
    def forbidden_factory(**kwargs):
        raise AssertionError("Factory must not be used without explicit live opt-in.")

    monkeypatch.setattr(module, "get_model", forbidden_factory)
    with pytest.raises(ValueError, match="--live"):
        module.run_demo()


@pytest.mark.parametrize("module", [demo, solution])
def test_run_demo_summary_with_explicit_offline_injected_double(
    module, monkeypatch, tmp_path,
):
    # live=True here only exercises control flow. The factory is replaced;
    # no ChatAnthropic is constructed and no live request is made.
    model = RecordingChatModelDouble()
    monkeypatch.setattr(module, "get_model", lambda **kwargs: model)
    report = module.run_demo(live=True, workdir=tmp_path)
    assert report["checked_turns"] == len(model.calls) == 2
    assert report["messages_per_request"] == [1, 1]
    assert report["prior_turns_forwarded"] is False
    assert report["stop_reason"] == "exit"
    assert json.loads(json.dumps(report))["checked_turns"] == 2
    assert list(tmp_path.iterdir()) == []


def test_starter_reports_incomplete_without_network_or_credentials(capsys):
    runpy.run_module("exercises.starters.l07", run_name="__main__")
    captured = capsys.readouterr()
    assert "STARTER_NOT_COMPLETED" in captured.out
    assert "status\": \"passed" not in captured.out
