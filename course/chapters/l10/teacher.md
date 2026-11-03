# L10 — Human–AI Drafter collaboration

## Explain: teaching purpose and preparation

Teach this core lesson after L09; allow 160 minutes. Students must distinguish a model's suggestion, a Python tool's action, and evidence on disk. Prerequisites are tool-call IDs, `add_messages`, and conditional edges.

Before class, activate the prepared environment and run only the focused offline tests. Parent live validation supplies execution figures; do not treat test-double output as Anthropic evidence. For an authorized demonstration, run `python -m course_lessons.l10 --live --backend none` with synthetic data and a fresh output directory. Never expose credentials.

Allocate 15 minutes to explanation, 10 to illustration, 25 to demonstration, 25 to guided practice, 65 to the independent workshop task, and 20 to review. Installation and service troubleshooting belong to P00, not to the practice allocation.

Frame the lesson around a controlled drafting collaboration: a per-graph closure over a dataclass holds the editable document, Python tools enforce file policy, and the host collects further human feedback until a real save succeeds. Emphasize the process-local limitation and defer state injection and durable approval to U2. The workshop notice is a complete practice task with explicit acceptance criteria.

<!-- CONCEPT_FIGURE -->

## Illustrate: establish the two stopping conditions

Ask students to explain what `END` proves. Expected initial response: “the graph stopped.” Refine it to “this invocation stopped”; that does not prove saving. Draw the no-tool route from agent back to the host, then the tool-success route that also leaves a non-null saved path. The host accepts another human turn only in the first case.

<!-- ORIGINAL_DIAGRAM -->

Review the reducer rule: the host supplies full previous history to a fresh, non-checkpointed invocation, but each node returns only its new messages during that invocation. `add_messages` handles message IDs as well as adding new messages. Current official graph documentation supports this distinction. [1011]

Ask where file authority resides. Expected answer: “Python executes the tool, and the restricted writer decides whether the path is acceptable.” Tool binding advertises capabilities; it does not execute them. Claude's client-tool protocol requires the application to perform actions and return results connected to tool-use IDs. [1012] [1013]

## Demonstrate: a 25-minute live walkthrough

In minutes 0–5, inspect `DraftSession` and the two tool closures. Explain the complete-document replacement rule. Incrementing `revision_count` means a successful update happened; it does not prove the model's prose is correct. Show that `saved_path` is assigned only after the file writer returns.

In minutes 5–12, run the baseline. Read the synthetic feedback sequence before execution: Tom, missed 10 a.m. meeting, initial sender Maya; then sender Priya and the literal revised phrase `12:00 New York time tomorrow`; finally a save request. Invite predictions about the number and types of messages, not exact wording. A usual drafting turn is Human → AI tool request → Tool result → AI preview. The save turn ends on the tool result without another model call.

In minutes 12–18, open the actual artifact reported by the summary and compare its text with `final_document`. The program asserts correspondence. Do not announce success if an assertion, provider error, or file error occurred. Explain that `--backend none` disables course tracing but still sends real requests to Anthropic.

In minutes 18–25, inspect the separate `write an email` session and its no-tool route. Binding is automatic/optional here; forcing a tool would undermine clarification. Show the four-model-call application budget and the separate recursion-limit configuration. Both the graph and nested model/tool invocations forward callback configuration. [1013]

<!-- EXECUTION_FIGURES -->

## Guided practice: make state changes observable

Have pairs trace the first and second turns in the baseline, then predict the saved file. Ask one learner to locate the point where the human's `save_requested=True` enters Python, and another to locate its reset in `finally`. Expected explanation: the host authorizes this turn; an LLM-generated tool argument cannot grant permission. This is not durable approval or an `interrupt()` call.

Run `python -m pytest tests/lessons/test_l10.py -q`. Read `ScriptedOfflineChatModel` with learners. Its authored responses exercise routes deterministically while settings loading and network access are blocked. These tests cover both demonstration and reference solution; they do not automatically grade a student's changed starter. Require the learner's own completed starter run and inspected artifacts as additional evidence.

Discuss the rejected multi-call batch. Although binding disables parallel tool requests, the executor still rejects an unexpected batch before performing any member, returning one error per ID. This makes an update-and-save ambiguity visible instead of silently doing both.

## Independent exercise: solution walkthrough

The exact task is the workshop notice in the student chapter and workbook. Students implement `make_tools`, `after_tools`, and `build_graph` in `exercises/starters/l10.py`; the supplied host driver and acceptance scenario stay in place. Initial content addresses Elena, postpones the training workshop, proposes `17 November at 09:00 Singapore time`, and signs Arun. The revision changes the schedule to `18 November at 14:30 Singapore time` and removes the old schedule, keeping a blank line before the closing.

Walk through `exercises/solutions/l10.py` only after an independent attempt. It is independent implementation, not an import of the baseline. `make_tools` protects empty/finished sessions, counts successful updates, and delegates safe file creation. `after_tools` routes on actual `saved_path` and the budget. `build_graph` supplies model, dispatch, matched messages, error statuses, and conditional edges.

The runner pre-creates `workshop_taken.txt` with `Existing classroom file: preserve me.` plus a newline. The requested save collides and returns an error; the existing file, draft content, and revision count remain intact. The model must explain and wait rather than invent a new filename. A new human request authorizes `workshop_notice.txt`. The solution verifies its bytes against the reviewed draft and checks a separate clarification session. Use `python -m exercises.solutions.l10 --live` for the authorized reference run, with a fresh output location.

<!-- SOLUTION_CODE -->

## Review: full answers to the three knowledge checks

### 1. Invocation end versus collaboration end

`write an email` lacks recipient and purpose, so the expected response is a clarifying question without a tool call. The agent's no-call route reaches `END` for that invocation. The host may accept more feedback because `saved_path` remains unset. Evidence includes no `ToolMessage` in this new session, unchanged empty content and zero revisions, and no written artifact. A question alone is insufficient evidence if a tool also ran earlier in the turn.

### 2. Collision and recovery

`FileExistsError` means the exclusive create failed. The existing file must retain its original text; the latest draft and its successful-update count must not change merely because saving failed. `saved_path` must remain `None`. Return an error result matched to the save call ID, let the assistant explain, and wait for a human-selected new basename. The subsequent approved save should write the unchanged final draft to `workshop_notice.txt`. Never mark success in an exception handler or overwrite the protected file to make the test pass.

### 3. Truthful exit and durability

Searching text for `saved` can match an untrue assistant assertion or an error such as “not saved.” Only actual successful file creation may set `saved_path` and trigger successful completion. Keeping message lists and a dataclass in Python preserves state only while the owning process and objects remain available. A restart loses them. A text file preserves content but not execution position or the conversation. U1/U2 introduce checkpoint/thread and explicit approval/resume mechanisms; this lesson does not claim them.

## Marking criteria, misconceptions, and recovery

Award ten points: two for whole-document updates and correct revision counting; two for conditional topology, message pairing, and callback forwarding; two for human-request gating and safe exclusive writing; two for truthful collision handling and subsequent recovery; one for clarification without tools; one for artifact inspection and an accurate explanation of process-local limits. Require all safety criteria even if the numerical score is otherwise high. Do not award literary-style points or require a memorized model response.

A frequent misconception is that returning `END` automatically saved something. Ask for the file path and contents. Another is that the closure is durable LangGraph state: ask what reloads it after restarting Python. If history is duplicated, inspect whole-history returns from nodes. If a budget error occurs, inspect the last tool error rather than raising limits. If model behavior misses a required fact or retries a collision, record it as a live failure and refine the instruction with the learner; do not substitute the offline double. Preserve failed evidence and use a new directory for the next run. Continue to U2 after L10 for the explicitly added safer-state lab.

## References

[1011]: https://docs.langchain.com/oss/python/langgraph/graph-api "Official LangGraph reducers and routing"
[1012]: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview "Official Claude application-executed tool protocol"
[1013]: https://docs.langchain.com/oss/python/langchain/models "Official LangChain model tool binding and result pairing"
