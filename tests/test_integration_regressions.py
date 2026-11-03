"""Targeted integration regressions; all models here are explicit offline doubles."""
from langchain_core.messages import AIMessage, HumanMessage
import pytest

from exercises.solutions import u1
from course_lessons import l11


class OfflineNotebookModel:
    def invoke(self, messages, config=None):
        human = " ".join(m.content for m in messages if isinstance(m, HumanMessage))
        destination = "Kyoto" if "Kyoto" in human else "Oslo" if "Oslo" in human else "UNKNOWN"
        return AIMessage(content=destination)


def test_both_recovered_snapshots_are_inspected_before_either_recall(tmp_path, monkeypatch):
    original = u1.build_notebook
    builds = 0
    events = []

    class ObservedReopenedGraph:
        def __init__(self, graph):
            self.graph = graph

        def get_state(self, config):
            events.append(("inspect", config["configurable"]["thread_id"]))
            return self.graph.get_state(config)

        def invoke(self, state, config=None):
            events.append(("invoke", config["configurable"]["thread_id"]))
            return self.graph.invoke(state, config=config)

    def build(model, saver):
        nonlocal builds
        builds += 1
        graph = original(model, saver)
        return ObservedReopenedGraph(graph) if builds == 2 else graph

    monkeypatch.setattr(u1, "build_notebook", build)
    result = u1.run_lab(OfflineNotebookModel(), tmp_path / "ordering.sqlite")
    assert events[:3] == [("inspect", "trip-a"), ("inspect", "trip-b"), ("invoke", "trip-a")]
    assert result["recovered_checkpoint_ids_match"] is True


def test_rag_demo_rejects_mixed_real_and_fabricated_non_pdf_marker():
    class OfflineFinalGraph:
        def invoke(self, state, config=None):
            return {"messages": [AIMessage(content=(
                "7 days [rag_teaching_handbook.pdf p.2] [invented.txt p.99]"
            ))], "tool_rounds": 1, "model_turns": 2,
                    "hits": [{"id": "p2", "source": "rag_teaching_handbook.pdf", "page": 2, "text": "7 days"}]}

    with pytest.raises(AssertionError, match="citations"):
        l11.ask(OfflineFinalGraph(), "How long is a loan?")
