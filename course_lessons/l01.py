"""L01: Python type hints and a deterministic two-node graph; no model calls."""
from __future__ import annotations

from pathlib import Path
from typing import Any, NotRequired, Optional, TypedDict, Union

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config, run_cli


class MovieState(TypedDict):
    """Inputs are title/year; the graph adds a card without requiring it at input."""

    title: str
    year: int
    card: NotRequired[str]


class TitleUpdate(TypedDict):
    title: str


class CardUpdate(TypedDict):
    card: str


def square(value: Union[int, float]) -> Union[int, float]:
    """Union[int, float] can also be written int | float on Python 3.12."""
    return value * value


def greet(name: Optional[str] = None) -> str:
    """Optional[str] means str | None; the default is separately specified."""
    return f"Hello, {name}!" if name is not None else "Hello, visitor!"


def echo(value: Any) -> Any:
    """Any relaxes static checking; it does not validate or convert the value."""
    return value


def normalize_title(state: MovieState) -> TitleUpdate:
    """Validate a boundary value and return only the changed field."""
    title = state["title"]
    if not isinstance(title, str):
        raise TypeError("title must be a string")
    clean = title.strip()
    if not clean:
        raise ValueError("title must not be blank")
    return {"title": clean}


def describe_movie(state: MovieState) -> CardUpdate:
    """Keep year/title in accumulated state without returning them again."""
    year = state["year"]
    # bool is a subclass of int, so an exact check excludes True and False.
    if type(year) is not int:
        raise TypeError("year must be an integer, not a boolean")
    return {"card": f"{state['title']} ({year})"}


def build_graph():
    """A builder describes topology; compile returns the executable runnable."""
    builder = StateGraph(MovieState)
    builder.add_node("normalize_title", normalize_title)
    builder.add_node("describe_movie", describe_movie)
    builder.add_edge(START, "normalize_title")
    builder.add_edge("normalize_title", "describe_movie")
    builder.add_edge("describe_movie", END)
    return builder.compile()


def message_examples() -> list:
    """Manually authored message objects, NOT responses from a live model."""
    return [
        SystemMessage(content="Use the supplied synthetic movie data."),
        HumanMessage(content="Square 3."),
        AIMessage(
            content="",
            tool_calls=[{
                "name": "square", "args": {"value": 3},
                "id": "l01-square-1", "type": "tool_call",
            }],
        ),
        ToolMessage(content="9", tool_call_id="l01-square-1"),
    ]


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Check real local graph behavior; live/workdir are shared CLI parameters."""
    original: MovieState = {"title": "  The Clockwork Garden  ", "year": 2025}
    graph = build_graph()
    result = graph.invoke(original, config=execution_config())
    assert result == {
        "title": "The Clockwork Garden", "year": 2025,
        "card": "The Clockwork Garden (2025)",
    }
    assert original == {"title": "  The Clockwork Garden  ", "year": 2025}
    squares = list(map(lambda number: number * number, [1, 2, 3, 4]))
    assert squares == [1, 4, 9, 16]
    assert square(2.5) == 6.25 and square(3) == 9
    assert greet(None) == "Hello, visitor!" and greet("Ada") == "Hello, Ada!"
    sample = {"tags": ["synthetic"]}
    assert echo(sample) is sample
    messages = message_examples()
    assert messages[2].tool_calls[0]["id"] == messages[3].tool_call_id
    assert [message.type for message in messages] == ["system", "human", "ai", "tool"]
    return {
        "mode": "deterministic_no_model", "movie": result,
        "squares": squares, "numeric_square": square(2.5),
        "fallback_greeting": greet(None),
        "message_roles": [message.type for message in messages],
        "message_objects_are_hand_authored": True,
        "tool_call_id_matches": True, "input_unchanged": True,
    }


if __name__ == "__main__":
    run_cli("L01", run_demo)
