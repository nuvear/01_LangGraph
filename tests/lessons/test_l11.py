"""L11 offline tests: explicit doubles, no credentials, downloads or live models."""
from __future__ import annotations

import json
from pathlib import Path

from langchain_core.messages import AIMessage, ToolMessage
import pytest

from course_lessons import l11 as demo
from course_support import retrieval
from exercises.solutions import l11 as solution

HIT = {"id": "p2-c1", "text": "Equipment loans last 7 days; one renewal is 3 days.",
       "source": "rag_teaching_handbook.pdf", "page": 2}
ANSWER = "Loan: 7 days. One renewal: 3 days. [rag_teaching_handbook.pdf p.2]"


class SearchCollectionTestDouble:
    """A Chroma result-shape double, explicitly not a semantic embedding test."""
    def __init__(self, hits=None):
        self.hits = [HIT] if hits is None else hits
        self.calls = []

    def count(self):
        return len(self.hits)

    def query(self, **kwargs):
        self.calls.append(kwargs)
        hits = self.hits[:kwargs["n_results"]]
        return {"ids": [[h["id"] for h in hits]],
                "documents": [[h["text"] for h in hits]],
                "metadatas": [[{"source": h["source"], "page": h["page"]}
                               for h in hits]]}


class PersistentCollectionTestDouble:
    """Stores ingestion arguments but never computes substitute embeddings."""
    def __init__(self, metadata):
        self.metadata = metadata
        self.ids = []
        self.upserts = []

    def count(self):
        return len(self.ids)

    def get(self, **kwargs):
        return {"ids": self.ids[:]}

    def upsert(self, **kwargs):
        self.upserts.append(kwargs)
        self.ids = kwargs["ids"][:]


class PersistentClientTestDouble:
    def __init__(self):
        self.options = []
        self.collection = None

    def get_or_create_collection(self, **kwargs):
        self.options.append(kwargs)
        if self.collection is None:
            self.collection = PersistentCollectionTestDouble(kwargs["metadata"])
        return self.collection


class ScriptedToolModelTestDouble:
    """Scripted normalized LangChain messages, not an Anthropic live response."""
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.bindings = []

    def bind_tools(self, tools, **kwargs):
        self.bindings.append((tools, kwargs))
        return self

    def invoke(self, messages, config=None):
        self.calls.append((messages, config))
        return self.replies.pop(0)


class AnswerModelTestDouble:
    def __init__(self, text=ANSWER):
        self.text = text
        self.calls = []

    def invoke(self, messages, config=None):
        self.calls.append((messages, config))
        return AIMessage(content=self.text)


def tool_request(*, name="retrieve_passages", args=None, call_id="lookup-1"):
    return AIMessage(content="", tool_calls=[{
        "name": name, "args": {"query": "equipment loans"} if args is None else args,
        "id": call_id, "type": "tool_call",
    }])


def test_pdf_is_original_three_page_dataset_with_real_page_metadata():
    from pypdf import PdfReader

    pages = PdfReader(retrieval.PDF_PATH).pages
    assert len(pages) == 3
    assert all("SYNTHETIC TEACHING DATASET" in p.extract_text() for p in pages)
    chunks = retrieval.load_chunks()
    assert {h["page"] for h in chunks} == {1, 2, 3}
    assert len({h["id"] for h in chunks}) == len(chunks)
    assert all(0 < len(h["text"]) <= retrieval.CHUNK_SIZE for h in chunks)
    assert any("7 calendar days" in h["text"] and h["page"] == 2 for h in chunks)


def test_missing_pdf_raises_without_network(tmp_path):
    with pytest.raises(FileNotFoundError):
        retrieval.load_chunks(tmp_path / "missing.pdf")


def test_textless_pdf_rejected(tmp_path):
    from pypdf import PdfWriter

    target = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.write(target)
    with pytest.raises(ValueError, match="no extractable text"):
        retrieval.load_chunks(target)


def test_prepare_uses_real_default_embedding_and_disables_telemetry(monkeypatch, tmp_path):
    import chromadb
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

    client = PersistentClientTestDouble()
    calls = []

    def client_factory(**kwargs):
        calls.append(kwargs)
        return client

    monkeypatch.setattr(chromadb, "PersistentClient", client_factory)
    first = retrieval.prepare_store(tmp_path)
    second = retrieval.prepare_store(tmp_path)
    assert first is second
    assert len(first.upserts) == 1  # reopens without appending duplicate chunks
    assert first.count() == len(retrieval.load_chunks())
    assert calls[0]["path"] == str(tmp_path / "chroma")
    assert calls[0]["settings"].anonymized_telemetry is False
    assert not calls[0]["settings"].chroma_otel_collection_endpoint
    assert isinstance(client.options[0]["embedding_function"], DefaultEmbeddingFunction)
    assert client.options[0]["configuration"]["hnsw"]["space"] == "cosine"
    assert all(m["page"] >= 1 for m in first.upserts[0]["metadatas"])


def test_search_preserves_metadata_and_caps_k():
    store = SearchCollectionTestDouble()
    assert retrieval.search(store, " loan ", 3) == [HIT]
    assert store.calls[0]["query_texts"] == ["loan"]
    assert store.calls[0]["n_results"] == 1
    assert set(retrieval.search(store, "loan")[0]) == {"id", "text", "source", "page"}


def test_blank_and_empty_search_do_not_embed():
    store = SearchCollectionTestDouble()
    assert retrieval.search(store, "  ") == []
    assert store.calls == []
    empty = SearchCollectionTestDouble([])
    assert retrieval.search(empty, "anything") == [] and empty.calls == []


@pytest.mark.parametrize("k", [0, -1, True, 1.5])
def test_search_rejects_invalid_k(k):
    with pytest.raises(ValueError):
        retrieval.search(SearchCollectionTestDouble(), "loan", k)


def test_search_rejects_bad_query_and_page_zero():
    with pytest.raises(TypeError):
        retrieval.search(SearchCollectionTestDouble(), None)
    with pytest.raises(ValueError, match="1-based"):
        retrieval.search(SearchCollectionTestDouble([{**HIT, "page": 0}]), "loan")


def test_tool_graph_executes_real_tool_function_with_named_store_double():
    model = ScriptedToolModelTestDouble([tool_request(), AIMessage(content=ANSWER)])
    result = demo.ask(demo.build_graph(model, SearchCollectionTestDouble()), "Loan?")
    assert result["answer"] == ANSWER
    assert result["tool_rounds"] == 1 and result["model_turns"] == 2
    assert result["hits"] == [HIT]
    tool_messages = [m for m in model.calls[1][0] if isinstance(m, ToolMessage)]
    assert tool_messages[0].tool_call_id == "lookup-1"
    assert json.loads(tool_messages[0].content)["hits"] == [HIT]
    assert model.calls[0][1]["recursion_limit"] == 40
    assert model.bindings[0][1]["tool_choice"] == "auto"


@pytest.mark.parametrize("hits", [[HIT], []])
def test_tool_graph_abstains_with_irrelevant_or_empty_evidence(hits):
    model = ScriptedToolModelTestDouble([
        tool_request(), AIMessage(content="NOT_IN_DOCUMENT"),
    ])
    result = demo.ask(demo.build_graph(model, SearchCollectionTestDouble(hits)), "Fee?")
    assert result["answer"] == "NOT_IN_DOCUMENT"


def test_unknown_tool_preserves_call_id_and_returns_error():
    model = ScriptedToolModelTestDouble([
        tool_request(name="not_available"), AIMessage(content="NOT_IN_DOCUMENT"),
    ])
    demo.ask(demo.build_graph(model, SearchCollectionTestDouble()), "Loan?")
    reply = [m for m in model.calls[1][0] if isinstance(m, ToolMessage)][0]
    assert reply.tool_call_id == "lookup-1"
    assert json.loads(reply.content)["error"] == "Unknown tool"


def test_bad_tool_query_is_not_a_successful_search():
    store = SearchCollectionTestDouble()
    model = ScriptedToolModelTestDouble([
        tool_request(args={"query": 42}), AIMessage(content="NOT_IN_DOCUMENT"),
    ])
    result = demo.ask(demo.build_graph(model, store), "Loan?")
    assert result["hits"] == [] and store.calls == []


def test_tool_loop_has_an_explicit_budget():
    model = ScriptedToolModelTestDouble([tool_request(), tool_request(call_id="lookup-2")])
    with pytest.raises(RuntimeError, match="budget exhausted"):
        demo.ask(demo.build_graph(model, SearchCollectionTestDouble(), max_turns=2), "Loan?")


def test_demo_rejects_uncited_or_unretrieved_answer():
    for text in ["7 days", "7 days [rag_teaching_handbook.pdf p.1]"]:
        model = ScriptedToolModelTestDouble([tool_request(), AIMessage(content=text)])
        with pytest.raises(AssertionError, match="citations"):
            demo.ask(demo.build_graph(model, SearchCollectionTestDouble()), "Loan?")


def test_demo_rejects_skipped_retrieval_and_blank_question():
    model = ScriptedToolModelTestDouble([AIMessage(content="NOT_IN_DOCUMENT")])
    graph = demo.build_graph(model, SearchCollectionTestDouble())
    with pytest.raises(ValueError, match="nonblank"):
        demo.ask(graph, " ")
    with pytest.raises(AssertionError, match="did not execute retrieval"):
        demo.ask(graph, "Loan?")


def test_solution_formats_empty_and_page_labeled_evidence():
    assert solution.format_evidence([]) == ""
    assert solution.format_evidence([HIT]) == (
        "[rag_teaching_handbook.pdf p.2]\n" + HIT["text"]
    )


def test_solution_grounded_card_deduplicates_sources():
    store = SearchCollectionTestDouble([HIT, {**HIT, "id": "p2-c2"}])
    model = AnswerModelTestDouble()
    graph = solution.build_graph(model, store)
    card = solution.answer_card(graph, "Loan?")
    assert card["status"] == "grounded" and card["answer"] == ANSWER
    assert card["sources"] == [{"source": HIT["source"], "page": 2}]
    assert set(card) == {"question", "answer", "status", "sources"}
    assert model.calls[0][1]["recursion_limit"] == 40
    assert "[rag_teaching_handbook.pdf p.2]" in model.calls[0][0][-1].content


def test_solution_empty_evidence_skips_model():
    model = AnswerModelTestDouble()
    card = solution.answer_card(
        solution.build_graph(model, SearchCollectionTestDouble([])), "Loan?",
    )
    assert card["status"] == "not_in_document" and card["sources"] == []
    assert model.calls == []


def test_solution_missing_fact_is_not_a_fabricated_fee():
    model = AnswerModelTestDouble("NOT_IN_DOCUMENT")
    card = solution.answer_card(
        solution.build_graph(model, SearchCollectionTestDouble()), "Late fee?",
    )
    assert card["answer"] == "NOT_IN_DOCUMENT" and card["sources"] == []
    assert len(model.calls) == 1  # nearest chunks do not imply answerability


def test_solution_rejects_blank_question_before_generation():
    model = AnswerModelTestDouble()
    with pytest.raises(ValueError, match="nonblank"):
        solution.answer_card(solution.build_graph(model, SearchCollectionTestDouble()), "")
    assert model.calls == []


def test_solution_rejects_missing_and_fabricated_citations():
    for answer in [
        "7 days", "7 days [rag_teaching_handbook.pdf p.99]",
        "7 days [rag_teaching_handbook.pdf p.2] [invented.txt p.99]",
    ]:
        with pytest.raises(AssertionError):
            solution.answer_card(solution.build_graph(
                AnswerModelTestDouble(answer), SearchCollectionTestDouble(),
            ), "Loan?")


def test_retrieval_failure_is_not_silently_reported_as_empty():
    def failing_search(store, query, k=3):
        raise OSError("named offline retrieval failure")

    with pytest.raises(OSError, match="offline retrieval failure"):
        solution.answer_card(solution.build_graph(
            AnswerModelTestDouble(), None, search_fn=failing_search,
        ), "Loan?")


@pytest.mark.parametrize("module", [demo, solution])
def test_live_opt_in_required_without_loading_environment(module, tmp_path):
    with pytest.raises(ValueError, match="--live"):
        module.run_demo(live=False, workdir=tmp_path)
    assert list(tmp_path.iterdir()) == []
