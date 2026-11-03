"""L07 starter: implement the workbook's stateless help-desk session.

Running this file performs no model call and does not load credentials.
Complete all three TODO functions; do not import the reference solution.
"""
from __future__ import annotations

from itertools import islice
from typing import Iterable, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from course_support.runtime import execution_config, message_text


class RequestState(TypedDict, total=False):
    prompt: str
    reply: str
    sent_messages: list[str]
    usage: dict


def classify_entry(raw: str) -> str:
    """Return 'exit', 'skip', or 'send'; reject non-string input."""
    # TODO 1: Use strip/casefold for decisions only. Do not alter sent text.
    raise NotImplementedError("Implement classify_entry.")


def build_bot(model):
    """Return a compiled START -> respond -> END graph; inject the model."""
    # TODO 2: Define a respond(state, config) node here. Send exactly one new
    # HumanMessage for state['prompt']; pass config to model.invoke. Reject
    # blank/exit input, non-AIMessage responses, and empty displayable text.
    # Return reply, usage ({} if missing), and sent_messages=[original prompt].
    # Register the node and both edges; compile without a checkpointer.
    raise NotImplementedError("Implement build_bot, including its nested node.")


def run_session(graph, entries: Iterable[str], *, max_entries: int = 6) -> dict:
    """Return turns, skipped, inspected, and stop_reason; no saved history."""
    # TODO 3: Reject nonpositive/noninteger limits. Inspect at most max_entries
    # raw entries with islice. Count blank and exit entries toward the limit.
    # Break before invoking on exit; skip blanks. Invoke with {'prompt': raw}
    # and execution_config(). Collect results only for the returned report.
    # Stop reasons: exit, limit (budget reached), exhausted (source ended early).
    raise NotImplementedError("Implement run_session.")


if __name__ == "__main__":
    print(
        "STARTER_NOT_COMPLETED: implement classify_entry, build_bot, and "
        "run_session. See course/chapters/l07/workbook.md for acceptance checks."
    )
