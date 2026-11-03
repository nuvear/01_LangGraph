# U2 — Safe draft state and human approval/resume

## Why a draft needs a boundary

A useful drafting assistant must distinguish “the model produced text” from “the user approved a file write.” This 90-minute lab makes that boundary executable. Complete L10 and U1 first. You should already recognize a state dictionary, a node, a conditional edge, a tool message, and a checkpoint thread.

The lab uses a shared draft-writing pattern as a starting point, then makes state ownership, approval, replay, and bounded recovery explicit. Everything required below is self-contained practice.

By the end, you will keep drafts in explicit thread state, inspect a real interrupt, resume the correct checkpoint, and prove that rejection creates no file. You will also test traversal, overwrite, and failed-save behavior. This is not an email sender or a production authorization service.

## Replace shared content with explicit state

A module-level variable such as `document_content` has one value for the Python process. If Cedar and Orchid sessions both update it, the second update can replace the first. A tool that later saves “the document” may save whichever value happens to be present. A variable name does not establish ownership.

The baseline instead defines `DraftState`. Each initial request supplies a session label, brief, and filename. It initializes draft, status, error, saved path, and messages explicitly. The checkpointer selects a separate state history using `thread_id`. The human-readable `session` field helps inspection; the configuration's thread ID actually selects the checkpoint. Do not confuse the two.

A node returns a partial update rather than modifying a global buffer. `draft` uses ordinary replacement semantics. Only `messages` uses `add_messages`, so an update to the draft is not accidentally concatenated with an earlier version. After generation, the state can say `awaiting_approval` while `saved_path` remains empty. That is an important truthful intermediate state.

Thread isolation is a data-management property, not access control. In a real service, the server must authorize which signed-in user may access a thread. Knowing a thread ID must not itself grant permission.

## How the update tool receives the right draft state

The baseline's `update_draft(content, runtime)` tool returns a `Command(update=...)`. Its `runtime.state` refers to the current graph task's state. `ToolNode` injects `ToolRuntime`; it is not a parameter the model chooses. The tool also returns a `ToolMessage` using `runtime.tool_call_id`, which matches the request being completed. Official [tool documentation](https://docs.langchain.com/oss/python/langchain/tools) describes both requirements.

There is a deliberate simplification here: Anthropic generates ordinary notice text, and Python constructs one fixed `update_draft` tool call carrying that text. The coordinator selects the handoff. This is not a demonstration of Claude autonomously choosing a tool, nor a new ReAct loop. It lets you study runtime injection without making the safety policy depend on model tool selection.

The installed imports use `langchain_core.tools.tool` and `langgraph.prebuilt.ToolRuntime`. Some current examples import these through the broader `langchain` package. The equivalent installed interfaces were checked locally; this module does not require installing that umbrella package. No draft content is stored in a cross-thread global.

## Pause now; resume the same thread later

The graph runs generation and the update tool, then enters `review`. This node calls `interrupt()` with a JSON-serializable payload containing the session, filename, and exact draft. The default `invoke()` result exposes pending interrupts under `__interrupt__`. Inspecting that result proves that execution paused; a printed “please approve” message alone would not.

A checkpointer and thread ID are essential. To approve the baseline, invoke the same graph with `Command(resume=True)` and the same configuration. To reject, use `Command(resume=False)`. Only the actual boolean `True` authorizes saving. The string `"yes"` and integer `1` are not accepted merely because Python treats them as truthy.

LangGraph restarts the interrupted node from its beginning on resume. It does not continue a frozen Python stack at the next line. For that reason, the review node contains no model call and no file write before `interrupt()`. Generating the draft is an earlier completed node; saving is a later node. Do not surround `interrupt()` with a broad exception handler. Its suspension signal must reach the graph runtime. These rules follow the official [interrupt guide](https://docs.langchain.com/oss/python/langgraph/interrupts).

The CLI demonstration supplies scripted approval and rejection responses so its assertions are reproducible. It exercises the real interrupt/resume mechanism, but does not claim an independent person approved anything. An application would display the payload and forward an authorized human's decision instead.

## Put filesystem policy outside the model

`save_draft` first requires approved state. It then calls the shared `safe_write_text` helper. The helper accepts a new simple `.txt` filename beneath an explicit output directory. It rejects path components, absolute paths, parent traversal, and symlink targets. Exclusive creation prevents silently replacing an existing file. Asking the model not to overwrite is not a substitute for these checks.

A successful write returns `status='saved'` and the actual saved path. A caught filesystem or filename error returns `status='save_failed'`, a nonempty error, and an empty saved path. Never set the success status before calling the writer. A permission failure does not become success because a model says “done.”

Use a trusted output directory. These teaching checks are not a complete sandbox against an attacker concurrently replacing parent directories. Filesystem writes and checkpoint commits also do not form one atomic transaction. A crash after creation but before checkpoint confirmation can leave a real file with uncertain graph status. An I/O failure can leave a partial file. Do not claim exactly-once delivery; inspect and reconcile such artifacts rather than overwriting them.

## Guided practice: observe two independent sessions

1. From the repository root, activate the prepared environment. Run `python -m exercises.starters.u2`. Before implementation it exits successfully with `STARTER_NOT_COMPLETED`; that is an honest unfinished status, not a test pass.
2. Read `course_lessons/u2.py`. Follow `generate → update → review`. Locate the separate save node and explain why it cannot run while review is interrupted.
3. When authorized to use the configured Anthropic model, run `python -m course_lessons.u2 --live --backend none`. This requires real API access; without `--live`, the example refuses to substitute canned output. The author has not run that live command here.
4. Follow the two thread configurations in `run_demo`. Both Cedar and Orchid pause before either output file is created. Cedar then resumes with approval. Orchid remains pending with its own draft until it resumes with rejection.
5. Inspect the returned saved path. The file must contain exactly Cedar's approved draft, including whitespace. Orchid must have no saved artifact. Do not grade the notice against a memorized sentence: model wording varies.
6. Read the overwrite and traversal assertions. These intentionally fail safely and must leave Cedar's existing bytes unchanged. Run `python -m pytest -q tests/lessons/test_u2.py` for offline evidence using explicitly named doubles, not live model responses.

<!-- ORIGINAL_DIAGRAM -->

The concept diagram separates the baseline path from the workbook extension. In both paths, a pending interrupt precedes any write. The extension has a second approval boundary only after the first save fails.

<!-- EXAMPLE_CODE -->

<!-- EXECUTION_FIGURES -->

## Independent task: approve exact content and repair once

Implement the workbook's **hash-bound approval and one filename repair** extension in `exercises/starters/u2.py`. Finish exactly three focused functions: `approval_update`, `attempt_save`, and `build_graph`. Supplied node bodies generate a draft once and compute its SHA-256 digest, a deterministic fingerprint of its exact UTF-8 bytes.

Approval must be a dictionary containing `approve: True` and the current `draft_hash`. Reject a missing, stale, malformed, or negative decision. Verify approval again before writing. If the first save fails, interrupt once more with its error and unchanged draft. Accept a new nonblank string filename only with fresh hash-matching approval. Try saving once more, then stop whether that attempt succeeds or fails. There is no regeneration, content editor, or retry loop.

Prove that two threads remain isolated, an existing file survives a collision, and a second unsafe filename ends with `save_failed` and no saved path. The independent reference is `exercises/solutions/u2.py`; it uses direct state updates rather than copying the baseline's tool adapter. Consult the workbook for decision payloads and completion criteria.

## Knowledge checks

1. Why can two different `session` labels still share the wrong checkpoint, and what configuration value actually separates their histories?
2. What executes again after `Command(resume=...)`, and why are generation and file writing outside the interrupted review node?
3. In the workbook extension, what should happen when approval contains an old draft hash, and what should happen when the one repaired filename is still unsafe?

## Troubleshooting and limits

If the CLI requests `--live`, use the prepared setup rather than modifying `get_model` to return a fake. If authentication or model access fails, return to P00; never paste credentials into state or traces. Offline tests use injected `NoticeModelDouble` instances and prohibit network connections and credential loading.

If a resume does not reach the expected draft, compare the original and resumed thread IDs and check that you kept the same graph/checkpointer instance. `InMemorySaver` loses checkpoints when the process exits; [persistence documentation](https://docs.langchain.com/oss/python/langgraph/persistence) distinguishes this from durable storage. U1 covers restart durability. Use an explicit rejection payload, not `Command(resume=None)`: the installed LangGraph version raises internally for an empty resume command.

If a filename fails, do not loosen validation. Select a new simple filename within the output directory. Default runs use fresh directories; reusing an explicit directory with an existing target should fail rather than replace prior work. Only focused local offline tests are evidence at authoring time. Parent validation supplies actual Anthropic runs and execution figures; no Windows, dashboard, or production durability success is asserted here.

## References

- [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts): suspension, same-thread resume, replay rules, and default `invoke` output.
- [LangChain tools](https://docs.langchain.com/oss/python/langchain/tools): runtime injection, hidden tool arguments, and state-updating commands.
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence): thread checkpoints, stores, and memory-only limitations.

The official documentation links above provide the current API guidance for this lab.
