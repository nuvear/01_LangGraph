"""U1 offline tests: named doubles are NOT real Anthropic validation."""
from __future__ import annotations

from pathlib import Path
import re
import socket
import subprocess
import sys

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langsmith import tracing_context
import pytest

from course_lessons import u1 as demo
from course_support import check_connections, runtime
from exercises.solutions import u1 as solution

ROOT = Path(__file__).resolve().parents[2]


class ProjectRecallDouble:
    """Deterministic model double; records exactly the visible human history."""
    def __init__(self):
        self.calls = []
        self.configs = []

    def invoke(self, messages, config=None):
        humans = [item.content for item in messages if isinstance(item, HumanMessage)]
        self.calls.append(humans)
        self.configs.append(config)
        match = re.search(r"My project code is ([A-Z]+-\d+)", "\n".join(humans))
        return AIMessage(content=match.group(1) if match else "UNKNOWN")


class DestinationRecallDouble:
    """A test double, not a language model and not evidence of live recall."""
    def __init__(self):
        self.calls = []

    def invoke(self, messages, config=None):
        humans = [item.content for item in messages if isinstance(item, HumanMessage)]
        self.calls.append(humans)
        match = re.search(r"My destination is (Kyoto|Oslo)\.", "\n".join(humans))
        return AIMessage(content=match.group(1) if match else "UNKNOWN")


class InvalidResponseDouble:
    def invoke(self, messages, config=None):
        return "Not an AIMessage"


class FailingModelDouble:
    def invoke(self, messages, config=None):
        raise RuntimeError("Synthetic offline model failure")


@pytest.fixture(autouse=True)
def no_network_or_settings(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Offline U1 tests must not read settings or use network")

    monkeypatch.setattr(runtime, "values", forbidden)
    monkeypatch.setattr(check_connections, "values", forbidden)
    monkeypatch.setattr(check_connections, "dotenv_values", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    with tracing_context(enabled=False):
        yield


@pytest.fixture
def sqlite_backend():
    module = pytest.importorskip(
        "langgraph.checkpoint.sqlite",
        reason="Parent must install langgraph-checkpoint-sqlite; no fake backend",
    )
    return module.SqliteSaver


@pytest.mark.parametrize("module", [demo, solution])
def test_run_demo_requires_live_without_reading_settings(module, tmp_path):
    with pytest.raises(ValueError, match="--live"):
        module.run_demo(workdir=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_starter_is_honestly_incomplete():
    completed = subprocess.run(
        [sys.executable, "-m", "exercises.starters.u1"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert "STARTER_NOT_COMPLETED" in completed.stdout
    assert "not a passing solution" in completed.stdout


@pytest.mark.parametrize("send", [demo.send_turn, solution.ask])
@pytest.mark.parametrize(
    "thread_id,text",
    [("", "hello"), ("  ", "hello"), (None, "hello"),
     ("valid", ""), ("valid", " \n"), ("valid", None)],
)
def test_reject_bad_inputs_before_invocation(send, thread_id, text):
    # object() has no invoke: validation must happen before calling the graph.
    with pytest.raises(ValueError, match="nonblank string"):
        send(object(), thread_id, text)


@pytest.mark.parametrize(
    "build,send", [(demo.build_graph, demo.send_turn),
                   (solution.build_notebook, solution.ask)],
)
def test_node_and_reducer_contract_only_in_memory(build, send):
    model = ProjectRecallDouble()
    graph = build(model, InMemorySaver())
    original = "  My project code is ORCHID-42. Remember it.  "
    one = send(graph, "a", original)
    two = send(graph, "a", "What is my project code?")
    other = send(graph, "b", "What is my project code?")
    assert len(one["messages"]) == 2
    assert len(two["messages"]) == 4
    assert len(other["messages"]) == 2
    assert model.calls[0] == [original]
    assert model.calls[1] == [original, "What is my project code?"]
    assert model.calls[2] == ["What is my project code?"]
    assert other["messages"][-1].content == "UNKNOWN"
    assert model.configs[0]["configurable"]["thread_id"] == "a"
    assert model.configs[0]["recursion_limit"] == 40


@pytest.mark.parametrize(
    "build,send", [(demo.build_graph, demo.send_turn),
                   (solution.build_notebook, solution.ask)],
)
def test_invalid_model_response_is_not_checkpointed_as_success(build, send):
    graph = build(InvalidResponseDouble(), InMemorySaver())
    with pytest.raises(TypeError, match="AIMessage"):
        send(graph, "a", "hello")


def test_demo_real_sqlite_reopen_and_new_process(sqlite_backend, tmp_path):
    model = ProjectRecallDouble()
    summary = demo.run_checkpoint_lab(model, tmp_path)
    assert summary["primary_message_count"] == 6
    assert summary["other_message_count"] == 2
    assert summary["fresh_process_checkpoint_read"] is True
    assert summary["closed_and_reopened"] is True
    assert [len(call) for call in model.calls] == [1, 2, 1, 3]
    assert "ORCHID-42" not in "\n".join(model.calls[2])
    database = Path(summary["database"])
    assert database.is_file()
    saved = demo.inspect_checkpoint(database, "project-a")
    assert saved["message_count"] == 6
    assert demo.inspect_checkpoint(database, "never-created") == {
        "exists": False, "message_count": 0, "human_texts": [],
    }


def test_solution_three_threads_recover_independent_facts(sqlite_backend, tmp_path):
    model = DestinationRecallDouble()
    summary = solution.run_lab(model, tmp_path / "travel.sqlite3")
    assert summary["message_counts"] == {"trip-a": 4, "trip-b": 4, "trip-c": 2}
    assert summary["answers"] == {
        "trip-a": "Kyoto", "trip-b": "Oslo", "trip-c": "UNKNOWN",
    }
    assert summary["recovered_checkpoint_ids_match"] is True
    assert summary["model_calls"] == 5
    assert [len(call) for call in model.calls] == [1, 1, 2, 2, 1]
    assert all("Oslo" not in item for item in model.calls[2])
    assert all("Kyoto" not in item for item in model.calls[3])
    assert model.calls[4] == ["What is my destination?"]
    with pytest.raises(FileExistsError, match="new database"):
        solution.run_lab(model, tmp_path / "travel.sqlite3")
    assert len(model.calls) == 5


def test_get_state_after_reopen_does_not_call_model(sqlite_backend, tmp_path):
    database = tmp_path / "read-only-inspection.sqlite3"
    with sqlite_backend.from_conn_string(str(database)) as saver:
        graph = demo.build_graph(ProjectRecallDouble(), saver)
        demo.send_turn(graph, "a", "My project code is ORCHID-42.")
    with sqlite_backend.from_conn_string(str(database)) as reopened:
        reader = demo.build_graph(FailingModelDouble(), reopened)
        snapshot = reader.get_state(runtime.execution_config("a"))
        assert len(snapshot.values["messages"]) == 2
        assert snapshot.next == ()
    assert demo.fresh_process_view(database, "a")["message_count"] == 2


@pytest.mark.parametrize(
    "build,send", [(demo.build_graph, demo.send_turn),
                   (solution.build_notebook, solution.ask)],
)
def test_model_failure_propagates_and_leaves_no_ai_turn(
    sqlite_backend, tmp_path, build, send,
):
    with sqlite_backend.from_conn_string(str(tmp_path / "failed.sqlite3")) as saver:
        graph = build(FailingModelDouble(), saver)
        with pytest.raises(RuntimeError, match="Synthetic offline model failure"):
            send(graph, "failed", "hello")
        state = graph.get_state(runtime.execution_config("failed"))
        assert len(state.values["messages"]) == 1
        assert isinstance(state.values["messages"][0], HumanMessage)
        assert state.next  # Work remains; this is NOT a successful AI response.


def test_missing_database_inspection_does_not_create_file(tmp_path):
    missing = tmp_path / "absent.sqlite3"
    with pytest.raises(FileNotFoundError):
        demo.inspect_checkpoint(missing, "a")
    assert not missing.exists()
