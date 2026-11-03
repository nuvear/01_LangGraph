"""L01 local behavior only: no model test doubles or live service requests."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import runpy
import socket
import sys

import pytest
from langsmith import tracing_context

from course_lessons import l01 as demo
from course_support import check_connections, observability, runtime
from exercises.solutions import l01 as solution
from exercises.starters import l01 as starter


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    """Fail on settings loading or network connections; disable ambient tracing."""
    def forbidden(*args, **kwargs):
        raise AssertionError("L01 tests must not load settings or use the network")

    monkeypatch.setattr(check_connections, "values", forbidden)
    monkeypatch.setattr(observability, "values", forbidden)
    monkeypatch.setattr(runtime, "values", forbidden)
    monkeypatch.setattr(runtime, "get_model", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    with tracing_context(enabled=False):
        yield


def test_demo_runs_and_is_json_serializable(tmp_path):
    summary = demo.run_demo(workdir=tmp_path)
    assert summary["mode"] == "deterministic_no_model"
    assert summary["movie"]["card"] == "The Clockwork Garden (2025)"
    assert summary["squares"] == [1, 4, 9, 16]
    assert summary["message_objects_are_hand_authored"] is True
    assert summary["tool_call_id_matches"] is True
    json.dumps(summary)
    assert list(tmp_path.iterdir()) == []


def test_demo_nodes_return_partial_updates_without_mutating():
    source = {"title": "  Original  ", "year": 2024}
    before = deepcopy(source)
    assert demo.normalize_title(source) == {"title": "Original"}
    assert source == before
    assert demo.describe_movie({"title": "Original", "year": 2024}) == {
        "card": "Original (2024)",
    }


@pytest.mark.parametrize("title,error", [
    ("", ValueError), (" \t\n", ValueError), (None, TypeError), (12, TypeError),
])
def test_demo_rejects_invalid_title(title, error):
    with pytest.raises(error):
        demo.build_graph().invoke(
            {"title": title, "year": 2024}, config=runtime.execution_config(),
        )


@pytest.mark.parametrize("year", ["2024", True, 2024.5])
def test_demo_year_annotations_do_not_replace_validation(year):
    with pytest.raises(TypeError, match="year must be an integer"):
        demo.build_graph().invoke(
            {"title": "Original", "year": year}, config=runtime.execution_config(),
        )


def test_demo_python_types_and_map():
    assert demo.square(-3) == 9
    assert demo.square(2.5) == 6.25
    assert demo.greet() == "Hello, visitor!"
    assert demo.greet("Ada") == "Hello, Ada!"
    assert demo.greet("") == "Hello, !"  # None is not the same value as blank.
    value = {"numbers": [1, 2]}
    assert demo.echo(value) is value
    iterator = map(lambda number: number * number, [1, 2, 3, 4])
    assert list(iterator) == [1, 4, 9, 16]
    assert list(iterator) == []  # map returns a consumed iterator, not a list.


def test_manually_authored_messages_match_tool_call_ids():
    messages = demo.message_examples()
    assert [message.type for message in messages] == ["system", "human", "ai", "tool"]
    assert messages[2].tool_calls[0]["args"] == {"value": 3}
    assert messages[2].tool_calls[0]["id"] == messages[3].tool_call_id
    assert messages[3].content == "9"


@pytest.mark.parametrize("module,node_names", [
    (demo, ["normalize_title", "describe_movie"]),
    (solution, ["normalize_name", "make_badge"]),
])
def test_graph_has_exact_linear_topology(module, node_names):
    graph = module.build_graph().get_graph()
    assert set(graph.nodes) == {"__start__", "__end__", *node_names}
    assert {(edge.source, edge.target) for edge in graph.edges} == {
        ("__start__", node_names[0]), (node_names[0], node_names[1]),
        (node_names[1], "__end__"),
    }


@pytest.mark.parametrize("name,sessions,clean,badge", [
    ("  Ada  ", 2, "Ada", "Ada: 2 sessions"),
    (None, 0, "Visitor", "Visitor: 0 sessions"),
    ("   ", 1, "Visitor", "Visitor: 1 session"),
    ("", 3, "Visitor", "Visitor: 3 sessions"),
    ("  Mei Lin  ", 1, "Mei Lin", "Mei Lin: 1 session"),
])
def test_solution_exact_task_cases_and_input_preservation(name, sessions, clean, badge):
    source = {"name": name, "sessions": sessions}
    before = deepcopy(source)
    result = solution.build_graph().invoke(source, config=runtime.execution_config())
    assert result == {"name": clean, "sessions": sessions, "badge": badge}
    assert source == before


def test_solution_partial_updates_are_new_dictionaries():
    source = {"name": "  Ada  ", "sessions": 2}
    before = dict(source)
    update = solution.normalize_name(source)
    assert update == {"name": "Ada"} and update is not source
    assert source == before
    normalized = {"name": "Ada", "sessions": 2}
    assert solution.make_badge(normalized) == {"badge": "Ada: 2 sessions"}
    assert normalized == {"name": "Ada", "sessions": 2}


@pytest.mark.parametrize("sessions,error", [
    (-1, ValueError), ("2", TypeError), (True, TypeError),
    (False, TypeError), (2.0, TypeError), (None, TypeError),
])
def test_solution_rejects_invalid_counts(sessions, error):
    with pytest.raises(error):
        solution.build_graph().invoke(
            {"name": "Ada", "sessions": sessions}, config=runtime.execution_config(),
        )


@pytest.mark.parametrize("name", [42, [], {}])
def test_solution_rejects_invalid_name(name):
    with pytest.raises(TypeError, match="name must be a string or None"):
        solution.build_graph().invoke(
            {"name": name, "sessions": 1}, config=runtime.execution_config(),
        )


def test_solution_checks_all_cases_and_is_independent(tmp_path):
    summary = solution.run_demo(workdir=tmp_path)
    assert summary["negative_sessions_rejected"] is True
    assert summary["inputs_unchanged"] is True
    assert len(summary["badges"]) == 3
    json.dumps(summary)
    assert list(tmp_path.iterdir()) == []
    assert "course_lessons" not in Path(solution.__file__).read_text()


@pytest.mark.parametrize("module", [demo, solution])
def test_cli_defaults_to_offline_without_settings(module, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["l01", "--output-dir", str(tmp_path)])
    runtime.run_cli("L01", module.run_demo)
    printed = json.loads(capsys.readouterr().out)
    assert printed["status"] == "passed"
    assert printed["backend"] == "none"
    assert printed["live_api_enabled"] is False
    assert printed["result"]["mode"] == "deterministic_no_model"


def test_starter_is_honestly_incomplete(capsys):
    with pytest.raises(NotImplementedError, match="TODO 3"):
        starter.check_work()
    runpy.run_path(starter.__file__, run_name="__main__")
    printed = capsys.readouterr().out
    assert "STARTER_NOT_COMPLETED" in printed
    assert "STARTER_CHECKS_PASSED" not in printed
    source = Path(starter.__file__).read_text()
    assert "exercises.solutions" not in source
    assert "course_lessons" not in source


def test_starter_checks_accept_the_reference_implementation(monkeypatch):
    # Exercise the starter's checking harness; do not modify the on-disk starter.
    monkeypatch.setattr(starter, "build_graph", solution.build_graph)
    monkeypatch.setattr(starter, "normalize_name", solution.normalize_name)
    assert starter.check_work() == {
        "status": "STARTER_CHECKS_PASSED", "checked_cases": 3,
    }
