# L08 — Conversation history and logging

## What you will learn

A chatbot can answer a follow-up about your name only if relevant information reaches the model again. In L07, each invocation received an independent input. Here you will retain both sides of a conversation, send accumulated turns, and export a readable transcript without correcting the user's text. You will also separate three things that are often called “memory”: the history held by Python, the messages included in a model request, and data written to disk.

Prerequisites are L07, Python lists and dictionaries, and the prepared Anthropic connection from P00. Allow 125 minutes including practice. Both completed examples require real Anthropic calls when run from the terminal. Offline tests use explicitly named doubles instead; they are not proof of model access or recall.

Use the Steve name-recall scenario, a state-prediction pause, the distinction between process restarts and retained history, and role-labeled logging to establish the lesson goal. The finite scripted runners, safe output files, reducer comparison, tests, and bounded-prompt task provide the practice. Anthropic is the configured provider for the live examples.

<!-- CONCEPT_FIGURE -->

## Explain: messages carry the conversation

A `HumanMessage` represents user input. An `AIMessage` represents the model's reply. The role is structured data, not merely a prefix added to a string. The list order matters: a completed plain-text turn is normally human then AI. A pending request adds another human message at the end. Our lesson intentionally excludes system instructions and tools from the history-window exercise; later lessons need policies that preserve their additional constraints.

Before the first call, the history contains `H1`. After the answer it contains `H1, A1`. Before the second call, send `H1, A1, H2`; afterward retain `H1, A1, H2, A2`. The model is not reading a hidden Python variable. Your program supplies the relevant messages in each request.

The demonstration defines an ordinary `TypedDict` channel named `messages`. Without a custom reducer, a returned update replaces that channel. Its node therefore returns a new list containing the input history and the new response. Returning just `[response]` would lose the human message and earlier turns. The code avoids mutating the caller's list and preserves the actual `AIMessage`, including its ID and usage metadata.[801]

Keep structured messages until you deliberately export text. Anthropic responses can contain text blocks rather than only a string; the shared `message_text` helper extracts visible text for this lesson. Reconstructing every reply with `AIMessage(content=response.content)` is unnecessary and can discard useful metadata.[803]

## Illustrate: two histories serve different purposes

The diagram shows the exercise's reducer path. “Full history” means all turns still held by the caller. “Prompt window” means the subset sent to this particular model call. Returning one AI delta updates full state; selecting a smaller prompt does not delete older state. The demonstration uses the same one-node graph shape but replaces its plain list with the complete updated list instead of using a reducer.

<!-- ORIGINAL_DIAGRAM -->

A text export branches away from state. There is deliberately no arrow from the file back into a new process: nothing in L08 reads it to restore history. U1, the added lab after L08 in the learning path, introduces thread-scoped checkpoints and durable storage. Creating a text file is useful, but it is not that checkpoint mechanism.[802]

## Demonstrate: carry history and write a log

From the repository root, with the P00 environment active, run:

```bash
python -m course_lessons.l08 --live --backend none
```

This performs three logical model invocations, excluding any retries. Two form a carried conversation: the synthetic user introduces Steve, then sends `gud morning! What name did I give you?`. The third supplies an empty prior history and asks about the name again. It is a reset simulation, not an automated restart of the operating-system process.

The runner asserts two then four stored messages, alternating roles, unchanged human text, and Steve appearing in the recall answer. The separate fresh-history result contains only its own human/AI pair. Its wording is variable and is reported for inspection, not compared with one memorized sentence. The runner then writes `conversation.txt` into the directory shown by `log_path` and verifies an exact read-back. Default runs use new directories under `.work/student-runs/l08/`; they do not write a log at the repository root.

The following marker is replaced with the exact tested demonstration source in the assembled handbook.

<!-- EXAMPLE_CODE -->

Running without `--live` intentionally refuses to construct a model. It does not silently produce a pretend answer. `--backend none` leaves course tracing disabled. Optional `langsmith`, `langwatch`, or `both` backends are separate observability work; use only synthetic data if an instructor enables them.

<!-- EXECUTION_FIGURES -->

## Guided practice: inspect the mechanism

1. Before executing, write the role sequence you expect immediately before and after the second response. Trace the two Python operations separately: `run_turn` adds a human message, then the node adds the AI message. Check that the resulting history has four entries, not three or six.
2. Inspect `run_turn` and `build_graph`. Find the full history passed to `graph.invoke`, the `execution_config()` supplied to it, and the config forwarded to `model.invoke`. Keeping the configuration allows selected callbacks and execution bounds to reach the actual call.
3. Open the reported log locally. Locate the exact misspelling `gud morning!`. The log places content below `Human:` or `AI:`. It must preserve spelling, spaces, case, and embedded newlines; it is not a grammar-correction operation. Avoid copying any unrelated configuration into the log or screenshots.
4. Read the fresh answer and its two-message count. Then, if approved to incur another run, close and rerun the command. The script starts a new list and reenacts its fixed inputs. It never loads yesterday's file. A successful second run therefore does not establish cross-restart recall.
5. Run only this lesson's offline checks:

   ```bash
   python -m pytest tests/lessons/test_l08.py -q
   ```

   The tests record inputs to explicit doubles and use temporary log directories. They forbid credential loading and network connections. Their evidence is about application logic; the instructor records real-call evidence separately.

## Independent task: bounded prompt, complete transcript

Complete `exercises/starters/l08.py` without importing the demonstration or reference solution. The provided orchestration already carries history and safely writes a file. Implement its three TODO functions.

1. `select_prompt(history, max_pairs=1)` accepts complete alternating human/AI pairs followed by one pending human. Return a new list containing at most the newest `max_pairs` pairs plus the pending human. Accept zero to keep only that human. Reject negative, Boolean, and noninteger limits, empty/even/nonalternating histories, and AI tool calls with `ValueError`. Do not mutate the input list.
2. `build_graph(model, max_pairs=1)` validates the limit at construction, uses `MessagesState`, and compiles `START → respond → END`. Inside the node, send the selected prompt with its configuration. Require a visible-text `AIMessage` without tool calls and return only `{"messages": [response]}`. Raise `TypeError` for a wrong role or tools, and `ValueError` for empty visible text. Do not add a checkpointer or call the model while building.
3. `format_transcript(history)` labels every message in the **full** history. Each entry is `<role>:\n<text>\n`, where the role is `Human` or `AI`; join entries with one additional newline. Return `""` for no messages and reject other roles with `TypeError`. Preserve raw content through `message_text`.

Use the workbook for the exact scenario and progressive hints. The fixed scenario introduces Mira, then sends the two-line input `gud morning!` followed by `What name did I give you?`, then asks for a short greeting. With one retained pair, the three prompt lengths must be **1, 3, 3**, while complete returned histories grow **2, 4, 6**. The log must contain all six messages and the original two-line human text. A separate fresh call has two messages and is not included in that six-message transcript.

`MessagesState` uses `add_messages`: new IDs append and matching IDs update existing messages.[801] Return a delta inside the node, rather than reconstructing old entries with fresh IDs. Because this exercise has no checkpointer, the caller still supplies full history at the start of each independent graph invocation. A reducer is not durable storage.

## Growth, safe trimming, and troubleshooting

Retain complete plain-text pairs when trimming an input window, avoiding an orphaned AI reply at the start of the prompt. This caps message count, not tokens: one long message may still exceed a model's context window. Official guidance also offers token-aware trimming, deletion, and summarization.[802] Anthropic's provider token-counting method uses a remote API; it is not an offline test helper.[803]

An omitted human turn does not guarantee forgetting. Its information may have been repeated in a retained AI reply. Nor does prompt trimming bound full-history RAM or log size. A production policy must address those separately and preserve tool-call/result relationships when tools are introduced.

If recall fails, inspect which messages reached the model before changing the prompt. If old turns disappear, check ordinary list replacement versus reducer updates. If turns duplicate, inspect message IDs and avoid creating new copies of old messages. A `FileExistsError` means the selected output directory already contains that filename; use a fresh directory, never delete evidence to hide the error. Authentication or rate-limit failures need the P00 checks, not hard-coded responses. Logs preserve sensitive content too, so use synthetic data and follow your organization's retention policy.

## Knowledge checks

1. Starting with `H1, A1`, a user sends `H2`. What are the roles and counts before and after the answer? What should the demonstration node return versus the `MessagesState` exercise node, and why?
2. A transcript is saved, the program exits, and a new invocation starts with an empty caller history. Which prior turns reach the model, and why does the file not automatically restore them? Which later lab addresses durable checkpoints?
3. For pending history `H1, A1, H2, A2, H3` and `max_pairs=1`, what is the selected prompt and the full history after `A3`? Does this policy bound tokens or guarantee forgetting? Explain both limits.

## References

[801]: https://docs.langchain.com/oss/python/langgraph/graph-api "LangGraph Graph API overview: reducers and MessagesState"
[802]: https://docs.langchain.com/oss/python/langgraph/add-memory "LangGraph memory: prompt trimming and persistence"
[803]: https://docs.langchain.com/oss/python/integrations/chat/anthropic "ChatAnthropic integration: invocation, content, and token counting"
