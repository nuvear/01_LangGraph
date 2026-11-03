# C01 — Document-grounded drafting capstone

## Prepare the capstone without confusing evidence types

**SUPPLEMENTARY · 180 minutes.** Learners need L01–L11, U1–U2 and S1–S2. The related source is [Drafter at 02:28:46](https://youtu.be/jGg_1h0qzaM?t=8926) and [RAG at 02:52:09](https://youtu.be/jGg_1h0qzaM?t=10329), not an original capstone assignment. Explain that this assessment combines earlier concepts and adds current approval and testing practices. The source video's global draft buffer and provider choices are not the required implementation.

Before class, have the parent or authorized instructor validate both real commands in fresh output directories. Confirm L11's `course_support.retrieval` and `data/rag_*` fixtures are integrated. Confirm the local embedding download has completed and record the actual fixture's name and nature. Do not claim the source video's finance answer or document page count for a replacement teaching document. Keep the runtime's credential handling unchanged; no credentials belong in teaching slides, graph state or screenshots.

The implementation author ran offline tests only. Treat a passing scripted-model test, a real Anthropic response, an inspected file and a server-side trace as different evidence. None substitutes for the others. Windows instructions remain unvalidated unless someone actually records a Windows run.

## Timed teaching sequence

### Minutes 0–15: explain and predict

Present the brief: produce a grounded teammate briefing, permit one revision, require review, and save a new file safely. Ask learners to draw the graph before displaying the original diagram. Expected predictions include a retrieval branch, a failure exit, an interrupt and a save node after approval. Challenge any drawing that saves within the model node or shares one global draft between threads.

<!-- ORIGINAL_DIAGRAM -->

### Minutes 15–40: demonstrate the baseline

Run `python -m pytest tests/lessons/test_c01.py -q`, then `python -m exercises.starters.c01`. Explain that the starter's honest result is `STARTER_NOT_COMPLETED`; the learner-acceptance test skips unfinished work rather than asserting that it passed. The other checks use named offline doubles and do not contact Chroma or Anthropic.

When authorized, run `python -m course_lessons.c01 --live --backend none`. Narrate the teaching driver: A and B both pause for clarification; A receives a request and reaches review; B remains empty. A requests one concise revision and is approved by the script. B receives an empty answer and terminates. Open the actual `saved_path`, compare its text with the reviewed state, and locate the source/page markers. Emphasize that a scripted approval demonstrates orchestration, not an authenticated person clicking an approval button.

### Minutes 40–65: inspect evidence and messages

Trace the three messages at the start of the state history: human request, AI tool request and matching `ToolMessage`. The next Anthropic call must see the result. Ask learners to compare a factual sentence with the actual fixture page. Expected response: valid references make checking possible but do not guarantee entailment.

Explain `tool_choice="auto"` for retrieval: current provider documentation lists models/settings that reject forced tool choices. The prompt explicitly requests the search and the graph rejects zero, multiple or unexpected calls. Drafting turns retain the tool schema for historical tool messages but use `tool_choice={"type": "none"}`. This bounds new tool activity without dropping the conversation protocol. Do not “repair” a missing tool call by injecting a fabricated AI response.

### Minutes 65–85: demonstrate failure handling

Inspect the focused tests rather than spending paid calls manufacturing every edge case. Show empty evidence, unknown citations, an invalid review decision, a second revision and a failed write. Expected statuses are `no_evidence`, `citation_failed`, `invalid_review`, `revision_limit` and `save_failed`. All must leave `saved_path` empty. On a failed write, approval may remain true: permission was granted, but the operation did not succeed. Have learners explain that distinction.

### Minutes 85–120: independent implementation

Assign the workbook's exact three functions in `exercises/starters/c01.py`: `assess_citations`, `decide_review` and `render_artifact`. Preserve the provided graph, real retrieval boundary and runtime. The exercise adds fingerprint-bound approval and a deterministic evidence inventory; it is not simply a rerun of the baseline. Offer the three hints in order, only when needed.

### Minutes 120–145: assess and recover

Run `python -m pytest tests/lessons/test_c01.py -q -k implemented_starter_acceptance`. A skip means the TODOs remain; require a genuine pass after implementation. Then run the entire C01 test file. Ask learners to inspect their starter with a deliberately stale fingerprint, not only an approved happy path. Use the complete reference solution after learners have attempted the task.

### Minutes 145–165: inspect live behavior and traces

Run `python -m exercises.solutions.c01 --live` in a fresh run directory. With synthetic fixtures only, repeat the demonstration separately using `--backend langsmith` and `--backend langwatch`. Locate the graph/tool/model relationships, review interrupts and save operation. Require server-side trace evidence before describing ingestion as successful. Defer backend-account issues to S1/S2 rather than modifying C01 to swallow them.

<!-- EXECUTION_FIGURES -->

### Minutes 165–180: review and defend decisions

Use the three student knowledge checks below. Ask each learner to distinguish thread isolation from durable persistence and fingerprint matching from authorization. Collect the saved artifact, test result and genuine live evidence; do not grade variable model wording as a literal-string exercise.

## Complete assessment answers

### 1. Why do retrieval and citation checks not prove grounding?

Similarity search normally returns top-k candidates even for a poorly supported request. A retrieved passage may be about the right topic without supporting the requested claim. The citation checker collects source/page markers and confirms a nonempty subset of retrieved markers; it does not compare sentence meaning with evidence. Tests should verify the actual retrieval invocation, matched tool-call IDs, source/page metadata, refusal/failure branches and file safety. A reviewer must open the cited page, compare the claim with its wording and reject unsupported inferences. The test suite intentionally documents that an invented sentence with a known marker can pass the structural gate.

### 2. Why resume A with A's ID, and what survives process exit?

The checkpointer selects state by thread ID. A's resume value must return to A's pending interrupt. Using B's ID would address B's clarification, not A's review; it does not transfer A's draft or authorization. Different fresh IDs isolate messages, hits, counters and draft state within the shared compiled graph. `InMemorySaver` loses these checkpoints when the process exits. The saved text file remains on disk, but it cannot reconstruct the entire approval checkpoint. U1 supplies the separate durable-backend discussion. Thread IDs organize state; they are not access-control credentials.

### 3. What happens with an old fingerprint or unsafe filename?

If D2 is current but the approval carries D1's fingerprint, `decide_review` returns `invalid_review`, `approved=False` and empty feedback. The graph ends without invoking save, and no draft file appears. If D2 is approved with its correct fingerprint but the name is `../escape.txt`, review succeeds and save is attempted. `safe_write_text` rejects traversal; the state becomes `save_failed`, `saved_path` stays empty, and no outside file is created. These are separate gates: content-bound permission first, filesystem restrictions second. A correct hash cannot authorize a path escape.

## Reference solution walkthrough

`assess_citations` rejects empty text and the insufficient-evidence sentinel before collecting markers with a regular expression. Its nonempty set must be a subset of exact helper-derived citations. `decide_review` initializes a fail-closed result, requires a dictionary, checks the current SHA-256 value for approval and strips bounded revision feedback. Every generated revision resets approval. `render_artifact` sorts de-duplicated `(source, page, id)` tuples and appends every retrieved chunk to `Evidence inventory`, preserving one trailing newline. This inventory describes available evidence rather than guaranteeing that all of it was cited.

The independent solution includes its own builder, `run_demo` and CLI; it does not import the baseline. The lazy L11 import prevents a concurrently absent sibling from breaking offline module imports. Live mode never falls back to the doubles. The solution driver asserts a real output file and unchanged content after unsafe and duplicate-write attempts.

<!-- SOLUTION_CODE -->

## Marking criteria and recovery

Assess five criteria at four points each: actual retrieval plus tool-message continuity; correct citation/refusal handling; current-fingerprint approval and one-revision termination; deterministic inventory plus safe file behavior; and clear test/live/trace evidence with thread-isolation explanation. Award full credit only when the behavior is demonstrated, partial credit for a correct explanation with incomplete implementation, and zero for a fabricated success path. Any credential exposure, save-before-approval or silent live-model replacement requires correction before completion, regardless of the subtotal.

For citation failures, compare exact source/page markers with the tool payload; do not weaken the checker. For stale approval, compute the fingerprint only after revision. For configuration-injection errors, use the installed API's `RunnableConfig` annotation. For missing embeddings/helper files, complete L11 integration rather than supplying a keyword fallback. For an existing filename, choose a fresh run directory; never delete another learner's artifact. A crash after file creation but before checkpoint completion is not transactional exactly-once delivery: no-overwrite protection prevents replacing the artifact, but recovery needs deliberate reconciliation.

## References

Verified on 3 November 2026: [LangGraph interrupts and replay](https://docs.langchain.com/oss/python/langgraph/interrupts), [ChatAnthropic integration](https://docs.langchain.com/oss/python/integrations/chat/anthropic), [Anthropic tool-choice compatibility](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools), [client-tool round trip](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) and [Chroma local embeddings](https://docs.trychroma.com/docs/embeddings/embedding-functions). Keep live validation and genuine screenshots separate from these documentation checks.
