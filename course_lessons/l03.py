"""L03 baseline: several input fields, one sum-processing node, no model."""
from pathlib import Path
from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config, run_cli


class SumState(TypedDict):
    """Inputs are required; derived outputs are absent until processing."""

    values: list[int]
    name: str
    total: NotRequired[int]
    result: NotRequired[str]


class SumUpdate(TypedDict):
    """The node returns only the fields it computes."""

    total: int
    result: str


def process_values(state: SumState) -> SumUpdate:
    """Validate inputs and return a sum without mutating the input dictionary."""
    values = state.get("values")
    name = state.get("name")
    if not isinstance(values, list) or any(type(item) is not int for item in values):
        raise ValueError("values must be a list of integers, not booleans")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a nonblank string")
    total = sum(values)
    return {"total": total, "result": f"Hi there {name}! Your sum = {total}."}


def build_graph():
    """Compile the START -> processor -> END topology."""
    builder = StateGraph(SumState)
    builder.add_node("processor", process_values)
    builder.add_edge(START, "processor")
    builder.add_edge("processor", END)
    return builder.compile()


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Check deterministic behavior; live/workdir are shared runtime arguments."""
    graph = build_graph()
    initial: SumState = {"values": [1, 2, 3, 4], "name": "Steve"}
    before = {"values": initial["values"].copy(), "name": initial["name"]}
    update = process_values(initial)
    assert update == {"total": 10, "result": "Hi there Steve! Your sum = 10."}
    assert initial == before
    answer = graph.invoke(initial, config=execution_config())
    assert answer == {**before, **update}
    empty = graph.invoke({"values": [], "name": "Ari"}, config=execution_config())
    assert empty["total"] == 0
    signed = graph.invoke(
        {"values": [-3, 0, 5], "name": "Mei"}, config=execution_config()
    )
    assert signed["total"] == 2
    assert initial == before
    return {
        "node": "processor",
        "input": before,
        "node_update": update,
        "final_state": answer,
        "selected_result": answer["result"],
        "empty_sum": empty["total"],
        "signed_sum": signed["total"],
        "inputs_unchanged": initial == before,
        "model_used": False,
    }


if __name__ == "__main__":
    run_cli("L03", run_demo)
