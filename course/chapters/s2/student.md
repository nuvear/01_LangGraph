# S2 — LangWatch observability and comparison

## Purpose and prerequisites

**Supplementary observability module · 90 minutes.** This is added course material, not a section of the source video, so it has no video start/end timestamp. Complete L09 first; L11 is useful when inspecting retrieval evidence. The original course's [tool-agent section at 02:03:20](https://youtu.be/jGg_1h0qzaM?t=7400) supplies the agent/tool-loop concept, not this LangWatch integration.

By the end, you should be able to attach tracing at the graph boundary, explain a parent trace and its child spans, follow a bounded model/tool loop, interpret ingestion evidence without exaggeration, and choose which tracing services receive synthetic data. You will also distinguish retrieval failure from exporter failure. You need the prepared Python 3.12 environment and authorized Anthropic access. LangWatch access is needed for the default live command; LangSmith access is needed only for comparison commands that select it. Never paste credentials into lesson code or screenshots.

## A trace explains the path, not whether an answer is true

A **trace** groups work belonging to one execution. A **span** records one step, its timing, and potentially its input, output, or error. A parent/child relationship tells you which operation caused another operation. A successful final answer alone cannot tell you whether a tool ran, whether a loop repeated, or whether retrieval returned a document.

Our demonstration asks a real Anthropic model to call `add_numbers` with 18 and 24. Python performs the addition, and a second real model call explains the result. The graph visits `prepare → agent → tools → agent → finish`. A repeated node name is normal: the agent runs once before and once after the tool result. The first call uses automatic tool choice with an explicit instruction, and the graph rejects a missing or multiple call. The second call uses the model without tools bound. The configured model rejected forced named-tool choices during live testing; using automatic selection keeps the chosen model and still checks that the actual tool round trip occurred.

The program checks the actual tool result, the two-call count, the event order, and a nonempty final response. It does not require a memorized sentence. It also does not inspect private chain-of-thought. Trace visible messages, tool arguments, observations, and routing instead.

<!-- ORIGINAL_DIAGRAM -->

The original S2 diagram follows the application path and then separates callback routing from export evidence. A route marked `none` means no tracing callbacks selected by this runtime; it does not remove the real model request.

## Attach the callback where the whole graph runs

The official [LangWatch LangGraph integration](https://langwatch.ai/docs/integration/python/integrations/langgraph) says to create a parent trace and place `get_langchain_callback()` in the graph invocation configuration. Attaching it only to a model inside one node loses the ordinary Python nodes and tool-node structure.

This course already implements that setup in `course_support/observability.py`. The CLI calls `graph_tracing`, creates the parent named `LangGraph Course S2`, and selects callbacks. `execution_config()` copies those callbacks and adds a recursion limit of 40. Each lesson passes this configuration to `graph.invoke`. Inside the graph, model and tool invocations preserve the node's received `config`, maintaining the nested relationship. Do not replace it with a new empty callback list while debugging.

The `messages` field uses `add_messages`, a reducer that combines new messages with existing state. The `events` list uses list addition to retain the visited-node sequence. A tool call includes an ID, and its `ToolMessage` must refer to the same ID. Passing the entire tool-call dictionary to the tool's `invoke` preserves that connection. The graph rejects an unknown tool, absent or multiple first-turn tool calls, further second-turn tool requests, and empty final text. An application-level two-call budget is more informative than waiting for a recursion-limit error.

<!-- EXAMPLE_CODE -->

## Guided practice: run and inspect the demonstration

1. Activate the prepared environment and work from the repository root. Read `course_lessons/s2.py`, especially `build_graph`, `tools`, and `run_demo`. Predict the five events before running anything.
2. With permission to make paid model requests and send synthetic telemetry, run:

   ```bash
   python -m course_lessons.s2 --live
   ```

   S2 automatically selects LangWatch. The explicit equivalent is `python -m course_lessons.s2 --live --backend langwatch`. No additional lesson-level SDK setup is necessary.
3. Inspect the terminal summary and the returned `report` path. The local report is a new `s2-demo.txt` below the selected output directory. Expect the tool result `42`, two model calls, the five-event sequence, and nonempty answer text. These are expected properties, not a record that a live run has already passed.
4. In the authorized LangWatch project, locate the run by its name and execution time. Expand the parent, graph nodes, model calls, and `add_numbers` tool. Check the call/result relationship and look for latency, errors, and token usage where the provider/integration supplies it. Record missing fields rather than guessing values. A graph's plain Python node should appear as a chain span, not as an LLM call.
5. Save sanitized evidence of what you actually inspected. The local `events` list is useful, but it does not establish that a remote trace exists. Execution figures are added only after the actual runs.

<!-- EXECUTION_FIGURES -->

The CLI also supports `--output-dir`. Use a fresh directory for each repeated command because the safe writer refuses to overwrite an existing report. The live flag is required for model-based runs; the offline tests use explicitly named test doubles instead of quietly substituting canned answers.

## Flush, acknowledgment, and visibility are different observations

LangWatch uses OpenTelemetry export machinery. The shared context closes the parent span before calling the dedicated provider's `force_flush` with a 15-second timeout, followed by shutdown. LangSmith's selected tracer similarly waits and flushes before closing. The [LangWatch guide](https://langwatch.ai/docs/integration/python/guide) describes exit flushing; explicit cleanup is especially useful for short classroom programs.

A flush attempts to drain queued work. It is not a dashboard inspection, and this helper does not return the exporter's acknowledgment as lesson evidence. `run_demo` returns before the CLI context flushes; its summary deliberately says remote ingestion is not checked. The CLI's `status: passed` means its application assertions completed without a raised error, not that a dashboard was inspected.

When authorized, separately run:

```bash
python -m course_support.check_connections --service langwatch
```

This checker sends its own synthetic connection-check trace. Inspect `http_status`, `ingestion_acknowledged`, and `rejected_spans` in its report under `.work/validation`. According to the [OTLP specification](https://opentelemetry.io/docs/specs/otlp/), HTTP 200 can still carry partial success with rejected spans. Require the full success conditions, not the status code alone. Even a successful checker proves only that check's ingestion, not storage or visibility of a later lesson trace. Inspect the lesson tree separately.

## Compare the same synthetic execution and its privacy boundary

Use one graph execution with two callback destinations:

```bash
python -m course_lessons.s2 --live --backend both
```

This is one synthetic scenario with one pair of model calls, not two separate model experiments. Both services receive callback events for that execution. Compare corresponding nodes, tool arguments/result, model calls, error reporting, and available timing/usage fields. Do not expect matching trace IDs, identical span counts, identical UI layout, or identical timing aggregation. Record unavailable observations honestly. Separate single-backend commands are also supported with `--backend langsmith` or `--backend langwatch`.

With `--backend none`, the course runtime selects no telemetry destination, but Anthropic still receives the model messages when `--live` is used. `langwatch` or `langsmith` selects one telemetry service; `both` duplicates this synthetic telemetry to two services. Potential exported data includes prompts, state, answers, tool arguments/results, and retrieved text. A synthetic-data tag is a label, not a filter.

The helper sets `capture_input=False` and `capture_output=False` on the LangWatch root. Those switches do not redact callback-generated child spans. LangSmith also has documented [hiding and masking controls](https://docs.langchain.com/langsmith/mask-inputs-outputs), but this lesson does not implement a general sanitization layer. Keep real personal data and secrets out of every state, prompt, tool result, metadata field, and screenshot. Choose destinations and retention policies before using non-synthetic data.

## Independent task: a retrieval trace and evidence interpreter

Implement the three TODO functions in `exercises/starters/s2.py`, following the exact workbook task. Build a bounded handout lookup graph, a four-backend privacy plan, and a conservative checker-record interpreter. Run `TRACE-101` and `MISSING-999`. The supplied exact-ID retriever returns one original synthetic handout with source/page metadata or an empty list. It is a real `BaseRetriever` callback path, not vector search or a replacement for L11's Chroma exercise.

The completed graph must retrieve through a model-requested tool, preserve callbacks into the retriever, set `supported` or `no_evidence` from retrieved evidence in Python, and never fabricate a missing document. The provided runner performs four real model calls in total. Use `python -m exercises.starters.s2` initially; it must print `STARTER_NOT_COMPLETED` without using a service. Enable its CLI only after implementing the TODOs. The independent reference is `python -m exercises.solutions.s2 --live`.

## Knowledge checks

1. Why must the LangWatch callback be attached to `graph.invoke`, rather than only to the model inside `agent`? Which additional operations should become visible?
2. A program exits after flush and a separate checker reports HTTP 200 with two rejected spans. What is established, what is not established, and what should you check next?
3. With `--live --backend none`, who still receives data? With `--backend both`, what changes, and why do disabled LangWatch root input/output capture flags not guarantee privacy?

## Troubleshooting and current-API differences

Missing model access or rate limits are provider problems, not proof of broken tracing. A model may succeed while export fails. Verify the selected backend, project scope, endpoint, and checker's sanitized status separately. Do not print exception headers or entire configuration files. If only model spans appear, look for a callback attached too low or a replaced invocation config. If an output file exists, choose a fresh directory rather than deleting evidence casually.

Configure `LANGWATCH_API_KEY`, `LANGWATCH_PROJECT_ID`, and the course's `LANGWATCH_ENDPOINT` through the prepared local configuration process. The official cloud default is `https://app.langwatch.ai`; this course helper intentionally allows that official endpoint only. Project-scoped/service-key requirements must match the authorized project. Comparison also requires the correct LangSmith project/workspace and regional endpoint from S1.

The current online guide shows newer `setup(project_id=..., flush_on_exit=...)` options. Read-only inspection found installed LangWatch 1.4.0 does not accept those keywords. The shared helper supplies project scope through the environment during setup and flushes its provider explicitly. Do not copy the documentation's OpenAI model example: this course uses current installed ChatAnthropic and real Anthropic requests. These are supplementary current-API adaptations, not changes claimed to be present in the original video.

## References

Official sources verified by search and page retrieval on 3 November 2026: [LangGraph instrumentation](https://langwatch.ai/docs/integration/python/integrations/langgraph), [Python integration guide](https://langwatch.ai/docs/integration/python/guide), [SDK reference](https://langwatch.ai/docs/integration/python/reference), [LangSmith selective tracing and shutdown](https://docs.langchain.com/langsmith/trace-with-langchain), [LangSmith sensitive-data controls](https://docs.langchain.com/langsmith/mask-inputs-outputs), and [OTLP success and partial-success semantics](https://opentelemetry.io/docs/specs/otlp/). The installed shared helper, rather than a copied online snippet, defines this course's supported configuration.
