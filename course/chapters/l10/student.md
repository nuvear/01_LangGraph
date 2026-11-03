# L10 — Human–AI Drafter collaboration

## Explain: a draft is not a saved document

Allow 160 minutes, including guided practice and review. Before starting, complete L09 and be comfortable reading `AIMessage.tool_calls`, matching tool-result IDs, and following a conditional graph edge. This lesson adds a document that changes across human feedback, plus a filesystem side effect: writing a file.

A Drafter drafts an email, receives corrections, and saves when the human is satisfied. Its important outcome is not beautiful prose. It is a controlled progression from request, to editable draft, to reviewed revision, to a real saved artifact. The system must also handle a request too vague to draft responsibly.

By the end, you should be able to explain an agent/tools graph, replace a whole draft through a tool, retain conversation history between human turns, and prove that a successful save wrote the latest content. You should also recognize what this baseline does **not** provide: durable memory, concurrent editing, or a suspended graph that resumes after a restart.

The workshop-email exercise below provides additional practice with the same collaboration pattern. Treat it as a complete classroom task with its own acceptance criteria.

<!-- CONCEPT_FIGURE -->

## Illustrate: model choices and Python authority

A tool schema describes an action the model may request. Binding `update` and `save` does not execute them and does not force either to run. Our Python tools node dispatches the requested operation and appends a `ToolMessage` with the corresponding call ID. LangChain exposes provider-neutral `AIMessage.tool_calls`; Anthropic's underlying representation uses tool-use and tool-result blocks. [1001] [1002]

The graph has two working nodes. `agent` calls the model. If there are tool calls, a conditional edge selects `tools`; otherwise the invocation returns to the human. After tools, a successful file write ends the entire collaboration. An update or error normally returns to the agent so it can show the draft or explain the problem. A four-model-call budget prevents an unproductive turn from looping indefinitely.

<!-- ORIGINAL_DIAGRAM -->

Two different meanings of “stop” matter. A clarification or draft preview ends the **current graph invocation**, but the host Python program can collect another human response. A successful save sets `saved_path`, and the host refuses further turns for that finished session. Reaching `END` alone therefore does not establish that a document was saved.

`DraftState` contains messages and a model-call counter. The `add_messages` reducer merges newly returned messages with the existing history, using message IDs when replacing existing entries. Nodes return only their new messages, not another copy of the entire history. Without that discipline it is easy to append the same conversation twice. [1003]

The document itself lives in `DraftSession`, a dataclass: a Python object whose declared fields provide a convenient initializer. Tool functions close over this object. A **closure** is a function that retains access to values from the enclosing function where it was created. This avoids a module-global buffer, but it remains mutable process-local storage. It is not LangGraph state injection, a checkpointer, or a multi-user service design.

## Demonstrate: run and inspect the meeting email

Activate the prepared Python 3.12 environment and work from the repository root. No extra platform or voice key is needed. The baseline requires real Anthropic access through the shared runtime; without explicit live permission it raises an informative error rather than substituting canned text.

```bash
python -m course_lessons.l10 --live --backend none
```

This command sends synthetic classroom content to Anthropic. `--backend none` disables the course tracing integrations; it does not make the model call local. Only use synthetic data during practice. The model and tracing setup belong to P00 and the shared runtime; do not put configuration or credentials into graph state.

The runner supplies a finite sequence of human feedback instead of waiting at terminal prompts. First it requests an email to Tom explaining that Maya cannot attend a 10 a.m. meeting. Next it changes the sender to Priya and proposes the exact phrase `12:00 New York time tomorrow`, with a blank line before the closing. Finally it explicitly requests `meeting_email.txt` without further editing. A separate empty session receives `write an email` to check clarification.

Stable success properties are checked inside the program: the draft changes, the requested facts survive, the former sender disappears, and the written UTF-8 text equals the last revised buffer. The last message of the successful save turn is the save tool result; no extra model response is required after saving. Exact prose and the clarifying question vary. These are expected properties, not a claim that live execution has already been observed in this chapter.

The summary prints the real artifact path. Open that file and compare it with `final_document` in the summary. Outputs use a unique lesson-run directory by default. If you supply `--output-dir`, choose a fresh directory; repeated fixed-directory runs intentionally encounter existing-file protection.

<!-- EXECUTION_FIGURES -->

### Read the implementation

Read `course_lessons/l10.py` in this order: the session dataclass, `make_tools`, the two routers, `build_graph`, `take_turn`, and `run_demo`. Notice that `take_turn` receives the complete previous message list because no checkpointer retains it between invocations. Inside an invocation, nodes return only new messages. These two responsibilities are different.

`save_requested` is a host-controlled flag for this turn. It must be true before the save tool can write, then a `finally` block resets it even if execution raises. This is a small authorization guard, not LangGraph `interrupt()` or durable approval. Never let a model-generated argument decide this flag.

The shared writer accepts a new simple `.txt` basename, rejects traversal and symlinks, and creates the file exclusively so it cannot silently overwrite one. `saved_path` is assigned only after that operation returns. The tools node converts expected validation and file errors into `status="error"` messages so the model can respond honestly. Prompt instructions alone cannot enforce these file policies.

Both graph invocation and nested model/tool invocation preserve runtime configuration, including selected callbacks. The model wrapper is `ChatAnthropic`. Tool binding remains the same general pattern in the current official integration. [1001]

The implementation also applies several direct safeguards: a conditional edge skips tools on a clarification turn; actual saved state replaces scanning result text for a successful-save phrase; the complete `.txt` filename is required rather than automatically adding an extension; and scripted human turns make classroom validation finite. None of these safeguards introduces durable interrupt/resume.

<!-- EXAMPLE_CODE -->

## Guided practice: trace the turns

1. Run the baseline and locate the resulting file using the returned path. Confirm Tom, Priya, and the revised time phrase in both memory's reported final document and disk content. Do not compare an exact sample email.
2. Trace the first drafting turn on paper: human message, AI update call, update result, AI preview. Repeat for the revision, then explain why the save turn needs only human message, AI save call, and tool result.
3. Inspect the clarification branch. There should be no `ToolMessage`, no document update, and no saved path. A normal assistant response is a valid result; an empty tools node is not required.
4. Run the focused tests below. Read the named `ScriptedOfflineChatModel` double before interpreting results. It tests orchestration using explicit messages; it cannot demonstrate that Claude will follow a prompt.

```bash
python -m pytest tests/lessons/test_l10.py -q
```

Disabling parallel tool requests reduces ambiguity, but the executor also rejects unexpected batches without executing any member. Every requested call ID still receives an error result. This prevents an unexpected update-and-save batch from quietly performing two side effects. The model-call budget is an application rule, separate from the shared graph recursion limit. [1004]

## Independent task: workshop notice with failed-save recovery

Use `exercises/starters/l10.py` and the matching workbook. Implement its three TODO functions without importing the demonstration or reference solution. Draft an email to Elena postponing a training workshop, initially proposing `17 November at 09:00 Singapore time`, signed Arun. Revise it to `18 November at 14:30 Singapore time`, remove the old schedule, and retain a blank line before the closing.

The supplied runner creates `workshop_taken.txt` containing `Existing classroom file: preserve me.` followed by a newline. A human save request to that filename must fail without overwriting it or setting `saved_path`. After another human request, save the unchanged revised email as `workshop_notice.txt`. Finish with a separate underspecified-request check. The solution is independent code in `exercises/solutions/l10.py`; use it only after your attempt. Full completion criteria and progressive hints are in the workbook.

## Review: three knowledge checks

1. Why can `write an email` end an invocation without ending the overall drafting collaboration, and what evidence proves no tool ran?
2. After a revised draft is prepared, saving raises `FileExistsError`. What must remain unchanged, what field must stay unset, and how does the user recover?
3. Why is searching AI/tool text for `saved` unsafe as an exit rule, and why does keeping history plus `DraftSession` not provide durable interrupt/resume?

## Troubleshooting and next steps

If the runner reports missing `--live`, use the explicit live command only when authorized to send real requests. Authentication, access, or network failures are not reasons to insert fake responses. Return to P00 connection diagnostics; do not print secrets.

If an assertion reports a missing fact, inspect the actual model response and update call. The assertions deliberately reveal a prompt-following failure rather than claiming success. If the turn budget is exhausted, find the last tool error instead of raising the limit without investigation. A filename collision calls for a new human-selected filename, not overwriting the old artifact.

If history disappears after a restart, that is this baseline's documented limitation. U1 teaches checkpoints; **continue to U2 after L10** for explicit draft state and approval/resume. A saved text file preserves document content, not the suspended graph's execution position or conversation.

## References

[1001]: https://docs.langchain.com/oss/python/integrations/chat/anthropic "Official ChatAnthropic integration and normalized tool calls"
[1002]: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview "Official Claude client-tool execution overview"
[1003]: https://docs.langchain.com/oss/python/langgraph/graph-api "Official LangGraph state reducers and conditional edges"
[1004]: https://docs.langchain.com/oss/python/langchain/models "Official LangChain model tool binding and tool-result loop"
