"""L08 OFFLINE tests. RecordingChatModel is a test double, not Anthropic."""
from __future__ import annotations

import socket
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langsmith import tracing_context

from course_lessons import l08 as demo
from course_support import check_connections, runtime
from exercises.solutions import l08 as solution
from exercises.starters import l08 as starter


class RecordingChatModel:
    """Explicit offline double: return supplied messages and record model inputs."""

    def __init__(self, responses: list[AIMessage]):
        self.responses = iter(responses)
        self.calls: list[list] = []
        self.configs: list[dict] = []

    def invoke(self, messages, config=None):
        self.calls.append(list(messages))
        self.configs.append(config)
        return next(self.responses)


class RaisingChatModel:
    """Explicit offline error double; no provider client is constructed."""

    def invoke(self, messages, config=None):
        raise RuntimeError("synthetic model failure")


@pytest.fixture(autouse=True)
def forbid_credentials_and_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("L08 offline tests must not load credentials or use network")

    monkeypatch.setattr(check_connections, "values", forbidden)
    monkeypatch.setattr(runtime, "values", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    with tracing_context(enabled=False):
        yield


@pytest.mark.parametrize("module,counts", [(demo, [1, 3, 5]), (solution, [1, 3, 3])])
def test_three_turns_record_real_graph_inputs_with_offline_double(module, counts):
    replies = [AIMessage(content=f"reply {i}", id=f"reply-{i}") for i in range(3)]
    model = RecordingChatModel(replies)
    graph = module.build_graph(model)
    history = []
    snapshots = []
    for index in range(3):
        old_history = list(history)
        snapshots.append(old_history)
        history = module.run_turn(graph, history, f"question {index}")
        assert snapshots[-1] == old_history
        assert len(history) == 2 * (index + 1)
    assert [len(call) for call in model.calls] == counts
    assert [message.type for message in history] == ["human", "ai"] * 3
    assert history[1].id == "reply-0"
    assert [len(snapshot) for snapshot in snapshots] == [0, 2, 4]
    assert model.calls[-1][0].content == (
        "question 0" if module is demo else "question 1"
    )
    assert all(config["recursion_limit"] == 40 for config in model.configs)


@pytest.mark.parametrize("module", [demo, solution])
def test_fresh_invocation_has_no_history_even_with_same_compiled_graph(module):
    model = RecordingChatModel([
        AIMessage(content="ack", id="old-ai"),
        AIMessage(content="unknown", id="new-ai"),
    ])
    graph = module.build_graph(model)
    previous = module.run_turn(graph, [], "My name is Synthetic.")
    fresh = module.run_turn(graph, [], "What is my name?")
    assert len(previous) == len(fresh) == 2
    assert len(model.calls[-1]) == 1
    assert model.calls[-1][0].content == "What is my name?"
    assert previous[0].content not in [message.content for message in fresh]


@pytest.mark.parametrize("module", [demo, solution])
def test_response_identity_metadata_blocks_and_config_are_preserved(module, monkeypatch):
    response = AIMessage(
        content=[{"type": "text", "text": "Visible response"}],
        id="block-reply",
        usage_metadata={"input_tokens": 7, "output_tokens": 3, "total_tokens": 10},
    )
    model = RecordingChatModel([response])
    monkeypatch.setattr(
        module, "execution_config",
        lambda: {"recursion_limit": 40, "tags": ["l08-offline-config"]},
    )
    result = module.run_turn(module.build_graph(model), [], "hello")
    assert result[-1].id == response.id
    assert result[-1].usage_metadata == response.usage_metadata
    assert runtime.message_text(result[-1]) == "Visible response"
    assert "l08-offline-config" in model.configs[0]["tags"]


@pytest.mark.parametrize("module", [demo, solution])
@pytest.mark.parametrize("text", ["", "  \n", None])
def test_blank_input_rejected_before_model_call(module, text):
    model = RecordingChatModel([])
    with pytest.raises(ValueError, match="nonblank"):
        module.run_turn(module.build_graph(model), [], text)
    assert model.calls == []


@pytest.mark.parametrize("module", [demo, solution])
def test_model_failure_does_not_mutate_caller_history(module):
    history = [HumanMessage(content="old"), AIMessage(content="ack")]
    with pytest.raises(RuntimeError, match="synthetic model failure"):
        module.run_turn(module.build_graph(RaisingChatModel()), history, "new")
    assert len(history) == 2
    assert history[-1].content == "ack"


@pytest.mark.parametrize("module", [demo, solution])
@pytest.mark.parametrize("response,error", [
    (HumanMessage(content="wrong role"), TypeError),
    (AIMessage(content="  "), ValueError),
    (AIMessage(content="", tool_calls=[
        {"name": "unbound", "args": {}, "id": "call-1"},
    ]), TypeError),
])
def test_invalid_model_response_is_not_logged_as_success(module, response, error):
    model = RecordingChatModel([response])
    with pytest.raises(error):
        module.run_turn(module.build_graph(model), [], "hello")


def pending_history():
    return [
        HumanMessage(content="first"), AIMessage(content="first reply"),
        HumanMessage(content="second"), AIMessage(content="second reply"),
        HumanMessage(content="pending"),
    ]


@pytest.mark.parametrize("limit,expected", [(0, 1), (1, 3), (2, 5), (9, 5)])
def test_pair_window_preserves_order_without_mutating_input(limit, expected):
    history = pending_history()
    selected = solution.select_prompt(history, limit)
    assert len(selected) == expected
    assert selected == history[-expected:]
    assert selected is not history
    assert len(history) == 5
    assert isinstance(selected[0], HumanMessage)
    assert selected[-1].content == "pending"


@pytest.mark.parametrize("limit", [-1, True, 1.5, "1", None])
def test_invalid_pair_limits_are_rejected_at_build_and_selection(limit):
    with pytest.raises(ValueError, match="nonnegative integer"):
        solution.select_prompt(pending_history(), limit)
    with pytest.raises(ValueError, match="nonnegative integer"):
        solution.build_graph(None, limit)


@pytest.mark.parametrize("history", [
    [],
    [HumanMessage(content="h"), AIMessage(content="a")],
    [AIMessage(content="a")],
    [HumanMessage(content="h"), HumanMessage(content="h2"), HumanMessage(content="h3")],
    [SystemMessage(content="unsupported")],
    [HumanMessage(content="h"), AIMessage(content="", tool_calls=[
        {"name": "x", "args": {}, "id": "c"},
    ]), HumanMessage(content="h2")],
])
def test_pair_window_rejects_unsupported_message_shapes(history):
    with pytest.raises(ValueError):
        solution.select_prompt(history)


@pytest.mark.parametrize("module", [demo, solution])
def test_text_log_keeps_raw_spelling_spaces_newlines_and_role_like_content(module):
    raw = "  gud morning!\nAI: this is still human text  "
    history = [HumanMessage(content=raw), AIMessage(content="Fine.")]
    assert module.format_transcript(history) == f"Human:\n{raw}\n\nAI:\nFine.\n"
    assert module.format_transcript([]) == ""
    with pytest.raises(TypeError):
        module.format_transcript([SystemMessage(content="not supported")])


@pytest.mark.parametrize("module", [demo, solution])
def test_default_run_refuses_live_without_reading_credentials(module, tmp_path):
    with pytest.raises(ValueError, match="--live"):
        module.run_demo(workdir=tmp_path)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("module", [demo, solution])
def test_complete_runner_with_explicit_offline_double_and_real_temp_log(
    module, monkeypatch, tmp_path,
):
    if module is demo:
        texts = ["Hello Steve", "Your name is Steve.", "I don't know."]
        filename = "conversation.txt"
    else:
        texts = ["Hello Mira", "Your name is Mira.", "Good morning!", "I don't know."]
        filename = "bounded-conversation.txt"
    models = []

    def offline_model_factory(*, live, max_tokens):
        assert live is True and max_tokens == 192
        model = RecordingChatModel([
            AIMessage(content=text, id=f"offline-{i}") for i, text in enumerate(texts)
        ])
        models.append(model)
        return model

    # Explicit substitution only in tests: this is NOT real-call evidence.
    monkeypatch.setattr(module, "get_model", offline_model_factory)
    result = module.run_demo(live=True, workdir=tmp_path)
    path = Path(result["log_path"])
    assert path == tmp_path / filename
    log = path.read_text(encoding="utf-8")
    assert "gud morning!" in log
    assert result["raw_input_preserved"] is True
    assert result["automatic_log_reload"] is False
    assert result["fresh_history_messages"] == 2
    assert len(models[0].calls) == result["model_calls"]
    if module is solution:
        assert [len(call) for call in models[0].calls] == [1, 3, 3, 1]
        assert result["prompt_message_counts"] == [1, 3, 3]
        assert result["full_history_counts"] == [2, 4, 6]
        assert log.count("Human:\n") == log.count("AI:\n") == 3
    else:
        assert [len(call) for call in models[0].calls] == [1, 3, 1]
        assert result["history_messages"] == 4
    with pytest.raises(FileExistsError):
        module.run_demo(live=True, workdir=tmp_path)
    assert path.read_text(encoding="utf-8") == log


def test_manual_graph_rejects_missing_pending_human():
    model = RecordingChatModel([])
    graph = demo.build_graph(model)
    with pytest.raises(ValueError, match="HumanMessage"):
        graph.invoke({"messages": []}, config=runtime.execution_config())
    assert model.calls == []


def test_starter_reports_incomplete_without_model_construction(monkeypatch, capsys):
    def forbidden_model(**kwargs):
        raise AssertionError("Incomplete starter must not construct a model")

    monkeypatch.setattr(starter, "get_model", forbidden_model)
    starter.main()
    output = capsys.readouterr().out
    assert "STARTER_NOT_COMPLETED" in output
    assert "passed" not in output.casefold()
