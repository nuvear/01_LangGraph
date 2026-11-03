"""Focused L06 offline tests: real local graphs, no model or service calls."""
from __future__ import annotations

from copy import deepcopy
import json
import socket

from langgraph.errors import GraphRecursionError
from langsmith import tracing_context
import pytest

from course_lessons import l06 as demo
from exercises.solutions import l06 as solution
from course_support import check_connections, observability, runtime


def deny_network(*args, **kwargs):
    raise AssertionError("L06 offline tests must not open a network connection")


def deny_settings(*args, **kwargs):
    raise AssertionError("L06 offline tests must not load configuration or .env")


def deny_model(*args, **kwargs):
    raise AssertionError("L06 is deterministic and must not construct a model")


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    """Fail closed on accidental settings, model, or socket access."""
    monkeypatch.setattr(socket.socket, "connect", deny_network)
    monkeypatch.setattr(socket.socket, "connect_ex", deny_network)
    monkeypatch.setattr(socket, "create_connection", deny_network)
    monkeypatch.setattr(check_connections, "dotenv_values", deny_settings)
    monkeypatch.setattr(check_connections, "values", deny_settings)
    monkeypatch.setattr(observability, "values", deny_settings)
    monkeypatch.setattr(runtime, "values", deny_settings)
    monkeypatch.setattr(runtime, "get_model", deny_model)
    with tracing_context(enabled=False):
        yield


def test_demo_summary_checks_actual_repeatable_runs(tmp_path):
    result = demo.run_demo(workdir=tmp_path)
    assert result["counter"] == len(result["numbers"]) == 5
    assert result["repeatable"] and result["stale_state_reset"]
    assert result["model_used"] is False
    json.dumps(result)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("counter", [-99, 0, 5, 100])
def test_demo_resets_stale_state_without_mutating_input(counter):
    graph = demo.build_graph()
    initial = {"name": "Ada", "numbers": [999], "counter": counter}
    snapshot = deepcopy(initial)
    result = graph.invoke(initial, config=runtime.execution_config())
    assert initial == snapshot
    assert result["name"] == "Ada"
    assert result["greeting"] == "Hi there, Ada!"
    assert result["counter"] == len(result["numbers"]) == 5
    assert all(0 <= number <= 10 for number in result["numbers"])


def test_demo_stream_shows_five_generation_updates():
    updates = list(
        demo.build_graph().stream(
            {"name": "Student", "numbers": [], "counter": -1},
            config=runtime.execution_config(),
            stream_mode="updates",
        )
    )
    assert [next(iter(update)) for update in updates] == ["greeting"] + [
        "generate"
    ] * 5
    counters = [update["generate"]["counter"] for update in updates[1:]]
    assert counters == [1, 2, 3, 4, 5]


def test_demo_repeated_invocation_has_no_shared_rng_or_list_state():
    graph = demo.build_graph(seed=31)
    state = {"name": "Ada", "numbers": [], "counter": 0}
    first = graph.invoke(state, config=runtime.execution_config())
    expected = first["numbers"].copy()
    first["numbers"].append(999)
    second = graph.invoke(state, config=runtime.execution_config())
    assert second["numbers"] == expected


@pytest.mark.parametrize("name", ["", "   ", None, 42])
def test_demo_rejects_invalid_names(name):
    with pytest.raises(ValueError, match="name"):
        demo.build_graph().invoke(
            {"name": name, "numbers": [], "counter": 0},
            config=runtime.execution_config(),
        )


@pytest.mark.parametrize("seed", [True, "23", 2.5])
def test_demo_rejects_noninteger_seed(seed):
    with pytest.raises(ValueError, match="seed"):
        demo.build_graph(seed=seed)


def test_route_labels_are_separate_from_updates():
    assert demo.loop_route({"counter": 4}) == "again"
    assert demo.loop_route({"counter": 5}) == "done"
    assert solution.game_route({"status": "playing"}) == "again"
    assert solution.game_route({"status": "won"}) == "stop"
    assert solution.game_route({"status": "lost"}) == "stop"


@pytest.mark.parametrize("target", range(1, 21))
def test_every_valid_target_succeeds_within_seven_and_bounds_narrow(target):
    initial = solution.new_game(target)
    snapshot = deepcopy(initial)
    state = deepcopy(initial)
    previous_guess = None
    visits = 0
    updates = solution.build_graph().stream(
        initial, config=runtime.execution_config(), stream_mode="updates"
    )
    for update in updates:
        if "guess" in update:
            old_lower, old_upper = state["lower"], state["upper"]
            patch = update["guess"]
            assert patch["guesses"][-1] == (old_lower + old_upper) // 2
            assert old_lower <= patch["guesses"][-1] <= old_upper
            previous_guess = patch["guesses"][-1]
            visits += 1
        if "feedback" in update:
            old_width = state["upper"] - state["lower"]
            state.update(update["feedback"])
            assert state["lower"] <= target <= state["upper"]
            if state["hint"] != "correct":
                assert state["upper"] - state["lower"] < old_width
                assert not state["lower"] <= previous_guess <= state["upper"]
        else:
            for patch in update.values():
                state.update(patch)
    assert initial == snapshot
    assert state["status"] == "won" and state["hint"] == "correct"
    assert state["guesses"][-1] == target
    assert 1 <= state["attempts"] == len(state["guesses"]) == visits <= 7
    assert len(state["guesses"]) == len(set(state["guesses"]))


def test_workbook_success_sequence_and_ordinary_exhaustion():
    success = solution.play_game(17)
    lost = solution.play_game(20, max_attempts=2)
    assert success["guesses"] == [10, 15, 18, 16, 17]
    assert success["status"] == "won" and success["attempts"] == 5
    assert lost["guesses"] == [10, 15]
    assert lost["lower"] == 16 and lost["upper"] == 20
    assert lost["hint"] == "higher" and lost["status"] == "lost"
    assert lost["attempts"] == 2


@pytest.mark.parametrize("target,budget", [(10, 1), (15, 2), (17, 5)])
def test_success_on_last_allowed_attempt_has_priority(target, budget):
    result = solution.play_game(target, max_attempts=budget)
    assert result["status"] == "won" and result["hint"] == "correct"
    assert result["attempts"] == budget


@pytest.mark.parametrize("target", [1, 20])
def test_one_guess_budget_has_honest_lost_status(target):
    result = solution.play_game(target, max_attempts=1)
    assert result["status"] == "lost"
    assert result["guesses"] == [10] and result["attempts"] == 1
    assert result["hint"] == ("lower" if target == 1 else "higher")


def test_game_resets_every_derived_field_and_preserves_configuration():
    graph = solution.build_graph()
    initial = solution.new_game(10, player_name="Grace")
    initial.update(
        lower=-100, upper=100, guesses=[99], attempts=-9,
        hint="lower", status="lost"
    )
    snapshot = deepcopy(initial)
    result = graph.invoke(initial, config=runtime.execution_config())
    assert initial == snapshot
    assert result["guesses"] == [10] and result["attempts"] == 1
    assert result["lower"] == 1 and result["upper"] == 20
    assert result["target"] == 10 and result["max_attempts"] == 7
    assert result["player_name"] == "Grace" and result["status"] == "won"


@pytest.mark.parametrize("target", [0, 21, -1, True, 1.5, "10", None])
def test_game_rejects_invalid_target(target):
    with pytest.raises(ValueError, match="target"):
        solution.play_game(target)


@pytest.mark.parametrize("budget", [0, 8, -1, True, 2.5, "7", None])
def test_game_rejects_invalid_attempt_budget(budget):
    with pytest.raises(ValueError, match="max_attempts"):
        solution.play_game(10, max_attempts=budget)


@pytest.mark.parametrize("name", ["", " \t", None, 7])
def test_game_rejects_invalid_player_name(name):
    with pytest.raises(ValueError, match="player_name"):
        solution.play_game(10, player_name=name)


def test_guess_node_does_not_mutate_input_or_consult_target():
    left = solution.new_game(1)
    right = solution.new_game(20)
    before = deepcopy(left)
    assert solution.guess_node(left) == solution.guess_node(right)
    assert left == before


def test_low_recursion_limit_is_an_error_not_a_game_loss():
    config = {**runtime.execution_config(), "recursion_limit": 2}
    with pytest.raises(GraphRecursionError):
        solution.build_graph().invoke(solution.new_game(17), config=config)


def test_solution_summary_checks_both_paths_and_all_targets(tmp_path):
    result = solution.run_demo(workdir=tmp_path)
    assert result["targets_checked"] == 20
    assert result["success"]["status"] == "won"
    assert result["exhausted"]["status"] == "lost"
    assert result["success_on_final_attempt"] == "won"
    assert result["max_attempts_observed"] <= 7
    assert result["model_used"] is False
    json.dumps(result)
    assert list(tmp_path.iterdir()) == []
