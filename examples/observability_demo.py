"""Supplementary setup demo: a two-node graph with optional tracing.

Run from the repository root:
    python -m examples.observability_demo --backend none
    python -m examples.observability_demo --backend both
No language-model calls are made. Inputs are synthetic classroom data.
"""
from __future__ import annotations

import argparse
import json
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from course_support.observability import BACKENDS, graph_tracing


class DemoState(TypedDict):
    value: int
    result: int
    label: str


def increment(state: DemoState) -> dict[str, int]:
    return {"result": state["value"] + 1}


def label_result(state: DemoState) -> dict[str, str]:
    return {"label": f"Result: {state['result']}"}


def build_graph():
    builder = StateGraph(DemoState)
    builder.add_node("increment", increment)
    builder.add_node("label_result", label_result)
    builder.add_edge(START, "increment")
    builder.add_edge("increment", "label_result")
    builder.add_edge("label_result", END)
    return builder.compile()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=BACKENDS, default="none")
    args = parser.parse_args()
    with graph_tracing(args.backend, name="LangGraph Course Two-Node Demo") as config:
        result = build_graph().invoke({"value": 2}, config=config)
    assert result == {"value": 2, "result": 3, "label": "Result: 3"}
    print(json.dumps({"backend": args.backend, "graph_result": result, "assertions": "passed"}, indent=2))
    if args.backend != "none":
        print("Tracing callbacks completed; use the connection checks to verify server ingestion.")


if __name__ == "__main__":
    main()
