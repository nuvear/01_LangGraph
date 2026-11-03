"""L06 workbook solution: automatic midpoint guessing with bounded routing.

Run: python -m exercises.solutions.l06 --backend none
This is independent of course_lessons.l06 and requires no language model.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config, run_cli


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
    """Create a complete input state; reset_game validates it before guessing."""
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
    """Validate configuration and reset all derived game fields."""
    if type(state["target"]) is not int or not 1 <= state["target"] <= 20:
        raise ValueError("target must be an integer from 1 to 20")
    budget = state["max_attempts"]
    if type(budget) is not int or not 1 <= budget <= 7:
        raise ValueError("max_attempts must be an integer from 1 to 7")
    name = state["player_name"]
    if not isinstance(name, str) or not name.strip():
        raise ValueError("player_name must be a nonblank string")
    return {
        "lower": 1,
        "upper": 20,
        "guesses": [],
        "attempts": 0,
        "hint": "",
        "status": "playing",
    }


def guess_node(state: GameState) -> dict:
    """Choose only from bounds; do not read the target to choose a guess."""
    guess = (state["lower"] + state["upper"]) // 2
    return {
        "guesses": [*state["guesses"], guess],
        "attempts": state["attempts"] + 1,
    }


def feedback_node(state: GameState) -> dict:
    """Compare the last guess; exclude a miss and classify termination."""
    guess = state["guesses"][-1]
    if guess == state["target"]:
        # Success wins even when this was the final permitted attempt.
        return {"hint": "correct", "status": "won"}
    if guess < state["target"]:
        update = {"hint": "higher", "lower": guess + 1}
    else:
        update = {"hint": "lower", "upper": guess - 1}
    update["status"] = (
        "lost" if state["attempts"] >= state["max_attempts"] else "playing"
    )
    return update


def game_route(state: GameState) -> Literal["again", "stop"]:
    """Return a path-map label, never a state-update dictionary."""
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


def play_game(
    target: int, *, max_attempts: int = 7, player_name: str = "Student"
) -> dict:
    """Run a fresh automatic game using the shared bounded invocation config."""
    return build_graph().invoke(
        new_game(target, max_attempts=max_attempts, player_name=player_name),
        config=execution_config(),
    )


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Verify both normal exit reasons and the whole allowed target interval."""
    graph = build_graph()
    success = graph.invoke(new_game(17), config=execution_config())
    exhausted = graph.invoke(
        new_game(20, max_attempts=2), config=execution_config()
    )
    final_attempt = graph.invoke(
        new_game(15, max_attempts=2), config=execution_config()
    )
    all_results = [
        graph.invoke(new_game(target), config=execution_config())
        for target in range(1, 21)
    ]
    assert success["guesses"] == [10, 15, 18, 16, 17]
    assert success["attempts"] == 5 and success["status"] == "won"
    assert success["hint"] == "correct"
    assert exhausted["guesses"] == [10, 15]
    assert exhausted["attempts"] == 2 and exhausted["status"] == "lost"
    assert exhausted["hint"] == "higher"
    assert final_attempt["status"] == "won"
    assert final_attempt["attempts"] == 2
    assert all(result["status"] == "won" for result in all_results)
    assert all(1 <= result["attempts"] <= 7 for result in all_results)
    assert all(
        result["attempts"] == len(result["guesses"])
        for result in all_results
    )
    return {
        "success": {
            key: success[key] for key in ("target", "guesses", "attempts", "status")
        },
        "exhausted": {
            key: exhausted[key]
            for key in ("target", "guesses", "attempts", "status", "hint")
        },
        "success_on_final_attempt": final_attempt["status"],
        "targets_checked": len(all_results),
        "max_attempts_observed": max(result["attempts"] for result in all_results),
        "model_used": False,
    }


if __name__ == "__main__":
    run_cli("L06", run_demo)
