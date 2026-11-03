# L07 — Anthropic stateless bot

## What you will build

You will put a real Anthropic chat-model call inside a one-node LangGraph graph. Its topology is still `START → call_model → END`, just like an earlier deterministic graph. The difference is the work performed inside the node: it asks a language model for a response instead of constructing an answer entirely with Python.

By the end, you should be able to construct a `HumanMessage`, distinguish model invocation from graph invocation, inspect response text and available token-usage metadata, and explain why a terminal loop does not create conversation memory. Prerequisites are L01–L06, the P00 environment checks, and approved Anthropic access. Allow about 80 minutes, including guided and independent practice. Paid requests require deliberate `--live` opt-in.

The source section is [01:31:01–01:42:54](https://youtu.be/jGg_1h0qzaM?t=5461). It demonstrates a basic model wrapper, a terminal input loop, and a name-recall failure. The presenter explicitly assigns no original exercise. Our Anthropic implementation, bounded execution, validation, offline tests, and help-desk exercise are **current-API updates and added practice**, not historical video homework.

## Explain: a model inside a node

A chat model accepts role-labeled messages and returns an assistant message. `HumanMessage` identifies user input; `AIMessage` represents the model's response. These are Python objects, not just strings with decorative labels. LangChain provides the message classes and `ChatAnthropic` integration; LangGraph controls when the node runs. The current [Anthropic integration guide](https://docs.langchain.com/oss/python/integrations/chat/anthropic) documents `model.invoke(messages)` and the returned message metadata.

There are three separate operations to keep straight. `builder.compile()` turns your registered nodes and edges into an executable graph. `graph.invoke(state, config=...)` starts one graph execution. Inside that execution, `model.invoke(messages, config=...)` requests a model response. The model returns an `AIMessage`; the node extracts selected fields and returns a partial state update. The graph returns accumulated state, which is a dictionary in this lesson. Compilation does not contact Claude or certify answer quality. See the [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api).

This is not yet a tool-using agent. There is no tool selection, tool execution, planning loop, or external information retrieval. A fluent response does not change the graph's capabilities. It is useful precisely because it isolates the model boundary before L08 introduces history and L09 introduces tools.

## Illustrate: where the missing memory went

The demo's `BotState` contains `messages`, `reply`, `usage`, and `sent_messages`. Input supplies one fresh human message. The model node returns the other fields; it does not append its response to an ever-growing conversation. `sent_messages` records the actual text list passed to the injected model, making the request boundary inspectable without recording credentials.

A **stateless** request does not carry conversational context from an earlier request unless your application supplies it. Anthropic's [Messages API guide](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) explicitly describes this contract. Sending “My name is Bob” once does not make the next fresh request contain Bob's name. Reusing the same model object does not add conversation history automatically. This concerns conversational context, not a claim about the provider's data-retention policy.

Our original diagram separates the outer Python loop from the graph execution. The arrow back to input is application control flow; there is no graph back-edge. Each visit to START receives new state.

<!-- ORIGINAL_DIAGRAM -->

The source introduces coding at [01:32:49](https://youtu.be/jGg_1h0qzaM?t=5569). A source figure around [01:33:00](https://youtu.be/jGg_1h0qzaM?t=5580) illustrates the original bot section; it is not evidence that the adapted Anthropic code ran.

<!-- VIDEO_FIGURE -->

## Demonstrate: read the complete implementation

The runnable baseline is `course_lessons/l07.py`. Read `build_bot` first, then `ask`, then `terminal_chat`. `build_bot(model)` accepts an injected model: production supplies real `ChatAnthropic`, while offline tests supply an explicitly named double. A **test double** is a substitute used to inspect deterministic program behavior without contacting a service. It cannot prove that your account, network, or chosen Claude model works.

<!-- EXAMPLE_CODE -->

`ask` constructs a new list containing exactly one `HumanMessage` on every call. The node rejects an empty list, multiple messages, a wrong message role, and blank text. `TypedDict` helps document the state shape, but it does not perform these runtime checks for you.

The shared `get_model` helper obtains the approved key and model configuration locally when live execution is authorized. Secrets never enter graph state. It creates `ChatAnthropic` with a response limit, timeout, and bounded retries. We do not set `temperature`: some current models reject non-default sampling parameters. Do not hard-code a model name merely because it appeared in a video or documentation example; use the model approved during P00.

`message_text` handles ordinary string content and textual content blocks. It does not print hidden thinking or dump all provider metadata. `usage_metadata` may supply input, output, and total token counts. A token is a unit used by a model to process text, not necessarily one word. Usage is returned when available, otherwise `{}`. It is not a price calculation or proof of memory.

## Guided practice: inspect two independent turns

1. Activate the prepared Python 3.12 environment and work from the repository root. Run the offline checks first:

   ```bash
   python -m pytest tests/lessons/test_l07.py -q
   python -m exercises.starters.l07
   ```

   The tests use named offline doubles. The unmodified starter prints `STARTER_NOT_COMPLETED` and exits successfully; that is an honest progress message, not a passing exercise grade.

2. Predict the requests before making a paid call. The demonstration submits `Hello, my name is Bob.`, then `What is my name?`, followed by `exit`. Write down which words the second model request will actually contain. The answer is determined by request construction, not by the model's eventual sentence.

3. With approved credentials already configured through P00, run:

   ```bash
   python -m course_lessons.l07 --live --backend none
   ```

   Without `--live`, the program raises a clear opt-in error rather than silently inventing an answer. The default command uses a finite scripted input sequence so unattended validation does not hang. It makes two logical model invocations, then exits. Provider retries can mean more than two underlying HTTP attempts on failure.

4. Inspect `checked_turns`, `messages_per_request`, `prior_turns_forwarded`, `stop_reason`, `replies`, and `usage` in the final summary. Expected structural properties are two checked turns, `[1, 1]`, `false`, and `exit`. Replies should contain displayable text; their exact wording and token counts vary. These are expected properties, not a report of live results already obtained by this author.

5. Explore terminal behavior without changing the graph. `terminal_chat` accepts injected `read` and `write` functions for offline checks, and defaults to real `input` and `print`. In a Python shell, importing `build_bot`, `terminal_chat`, and `get_model` lets you call `terminal_chat(build_bot(get_model(live=True)))` for an authorized interactive session. It allows at most ten raw entries, skips blanks, accepts whitespace/case variations of `exit`, and stops cleanly on end-of-input. A blank entry still consumes one entry of the budget. Do not use personal data for this demonstration.

<!-- EXECUTION_FIGURES -->

## Independent task: stateless help-desk session

This is added practice. Complete the separate starter `exercises/starters/l07.py`, without importing the demonstration or solution. Implement its three TODO functions: `classify_entry`, `build_bot`, and `run_session`. The workbook contains the precise interface and acceptance harness.

Your one-node graph receives a `prompt` string and returns displayable `reply`, optional `usage`, and `sent_messages` recording the one original prompt sent. Its input schema deliberately differs from the demonstration so you must construct the message yourself. The session controller must preserve raw prompt text, skip whitespace-only entries, stop before calling the model for `exit`, and inspect at most six raw entries by default. Returned turns are a local report, never input for later calls.

Use exactly this assessment sequence: `"  "`, `"My name is Mira. Say hello briefly."`, `"What is my name?"`, `" ExIt "`, `"This must never be sent."`. Expect one skipped entry, four inspected entries, two one-message requests, and an `exit` stop reason. Nothing after exit is processed. Require nonempty reply text, not a memorized denial of knowing Mira's name.

## Knowledge checks

1. After `ask(graph, "My name is Bob.")` and then `ask(graph, "What is my name?")`, how many `HumanMessage` objects are in the second model request? Why does the surrounding Python loop not create memory?
2. What do `builder.compile()`, `graph.invoke(...)`, and `model.invoke(...)` each do? Which one directly returns an `AIMessage` here?
3. For the independent task's five-entry assessment sequence, which entries are sent, how many are inspected and skipped, and what is the stop reason? Why is an exact “I don't know your name” assertion unsuitable?

## Troubleshooting and next steps

An authentication, model-access, rate-limit, or network error is not proof that LangGraph is broken. Return to P00's approved connection checks; never paste a key into state or a screenshot. An empty-response error means no displayable text was returned; inspect the error and permitted response settings rather than reporting success. If the process waits for input, check whether you deliberately entered the interactive shell path instead of the finite module command.

If the model guesses Bob or Mira, inspect the actual request messages. A plausible guess does not establish memory. Conversely, failure to recall a name is not sufficient proof that history was absent. Our deterministic evidence is that only the current message was supplied. L08 deliberately changes that design by passing history; U1 later adds [checkpoint/thread persistence](https://docs.langchain.com/oss/python/langgraph/add-memory). Do not add those mechanisms to fix this lesson's intended stateless behavior.

## References

Official documentation was verified by search and page extraction on 3 November 2026: [ChatAnthropic integration](https://docs.langchain.com/oss/python/integrations/chat/anthropic), [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [LangGraph memory](https://docs.langchain.com/oss/python/langgraph/add-memory), and [Anthropic Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages). Source attribution is to Vaibhav Mehra/freeCodeCamp's [video section](https://youtu.be/jGg_1h0qzaM?t=5461), originally using OpenAI rather than Anthropic. The supplied whole-track review confirms topic identity with sampled visuals; publication figures and live evidence are added separately.
