# S2 — LangWatch observability and comparison

## Teaching purpose and preparation

**Supplementary module · 90 minutes · prerequisite L09; L11 recommended for retrieval context.** S2 develops graph-level tracing, bounded tool loops, privacy comparison, and conservative evidence interpretation.

Prepare the approved Python 3.12 environment and authorized Anthropic/LangWatch project access. Comparison needs LangSmith access with its correct workspace and regional endpoint. Never display credential files. Read `course_support/runtime.py` and `course_support/observability.py` before class: the CLI already creates the parent trace, selects callbacks, and flushes on context exit. Students should not add a second SDK initialization or attach another callback inside every node.

Run only the focused offline check while developing S2:

```bash
python -m pytest tests/lessons/test_s2.py -q
```

Its named `ScriptedChatModelDouble` produces local callback events without provider access. This is not live trace evidence. The delivered module requires separate authorized live validation; do not describe dashboards, screenshots, or actual Anthropic calls as passed until those checks are recorded.

## Explain and illustrate: minutes 0–20

In minutes 0–10, establish the distinction between an application assertion and telemetry evidence. Ask, “If the final text says 42, does that prove the addition tool ran?” Expected response: no; inspect the tool call/result and the program's actual result checks. Define a trace as grouped execution and a span as one timed operation. Parentage explains causality, not answer truth.

In minutes 10–20, trace the diagram and have learners predict `prepare, agent, tools, agent, finish`. Clarify that the two `agent` visits are intentional. The first model call uses automatic tool choice with an explicit instruction; the graph rejects a missing or multiple first call. The second call is unbound. Forced named-tool choices were rejected by the configured model during live validation, so the course keeps its chosen model and uses the supported option. A two-call budget and explicit validation bound failures before a recursion-limit error.

<!-- ORIGINAL_DIAGRAM -->

Explain `add_messages` as the message-combining rule and list addition as the event-combining rule. Both nodes return partial updates. Show the tool-call ID on the AI message and the matching `ToolMessage`. The solution later uses the same relationship for a retrieval tool, with a real `BaseRetriever` callback nested inside it.

## Timed demonstration: minutes 20–40

1. At minute 20, open `course_lessons/s2.py`. Show `execution_config()` at graph invocation and the received `config` passed to nested model/tool calls. Ask what disappears if instrumentation is attached only to the model. Expect plain-node and tool structure to be lost.
2. Run `python -m course_lessons.s2 --live` only with authorization for paid requests and synthetic telemetry. Explain that S2 defaults to LangWatch. Expected local properties are result `42`, two model calls, five ordered events, nonempty final text, and a newly written report. Do not grade wording exactly.
3. Inspect the authorized project by execution time and name `LangGraph Course S2`. Expand the root, graph nodes, model calls, and arithmetic tool. Record only visible timing, usage, and error fields. No visible trace means “not yet verified,” not permission to invent one.
4. Explain cleanup after `run_demo` returns: parent context closes, provider flush is attempted, then shutdown occurs. The helper does not expose exporter acknowledgment through the lesson summary. The terminal `passed` label is not a dashboard certificate.
5. If time and permissions permit, run `python -m course_support.check_connections --service langwatch`. Inspect its HTTP status and rejected-span count. This is a separate connection-check trace, not read-back of the demonstration.

<!-- EXECUTION_FIGURES -->

If a real service is unavailable, continue with the offline callback test and label that evidence accordingly. Defer remote evidence rather than substituting a fabricated screenshot.

## Guided comparison: minutes 40–55

Run `python -m course_lessons.s2 --live --backend both` when both services are authorized. This executes the same synthetic graph once while dispatching callbacks to both destinations. Ask learners to compare corresponding model/tool operations, not trace IDs or total span counts. Each product can represent structure and aggregate time differently. A missing field is an observation, not a zero value.

Use `--backend none` to explain the privacy boundary, not to promise an offline model. Anthropic still receives messages under `--live`. One backend adds one telemetry destination; `both` sends the synthetic callback data to both. Root `capture_input=False` and `capture_output=False` do not redact callback-generated children. The synthetic-data tag is not a sanitization function. Require students to mention prompts, state, retrieved text, tool arguments/results, and metadata when discussing what can leave the process.

## Independent exercise and reference walkthrough: minutes 55–80

The exact workbook task is to implement `privacy_plan`, `classify_ingestion`, and `build_graph` in `exercises/starters/s2.py`. It is not an arithmetic rewrite alone. The supplied retriever and runner provide the fixture and acceptance checks, leaving three focused functions to complete. The reference solution is independent of the demonstration:

```bash
python -m exercises.starters.s2
python -m exercises.solutions.s2 --live
```

The untouched starter prints `STARTER_NOT_COMPLETED` and makes no requests. After finishing, learners replace the bottom `main()` call with `run_cli("S2", run_demo)` to enable its standard CLI. A fresh output directory prevents no-overwrite failures.

Walk through the reference in this order. `privacy_plan` maps the four exact backend names to selected telemetry recipients and always notes Anthropic under live execution. Unknown names raise `ValueError`. It explicitly rejects the claim that root capture flags sanitize children.

Next, `classify_ingestion` requires a LangWatch record, `passed`, HTTP 200, explicit acknowledgment, and an integer zero rejected-span count. Missing, partial-success, wrong-service, or failing records remain `not_established`. Even an accepted checker record leaves lesson ingestion and dashboard visibility `not_checked`. No success fixture is manufactured inside the live runner.

Finally, the graph forces `lookup_handout` once with the requested document ID, invokes that tool with the received config, and invokes the retriever with config inside the tool. `TRACE-101` returns one original synthetic document, source `synthetic-s2-handout`, page 1. `MISSING-999` returns no documents. Python derives `supported` or `no_evidence` from that payload, not from model wording. This status means evidence exists, not that every generated sentence is correct; review whether the answer stays within the evidence. The fixture is exact-ID retrieval, not embeddings, similarity search, or the L11 corpus.

The runner invokes two cases, each with two real model calls, and writes the actual evidence and generated answers into a new local report. It validates event order, metadata, nonempty text, and empty retrieval behavior. Tests additionally reject changed IDs, unknown tools, multiple or absent first calls, repeated tool requests, blank input, and empty final responses.

<!-- SOLUTION_CODE -->

## Review and exact knowledge-check answers: minutes 80–90

### Answer 1: callback placement

Attach the callback to `graph.invoke` so the graph propagates it into every executed node and nested runnable. Besides model spans, expect ordinary Python nodes, tool-node execution, individual tool calls, repeated agent visits, and—when the solution runs—the retriever operation. Attaching it only inside `agent` records too narrow a part of the workflow. Preserving the node config also preserves parent/child relationships.

### Answer 2: flush and partial success

Exit after flush establishes that local cleanup attempted to drain pending export work, not that every span was accepted or displayed. HTTP 200 with two rejected spans is partial acceptance, not the required no-rejection result. Check the parsed acknowledgment and sanitized checker status, then correct scope/permissions/payload issues as appropriate. A successful retry of a separately authorized check still does not prove the lesson trace exists: inspect that execution's tree separately. Do not blindly retry partial-success payloads; the OTLP specification says not to retry a partial-success response.

### Answer 3: recipients and privacy

`--live --backend none` still sends model messages to Anthropic; the course selects no tracing callbacks. `both` adds LangSmith and LangWatch as telemetry destinations for one execution. Model/tool/state/retrieval payloads may be exported. Root capture switches govern the parent span only; callback children can still contain content. Data minimization, tested masking where appropriate, destination/retention decisions, and avoiding secrets in graph data remain necessary. This runtime is not a firewall against unrelated host instrumentation.

## Marking, misconceptions, and recovery

Use a ten-point rubric: two points for the correct four-backend privacy plan; two for conservative ingestion interpretation including partial success; two for callback-preserving model/tool/retriever execution; two for known/missing cases with exact source/page evidence; and two for bounded failures and honest evidence notes. Full credit requires substantive implementation, not an unchanged incomplete starter or a passing reference test alone.

Common misconceptions are treating `supported` as automatic factual correctness, treating HTTP 200 as complete acceptance, equating `none` with no network, and treating identical-looking answers as evidence of identical traces. Ask students which specific field or visible span supports each claim.

For provider failures, check sanitized model access/rate-limit diagnostics without showing headers. For export failures, check LangWatch project scope and the course-supported cloud endpoint separately. For missing nodes, inspect callback placement/config propagation. For file collisions, select a new output directory. For current SDK mismatch, do not use `setup(project_id=..., flush_on_exit=...)`: installed LangWatch 1.4.0 lacks those keywords, and the shared helper already handles scope and flush.

## References

Official pages verified on 3 November 2026: [LangWatch LangGraph integration](https://langwatch.ai/docs/integration/python/integrations/langgraph), [setup and shutdown guide](https://langwatch.ai/docs/integration/python/guide), [SDK reference](https://langwatch.ai/docs/integration/python/reference), [LangSmith selective tracing and flush](https://docs.langchain.com/langsmith/trace-with-langchain), [LangSmith masking and disabling](https://docs.langchain.com/langsmith/mask-inputs-outputs), and [OTLP acknowledgment semantics](https://opentelemetry.io/docs/specs/otlp/). The documentation's example provider and newer arguments are not this course's installed Anthropic implementation.
