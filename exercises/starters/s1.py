"""S1 learner starter: implement three TODOs; supplied plumbing is independent.

Initial command: python -m exercises.starters.s1
After completing TODOs: python -m exercises.starters.s1 --live
The initial incomplete run does not load configuration or contact any service.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from time import perf_counter
from typing import Any, TypedDict
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph

from course_support.runtime import (
    execution_config, get_model, message_text, output_directory,
    run_cli, safe_write_text,
)

SOURCE = "shipping-policy-v1"
MAX_ATTEMPTS = 2
EXAMPLES = (
    {"id": "local-two", "inputs": {"region": "local", "weight": 2},
     "reference_outputs": {"total": 7, "source": SOURCE}},
    {"id": "regional-three", "inputs": {"region": "regional", "weight": 3},
     "reference_outputs": {"total": 14, "source": SOURCE}},
    {"id": "local-one", "inputs": {"region": "local", "weight": 1},
     "reference_outputs": {"total": 5, "source": SOURCE}},
)


def shipping_quote(region: str, weight: int) -> dict:
    """TODO 1: local=3+2*kg, regional=5+3*kg, in synthetic credits.

    Return exactly total, unit='credits', source=SOURCE. Raise ValueError for an
    unsupported region or weight outside integer 1..10, including bool/float.
    """
    raise NotImplementedError("TODO 1: implement shipping_quote")


def decode_receipt(text: str) -> dict:
    """TODO 2: decode strict JSON; return {} if JSON/schema is invalid.

    Exactly total, unit, source are required. total must be an int, not bool;
    unit must be credits; source must be a nonblank string. No Markdown fences.
    Do not correct an amount or replace a source: correctness is graded later.
    """
    raise NotImplementedError("TODO 2: implement decode_receipt")


def evaluate_receipt(outputs: dict, reference_outputs: dict) -> dict[str, bool]:
    """TODO 3: return the workbook's five boolean metrics, not an overall guess.

    Read the actual outputs['raw'] with decode_receipt. Compare total and source
    to reference_outputs. Check attempts is an integer 1..MAX_ATTEMPTS. Check the
    tool_result source is SOURCE and trace_log contains quote exactly once.
    Metric names: schema_ok, amount_ok, source_ok, bounded_attempts, tool_evidence.
    Missing raw/tool evidence must fail the relevant checks, not crash.
    """
    raise NotImplementedError("TODO 3: implement evaluate_receipt")


@tool
def shipping_tool(region: str, weight: int) -> dict:
    """Calculate teaching-only shipping credits from shipping-policy-v1."""
    return shipping_quote(region, weight)


class ShippingState(TypedDict):
    region: str
    weight: int
    tool_result: dict
    raw: str
    receipt: dict
    format_ok: bool
    attempts: int
    trace_log: list[str]


def build_graph(model: Any):
    """Supplied: one tool invocation and a model/schema-check loop."""
    def quote(state: ShippingState, config: RunnableConfig) -> dict:
        # Validate raw state before a tool schema can coerce bool/float to int.
        if type(state["weight"]) is not int:
            raise ValueError("Weight must be an integer from 1 through 10.")
        result = shipping_tool.invoke(
            {"region": state["region"], "weight": state["weight"]}, config=config
        )
        return {"tool_result": result, "trace_log": ["quote"]}

    def format_receipt(state: ShippingState, config: RunnableConfig) -> dict:
        instructions = (
            "Return ONLY a JSON object with exactly total, unit, source. "
            "Copy all three values from the synthetic tool result. "
            "total must be an integer; unit must be credits. No Markdown."
        )
        if state["attempts"]:
            instructions += " Your previous output failed JSON/schema validation."
        response = model.invoke(
            [SystemMessage(content=instructions),
             HumanMessage(content=json.dumps(state["tool_result"]))],
            config=config,
        )
        return {"raw": message_text(response),
                "attempts": state["attempts"] + 1,
                "trace_log": state["trace_log"] + ["format"]}

    def check(state: ShippingState) -> dict:
        receipt = decode_receipt(state["raw"])
        return {"receipt": receipt, "format_ok": bool(receipt),
                "trace_log": state["trace_log"] + ["check"]}

    def route(state: ShippingState) -> str:
        if not state["format_ok"] and state["attempts"] < MAX_ATTEMPTS:
            return "retry"
        return "finish"

    builder = StateGraph(ShippingState)
    builder.add_node("quote", quote)
    builder.add_node("format", format_receipt)
    builder.add_node("check", check)
    builder.add_edge(START, "quote")
    builder.add_edge("quote", "format")
    builder.add_edge("format", "check")
    builder.add_conditional_edges(
        "check", route, {"retry": "format", "finish": END}
    )
    return builder.compile()


def run_evaluation(model: Any, *, workdir: Path | None = None) -> dict:
    """Supplied: evaluate all cases, save a NEW report, then assert acceptance."""
    graph = build_graph(model)
    rows = []
    for example in EXAMPLES:
        run_id = uuid4()
        started_at = datetime.now(timezone.utc).isoformat()
        config = execution_config()
        config.update(run_id=run_id, run_name=f"S1 starter {example['id']}")
        config["metadata"] = {
            **config.get("metadata", {}), "lesson": "S1", "variant": "starter",
            "case_id": example["id"], "synthetic": True,
        }
        start = perf_counter()
        outputs = graph.invoke(
            {**example["inputs"], "attempts": 0, "trace_log": []}, config=config
        )
        checks = evaluate_receipt(outputs, example["reference_outputs"])
        rows.append({
            "id": example["id"], "run_id": str(run_id),
            "started_at": started_at,
            "elapsed_ms": round((perf_counter() - start) * 1000, 2),
            "checks": checks, "passed": all(checks.values()),
            "attempts": outputs["attempts"], "path": outputs["trace_log"],
            "raw": outputs["raw"],
        })
    report = {"dataset": "s1-shipping-v1", "examples": len(rows),
              "passed": sum(row["passed"] for row in rows), "rows": rows,
              "langsmith_experiment_created": False,
              "dashboard_visually_verified": False}
    directory = output_directory(workdir, "S1")
    path = safe_write_text(
        directory, "s1-starter-evaluation.txt", json.dumps(report, indent=2) + "\n"
    )
    assert report["examples"] == 3
    assert report["passed"] == 3, f"Evaluation failed; inspect {path}"
    calls = sum(row["attempts"] for row in rows)
    assert 3 <= calls <= 6
    return {"examples": 3, "passed": report["passed"], "model_calls": calls,
            "report_path": str(path), "langsmith_experiment_created": False,
            "dashboard_visually_verified": False}


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    model = get_model(live=live, max_tokens=192)
    return run_evaluation(model, workdir=workdir)


def main() -> None:
    # Readiness is not a passing evaluation. No service setup before TODO checks.
    try:
        shipping_quote("local", 1)
        decode_receipt('{"total":5,"unit":"credits","source":"example"}')
        evaluate_receipt({}, {"total": 5, "source": SOURCE})
    except NotImplementedError as exc:
        print(f"STARTER_NOT_COMPLETED: {exc}. See the S1 workbook.")
        return
    run_cli("S1", run_demo)


if __name__ == "__main__":
    main()
