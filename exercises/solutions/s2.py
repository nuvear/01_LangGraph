"""S2 reference solution: trace synthetic retrieval and interpret evidence honestly.

This is independent of course_lessons.s2. No service client is constructed until
run_demo(live=True). A BaseRetriever supplies real retriever callback events, but
its tiny exact-ID corpus is a tracing fixture, not semantic/vector RAG.
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
    execution_config,
    get_model,
    message_text,
    output_directory,
    run_cli,
    safe_write_text,
)

DOCUMENT_ID = "TRACE-101"
DOCUMENT_TEXT = (
    "Flush drains pending export work. Check server acknowledgment separately; "
    "a flush does not prove dashboard visibility."
)


class HandoutRetriever(BaseRetriever):
    """Retrieve one original synthetic handout by its exact ID, not similarity."""

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
    """Describe routes selected by the supplied runtime, not a privacy guarantee."""
    routes = {
        "none": [], "langsmith": ["LangSmith"], "langwatch": ["LangWatch"],
        "both": ["LangSmith", "LangWatch"],
    }
    if backend not in routes:
        raise ValueError("Choose none, langsmith, langwatch, or both.")
    return {
        "backend": backend,
        "telemetry_recipients": routes[backend],
        "model_recipient": "Anthropic when --live is used",
        "payload": "synthetic messages, state, tool arguments/results, retrieved text",
        "root_capture_is_child_redaction": False,
        "plan_only": True,
    }


def classify_ingestion(report: dict) -> dict:
    """Interpret a LangWatch checker record, never infer lesson/UI visibility."""
    acknowledged = (
        report.get("service") == "langwatch"
        and report.get("status") == "passed"
        and report.get("http_status") == 200
        and report.get("ingestion_acknowledged") is True
        and type(report.get("rejected_spans")) is int
        and report["rejected_spans"] == 0
    )
    return {
        "checker_ingestion": "acknowledged" if acknowledged else "not_established",
        "lesson_trace_ingestion": "not_checked",
        "dashboard_visibility": "not_checked",
    }


def build_graph(model):
    """Build prepare -> agent -> tools/retrieve -> agent -> finish, bounded."""
    retriever = HandoutRetriever()

    @tool
    def lookup_handout(document_id: str, config: RunnableConfig) -> str:
        """Retrieve the synthetic training handout by exact document_id."""
        documents = retriever.invoke(document_id, config=config)
        items = [
            {**item.metadata, "text": item.page_content} for item in documents
        ]
        return json.dumps({"found": bool(items), "documents": items})

    tool_model = model.bind_tools(
        [lookup_handout], tool_choice="auto", parallel_tool_calls=False
    )

    def prepare(state: EvidenceState) -> dict:
        if not state["document_id"].strip():
            raise ValueError("document_id must not be blank.")
        return {"events": ["prepare"]}

    def agent(state: EvidenceState, config: RunnableConfig) -> dict:
        calls = state["model_calls"]
        if calls >= 2:
            raise RuntimeError("Model call budget exhausted.")
        selected = tool_model if calls == 0 else model
        response = selected.invoke(
            [SystemMessage(content=(
                "Use lookup_handout exactly once with document_id="
                f"{state['document_id']}. After the tool result, give a brief "
                "answer supported only by that result. If empty, state that "
                "there is no evidence. Do not invent a replacement document."
            ))] + state["messages"],
            config=config,
        )
        if not isinstance(response, AIMessage):
            raise TypeError("The chat model must return an AIMessage.")
        if calls == 0 and len(response.tool_calls) != 1:
            raise ValueError("Expected exactly one first-turn tool call.")
        if calls == 1 and response.tool_calls:
            raise RuntimeError("Tool round budget exhausted.")
        return {
            "messages": [response], "model_calls": calls + 1,
            "events": ["agent"],
        }

    def tools(state: EvidenceState, config: RunnableConfig) -> dict:
        call = state["messages"][-1].tool_calls[0]
        if call["name"] != lookup_handout.name:
            raise ValueError("Unknown tool requested.")
        if call["args"].get("document_id") != state["document_id"]:
            raise ValueError("The model changed the requested document ID.")
        observation = lookup_handout.invoke(call, config=config)
        return {
            "messages": [observation],
            "evidence": json.loads(observation.content), "events": ["tools"],
        }

    def route(state: EvidenceState) -> str:
        return "tools" if state["messages"][-1].tool_calls else "finish"

    def finish(state: EvidenceState) -> dict:
        answer = message_text(state["messages"][-1]).strip()
        if not answer:
            raise ValueError("Expected a nonempty final model response.")
        # Python, not model prose, sets the deterministic assessment status.
        status = "supported" if state["evidence"]["found"] else "no_evidence"
        return {"answer": answer, "status": status, "events": ["finish"]}

    builder = StateGraph(EvidenceState)
    for name, node in (
        ("prepare", prepare), ("agent", agent),
        ("tools", tools), ("finish", finish),
    ):
        builder.add_node(name, node)
    builder.add_edge(START, "prepare")
    builder.add_edge("prepare", "agent")
    builder.add_conditional_edges(
        "agent", route, {"tools": "tools", "finish": "finish"}
    )
    builder.add_edge("tools", "agent")
    builder.add_edge("finish", END)
    return builder.compile()


def initial_state(document_id: str) -> EvidenceState:
    return {
        "messages": [HumanMessage(content=(
            f"Look up handout {document_id}; what does it say about flush?"
        ))],
        "events": [], "model_calls": 0, "document_id": document_id,
        "evidence": {}, "answer": "", "status": "pending",
    }


def run_demo(*, live: bool = False, workdir: Path | None = None) -> dict:
    model = get_model(live=live, max_tokens=256)
    graph = build_graph(model)
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
        # No fabricated checker success; this module did not call that service.
        "remote_evidence": classify_ingestion({}),
        "flush_owner": "CLI tracing context after run_demo returns",
    }
    directory = output_directory(workdir, "s2")
    report = safe_write_text(
        directory, "s2-solution.txt", json.dumps(summary, indent=2) + "\n"
    )
    return {**summary, "report": str(report)}


if __name__ == "__main__":
    run_cli("S2", run_demo)
