"""U2 offline tests: explicit doubles only; no credentials, APIs, or telemetry."""
from pathlib import Path
import socket

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.types import Command
from langsmith import tracing_context
import pytest

from course_lessons import u2 as demo
from course_support import check_connections, runtime
from exercises.solutions import u2 as solution
from exercises.starters import u2 as starter


class NoticeModelDouble:
    """Deterministic OFFLINE double, not an Anthropic response or live evidence."""
    def __init__(self):
        self.calls = []

    def invoke(self, messages, config=None):
        self.calls.append((messages, config))
        return AIMessage(content=f"OFFLINE TEST DOUBLE notice: {messages[-1].content}")


class EmptyModelDouble:
    """Explicit failure double for empty model output."""
    def invoke(self, messages, config=None):
        return AIMessage(content="  ")


@pytest.fixture(autouse=True)
def forbid_network_and_credentials(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Offline U2 tests forbid network and .env loading")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(runtime, "values", forbidden)
    monkeypatch.setattr(check_connections, "dotenv_values", forbidden)
    with tracing_context(enabled=False):
        yield


def config(thread):
    return runtime.execution_config(thread)


def approve(state, **extra):
    return {"approve": True, "draft_hash": state["draft_hash"], **extra}


def solution_pause(tmp_path, filename="notice.txt", thread="a"):
    model = NoticeModelDouble()
    graph = solution.build_graph(model, tmp_path)
    cfg = config(thread)
    paused = graph.invoke(solution.initial_state("a", "Cedar workshop", filename), cfg)
    return model, graph, cfg, paused


def test_baseline_two_sessions_pause_then_approve_and_reject(tmp_path):
    model = NoticeModelDouble()
    graph = demo.build_graph(model, tmp_path)
    a, b = config("a"), config("b")
    cedar = graph.invoke(demo.initial_state("a", "Cedar", "a.txt"), a)
    orchid = graph.invoke(demo.initial_state("b", "Orchid", "b.txt"), b)
    assert cedar["__interrupt__"][0].value["draft"] == cedar["draft"]
    assert cedar["draft"] != orchid["draft"]
    assert list(tmp_path.iterdir()) == []
    assert all(isinstance(result["messages"][-1], ToolMessage)
               for result in (cedar, orchid))
    call = cedar["messages"][0].tool_calls[0]
    assert cedar["messages"][-1].tool_call_id == call["id"]
    saved = graph.invoke(Command(resume=True), a)
    assert Path(saved["saved_path"]).read_text() == cedar["draft"]
    pending_b = graph.get_state(b)
    assert pending_b.values["draft"] == orchid["draft"]
    assert pending_b.next == ("review",)
    rejected = graph.invoke(Command(resume=False), b)
    assert rejected["status"] == "rejected" and not rejected["saved_path"]
    assert not (tmp_path / "b.txt").exists()
    assert len(model.calls) == 2, "Approval replay must not regenerate drafts."
    assert model.calls[0][1]["configurable"]["thread_id"] == "a"
    assert model.calls[0][1]["recursion_limit"] == 40


def test_runtime_is_not_a_model_visible_tool_argument():
    schema = demo.update_draft.tool_call_schema.model_json_schema()
    assert set(schema["properties"]) == {"content"}


@pytest.mark.parametrize("decision", [False, None, "yes", 1, {"approve": True}])
def test_baseline_approval_requires_exact_true(decision):
    assert demo.approval_update(decision)["status"] == "rejected"


def test_baseline_failed_save_is_honest_and_terminal(tmp_path):
    graph = demo.build_graph(NoticeModelDouble(), tmp_path)
    cfg = config("bad")
    graph.invoke(demo.initial_state("bad", "Cedar", "../escape.txt"), cfg)
    result = graph.invoke(Command(resume=True), cfg)
    assert result["status"] == "save_failed" and result["error"]
    assert not result["saved_path"] and graph.get_state(cfg).next == ()
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("module", [demo, solution])
@pytest.mark.parametrize("filename", [
    "../escape.txt", "nested/file.txt", "/tmp/u2-escape.txt", "wrong.md",
    "..txt", "bad\\file.txt", "", "..\\escape.txt",
])
def test_safe_savers_reject_unsafe_names(module, filename, tmp_path):
    if module is demo:
        state = {**demo.initial_state("a", "brief", filename),
                 "draft": "text", "status": "approved"}
        result = demo.save_draft(state, tmp_path)
    else:
        digest = solution.draft_digest("text")
        state = {**solution.initial_state("a", "brief", filename),
                 "draft": "text", "draft_hash": digest,
                 "approved_hash": digest, "status": "approved"}
        result = solution.attempt_save(state, tmp_path)
    assert result["status"] == "save_failed" and result["error"]
    assert not result["saved_path"] and list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("module", [demo, solution])
def test_savers_refuse_overwrite_and_symlink(module, tmp_path):
    original = tmp_path / "existing.txt"
    original.write_text("keep me", encoding="utf-8")
    link = tmp_path / "linked.txt"
    link.symlink_to(original)
    for filename in ("existing.txt", "linked.txt"):
        state = {**module.initial_state("a", "brief", filename),
                 "draft": "replacement", "status": "approved"}
        if module is solution:
            digest = solution.draft_digest(state["draft"])
            state.update(draft_hash=digest, approved_hash=digest)
        saver = demo.save_draft if module is demo else solution.attempt_save
        result = saver(state, tmp_path)
        assert result["status"] == "save_failed" and not result["saved_path"]
        assert original.read_text() == "keep me"


@pytest.mark.parametrize("module", [demo, solution])
def test_unapproved_save_is_forbidden(module, tmp_path):
    saver = demo.save_draft if module is demo else solution.attempt_save
    with pytest.raises(ValueError, match="approv"):
        saver(module.initial_state("a", "brief", "a.txt"), tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_solution_hash_approval_and_single_repair_preserve_text(tmp_path):
    model, graph, cfg, paused = solution_pause(tmp_path, "../escape.txt")
    assert not list(tmp_path.iterdir())
    failed = graph.invoke(Command(resume=approve(paused)), cfg)
    assert failed["status"] == "save_failed" and not failed["saved_path"]
    payload = failed["__interrupt__"][0].value
    assert payload["action"] == "repair_filename_once" and payload["error"]
    assert failed["repairs"] == 0
    saved = graph.invoke(Command(resume=approve(paused, filename="fixed.txt")), cfg)
    assert saved["status"] == "saved" and saved["repairs"] == 1
    assert saved["draft"] == paused["draft"]
    assert (tmp_path / "fixed.txt").read_text() == paused["draft"]
    assert graph.get_state(cfg).next == () and len(model.calls) == 1


@pytest.mark.parametrize("decision", [
    True, "yes", {"approve": 1}, {"approve": True, "draft_hash": "stale"},
    {"approve": False},
])
def test_solution_rejects_malformed_or_stale_approval(tmp_path, decision):
    _, graph, cfg, _ = solution_pause(tmp_path)
    result = graph.invoke(Command(resume=decision), cfg)
    assert result["status"] == "rejected" and not result["saved_path"]
    assert not list(tmp_path.iterdir())


def test_solution_null_decision_is_rejected_at_validator_boundary():
    state = solution.initial_state("a", "brief", "a.txt")
    assert solution.approval_update(state, None)["status"] == "rejected"


def test_solution_second_bad_filename_stops_without_third_interrupt(tmp_path):
    model, graph, cfg, paused = solution_pause(tmp_path, "../bad.txt")
    graph.invoke(Command(resume=approve(paused)), cfg)
    final = graph.invoke(Command(resume=approve(paused, filename="../again.txt")), cfg)
    assert final["status"] == "save_failed" and final["repairs"] == 1
    assert not final["saved_path"] and final["error"]
    assert "__interrupt__" not in final and graph.get_state(cfg).next == ()
    assert len(model.calls) == 1 and not list(tmp_path.iterdir())


def test_solution_collision_repair_preserves_existing_file(tmp_path):
    original = tmp_path / "notice.txt"
    original.write_text("existing", encoding="utf-8")
    _, graph, cfg, paused = solution_pause(tmp_path)
    graph.invoke(Command(resume=approve(paused)), cfg)
    saved = graph.invoke(Command(resume=approve(paused, filename="new.txt")), cfg)
    assert saved["status"] == "saved" and original.read_text() == "existing"
    assert (tmp_path / "new.txt").read_text() == paused["draft"]


@pytest.mark.parametrize("repair_name", [None, "", "   ", 123])
def test_solution_malformed_repair_rejected(tmp_path, repair_name):
    _, graph, cfg, paused = solution_pause(tmp_path, "../bad.txt")
    graph.invoke(Command(resume=approve(paused)), cfg)
    final = graph.invoke(Command(resume=approve(paused, filename=repair_name)), cfg)
    assert final["status"] == "rejected" and final["repairs"] == 1
    assert not final["saved_path"] and not list(tmp_path.iterdir())


def test_solution_detects_draft_edit_after_approval(tmp_path):
    state = {**solution.initial_state("a", "brief", "a.txt"),
             "draft": "before", "draft_hash": solution.draft_digest("before")}
    approved = {**state, **solution.approval_update(state, approve(state))}
    with pytest.raises(ValueError, match="exact current draft"):
        solution.attempt_save({**approved, "draft": "after"}, tmp_path)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("module", [demo, solution])
def test_os_error_never_reports_success(module, monkeypatch, tmp_path):
    def denied_writer_double(*args):
        raise PermissionError("OFFLINE permission error double")

    monkeypatch.setattr(module, "safe_write_text", denied_writer_double)
    state = {**module.initial_state("a", "brief", "a.txt"),
             "draft": "text", "status": "approved"}
    if module is solution:
        state["approved_hash"] = solution.draft_digest("text")
    saver = demo.save_draft if module is demo else solution.attempt_save
    failed = saver(state, tmp_path)
    assert failed["status"] == "save_failed" and "PermissionError" in failed["error"]
    assert not failed["saved_path"] and not list(tmp_path.iterdir())


@pytest.mark.parametrize("module", [demo, solution])
def test_empty_model_text_stops_without_save(module, tmp_path):
    graph = module.build_graph(EmptyModelDouble(), tmp_path)
    with pytest.raises(ValueError, match="empty draft"):
        graph.invoke(module.initial_state("a", "brief", "a.txt"), config("empty"))
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("module", [demo, solution])
def test_both_complete_run_demos_with_explicit_offline_model_double(
    module, monkeypatch, tmp_path,
):
    model = NoticeModelDouble()

    def offline_get_model_double(*, live):
        assert live is False
        return model

    monkeypatch.setattr(module, "get_model", offline_get_model_double)
    result = module.run_demo(live=False, workdir=tmp_path)
    assert result["isolation_checked"] is True and len(model.calls) == 2
    assert Path(result["saved_path"]).is_file()
    assert result["overwrite_status"] == "save_failed"


@pytest.mark.parametrize("module", [demo, solution])
def test_real_entrypoints_require_explicit_live_opt_in(module, tmp_path):
    with pytest.raises(ValueError, match="--live"):
        module.run_demo(workdir=tmp_path)
    assert not list(tmp_path.iterdir())


def test_starter_is_actionable_and_does_not_claim_a_pass(capsys):
    starter.main()
    output = capsys.readouterr().out
    assert "STARTER_NOT_COMPLETED" in output and "TODO 1" in output
    assert '"status": "passed"' not in output


@pytest.fixture(params=[solution, starter], ids=["reference", "learner"])
def completed_starter(request):
    module = request.param
    state = module.initial_state("probe", "brief", "probe.txt")
    try:
        module.approval_update(state, {"approve": False})
        try:
            module.attempt_save(state, Path("."))
        except ValueError:
            pass
        module.build_graph(None, Path("."))
    except NotImplementedError:
        pytest.skip("STARTER_NOT_COMPLETED: learner TODOs remain; not a pass")
    return module


@pytest.mark.parametrize("scenario", [
    "recover", "collision", "stale", "truthy", "repair_exhausted",
    "malformed_repair", "edited_draft",
])
def test_completed_starter_contract(completed_starter, scenario, tmp_path):
    module = completed_starter
    filename = "notice.txt" if scenario == "collision" else "../unsafe.txt"
    if scenario == "collision":
        (tmp_path / filename).write_text("existing", encoding="utf-8")
    before = {path.name: path.read_text() for path in tmp_path.iterdir()}
    model = NoticeModelDouble()
    graph = module.build_graph(model, tmp_path)
    a, b = config("starter-a"), config("starter-b")
    paused = graph.invoke(module.initial_state("a", "Cedar", filename), a)
    other = graph.invoke(module.initial_state("b", "Orchid", "other.txt"), b)
    assert paused["__interrupt__"] and other["__interrupt__"]
    assert paused["draft"] != other["draft"]
    assert {path.name: path.read_text() for path in tmp_path.iterdir()} == before
    if scenario in ("stale", "truthy"):
        decision = {"approve": True, "draft_hash": "old"}
        if scenario == "truthy":
            decision = {"approve": 1, "draft_hash": paused["draft_hash"]}
        final = graph.invoke(Command(resume=decision), a)
        assert final["status"] == "rejected" and not final["saved_path"]
        assert {path.name: path.read_text() for path in tmp_path.iterdir()} == before
    elif scenario == "edited_draft":
        approved = {**paused, **module.approval_update(paused, approve(paused))}
        with pytest.raises(ValueError):
            module.attempt_save({**approved, "draft": "changed"}, tmp_path)
        assert {path.name: path.read_text() for path in tmp_path.iterdir()} == before
    else:
        failed = graph.invoke(Command(resume=approve(paused)), a)
        assert failed["status"] == "save_failed" and failed["error"]
        assert not failed["saved_path"] and failed["__interrupt__"]
        assert len(model.calls) == 2
        repair_name = {
            "repair_exhausted": "../again.txt", "malformed_repair": "",
        }.get(scenario, "fixed.txt")
        final = graph.invoke(Command(resume=approve(
            paused, filename=repair_name,
        )), a)
        assert final["repairs"] == 1 and graph.get_state(a).next == ()
        assert final["draft"] == paused["draft"]
        if scenario in ("recover", "collision"):
            assert final["status"] == "saved"
            assert (tmp_path / "fixed.txt").read_text() == paused["draft"]
        else:
            expected = "rejected" if scenario == "malformed_repair" else "save_failed"
            assert final["status"] == expected and not final["saved_path"]
            assert {path.name: path.read_text() for path in tmp_path.iterdir()} == before
    if scenario == "collision":
        assert (tmp_path / "notice.txt").read_text() == "existing"
    assert graph.get_state(b).values["draft"] == other["draft"]
    assert graph.get_state(b).next == ("review",)
    rejected = graph.invoke(Command(resume={"approve": False}), b)
    assert rejected["status"] == "rejected" and not (tmp_path / "other.txt").exists()
    assert len(model.calls) == 2
