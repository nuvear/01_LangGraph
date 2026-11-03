# U2 — Safe draft state and human approval/resume

## Task: approve exact content, repair a filename once

This is **added supplementary practice**, not original video homework. Allow about 30 minutes within the 90-minute U2 lab. Complete L10 and U1 first. You are extending the safety protocol, not writing a GUI or adding another provider.

Your fictional workshop assistant must generate each thread's notice once, pause before writing, and bind approval to the exact draft. If the first write fails, offer one filename-repair opportunity. Never regenerate or edit the text during repair. A second failed write must stop rather than create a retry loop.

Edit `exercises/starters/u2.py`. It is independent of the demonstration and has three focused TODO functions. Read `course_lessons/u2.py` for the baseline pattern. Consult `exercises/solutions/u2.py` only after attempting the task or during teacher review. The reference uses direct state updates and an additional hash/repair protocol; it is not an import of the baseline.

## Establish the starting behavior

From the repository root with the prepared environment active, run:

```bash
python -m exercises.starters.u2
python -m pytest -q tests/lessons/test_u2.py
```

The untouched starter prints `STARTER_NOT_COMPLETED` and exits successfully without loading credentials, invoking a model, or claiming a pass. The offline suite validates the demonstration and reference with named model doubles. Its completed-starter acceptance cases are explicitly skipped until your TODO functions exist; a skip is not exercise completion.

When authorized for real model use, the supplied reference commands are:

```bash
python -m course_lessons.u2 --live --backend none
python -m exercises.solutions.u2 --live --backend none
```

After completing your starter, run `python -m exercises.starters.u2 --live --backend none`. Do not modify the shared runtime, load credentials into graph state, or replace the real CLI model with canned output. Each live harness generates two notices and supplies scripted decisions; the approval protocol is real, but a separate human is not being simulated as evidence.

## Implement the three functions

1. **`approval_update`:** accept only a dictionary containing the actual boolean `True` under `approve` and a `draft_hash` matching the exact current draft and stored fingerprint. Reject malformed, missing, negative, or stale decisions. Clear any saved path. During repair, require a nonblank string filename, increment `repairs` once, and copy the filename only on valid approval. Never change `draft`.
2. **`attempt_save`:** require approved status and an approval fingerprint matching current content. Raise `ValueError` if that guard fails. Then call `safe_write_text`, returning `saved` and the actual path only after success. A writer `OSError` or `ValueError` must return `save_failed`, an empty path, and a useful error. Preserve any existing file.
3. **`build_graph`:** register the supplied nodes and compile with the supplied checkpointer or a new `InMemorySaver`. Route `START → generate → review`. Approved review goes to save; rejection ends. Successful save ends; first failure goes to repair. Approved repair goes to retry_save; rejection ends. retry_save always ends, including on failure. There must be no back edge.

Resume a pending ordinary review on the same thread with `Command(resume={"approve": True, "draft_hash": paused["draft_hash"]})`. Resume a repair with the same keys plus `"filename": "recovered.txt"`. Reject using `{"approve": False}`. Do not use an empty `Command(resume=None)` as rejection: the installed runtime does not treat it as a valid decision.

The SHA-256 digest fingerprints exact UTF-8 bytes, including whitespace. It detects stale approval; it does not authenticate a person. A server would separately authorize thread access. Keep the same graph/checkpointer instance for in-process resume; this lab does not promise restart persistence.

## Three progressive hints

### Hint 1: separate decision and effect

An interrupt payload is a request for a decision, not permission to write. The review node may replay. Return state updates after the decision; keep the writer in its later node. Use `is True`, not a generic truthiness test.

### Hint 2: compare the right hashes

Compare the submitted hash to the digest of current text, and ensure the stored fingerprint is also current. Before saving, compare `approved_hash` to the text again. A stale decision must never be repaired by silently changing its hash.

### Hint 3: bound recovery structurally

Use a separate `retry_save` node with an edge directly to END. Reusing the Python save function is fine; routing retry failure back to repair is not. Validate malformed repair names before approval, and let the safe writer reject traversal and collisions.

## Record concrete observed results

Record the command used and whether the evidence came from an offline double or a real Anthropic run: __________.

Record Cedar's thread ID, Orchid's different thread ID, and the two pending node names before either write: __________.

Record the first failed filename, failure status, empty saved-path value, and error class: __________.

Record the final artifact path and whether its exact text equals the original paused draft: __________.

Record the model-call count across repair, final repair count, and Orchid's unchanged pending draft before rejection: __________.

Record the stale-hash result and the terminal result after a second unsafe filename: __________.

These fields require observations, not predicted screenshots. Model wording can vary; do not require a particular greeting.

## Completion criteria and stretch

Run `python -m pytest -q tests/lessons/test_u2.py -k completed_starter` after implementation. All completed-starter acceptance cases must run rather than skip. Also run the full focused U2 test file, not the whole course suite.

Completion requires no write before approval; isolated pending drafts; rejection of stale approval; an unchanged existing file after collision; exactly one repair; unchanged content and no extra generation during repair; and a terminal honest failure if the repaired name remains unsafe. A fresh successful output must contain the exact approved bytes. Only authorized parent or classroom live validation establishes real model behavior; offline doubles cannot do so.

As a stretch, design a reconciliation policy for a crash after file creation but before checkpoint confirmation. Describe how to inspect the existing artifact without overwriting it or falsely declaring exactly-once delivery. Implementation is optional and must not weaken the required bounded workflow.

## Reference

The current [LangGraph interrupt documentation](https://docs.langchain.com/oss/python/langgraph/interrupts), searched and fetched on 3 November 2026, explains same-thread `Command` resume and replay rules. The accompanying student chapter explains how this added task differs from L10's video workflow.
