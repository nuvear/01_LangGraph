# L07 — Anthropic stateless bot

## Teaching purpose and preparation

Teach one new boundary: a Python graph node can invoke a language model. Preserve the intentionally stateless behavior; do not introduce a checkpointer, append previous messages, or add tools. Learners should leave with a precise account of what was sent, not a belief that a Python loop automatically gives a bot memory.

Allocate 80 minutes: 10 to explain, 10 to illustrate, 15 for demonstration, 15 for guided practice, 20 for the independent task, and 10 for review. Prerequisites are L06 completion and an approved P00 Anthropic setup. Prepare synthetic prompts, the project environment, and permission for paid requests. Run the focused offline file, not the entire course suite while other lessons are being developed.

The example is a basic wrapper rather than a mature agent. The Anthropic implementation and help-desk assignment provide the complete practice sequence.

## Explain and illustrate: minutes 0–20

Ask learners to predict which component chooses the next node. Expected answer: LangGraph follows the registered edges; the model does not control topology here. Define `HumanMessage` as a user-role message and `AIMessage` as a model-response object. Use the [current integration documentation](https://docs.langchain.com/oss/python/integrations/chat/anthropic) to separate the shared chat interface from the underlying provider.

Trace the three invocations verbally. Compilation creates an executable graph. Graph invocation processes state. Model invocation inside the node produces an `AIMessage`. Emphasize partial updates: returning `reply`, `usage`, and `sent_messages` does not remove unchanged `messages` from the final graph state. A `TypedDict` annotation describes shape but does not validate incoming values; explicit checks enforce the lesson's one-message contract. These behaviors follow the [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api).

Use the concept diagram to distinguish the external input loop from a graph cycle. Point at the fresh-state node before each START. Collecting results for display is not the same as forwarding them to the model.

<!-- ORIGINAL_DIAGRAM -->

Use the concept figure to establish the intended teaching question: could the model guess a name even with no history?

<!-- CONCEPT_FIGURE -->

Ask, “Could the model guess a name even with no history?” Expected answer: yes. This is why exact response wording is not our test of state isolation. Anthropic's [Messages API documentation](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) states that conversational context must be supplied by the caller. Explain that API statelessness is not a promise about data-retention policy.

## Timed demonstration: minutes 20–35

For the first four minutes, show `build_bot` and its injected model, then `ask`. Highlight the fresh list allocation and the lack of a checkpointer. Show that the node forwards its `RunnableConfig` to the model, while `ask` obtains selected callbacks through `execution_config()`. No callback replacement is needed to teach the model boundary.

For the next four minutes, execute:

```bash
python -m pytest tests/lessons/test_l07.py -q
python -m course_lessons.l07 --live --backend none
```

The first command exercises named offline doubles. The second is a paid, real Anthropic run and must be authorized. It uses a scripted `read` function for two prompts and exit, avoiding an unattended input hang. Logical invocations number two; bounded provider retries may add HTTP attempts. The author has not made those live requests; record actual evidence before publication.

Spend four minutes interpreting the summary: `checked_turns` is two, `messages_per_request` is `[1, 1]`, `prior_turns_forwarded` is false, and the stop reason is `exit`. Replies must have displayable text, but no specific sentence is required. Usage may be `{}` when absent. Never translate a fixed token count into a historical price claim.

Use the final three minutes to inspect `terminal_chat`: blank input is skipped, exit is recognized after strip/casefold normalization, raw sent text is preserved, EOF is handled, and ten entries is the default cap. This is ordinary bounded Python control flow. A model exception is propagated; it is not replaced by a fabricated success response.

<!-- EXECUTION_FIGURES -->

## Guided practice and task briefing: minutes 35–50

Have pairs annotate the actual second request. Correct response: only `What is my name?`, without Bob, the first greeting, or an earlier AI response. Ask learners to predict behavior for blank input, ` ExIt `, and a model returning text blocks. The first two cause no model call; the helper extracts only textual response blocks from the third.

Introduce `exercises/starters/l07.py`. It is a separate implementation exercise with three TODO functions, not an import wrapper. Its initial CLI deliberately prints `STARTER_NOT_COMPLETED`; successful process exit is not successful assessment. Learners use the workbook's offline harness to check their own implementation. The delivered focused tests validate the demo and reference answer; the workbook harness assesses the learner functions.

The task's graph input is `prompt`, not the demonstration's `messages`. This deliberate variation checks whether learners can construct a message rather than merely copy a call. The required input sequence contains a blank, Mira's introduction, a name question, a mixed-case exit, and an unreachable final prompt. Require exact control behavior and inspectable one-message requests.

## Independent task and solution walkthrough: minutes 50–70

`classify_entry` validates string input and normalizes only the control comparison. It returns `exit`, `skip`, or `send`. Do not return normalized prompt text: whitespace preservation is part of this task.

`build_bot` creates a nested `respond` node. The node rejects control entries, constructs one `HumanMessage`, invokes the injected model with `config`, checks `AIMessage` and nonempty displayable text, and returns `reply`, `usage`, and the exact sent-text list. Two explicit boundary edges yield one node and no graph cycle.

`run_session` rejects invalid entry budgets, including booleans. `islice` bounds raw entries without consuming an extra item from an iterator. Increment `inspected` before branching so blank and exit entries count. On exit, break immediately; on blank, increment `skipped`; otherwise invoke with a new `{'prompt': raw}` dictionary. Collect returned states solely for reporting. The stop reason is `limit` when the budget is reached, even if the source also happens to end exactly there; otherwise early source exhaustion yields `exhausted`.

<!-- SOLUTION_CODE -->

The reference answer is independently runnable:

```bash
python -m exercises.solutions.l07 --live
```

It makes the same two logical model calls as the workbook sequence. It asserts two turns, one skip, four inspected entries, exit, and exact sent-message lists. Missing or unusable response text and simulated provider failures are covered offline. These checks cannot establish real credentials or model access.

## Full assessment answers: minutes 70–80

### Knowledge check 1

The second request contains exactly one `HumanMessage`, with `What is my name?`. `ask` constructs a new list for each invocation, the caller does not pass the earlier result back, and the graph has no checkpointer. The loop repeats execution, not conversational context. Reusing a graph or model instance is insufficient to create history.

### Knowledge check 2

`builder.compile()` produces the runnable graph after structural checks. `graph.invoke(...)` executes its nodes and returns graph state. `model.invoke(...)` performs the chat-model request and directly returns an `AIMessage`. The node converts selected message information into a partial state update. Compilation neither requests an answer nor verifies semantic correctness.

### Knowledge check 3

Only `My name is Mira. Say hello briefly.` and `What is my name?` are sent. Four entries are inspected, one blank is skipped, two turns are recorded, and the stop reason is `exit`. The fifth entry remains unprocessed. An exact denial assertion is unsuitable because generation varies and the model can guess or hedge; deterministic acceptance inspects the actual one-message payload, not a phrase.

## Marking, misconceptions, and recovery

Award ten marks: two for control classification and preserving raw text; three for the single-node graph, correct messages, and callback forwarding; three for bounded session behavior and exact counters; and two for explaining request isolation using recorded payloads. Require at least eight marks and all safety gates: no call for blank/exit, no forwarded history, finite processing, and no credentials in state. Fluent wording does not compensate for a failed gate.

If learners accidentally append history, remove that list and reconstruct state at the invocation boundary; explain that their change belongs in L08. If they add a thread ID alone, explain that persistent state also requires a configured checkpointer and suitable message-state handling; see [LangGraph memory](https://docs.langchain.com/oss/python/langgraph/add-memory), reserved for U1. If authentication fails, return to P00 without exposing secrets. If the starter still prints its initial status, use the harness rather than editing a success message. Do not solve a model-access error by weakening assertions or introducing canned production replies.

## References

References: [ChatAnthropic integration](https://docs.langchain.com/oss/python/integrations/chat/anthropic), [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [memory](https://docs.langchain.com/oss/python/langgraph/add-memory), and [Anthropic Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages).
