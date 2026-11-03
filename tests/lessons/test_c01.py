"""C01 offline tests: scripted doubles are NOT evidence of live model calls."""
from __future__ import annotations

import copy
import importlib
import json
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.types import Command

from course_support.runtime import execution_config

MODULES = ["course_lessons.c01", "exercises.solutions.c01"]
# Explicit synthetic test data, not a second live knowledge base.
TEST_HITS = [{
    "id": "offline-test-1", "text": "Synthetic test rule: review before saving.",
    "source": "rag_offline_test.pdf", "page": 1,
}]


class ExplicitOfflineRetriever:
    """Test double recording requests; never initializes Chroma or downloads."""
    def __init__(self, hits=None, error=None):
        self.hits = TEST_HITS if hits is None else hits
        self.error = error
        self.calls = []

    def __call__(self, query, k):
        self.calls.append((query, k))
        if self.error:
            raise self.error
        return copy.deepcopy(self.hits)


class ExplicitOfflineBoundSearchModel:
    def __init__(self, owner):
        self.owner = owner

    def invoke(self, messages, config=None):
        self.owner.configs.append(config)
        self.owner.search_prompts.append(messages)
        if self.owner.tool_mode == "missing":
            return AIMessage(content="No tool requested.")
        calls = [{
            "name": "retrieve_passages", "args": {"query": "teaching rules"},
            "id": "offline-call-" + uuid4().hex, "type": "tool_call",
        }]
        if self.owner.tool_mode == "unknown":
            calls[0]["name"] = "unapproved_tool"
        elif self.owner.tool_mode == "multiple":
            calls.append({**calls[0], "id": "second-offline-call"})
        elif self.owner.tool_mode == "blank_query":
            calls[0]["args"] = {"query": " "}
        elif self.owner.tool_mode == "extra_args":
            calls[0]["args"]["unsafe_path"] = "../not-allowed.txt"
        return AIMessage(content="", tool_calls=calls)


class ExplicitOfflineBoundDraftModel:
    def __init__(self, owner):
        self.owner = owner

    def invoke(self, messages, config=None):
        return self.owner.invoke(messages, config=config)


class ExplicitOfflineModel:
    """A named, deliberately scripted model test double, never ChatAnthropic."""
    def __init__(self, *, text_mode="grounded", tool_mode="valid"):
        self.text_mode = text_mode
        self.tool_mode = tool_mode
        self.configs = []
        self.search_prompts = []
        self.draft_prompts = []
        self.bindings = []

    def bind_tools(self, tools, **kwargs):
        self.bindings.append((tools, kwargs))
        if kwargs.get("tool_choice") == {"type": "none"}:
            return ExplicitOfflineBoundDraftModel(self)
        return ExplicitOfflineBoundSearchModel(self)

    def invoke(self, messages, config=None):
        self.configs.append(config)
        self.draft_prompts.append(messages)
        results = [m for m in messages if isinstance(m, ToolMessage)]
        assert len(results) == 1, "Tool results must reach the drafting model."
        tool_requests = [m for m in messages if getattr(m, "tool_calls", [])]
        assert results[0].tool_call_id == tool_requests[0].tool_calls[0]["id"]
        hits = json.loads(results[0].content)
        marker = hits[0]["citation"]
        if self.text_mode == "unsupported":
            text = "INSUFFICIENT_EVIDENCE"
        elif self.text_mode == "uncited":
            text = "A statement without a source."
        elif self.text_mode == "unknown_citation":
            text = "A statement [rag_unknown.pdf p.99]"
        elif self.text_mode == "empty":
            text = ""
        else:
            text = f"Review before saving. {marker}"
            if len(self.draft_prompts) > 1:
                text = f"Review first. {marker}"
        return AIMessage(content=text)


class ExplicitOfflineToolSpanRecorder(BaseCallbackHandler):
    def __init__(self):
        self.started = 0
        self.ended = 0

    def on_tool_start(self, serialized, input_str, **kwargs):
        self.started += 1

    def on_tool_end(self, output, **kwargs):
        self.ended += 1


@pytest.fixture(params=MODULES)
def module(request):
    return importlib.import_module(request.param)


def config():
    return execution_config("c01-offline-" + uuid4().hex)


def paused_graph(module, tmp_path, *, retriever=None, model=None,
                 filename="brief.txt"):
    model = model or ExplicitOfflineModel()
    retrieve = retriever or ExplicitOfflineRetriever()
    graph = module.build_graph(model, retrieve, tmp_path)
    cfg = config()
    state = graph.invoke(module.initial_state(module.REQUEST, filename), config=cfg)
    return graph, cfg, state, model, retrieve


def approval(module, state):
    return {"action": "approve", "fingerprint": module.fingerprint(state["draft"])}


def test_grounded_tool_round_trip_and_approved_save(module, tmp_path):
    graph, cfg, state, model, retrieve = paused_graph(module, tmp_path)
    assert state.get("__interrupt__")
    assert state["model_calls"] == 2 and len(retrieve.calls) == 1
    assert model.bindings[0][1] == {
        "tool_choice": "auto", "parallel_tool_calls": False,
    }
    assert model.bindings[1][1] == {"tool_choice": {"type": "none"}}
    assert not list(tmp_path.glob("*.txt"))
    final = graph.invoke(Command(resume=approval(module, state)), config=cfg)
    assert final["status"] == "saved" and final["approved"] is True
    path = Path(final["saved_path"])
    assert path.parent == tmp_path
    assert path.read_text() == module.render_artifact(final["draft"], final["hits"])
    assert all(c["configurable"]["thread_id"] == cfg["configurable"]["thread_id"]
               for c in model.configs)
    assert all(c["recursion_limit"] == 40 for c in model.configs)


def test_tool_callbacks_survive_graph_invocation(module, tmp_path):
    recorder = ExplicitOfflineToolSpanRecorder()
    cfg = {**config(), "callbacks": [recorder]}
    graph = module.build_graph(
        ExplicitOfflineModel(), ExplicitOfflineRetriever(), tmp_path,
    )
    graph.invoke(module.initial_state(module.REQUEST), config=cfg)
    assert recorder.started == 1 and recorder.ended == 1


def test_clarification_and_two_thread_isolation(module, tmp_path):
    graph = module.build_graph(
        ExplicitOfflineModel(), ExplicitOfflineRetriever(), tmp_path,
    )
    a, b = config(), config()
    assert graph.invoke(module.initial_state(""), config=a).get("__interrupt__")
    assert graph.invoke(module.initial_state(""), config=b).get("__interrupt__")
    resumed = graph.invoke(Command(resume=module.REQUEST), config=a)
    assert resumed["draft"] and resumed.get("__interrupt__")
    other = graph.get_state(b).values
    assert other["draft"] == "" and other["hits"] == []
    assert other["model_calls"] == 0 and not other["approved"]
    failed = graph.invoke(Command(resume=""), config=b)
    assert failed["status"] == "clarification_failed"
    assert graph.get_state(a).values["draft"] == resumed["draft"]


def test_one_revision_then_second_revision_stops(module, tmp_path):
    graph, cfg, state, model, _ = paused_graph(module, tmp_path)
    revised = graph.invoke(Command(resume={
        "action": "revise", "feedback": "  Shorter, please.  ",
    }), config=cfg)
    assert revised.get("__interrupt__") and revised["revisions"] == 1
    assert revised["model_calls"] == 3 and revised["draft"] != state["draft"]
    assert revised["feedback"] == "Shorter, please."
    stopped = graph.invoke(Command(resume={
        "action": "revise", "feedback": "Again.",
    }), config=cfg)
    assert stopped["status"] == "revision_limit"
    assert stopped["approved"] is False and not stopped["saved_path"]
    assert len(model.draft_prompts) == 2 and not list(tmp_path.glob("*.txt"))


@pytest.mark.parametrize("payload,status", [
    ({"action": "reject"}, "rejected"),
    (True, "invalid_review"),
    ({"action": "revise", "feedback": " "}, "invalid_review"),
    ({"action": "revise", "feedback": "x" * 501}, "invalid_review"),
    ({"action": "invented"}, "invalid_review"),
])
def test_review_failure_paths_no_file(module, tmp_path, payload, status):
    graph, cfg, _, _, _ = paused_graph(module, tmp_path)
    final = graph.invoke(Command(resume=payload), config=cfg)
    assert final["status"] == status and not final["saved_path"]
    assert final["approved"] is False and not list(tmp_path.glob("*.txt"))


def test_empty_evidence_stops_before_generation(module, tmp_path):
    graph, cfg, state, model, _ = paused_graph(
        module, tmp_path, retriever=ExplicitOfflineRetriever([]),
    )
    assert state["status"] == "no_evidence" and state["model_calls"] == 1
    assert not model.draft_prompts and not state.get("__interrupt__")
    assert not list(tmp_path.glob("*.txt"))


@pytest.mark.parametrize("mode,status", [
    ("unsupported", "unsupported"), ("uncited", "citation_failed"),
    ("unknown_citation", "citation_failed"), ("empty", "citation_failed"),
])
def test_unsupported_and_bad_citations_stop(module, tmp_path, mode, status):
    _, _, state, _, _ = paused_graph(
        module, tmp_path, model=ExplicitOfflineModel(text_mode=mode),
    )
    assert state["status"] == status and not state.get("__interrupt__")
    assert not list(tmp_path.glob("*.txt"))


@pytest.mark.parametrize("mode,status", [
    ("missing", "tool_error"), ("unknown", "tool_error"),
    ("multiple", "tool_error"), ("blank_query", "retrieval_failed"),
    ("extra_args", "tool_error"),
])
def test_malformed_tool_requests_fail_closed(module, tmp_path, mode, status):
    _, _, state, model, _ = paused_graph(
        module, tmp_path, model=ExplicitOfflineModel(tool_mode=mode),
    )
    assert state["status"] == status and not state["saved_path"]
    assert not model.draft_prompts and not list(tmp_path.glob("*.txt"))


@pytest.mark.parametrize("bad_hit", [
    {**TEST_HITS[0], "page": 0}, {**TEST_HITS[0], "page": True},
    {**TEST_HITS[0], "text": ""}, {"id": "missing-metadata"},
])
def test_invalid_retrieval_metadata(module, tmp_path, bad_hit):
    _, _, state, _, _ = paused_graph(
        module, tmp_path, retriever=ExplicitOfflineRetriever([bad_hit]),
    )
    assert state["status"] == "retrieval_failed" and state["error"] == "ValueError"


def test_retrieval_error_is_not_an_empty_success(module, tmp_path):
    _, _, state, _, _ = paused_graph(
        module, tmp_path,
        retriever=ExplicitOfflineRetriever(error=RuntimeError("offline fault")),
    )
    assert state["status"] == "retrieval_failed" and not state["saved_path"]


@pytest.mark.parametrize("filename", ["../escape.txt", "/tmp/escape.txt", "bad.md"])
def test_unsafe_approved_filename_is_not_saved(module, tmp_path, filename):
    graph, cfg, state, _, _ = paused_graph(module, tmp_path, filename=filename)
    final = graph.invoke(Command(resume=approval(module, state)), config=cfg)
    assert final["status"] == "save_failed" and not final["saved_path"]
    assert final["error"] == "ValueError"
    assert not list(tmp_path.glob("*.txt"))


def test_existing_file_preserved_and_no_false_save(module, tmp_path):
    path = tmp_path / "brief.txt"
    path.write_text("original")
    graph, cfg, state, _, _ = paused_graph(module, tmp_path)
    final = graph.invoke(Command(resume=approval(module, state)), config=cfg)
    assert final["status"] == "save_failed" and not final["saved_path"]
    assert final["error"] == "FileExistsError" and path.read_text() == "original"


def test_citation_gate_structural_not_entailment(module):
    marker = module.citation(TEST_HITS[0])
    assert module.assess_citations("Supported. " + marker, TEST_HITS)
    assert not module.assess_citations("Uncited.", TEST_HITS)
    assert not module.assess_citations(marker + " [rag_other.pdf p.2]", TEST_HITS)
    assert not module.assess_citations("INSUFFICIENT_EVIDENCE " + marker, TEST_HITS)
    assert not module.assess_citations(marker, [])
    # Deliberately documents the gate's limitation: humans check the actual claim.
    assert module.assess_citations("An invented claim. " + marker, TEST_HITS)


def assert_exercise_contract(implementation):
    """Learners may call this offline assertion helper on their own starter."""
    draft = "Review first. " + implementation.citation(TEST_HITS[0])
    assert implementation.assess_citations(draft, TEST_HITS)
    assert not implementation.assess_citations("uncited", TEST_HITS)
    assert not implementation.assess_citations(draft + " [rag_bad.pdf p.9]", TEST_HITS)
    assert not implementation.assess_citations("INSUFFICIENT_EVIDENCE", TEST_HITS)
    assert not implementation.assess_citations("", TEST_HITS)
    for payload in (True, None, {}, {"action": "approve", "fingerprint": "stale"}):
        assert implementation.decide_review(payload, draft, 0) == {
            "approved": False, "feedback": "", "status": "invalid_review",
        }
    ok = {"action": "approve", "fingerprint": implementation.fingerprint(draft)}
    assert implementation.decide_review(ok, draft, 0)["approved"] is True
    assert implementation.decide_review({"action": "reject"}, draft, 0)["status"] \
        == "rejected"
    revise = {"action": "revise", "feedback": "  Shorter.  "}
    update = implementation.decide_review(revise, draft, 0)
    assert update == {
        "approved": False, "feedback": "Shorter.", "status": "revision_requested",
    }
    assert implementation.decide_review(revise, draft, 1)["status"] == "revision_limit"
    for feedback in (" ", "x" * 501, None):
        assert implementation.decide_review(
            {"action": "revise", "feedback": feedback}, draft, 0,
        )["status"] == "invalid_review"
    second = {**TEST_HITS[0], "page": 2, "id": "offline-test-2"}
    artifact = implementation.render_artifact(draft, [second, *TEST_HITS, second])
    assert artifact == (
        draft + "\n\nEvidence inventory\n"
        "- [rag_offline_test.pdf p.1] (chunk offline-test-1)\n"
        "- [rag_offline_test.pdf p.2] (chunk offline-test-2)\n"
    )


def test_reference_solution_matches_exact_workbook_contract():
    assert_exercise_contract(importlib.import_module("exercises.solutions.c01"))


def test_stale_approval_after_revision_cannot_save(tmp_path):
    solution = importlib.import_module("exercises.solutions.c01")
    graph, cfg, old, _, _ = paused_graph(solution, tmp_path)
    revised = graph.invoke(Command(resume={
        "action": "revise", "feedback": "Shorter.",
    }), config=cfg)
    assert solution.fingerprint(revised["draft"]) != solution.fingerprint(old["draft"])
    final = graph.invoke(Command(resume=approval(solution, old)), config=cfg)
    assert final["status"] == "invalid_review" and not final["saved_path"]
    assert not list(tmp_path.glob("*.txt"))


def test_lazy_l11_helper_dependency_and_injected_contract(
        module, tmp_path, monkeypatch):
    calls = []
    helper = SimpleNamespace(
        prepare_store=lambda path: calls.append(path) or "offline-store",
        search=lambda store, query, k: calls.append((store, query, k)) or TEST_HITS,
    )
    def import_double(name):
        assert name == "course_support.retrieval"
        return helper
    monkeypatch.setattr(module.importlib, "import_module", import_double)
    retrieve = module.load_retriever(tmp_path)
    assert retrieve("rules", 3) == TEST_HITS
    assert calls == [tmp_path, ("offline-store", "rules", 3)]


def test_missing_l11_reports_integration_blocker(module, tmp_path, monkeypatch):
    def missing(name):
        raise ModuleNotFoundError(name, name=name)
    monkeypatch.setattr(module.importlib, "import_module", missing)
    with pytest.raises(RuntimeError, match="not integrated"):
        module.load_retriever(tmp_path)


def test_run_demo_default_does_not_silently_use_a_fake(module, tmp_path):
    with pytest.raises(ValueError, match="--live"):
        module.run_demo(workdir=tmp_path)


def test_run_demo_driver_with_explicit_offline_dependencies(
        module, tmp_path, monkeypatch):
    model = ExplicitOfflineModel()
    def get_model_double(*, live, max_tokens):
        assert live is True and max_tokens == 1000
        return model
    monkeypatch.setattr(module, "get_model", get_model_double)
    monkeypatch.setattr(
        module, "load_retriever", lambda directory: ExplicitOfflineRetriever(),
    )
    summary = module.run_demo(live=True, workdir=tmp_path)
    assert summary["status"] == "saved" and summary["model_calls"] == 3
    assert summary["thread_isolation"] and summary["unsafe_and_duplicate_saves_blocked"]
    assert Path(summary["saved_path"]).is_file()


def test_starter_is_actionable_and_does_not_run_a_model(capsys):
    starter = importlib.import_module("exercises.starters.c01")
    try:
        starter.assess_citations("", [])
    except NotImplementedError:
        starter.run_starter()
        assert "STARTER_NOT_COMPLETED" in capsys.readouterr().out
    else:
        # Once completed, apply the same contract rather than requiring TODOs.
        assert_exercise_contract(starter)


def test_implemented_starter_acceptance(tmp_path):
    """A skip means unfinished, never a completed capstone or a live check."""
    starter = importlib.import_module("exercises.starters.c01")
    try:
        starter.assess_citations("", [])
    except NotImplementedError:
        pytest.skip("C01 starter TODOs remain: not completion evidence.")
    assert_exercise_contract(starter)
    test_grounded_tool_round_trip_and_approved_save(starter, tmp_path / "approved")
    test_one_revision_then_second_revision_stops(starter, tmp_path / "bounded")
    graph, cfg, state, _, _ = paused_graph(starter, tmp_path / "stale")
    final = graph.invoke(Command(resume={
        "action": "approve", "fingerprint": "stale",
    }), config=cfg)
    assert final["status"] == "invalid_review" and not final["saved_path"]
