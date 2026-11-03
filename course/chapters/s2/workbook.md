# S2 — LangWatch observability and comparison

## Exercise: trace a handout lookup without overstating evidence

**Supplementary practice · 25 minutes within the 90-minute module.** Complete the S2 guided arithmetic demonstration first. You will build a handout lookup workflow with real model, tool, and retriever operations, plus two small privacy/evidence helpers. This is a tracing fixture, not a replacement for L11 vector retrieval.

Your starter is `exercises/starters/s2.py`; the independent reference is `exercises/solutions/s2.py`. Do not import the solution into the starter. The supplied `HandoutRetriever` returns one document for `TRACE-101` and no documents for `MISSING-999`. Its original text explains that flush does not prove acknowledgment or dashboard visibility. A found document has ID `TRACE-101`, source `synthetic-s2-handout`, page 1, and text in `DOCUMENT_TEXT`.

Run from the repository root with the prepared environment:

```bash
python -m exercises.starters.s2
python -m pytest tests/lessons/test_s2.py -q
```

Initially the starter must exit successfully with `STARTER_NOT_COMPLETED`. It must not claim a pass or make requests. The supplied focused tests exercise the demonstration and reference solution using named offline doubles; passing them alone does not assess your edited starter. Redirect or add equivalent local tests for your implementation before claiming completion.

## Implement exactly three functions

1. Complete `privacy_plan(backend)`. Accept only `none`, `langsmith`, `langwatch`, and `both`; reject unknown names with `ValueError`. Return `backend`, `telemetry_recipients`, `model_recipient`, `payload`, `root_capture_is_child_redaction`, and `plan_only`. Recipients are respectively an empty list, `["LangSmith"]`, `["LangWatch"]`, and `["LangSmith", "LangWatch"]`. Use the model-recipient text `Anthropic when --live is used`. Set the last two fields to `False` and `True`. Describe synthetic messages, state, tool arguments/results, and retrieved text in `payload`. This is a routing plan, not a redaction guarantee.
2. Complete `classify_ingestion(report)`. Acknowledge only a record with `service="langwatch"`, `status="passed"`, `http_status=200`, `ingestion_acknowledged` equal to boolean `True`, and `rejected_spans` equal to integer zero. Missing fields, string zero, boolean false, partial rejection, or failures must not pass. Return `checker_ingestion` as `acknowledged` or `not_established`; always leave `lesson_trace_ingestion` and `dashboard_visibility` as `not_checked`. Never create a success record merely because your graph finished.
3. Complete `build_graph(model)`. Make a `HandoutRetriever` and a tool named `lookup_handout`. The tool accepts `document_id` and the injected `RunnableConfig`; invoke the retriever with that config. Return JSON with `found` and `documents`, where each document contains `id`, `source`, `page`, and `text`. Bind this tool for the first model call with `tool_choice="auto"`, explicitly request its use in the prompt, and disable parallel tool calls. Validate that exactly the intended call actually occurred; automatic selection is not a guarantee. Use the unbound model for the second call.
4. Inside that builder, register `prepare`, `agent`, `tools`, and `finish`. Connect `START → prepare → agent`, route `agent` to `tools` if a call is present or to `finish` otherwise, connect `tools → agent`, and connect `finish → END`. Preserve the config on model/tool invocations and pass the entire tool-call dictionary into the tool. Reject blank document IDs, absent/multiple first calls, unknown tools, changed requested IDs, more than two model calls, further second-turn tool requests, and empty final text.
5. Return partial state updates and append events. A successful case must visit `prepare, agent, tools, agent, finish`, make two model calls, and set status to `supported` or `no_evidence` from the retrieved payload in Python. Require nonempty model text, but do not compare an exact sentence. Manually review whether it respects retrieved evidence.
6. After all TODOs are implemented and locally checked, replace the bottom `main()` call with `run_cli("S2", run_demo)`. With authorization, run `python -m exercises.starters.s2 --live`. The supplied runner checks both IDs and writes a new report; it makes four real Anthropic calls. S2 defaults to LangWatch. Use a fresh output directory when repeating a run.

## Three progressive hints

**Hint 1 — separate responsibilities.** Privacy mapping and checker interpretation are ordinary Python functions. Test these without a model. An HTTP status code alone cannot tell you how many spans were rejected.

**Hint 2 — preserve the nested operation.** The graph receives runtime callbacks through `execution_config()`. Nodes receive `config`; carry that same config into the model, tool, and retriever. Use the existing demonstration's message-ID handling as a pattern, not its arithmetic tool as the answer.

**Hint 3 — make absence deterministic.** Parse the tool's JSON into `evidence`. Derive the final status from `evidence["found"]`; do not ask the model to invent a missing handout or trust a generated “success” label. Force one first tool call, then reject additional rounds instead of looping indefinitely.

## Observe the result and compare destinations

After authorization, use the reference and service checker separately:

```bash
python -m exercises.solutions.s2 --live
python -m exercises.solutions.s2 --live --backend both
python -m course_support.check_connections --service langwatch
```

The `both` command routes one execution to two telemetry services; it does not double the model calls. Inspect actual corresponding operations in each authorized project. A checker acknowledgment belongs to its own check, not automatically to the lesson run.

Record concise observations: your command and report path; status and document count for each ID; source/page for the found document; model-call count and event order; selected telemetry destinations and the remaining Anthropic destination; checker status/rejected count; and whether you personally inspected the lesson's model/tool/retriever tree. Mark unperformed checks `not_checked`. Do not record keys, real personal information, fabricated trace IDs, or invented screenshots.

## Completion criteria and stretch

Complete means all three functions are implemented, known/missing cases have the specified evidence and statuses, callbacks reach model/tool/retriever, call IDs match, budgets and invalid-input cases fail honestly, and the report is written without overwriting. Distinguish offline-double evidence, local application success, separate checker acknowledgment, and actual dashboard inspection. Passing local assertions alone is not proof of remote visibility.

**Stretch:** add an offline test in your own implementation that emits a second-turn tool request and proves termination before a third model call. Then write a short comparison of one genuinely inspected `both` execution, noting unavailable fields rather than assuming identical tree layout or timing.

## References

Use the verified official [LangWatch graph callback guide](https://langwatch.ai/docs/integration/python/integrations/langgraph) and [OTLP partial-success specification](https://opentelemetry.io/docs/specs/otlp/) to justify callback placement and evidence handling. The current online setup examples may use arguments absent from installed LangWatch 1.4.0; keep using the supplied shared runtime instead of replacing its configuration.
