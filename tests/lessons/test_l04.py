"""Focused L04 tests. No model doubles: this lesson has no model at all."""
from copy import deepcopy
import json
import socket

from langsmith import tracing_context
import pytest

from course_lessons import l04 as demo
from course_support import check_connections, observability, runtime
from exercises.solutions import l04 as solution
from exercises.starters import l04 as starter


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    """Reject network and configuration access, including accidental .env reads."""
    def forbidden(*args, **kwargs):
        raise AssertionError("L04 must not use network, credentials, or models")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden)
    monkeypatch.setattr(check_connections, "dotenv_values", forbidden)
    monkeypatch.setattr(check_connections, "values", forbidden)
    monkeypatch.setattr(observability, "values", forbidden)
    monkeypatch.setattr(runtime, "values", forbidden)
    monkeypatch.setattr(runtime, "get_model", forbidden)
    with tracing_context(enabled=False):
        yield


def invoke(graph, initial):
    return graph.invoke(initial, config=runtime.execution_config())


@pytest.mark.parametrize("module", [demo, solution])
def test_run_demo_checks_real_graph_and_returns_json(module, tmp_path):
    summary = module.run_demo(workdir=tmp_path)
    assert summary["model_calls"] == 0
    assert summary["inputs_unchanged"] is True
    assert json.loads(json.dumps(summary)) == summary
    assert not list(tmp_path.iterdir())


def test_deliberate_overwrite_is_not_fixed_by_edges():
    initial = demo.make_input("Charlie", 20)
    broken = invoke(demo.build_graph(demonstrate_overwrite=True), initial)
    fixed = invoke(demo.build_graph(), initial)
    assert broken["final"] == "You are 20 years old."
    assert fixed["final"] == "Hi Charlie. You are 20 years old."
    assert broken["visited"] == fixed["visited"] == ["greet", "age"]
    assert initial == {"name": "Charlie", "age": 20}


def test_demo_stream_updates_are_not_whole_state():
    graph = demo.build_graph()
    updates = list(graph.stream(
        demo.make_input("Charlie", 20), config=runtime.execution_config(),
        stream_mode="updates",
    ))
    assert [next(iter(item)) for item in updates] == ["greet", "age"]
    assert updates[0]["greet"] == {
        "final": "Hi Charlie.", "visited": ["greet"]
    }
    assert "name" not in updates[-1]["age"]
    assert updates[-1]["age"]["final"] == "Hi Charlie. You are 20 years old."


@pytest.mark.parametrize("age, unit", [(0, "years"), (1, "year"), (99, "years")])
def test_demo_age_boundaries(age, unit):
    final = invoke(demo.build_graph(), demo.make_input("Ren", age))
    assert final["final"] == f"Hi Ren. You are {age} {unit} old."


@pytest.mark.parametrize(
    "name, age, skills, expected",
    [
        ("Linda", 31, ["Python", "machine learning", "LangGraph"],
         "Linda welcome to the system. You are 31 years old and you have "
         "skills in Python, machine learning and LangGraph."),
        ("Ari", 0, [],
         "Ari welcome to the system. You are 0 years old and you have no "
         "listed skills."),
        ("Jo", 1, ["Python"],
         "Jo welcome to the system. You are 1 year old and you have skills "
         "in Python."),
        ("Bo", 2, ["Python", "SQL"],
         "Bo welcome to the system. You are 2 years old and you have skills "
         "in Python and SQL."),
        ("美咲", 40, ["SQL", "Python", "SQL", "testing"],
         "美咲 welcome to the system. You are 40 years old and you have skills "
         "in SQL, Python, SQL and testing."),
    ],
)
def test_solution_profile_cases_and_input_preservation(name, age, skills, expected):
    initial = solution.make_input(name, age, skills)
    before = deepcopy(initial)
    final = invoke(solution.build_graph(), initial)
    assert final["result"] == expected
    assert final["visited"] == ["welcome", "age", "skills"]
    assert initial == before
    assert {key: final[key] for key in before} == before
    assert initial["skills"] is not skills


def test_three_node_topology_has_only_four_required_edges():
    edges = solution.build_graph().get_graph().edges
    assert {(edge.source, edge.target) for edge in edges} == {
        ("__start__", "welcome"), ("welcome", "age"),
        ("age", "skills"), ("skills", "__end__"),
    }


def test_solution_partial_updates_and_nodes_do_not_mutate_state():
    state = solution.make_input("Linda", 31, ["Python", "SQL"])
    for node in (solution.welcome, solution.describe_age, solution.describe_skills):
        before = deepcopy(state)
        update = node(state)
        assert set(update) == {"result", "visited"}
        assert state == before
        state = {**state, **update}
    assert state["visited"] == ["welcome", "age", "skills"]
    assert state["result"].endswith("skills in Python and SQL.")


def test_reusing_compiled_graph_does_not_accumulate_another_profile():
    graph = solution.build_graph()
    first = solution.make_input("Linda", 31, ["Python"])
    stale = invoke(graph, first)
    again = invoke(graph, stale)
    assert again == stale  # welcome resets generated fields on each invocation
    second = invoke(graph, solution.make_input("Ari", 0, []))
    assert "Linda" not in second["result"]
    assert "Python" not in second["result"]
    assert second["visited"] == ["welcome", "age", "skills"]


@pytest.mark.parametrize("name", ["", "   ", None, 7])
@pytest.mark.parametrize("module", [demo, solution, starter])
def test_invalid_names_rejected(module, name):
    with pytest.raises(ValueError, match="name"):
        if module is demo:
            module.make_input(name, 20)
        else:
            module.make_input(name, 20, [])


@pytest.mark.parametrize("age", [-1, "31", 3.5, True, None])
@pytest.mark.parametrize("module", [demo, solution, starter])
def test_invalid_ages_rejected(module, age):
    with pytest.raises(ValueError, match="age"):
        if module is demo:
            module.make_input("Linda", age)
        else:
            module.make_input("Linda", age, [])


@pytest.mark.parametrize("skills", ["Python", ("Python",), [""], [" "], [1]])
@pytest.mark.parametrize("module", [solution, starter])
def test_invalid_skill_collections_rejected(module, skills):
    with pytest.raises(ValueError, match="skills"):
        module.make_input("Linda", 31, skills)


def test_unfinished_starter_exits_honestly(capsys):
    starter.main()
    output = capsys.readouterr().out
    assert "STARTER_NOT_COMPLETED" in output
    assert "STARTER_CHECKS_PASSED" not in output


def test_starter_scaffold_accepts_correct_node_implementations(monkeypatch, capsys):
    # Named real deterministic functions, not fake LLM behavior. This tests the
    # supplied scaffold; the unmodified learner TODOs remain unfinished.
    monkeypatch.setattr(starter, "welcome", solution.welcome)
    monkeypatch.setattr(starter, "describe_age", solution.describe_age)
    monkeypatch.setattr(starter, "describe_skills", solution.describe_skills)
    starter.main()
    output = capsys.readouterr().out
    assert "STARTER_CHECKS_PASSED" in output
    assert "STARTER_NOT_COMPLETED" not in output
