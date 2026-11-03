"""L11 starter: implement the workbook's retrieve-first answer-card graph.

Run: python -m exercises.starters.l11
No live calls are made by this starter. Add your own run_demo/CLI only after
completing and offline-testing the three TODO functions below. Do not import
course_lessons.l11 or exercises.solutions.l11 as your implementation.
"""
from __future__ import annotations

from typing import Any, Callable, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from course_support.retrieval import search
from course_support.runtime import message_text


class CardState(TypedDict, total=False):
    question: str
    hits: list[dict]
    answer: str
    status: str
    sources: list[dict]


def format_evidence(hits: list[dict]) -> str:
    # TODO 1: join [source p.page] plus text per hit, separated by blank lines.
    # Empty evidence must produce the empty string. Pages are already 1-based.
    raise NotImplementedError("TODO 1: format evidence with source/page labels")


def build_graph(model: Any, store: Any, *, search_fn: Callable = search):
    # TODO 2: retrieve the nonblank question with k=3. Empty hits route to an
    # abstain node WITHOUT invoking model. Nonempty hits route to generate.
    # In generate, invoke injected model with SystemMessage and HumanMessage,
    # passing config: RunnableConfig through to model.invoke(..., config=config).
    # Use format_evidence; require exact NOT_IN_DOCUMENT for missing facts,
    # otherwise source/page citations and digit durations. Set answer, status
    # (grounded or not_in_document), and sorted deduplicated evidence sources.
    # sources is [] for NOT_IN_DOCUMENT. Finish both branches at END.
    # Return graph.compile(), not the builder. No checkpointer needed here.
    raise NotImplementedError("TODO 2: build retrieve/generate/abstain graph")


def validate_card(result: dict) -> dict:
    # TODO 3: reject unsupported status and missing/unretrieved citations.
    # An abstention must be exactly NOT_IN_DOCUMENT and have no sources.
    # A grounded card needs nonempty hits and source/page citations that all
    # belong to hits. Its sources must be the sorted deduplicated evidence list.
    # Return only question, answer, status and sources. This is provenance
    # checking, not proof that every sentence is entailed by its citation.
    raise NotImplementedError("TODO 3: validate and return the answer card")


def main() -> None:
    sample = {"question": "Missing fact?", "hits": [],
              "answer": "NOT_IN_DOCUMENT", "status": "not_in_document",
              "sources": []}
    try:
        assert format_evidence([]) == ""
        build_graph(None, None)  # compile only; never invoke a model here
        validate_card(sample)
    except NotImplementedError as error:
        print(f"STARTER_NOT_COMPLETED: {error}")
        print("Implement all three TODOs, add offline cases, then run --live safely.")
        return
    print("Starter functions are present; this is NOT a completion or live pass.")
    print("Run your offline cases and inspect the two real live answer cards.")


if __name__ == "__main__":
    main()
