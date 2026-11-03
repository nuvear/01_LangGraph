"""S1: observe a synthetic seat quote; evaluate actual model receipts locally.

Run: python -m course_lessons.s1 --live
The shared CLI selects LangSmith unless --backend none is explicitly requested.
Offline tests inject named test doubles; this CLI never substitutes a fake model.
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
    execution_config,
    get_model,
    message_text,
    output_directory,
    run_cli,
    safe_write_text,
)

MAX_ATTEMPTS = 2
SOURCE = "seat-policy-v1"
EXAMPLES = (
    {"id": "basic-three", "inputs": {"plan": "basic", "seats": 3},
     "reference_outputs": {"total": 12, "source": SOURCE}},
    {"id": "team-two", "inputs": {"plan": "team", "seats": 2},
     "reference_outputs": {"total": 14, "source": SOURCE}},
    {"id": "basic-one", "inputs": {"plan": "basic", "seats": 1},
     "reference_outputs": {"total": 4, "source": SOURCE}},
)


class QuoteState(TypedDict):
    plan: str
    seats: int
    tool_result: dict
    raw: str
    receipt: dict
    format_ok: bool
    attempts: int
    trace_log: list[str]


@tool
def seat_quote(plan: str, seats: int) -> dict:
    """Compute synthetic credit totals from seat-policy-v1, not real prices."""
    rates = {"basic": 4, "team": 7}
    if plan not in rates:
        raise ValueError("Unsupported synthetic plan.")
    if type(seats) is not int or not 1 <= seats <= 10:
        raise ValueError("Seats must be an integer from 1 through 10.")
    return {"total": rates[plan] * seats, "unit": "credits", "source": SOURCE}


def parse_receipt(text: str) -> dict:
    """Accept one strict JSON object, not Markdown or bool-as-integer totals."""
    try:
        receipt = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {}
    if not isinstance(receipt, dict):
        return {}
    if set(receipt) != {"total", "unit", "source"}:
        return {}
    if type(receipt["total"]) is not int or receipt["unit"] != "credits":
        return {}
    if not isinstance(receipt["source"], str) or not receipt["source"].strip():
        return {}
    return receipt


def build_graph(model: Any):
    """Inject a real chat model, or an explicit offline test double."""
    def quote(state: QuoteState, config: RunnableConfig) -> dict:
        # Tool schemas may coerce numbers; validate the original state first.
        if type(state["seats"]) is not int:
            raise ValueError("Seats must be an integer from 1 through 10.")
        result = seat_quote.invoke(
            {"plan": state["plan"], "seats": state["seats"]}, config=config
        )
        return {"tool_result": result, "trace_log": ["quote"]}

    def format_receipt(state: QuoteState, config: RunnableConfig) -> dict:
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

    def check(state: QuoteState) -> dict:
        receipt = parse_receipt(state["raw"])
        return {"receipt": receipt, "format_ok": bool(receipt),
                "trace_log": state["trace_log"] + ["check"]}

    def route(state: QuoteState) -> str:
        if not state["format_ok"] and state["attempts"] < MAX_ATTEMPTS:
            return "retry"
        return "finish"

    builder = StateGraph(QuoteState)
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


def evaluate_receipt(outputs: dict, reference_outputs: dict) -> dict[str, bool]:
    """Score actual model output, not merely the tool's correct calculation."""
    receipt = parse_receipt(outputs.get("raw", ""))
    attempts = outputs.get("attempts", 0)
    return {
        "schema_ok": bool(receipt),
        "amount_ok": receipt.get("total") == reference_outputs["total"],
        "source_ok": receipt.get("source") == reference_outputs["source"],
        "bounded_attempts": type(attempts) is int and 1 <= attempts <= MAX_ATTEMPTS,
        "tool_evidence": outputs.get("tool_result", {}).get("source") == SOURCE
        and outputs.get("trace_log", []).count("quote") == 1,
    }


def run_evaluation(model: Any, *, workdir: Path | None = None) -> dict:
    """Run three examples sequentially; persist diagnostics before asserting."""
    graph = build_graph(model)
    rows = []
    for example in EXAMPLES:
        run_id = uuid4()
        started_at = datetime.now(timezone.utc).isoformat()
        config = execution_config()
        config.update(run_id=run_id, run_name=f"S1 demo {example['id']}")
        config["metadata"] = {
            **config.get("metadata", {}), "lesson": "S1", "variant": "demo",
            "case_id": example["id"], "synthetic": True,
        }
        start = perf_counter()
        outputs = graph.invoke(
            {**example["inputs"], "attempts": 0, "trace_log": []}, config=config
        )
        elapsed_ms = round((perf_counter() - start) * 1000, 2)
        checks = evaluate_receipt(outputs, example["reference_outputs"])
        rows.append({
            "id": example["id"], "run_id": str(run_id),
            "started_at": started_at, "elapsed_ms": elapsed_ms,
            "checks": checks, "passed": all(checks.values()),
            "attempts": outputs["attempts"], "path": outputs["trace_log"],
            "raw": outputs["raw"],
        })
    report = {"dataset": "s1-seat-v1", "examples": len(rows),
              "passed": sum(row["passed"] for row in rows), "rows": rows,
              "langsmith_experiment_created": False,
              "dashboard_visually_verified": False}
    directory = output_directory(workdir, "S1")
    path = safe_write_text(
        directory, "s1-demo-evaluation.txt", json.dumps(report, indent=2) + "\n"
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


if __name__ == "__main__":
    run_cli("S1", run_demo)
