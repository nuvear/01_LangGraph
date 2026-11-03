# L10 — Human–AI Drafter collaboration

## Your task: workshop notice and honest save recovery

This **added practice** follows the video's 02:28:46–02:52:09 drafting workflow, not a detailed original assignment. See the [Drafter introduction](https://youtu.be/jGg_1h0qzaM?t=8926). Prerequisite: L09. Allow 90 minutes including guided practice; use synthetic data only.

Build a process-local Drafter that revises a complete email, fails safely on an occupied filename, then saves after new human feedback. Assess orchestration and file evidence, not exact wording. Persistence, voice, GUI, retrieval, and durable interrupts are outside this task; U2 adds safer state and approval/resume.

Implement `exercises/starters/l10.py` without importing the baseline `course_lessons/l10.py` or reference `exercises/solutions/l10.py`. Leave the reference closed during your first attempt.

## Exact scenario and implementation boundary

The supplied runner already provides the following human turns. Keep the scenario and its acceptance checks intact.

1. Draft an email to **Elena** postponing the training workshop. Initially propose `17 November at 09:00 Singapore time` and sign **Arun**. Call `update` with the entire email, then show the draft without saving.
2. Revise the schedule to the literal phrase `18 November at 14:30 Singapore time`. Remove `17 November` and `09:00`; preserve Elena and Arun. Put a blank line before the closing. Update the entire document again and wait.
3. The runner creates `workshop_taken.txt` with the exact text `Existing classroom file: preserve me.` followed by a newline. Request a save to this occupied name. It must fail without changing that file, revising the document, or claiming completion. Explain the failure and wait rather than choosing a new filename automatically.
4. After new human feedback, save the unchanged reviewed email as `workshop_notice.txt`. End immediately after the successful save tool result. Start a separate empty session with `write an email`; obtain clarification without a tool call, document update, or file write.

Implement only the three marked functions. In `make_tools`, define decorated `update(content: str)` and `save(filename: str)` tools closed over the supplied session. Reject blank drafts, finished sessions, unauthorized saves, and empty-document saves. Count successful updates only. Use the shared `safe_write_text` helper; set `saved_path` only after it returns.

In `after_tools`, return `end` when a real saved path exists or the four-model-call budget is exhausted; otherwise return `agent`. In `build_graph`, bind the tools, implement agent and tools nodes, preserve callbacks/configuration, and compile conditional routes. Reject unexpected multi-call batches without executing any member, but return an error for every call ID. Convert expected validation and filesystem exceptions into error `ToolMessage` results. The supplied host driver resets save permission and reports budget exhaustion.

Current model documentation distinguishes requesting a tool from executing it. A `ToolMessage` must match the request ID; tool availability does not force use. [1021]

## Run commands and collect evidence

From the repository root, with the prepared environment activated:

```bash
python -m exercises.starters.l10
python -m pytest tests/lessons/test_l10.py -q
```

The untouched starter prints `STARTER_NOT_COMPLETED` and exits successfully without a model request or fake pass. Focused tests validate the demonstration/reference using named offline doubles, not your edited starter.

After implementation, run your starter with authorized real calls:

```bash
python -m exercises.starters.l10 --live --backend none
```

For comparison after your attempt:

```bash
python -m course_lessons.l10 --live --backend none
python -m exercises.solutions.l10 --live
```

Use the default unique directory or a fresh `--output-dir`. Never disable collision protection to repeat a run. Inspect facts and state rather than exact prose. `--backend none` still sends model input to Anthropic.

Record these observed results in your working notes:

- **Draft revision:** record the initial and revised schedule, retained recipient/sender, revision count, and whether the closing has a preceding blank line.
- **Collision:** record the error type, `saved_path` value after failure, and the unchanged contents of `workshop_taken.txt`.
- **Recovery:** record the actual final path and the result of comparing its complete UTF-8 text with the revised in-memory document.
- **Clarification:** record the assistant's question, tool-result count, content length, and saved-path state for the new empty session.

## Three progressive hints

### Hint 1: separate history from the draft

`messages` is reducer-managed graph state, while the document is in the supplied process-local session. Return only new messages from nodes. At the next host invocation, pass the previous returned history once. Replacing a complete document is easier to verify than applying an ambiguous prose patch.

### Hint 2: implement truth before routing

Make the file writer the authority. A `FileExistsError` must reach the tools node, which produces `status="error"` with the same call ID. Do not set the path in advance, in `finally`, or in an exception branch. Then let the router inspect actual session state, not words such as “saved” in the assistant response.

### Hint 3: inspect the last message

After `agent`, route to tools only if the newest `AIMessage` has tool calls. After a successful save, do not call the model again. After an update or expected error, another model response can show the draft or explain the error. Forward the received `RunnableConfig` to both model and tool invocation; use `execution_config()` when entering the graph.

## Completion and stretch

You are complete when the three functions are implemented independently; two successful whole-document updates retain the required facts; the occupied file remains byte-for-byte unchanged; failed saving leaves `saved_path=None`; a new human request saves the latest draft to `workshop_notice.txt`; execution stops on that successful tool result; and the separate vague request uses no tool. Also demonstrate rejection of an unsafe basename or missing save permission, and explain why this process-local session is not durable interrupt/resume. Preserve your notes and actual artifacts as evidence.

For a stretch task, drive exactly three manually entered feedback turns through `take_turn`, displaying `session.content` after each. Keep the turn count bounded and retain the same save guards. Do not add an unbounded terminal loop or claim checkpoint persistence. Report which behavior depends on the model and which behavior is enforced by Python.

## References

[1021]: https://docs.langchain.com/oss/python/langchain/models "Official LangChain tool requests, execution loops, and matching result IDs"
