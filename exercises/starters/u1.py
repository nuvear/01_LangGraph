"""U1 starter: implement the three functions, without importing the solution.

Run: python -m exercises.starters.u1
The initial file performs no model calls, writes no database, and exits normally.
After completion, this command runs the lab with an explicit offline double.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, MessagesState, StateGraph

from course_support.runtime import execution_config, message_text

NOTEBOOK_RULE = (
    "You are a synthetic classroom travel notebook. Remember destinations only "
    "from this conversation. When asked for the destination, include its exact "
    "spelling if supplied; otherwise reply UNKNOWN without inventing a city. "
    "Use one short sentence."
)


class StarterDestinationDouble:
    """Offline self-check only: not Anthropic and not a live recall claim."""
    def invoke(self, messages, config=None):
        humans = [
            item.content for item in messages if isinstance(item, HumanMessage)
        ]
        match = re.search(r"My destination is (Kyoto|Oslo)\.", "\n".join(humans))
        return AIMessage(content=match.group(1) if match else "UNKNOWN")


def build_notebook(model: Any, checkpointer: Any):
    """TODO 1: compile START -> answer -> END with MessagesState.

    Define answer(state, config), invoke the injected model with NOTEBOOK_RULE
    plus state['messages'], pass config, and return ONLY its new AIMessage.
    Compile with the supplied checkpointer. Never create the model here.
    """
    raise NotImplementedError("TODO 1: build_notebook")


def ask(graph: Any, thread_id: str, text: str) -> dict:
    """TODO 2: reject non-string/blank IDs and text with ValueError.

    Send a single new HumanMessage and config=execution_config(thread_id).
    Preserve the supplied text, not text.strip(); use strip only to validate.
    """
    raise NotImplementedError("TODO 2: ask")


def run_lab(model: Any, database: Path) -> dict:
    """TODO 3: implement the exact workbook acceptance scenario.

    Import SqliteSaver from langgraph.checkpoint.sqlite inside this function.
    Refuse an existing database with FileExistsError; create its parent folder.
    Context 1: seed trip-a with 'My destination is Kyoto. Remember it.' and
    trip-b with 'My destination is Oslo. Remember it.' Save checkpoint IDs.
    EXIT context 1. Context 2: reopen the SAME file, compile a NEW graph, inspect
    the saved snapshots/IDs, then ask 'What is my destination?' in a, b, and c.
    Assert counts 4,4,2; no crossed city facts; c must answer UNKNOWN. Check
    exact human histories, not exact generated prose. Return a JSON-friendly
    summary with database, closed_and_reopened, recovered_checkpoint_ids_match,
    thread_isolation, message_counts, answers, and model_calls=5.
    Do not call get_model or read configuration here: model is injected.
    """
    raise NotImplementedError("TODO 3: run_lab")


if __name__ == "__main__":
    try:
        with TemporaryDirectory(prefix="u1-starter-") as temporary:
            result = run_lab(
                StarterDestinationDouble(), Path(temporary) / "travel.sqlite3"
            )
            assert result["message_counts"] == {
                "trip-a": 4, "trip-b": 4, "trip-c": 2,
            }
            print("OFFLINE_SELF_CHECK_ONLY: temporary database removed on exit.")
            print(json.dumps(result, indent=2))
    except NotImplementedError as error:
        print(
            "STARTER_NOT_COMPLETED: implement build_notebook, ask, and run_lab. "
            "This is not a passing solution. " + str(error)
        )
