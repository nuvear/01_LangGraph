"""L06 starter: implement the three TODO functions, then run this module.

Run from the repository root: python -m exercises.starters.l06
No solution imports, model calls, input prompts, or credential access are needed.
"""
from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langsmith import tracing_context

from course_support.runtime import execution_config


class GameState(TypedDict):
    player_name: str
    target: int
    max_attempts: int
    lower: int
    upper: int
    guesses: list[int]
    attempts: int
    hint: Literal["", "higher", "lower", "correct"]
    status: Literal["playing", "won", "lost"]


def new_game(
    target: int, *, max_attempts: int = 7, player_name: str = "Student"
) -> GameState:
    return {
        "player_name": player_name,
        "target": target,
        "max_attempts": max_attempts,
        "lower": 1,
        "upper": 20,
        "guesses": [],
        "attempts": 0,
        "hint": "",
        "status": "playing",
    }


def reset_game(state: GameState) -> dict:
    """TODO 1: validate configuration and reset all derived game fields.

    Reject target outside integer 1..20, budget outside integer 1..7, and a blank
    or non-string player name. Reject bool for target/budget. Return bounds 1/20,
    empty guesses, attempts 0, hint '', and status 'playing'. Preserve config.
    """
    raise NotImplementedError("TODO 1: implement reset_game")


def guess_node(state: GameState) -> dict:
    """TODO 2: choose a midpoint without consulting target.

    Return a new guesses list with the integer midpoint appended and attempts
    increased by one. Do not mutate the incoming list or adjust bounds here.
    """
    raise NotImplementedError("TODO 2: implement guess_node")


def feedback_node(state: GameState) -> dict:
    """TODO 3: compare the latest guess, update hint/bounds/status.

    Equality -> correct/won, including on the last allowed guess. A miss ->
    higher and lower=guess+1 OR lower and upper=guess-1. After a miss, status is
    lost if attempts >= max_attempts, otherwise playing. Return partial updates.
    """
    raise NotImplementedError("TODO 3: implement feedback_node")


def game_route(state: GameState) -> Literal["again", "stop"]:
    return "again" if state["status"] == "playing" else "stop"


def build_graph():
    builder = StateGraph(GameState)
    builder.add_node("reset", reset_game)
    builder.add_node("guess", guess_node)
    builder.add_node("feedback", feedback_node)
    builder.add_edge(START, "reset")
    builder.add_edge("reset", "guess")
    builder.add_edge("guess", "feedback")
    builder.add_conditional_edges(
        "feedback", game_route, {"again": "guess", "stop": END}
    )
    return builder.compile()


def check_work() -> dict:
    """Starter self-checks become meaningful only after all TODOs are done."""
    graph = build_graph()
    success = graph.invoke(new_game(17), config=execution_config())
    exhausted = graph.invoke(
        new_game(20, max_attempts=2), config=execution_config()
    )
    final_attempt = graph.invoke(
        new_game(15, max_attempts=2), config=execution_config()
    )
    assert success["guesses"] == [10, 15, 18, 16, 17]
    assert success["status"] == "won" and success["attempts"] == 5
    assert exhausted["guesses"] == [10, 15]
    assert exhausted["status"] == "lost" and exhausted["attempts"] == 2
    assert exhausted["hint"] == "higher"
    assert final_attempt["status"] == "won"
    for target in range(1, 21):
        result = graph.invoke(new_game(target), config=execution_config())
        assert result["status"] == "won"
        assert result["attempts"] == len(result["guesses"]) <= 7
    dirty = new_game(10)
    dirty.update(lower=-9, upper=99, guesses=[999], attempts=-8, status="lost")
    clean = graph.invoke(dirty, config=execution_config())
    assert clean["guesses"] == [10] and clean["attempts"] == 1
    assert dirty["guesses"] == [999]
    for target, budget in ((0, 7), (21, 7), (True, 7), (10, 0), (10, 8)):
        try:
            graph.invoke(
                new_game(target, max_attempts=budget), config=execution_config()
            )
        except ValueError:
            continue
        raise AssertionError("Invalid configuration must raise ValueError")
    return {"success_guesses": success["guesses"], "targets_checked": 20}


def main() -> None:
    import json

    # Explicitly disable ambient tracing; the starter never loads .env.
    with tracing_context(enabled=False):
        try:
            result = check_work()
        except NotImplementedError as error:
            print(f"STARTER_NOT_COMPLETED: {error}")
            return
    print(json.dumps({"status": "STARTER_CHECKS_PASSED", "result": result}))


if __name__ == "__main__":
    main()
