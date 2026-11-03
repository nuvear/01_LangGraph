# U2 — Safe draft state and human approval/resume

## Teaching position and evidence

Teach this supplementary 90-minute lab after L10, with U1 completed first. Begin with the shared draft-buffer pattern, then make state ownership, checkpointed approval, and bounded filename repair explicit. Keep the focus on the assigned protocol rather than adding a GUI, voice interface, or knowledge-base integration.

The student sequence is explanation, baseline illustration, timed demonstration, guided practice, one independent workbook task, and review. Preserve it. The baseline demonstrates runtime-injected state through `ToolNode`. The workbook independently implements direct state updates with hash-bound approval and a single filename-repair opportunity. Both call real Anthropic through the shared runtime when explicitly run live. Offline evidence is produced with named doubles only.

At authoring time no live API, tracing, or Windows validation has been performed by this lesson author. Parent integration must run both entrypoints, inspect the actual files, and insert execution figures. Avoid announcing that a screenshot or dashboard exists before that evidence is available.

## Minutes 0–15: explain state and side effects

Start with two fictional sessions, Cedar and Orchid. Ask what happens if both write a module-level `document_content`. Expected answer: there is only one shared variable, so the later draft can replace the earlier draft regardless of who requested the save. A Python module is not automatically a user session.

Open `DraftState` and `initial_state`. Ask which value identifies the checkpoint. Learners often point to `session`; correct them gently. That label is ordinary state. `configurable.thread_id`, passed through `execution_config`, selects the history. The checkpointer must also be the same retained instance when resuming.

Explain that a side effect changes something outside graph state. A text file remains after an in-memory graph disappears. Conversely, an interrupted state can exist without any file. Require learners to describe these as separate facts. A `saved` flag alone is not artifact evidence.

## Minutes 15–30: illustrate runtime injection and replay

Trace `generate → update → review → save`. Anthropic returns plain text. The coordinator builds a fixed update-tool request, and `ToolNode` injects `runtime.state`. Make the distinction explicit: Claude is not autonomously selecting this tool. Keeping that choice in the coordinator makes state ownership and approval behavior observable.

Show the tool's `Command(update=...)` and the `ToolMessage` with the matching call ID. The runtime parameter is hidden from the model-facing schema. The official [tool guide](https://docs.langchain.com/oss/python/langchain/tools) documents this pattern; the local imports use `langchain_core` and `langgraph.prebuilt` rather than requiring the umbrella `langchain` distribution.

Next, explain that `interrupt()` suspends through the graph runtime, and the interrupted node restarts from its beginning on resume. A model call before the interrupt inside that same node could run twice. A file write there could happen before approval and repeat on resume. Separate completed generation and later saving solve the teaching case. Do not wrap the interrupt in a broad `try/except`. The [interrupt guide](https://docs.langchain.com/oss/python/langgraph/interrupts) is the current source for these rules.

<!-- ORIGINAL_DIAGRAM -->

## Minutes 30–45: timed baseline demonstration

1. **Minutes 30–33:** run `python -m exercises.starters.u2`. Show `STARTER_NOT_COMPLETED`, exit success, and no false pass. State that a starter is not a completed exercise.
2. **Minutes 33–37:** when live use is authorized, run `python -m course_lessons.u2 --live --backend none`. Explain that the harness creates two real drafts, reaches two real interrupts, and then supplies scripted decisions. These are reproducible protocol checks, not independent human review.
3. **Minutes 37–41:** inspect the returned artifact. It must contain the exact Cedar draft. Orchid must remain unchanged until its rejection, with no Orchid file. The live notice wording need not match an example sentence.
4. **Minutes 41–45:** show the traversal and collision failure checks. Success means the unsafe requests fail, their saved paths remain empty, and the existing Cedar file is unchanged. Run `python -m pytest -q tests/lessons/test_u2.py` if time permits; clearly label doubles and distinguish these results from live service evidence.

The default run uses a fresh directory. With an explicit reused output directory, an existing target should produce a failure, not an overwrite. Do not delete a learner's artifact simply to force a green demonstration; choose a new directory.

<!-- EXECUTION_FIGURES -->

## Minutes 45–75: independent workbook task and solution walkthrough

Assign exactly the student's hash-bound approval and one filename-repair extension. Learners finish `approval_update`, `attempt_save`, and `build_graph` in `exercises/starters/u2.py`. The supplied nodes already generate once, compute a SHA-256 fingerprint, expose the review payload, and prepare a repair interrupt. This is not a request to add a GUI, build a ReAct agent, or make a second content revision.

In `approval_update`, require a dictionary with `approve is True` and a hash equal to both the recorded fingerprint and the digest of current text. Reject malformed decisions rather than relying on truthiness. Ordinary approval does not change the requested filename. Repair additionally requires a nonblank string filename, increments `repairs`, and still cannot modify the draft. Unsafe-but-nonblank names reach the safe writer and fail honestly; blank or nonstring repair names are rejected earlier.

In `attempt_save`, check approved status and the current content's hash before calling the shared writer. Only return `saved` after it succeeds. Catch filename and filesystem failures around the writer, not around the interrupt. Preserve `saved_path=''` and a nonempty error on failure. The hash detects stale content; it is not a signature, identity check, or permission system.

In `build_graph`, require five nodes: generate, review, save, repair, and retry_save. First failure routes to repair. Approved repair routes to retry_save, which always ends. There is no backward edge and no third approval prompt. A repaired unsafe filename therefore produces a terminal `save_failed`, not a recursion-limit exception. Rejection at either approval ends without a new write.

The independent reference implementation lives at `exercises/solutions/u2.py`. Run `python -m exercises.solutions.u2 --live --backend none` only when authorized. Its first filename deliberately traverses upward, then its scripted repair chooses `recovered.txt`. Expected stable properties are one generation per thread, unchanged text across repair, one repair consumed, a real exact-content file, and the second thread untouched until rejection.

<!-- SOLUTION_CODE -->

## Minutes 75–90: assessment answers and marking

### Knowledge check 1

Two different `session` labels do not establish different checkpoint histories. They are ordinary fields, and reusing the same `configurable.thread_id` addresses the same thread. Use separate thread IDs while retaining the intended checkpointer. In a real multi-user service, authenticate the caller and authorize thread ownership separately. A global buffer remains unsafe even if labels differ.

### Knowledge check 2

The interrupted review node executes again from its beginning. Earlier completed generation is not repeated merely because review resumes; the separate save node runs only after an accepted decision. Keeping expensive or non-idempotent work outside the replayed prefix avoids duplicate model calls and premature writes. Explain that this layout does not make file creation and checkpoint storage one atomic transaction.

### Knowledge check 3

An old hash must produce rejection with no save. After the first failed save, the repair opportunity can supply a new filename with current hash approval. If that repaired name is still unsafe, the final attempt ends with `save_failed`, an empty saved path, and a useful error. No third interrupt, silent overwrite, or automatic regeneration is permitted.

Award ten marks: two for explicit isolated state and two pending threads; two for strict current-hash approval and rejection; two for guarded safe writes and truthful error state; two for exactly one repair with unchanged text; and two for observable acceptance evidence, including preserved existing bytes and no regeneration. A solution that writes before approval cannot pass even if its final status looks correct. Do not score prose quality of model output as protocol correctness.

## Recovery and misconceptions

If a learner gets no expected resume, inspect thread ID, checkpointer identity, and pending `snapshot.next` before changing node logic. Use explicit rejection payloads rather than `Command(resume=None)`; the installed LangGraph version raises internally for an empty resume command. If the process restarted, `InMemorySaver` lost its checkpoints. The [persistence guide](https://docs.langchain.com/oss/python/langgraph/persistence) explains the difference; reuse U1's durable-backend lesson rather than claiming RAM persists.

If saving fails, inspect the error and output directory. Do not bypass traversal or overwrite checks. A crash or partial I/O error can leave an artifact requiring reconciliation, even with no successful checkpoint. Thread isolation is not filesystem isolation: two threads choosing the same path can collide, and safe exclusive creation should protect the first file. Keep output directories trusted and use only fictional classroom content if tracing is later enabled.

## References

Use the official [interrupt guide](https://docs.langchain.com/oss/python/langgraph/interrupts), [tool guide](https://docs.langchain.com/oss/python/langchain/tools), and [persistence guide](https://docs.langchain.com/oss/python/langgraph/persistence) for the current API behavior. Metadata records the locally checked package versions and remaining live-validation limits.
