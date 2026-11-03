"""S2 starter: implement three functions, then enable the live runner.

Run safely now: python -m exercises.starters.s2
This starter does not import the solution, load configuration, or call a service.
Use the workbook for exact acceptance criteria and the demo for graph patterns.
"""
from __future__ import annotations

import json
import operator
from pathlib import Path
from typing import Annotated, TypedDict

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from course_support.runtime import (
    execution_config, get_model, message_text, output_directory, run_cli,
    safe_write_text,
)

DOCUMENT_ID = "TRACE-101"
DOCUMENT_TEXT = (
    "Flush drains pending export work. Check server acknowledgment separately; "
    "a flush does not prove dashboard visibility."
)


class HandoutRetriever(BaseRetriever):
    """An original synthetic exact-ID fixture, deliberately not vector RAG."""

    def _get_relevant_documents(self, query: str, *, run_manager) -> list[Document]:
        if query.strip().upper() != DOCUMENT_ID:
            return []
        return [Document(
            page_content=DOCUMENT_TEXT,
            metadata={"id": DOCUMENT_ID, "source": "synthetic-s2-handout", "page": 1},
        )]


class EvidenceState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    events: Annotated[list[str], operator.add]
    model_calls: int
    document_id: str
    evidence: dict
    answer: str
    status: str


def privacy_plan(backend: str) -> dict:
    # TODO 1: Map none/langsmith/langwatch/both to telemetry_recipients.
    # Return backend, telemetry_recipients, model_recipient, payload,
    # root_capture_is_child_redaction=False, and plan_only=True.
    # Unknown values must raise ValueError. --live still sends data to Anthropic.
    raise NotImplementedError("Implement privacy_plan from workbook step 1.")


def classify_ingestion(report: dict) -> dict:
    # TODO 2: Only acknowledge a LangWatch checker record if service=langwatch,
    # status=passed, http_status=200, ingestion_acknowledged is True, and
    # rejected_spans is the integer zero. All incomplete/failing cases remain
    # not_established. Never infer lesson trace ingestion or dashboard visibility.
    raise NotImplementedError("Implement classify_ingestion from workbook step 2.")


def build_graph(model):
    # TODO 3: Build the complete bounded graph; do not import the solution.
    # 1. Make HandoutRetriever; define @tool lookup_handout(document_id, config).
    #    Invoke retriever with config and return JSON {found, documents} where
    #    each document has id, source, page, text.
    # 2. Bind the first model call with tool_choice='lookup_handout' and
    #    parallel_tool_calls=False. Use the unbound model for the second call.
    # 3. Add prepare, agent, tools, finish nodes with partial state updates.
    #    prepare rejects blank IDs; agent permits <=2 model calls and rejects
    #    absent/multiple first calls or further second-turn tool requests.
    #    tools validates tool name and exact requested document_id; invoke the
    #    full tool-call dict with config to retain the ToolMessage call ID.
    #    finish requires nonempty text and sets supported/no_evidence using the
    #    retrieved documents, never guessed model wording.
    # 4. START -> prepare -> agent; route tools or finish; tools -> agent;
    #    finish -> END. Preserve callback configuration on nested invocations.
    #    Append events so a successful run records:
    #    ['prepare', 'agent', 'tools', 'agent', 'finish'].
    raise NotImplementedError("Implement build_graph from workbook steps 3-5.")


def initial_state(document_id: str) -> EvidenceState:
    return {
        "messages": [HumanMessage(content=(
            f"Look up handout {document_id}; what does it say about flush?"
        ))],
        "events": [], "model_calls": 0, "document_id": document_id,
        "evidence": {}, "answer": "", "status": "pending",
    }


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    """Ready-to-use runner once the three functions have been implemented."""
    graph = build_graph(get_model(live=live, max_tokens=256))
    cases = []
    for document_id, expected in ((DOCUMENT_ID, "supported"),
                                  ("MISSING-999", "no_evidence")):
        result = graph.invoke(initial_state(document_id), config=execution_config())
        assert result["status"] == expected
        assert result["model_calls"] == 2
        assert result["events"] == ["prepare", "agent", "tools", "agent", "finish"]
        assert result["answer"]
        documents = result["evidence"]["documents"]
        if expected == "supported":
            assert documents == [{
                "id": DOCUMENT_ID, "source": "synthetic-s2-handout", "page": 1,
                "text": DOCUMENT_TEXT,
            }]
        else:
            assert documents == []
        cases.append({
            "document_id": document_id, "status": result["status"],
            "model_calls": result["model_calls"], "events": result["events"],
            "evidence": result["evidence"], "answer": result["answer"],
        })
    summary = {
        "cases": cases,
        "privacy_plans": [privacy_plan(item) for item in (
            "none", "langsmith", "langwatch", "both"
        )],
        "remote_evidence": classify_ingestion({}),
        "flush_owner": "CLI tracing context after run_demo returns",
    }
    report = safe_write_text(
        output_directory(workdir, "s2"), "s2-starter-completed.txt",
        json.dumps(summary, indent=2) + "\n",
    )
    return {**summary, "report": str(report)}


def main() -> None:
    # Keep this successful, explicit incomplete check until all TODOs are done.
    try:
        privacy_plan("none")
        classify_ingestion({})
        build_graph(None)
    except (NotImplementedError, AttributeError):
        print("STARTER_NOT_COMPLETED: implement all three TODO functions; "
              "then replace main() with run_cli('S2', run_demo).")
        return
    print("STARTER_NOT_COMPLETED: review all TODOs, then enable the live CLI.")


if __name__ == "__main__":
    main()
