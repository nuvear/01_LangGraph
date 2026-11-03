# S1 — LangSmith observability and evaluation

## Purpose and prerequisites

**SUPPLEMENTARY · 90 minutes · Prerequisite: L09; L11 before inspecting retrieval.** This module has no source-video start or end time. The source course introduces graph execution and tool loops, but does not teach this LangSmith lab. The demonstration, shipping exercise, diagram, and evaluation rules here are original course additions. The whole-track review supersedes earlier caption-boundary caveats; it does not turn supplementary observability into a video topic.

By the end, you should be able to follow a graph invocation into its node, tool, and model runs; distinguish sending telemetry from verifying stored data; and evaluate model output using fixed reference examples. You need the course Python 3.12 environment and instructor-approved Anthropic and LangSmith access. Keep keys in the established private configuration, never in this chapter's examples or graph state.

## Explain: what a trace proves

A **run** records one instrumented operation. A **trace** connects a root run to its children. In this lab, a graph is the root, `quote`, `format`, and `check` are node runs, and the tool and chat model create nested runs. Seeing the final receipt alone cannot explain whether a tool ran once, whether formatting retried, or where an error occurred. Parent/child relationships provide that execution evidence. LangSmith supports tracing LangGraph workflows and LangChain model/tool calls [1401].

Our program chooses the tool deterministically. It is not asking the model to select a tool, and it is not a new ReAct implementation. The model's job is deliberately small: turn a trusted synthetic tool result into a strict JSON receipt. This keeps observability teaching separate from uncertain tool-selection behavior.

An **evaluation** applies stated criteria to actual output. A correct tool calculation does not guarantee a correct model receipt. A model could emit valid JSON containing the wrong total. A deterministic evaluator catches that by comparing fields, without asking another model for an opinion. An LLM judge can assess qualities such as clarity, but adds cost, variability, and a rubric that also needs validation [1402]. We use no judge model here.

## Illustrate: follow the bounded path

The normal path is START → quote → format → check → END. If the receipt is malformed, `check` allows one return to `format`. After the second attempt, execution ends even if formatting is still invalid. The later evaluator records failure; the graph does not silently replace the model's answer with the tool's correct result.

<!-- ORIGINAL_DIAGRAM -->

The original diagram distinguishes local evaluation from the separate telemetry pipeline. `trace_log` is a small teaching record of visited nodes, not proof that LangSmith stored a trace. Likewise, `run_id` is assigned locally before invocation; its presence in a report is not an ingestion acknowledgment.

## Configure destination and privacy

The shared CLI defaults **S1 to LangSmith**. `--backend none` disables the selected tracing callbacks but does not make a live Anthropic call offline. `both` deliberately sends instrumented data to two services; do not enable it casually. The shared helper passes callbacks through `execution_config()` and flushes on context exit. Do not create a second client or add ambient tracing flags to this lesson.

Configuration names include `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, and, when required, `LANGSMITH_WORKSPACE_ID`. Choose the API endpoint matching the account region: GCP US uses `https://api.smith.langchain.com`, EU uses `https://eu.api.smith.langchain.com`, APAC uses `https://apac.api.smith.langchain.com`, and AWS US uses `https://aws.api.smith.langchain.com` [1401]. A valid key sent to the wrong region can fail authentication.

Current official documentation also describes agent-based workspaces. The existing course helper selects a project; an instructor using an agent-based workspace must provision the agent/environment and use its compatibility tracing-project name. Do not assume every workspace has identical navigation. A tracing-only key can ingest traces but cannot read them or run experiments; read-back needs appropriate additional permissions [1403].

Use synthetic inputs only. Prompts, tool arguments, node state, outputs, and metadata can leave the machine. A `synthetic` tag is a label, not a redaction filter. Never add configuration dictionaries, real names, customer documents, or arbitrary exceptions to a trace or screenshot.

## Demonstrate: observe the seat-quote baseline

From the repository root, with the prepared environment active, run these commands only when live access is approved:

```bash
python -m course_support.check_connections --service langsmith
python -m course_lessons.s1 --live
```

The first command is the existing credential-safe service checker, not lesson code. It writes one synthetic connection-check run and verifies persisted inputs and outputs. The second command makes real Anthropic calls and traces the demonstration. Run them separately so a connection-check result cannot be mistaken for evidence about the graph.

The demo dataset contains `basic` with three seats, `team` with two, and `basic` with one. The synthetic rates are four and seven credits per seat. Each example invokes the tool once. The graph performs one or two model invocations per example; SDK-level retries can issue additional requests. These are teaching values, not commercial prices.

The report is JSON text saved as a new `s1-demo-evaluation.txt` below the run's output directory. Its rows include the case identifier, assigned root run ID, start time, elapsed milliseconds, node path, raw model receipt, and five checks. Expected acceptance is three passing rows, with three to six graph-level model invocations overall. These are expected properties, not a claim that this authoring session performed live validation.

<!-- EXAMPLE_CODE -->

## Guided practice: collect evidence in order

1. Read `build_graph` before running it. Predict which node invokes the tool, which invokes the model, and why an invalid receipt cannot create an endless loop. Notice the `config` forwarded to both nested calls.
2. Run the demonstration after instructor approval. Find its report using the returned `report_path`. Compare each raw receipt with that case's reference total. JSON key order and whitespace are irrelevant; field types and values matter.
3. Inspect the actual graph trace in the correct workspace, project, and time window. Match a report's run ID to the graph run. Locate its node children, the nested tool, and the nested chat model. Record only relationships you can actually see.
4. Inspect duration and, where present, model token usage. Local `elapsed_ms` measures the whole graph invocation, not provider-only latency. Missing token fields are missing evidence, not zero tokens. Check error runs rather than concluding that a fast run is good.
5. Inspect the existing checker's asynchronous read-back. It awaits `aread_project`, then `client.runs.retrieve` with the owning `project_id`, a start-time hint, and explicit `ID`, `INPUTS`, and `OUTPUTS` selections. Current retrieval is asynchronous and otherwise returns only the ID by default [1404]. Its bounded retry handles ingestion delay; it is not an unlimited polling loop.

Flushing means queued submission was attempted. Stored read-back verifies a particular persisted payload. Dashboard inspection verifies what you personally saw. None implies all the others. The report deliberately leaves `dashboard_visually_verified` false. Do not edit it to true because a command exited successfully.

For an L11 RAG trace, also inspect retrieved passage IDs, source/page metadata, and tool outputs. Correct retrieval and a grounded final answer are separate checks. This seat-quote module performs no retrieval, so it cannot provide retrieval-quality evidence.

<!-- EXECUTION_FIGURES -->

## Independent task: shipping-receipt audit

Complete the separate starter at `exercises/starters/s1.py`, following the S1 workbook. Implement exactly three functions: `shipping_quote`, `decode_receipt`, and `evaluate_receipt`. Do not import the demonstration or teacher solution.

Use synthetic shipping credits: local costs `3 + 2 * weight`; regional costs `5 + 3 * weight`. Weight must be an integer from one through ten, excluding booleans and floats. Unsupported regions or invalid weights raise `ValueError`. Return `total`, `unit` equal to `credits`, and `source` equal to `shipping-policy-v1`.

Decode only a strict JSON object containing exactly those three fields. Require an integer total, the correct unit, and a nonblank string source. A structurally valid but incorrect source remains parseable so the evaluator can identify a factual failure. Return `{}` for invalid JSON/schema; do not repair the output yourself.

The evaluator returns five booleans: `schema_ok`, `amount_ok`, `source_ok`, `bounded_attempts`, and `tool_evidence`. Compare the actual raw model receipt to reference outputs; require one or two attempts, the expected tool source, and exactly one `quote` entry. The supplied dataset expects local/two kilograms → seven credits, regional/three → fourteen, and local/one → five. The independent reference solution is `exercises/solutions/s1.py`.

## Knowledge checks

1. The tool returned seven credits, but the model returned valid JSON with eight. Which metric must fail, and should this schema-only retry loop retry?
2. A LangSmith flush completed and a local run ID exists. What can you claim, and what additional evidence distinguishes stored read-back from dashboard visibility?
3. Why does the current asynchronous read-back supply `project_id` and select `INPUTS` and `OUTPUTS`, and why must credentials stay outside state and metadata?

## Troubleshooting and current-API differences

If authentication fails, ask the instructor to check region, workspace, key permissions, and model access without exposing values. A write-only tracing key can explain successful ingestion but failed read-back. If a graph finishes yet is not visible, first check destination and filters, then allow bounded ingestion delay. Do not spam new paid runs to diagnose a UI filter.

A failed evaluation still saves its diagnostic report before asserting. A model or tool exception propagates instead of fabricating a receipt; an interrupted run may have no report. Reusing an explicit output directory with the same report filename raises `FileExistsError` rather than overwriting evidence. Use a new directory for a new validation run.

Unlike common older snippets, this lesson uses explicit runtime callbacks, real ChatAnthropic calls, asynchronous retrieval guidance, and a bounded repair loop. Its local report is **not** an uploaded LangSmith dataset or experiment. Official SDK `evaluate` can run examples with evaluators and create an experiment, but that is a later deliberate workflow with separate permissions [1405]. A three-case teaching set is not a production benchmark.

## References

[1401]: https://docs.langchain.com/langsmith/trace-with-langgraph "Official LangGraph tracing and regional configuration"
[1402]: https://docs.langchain.com/langsmith/evaluation-concepts "Official evaluation concepts and deterministic evaluators"
[1403]: https://docs.langchain.com/langsmith/create-account-api-key "Official API key types and workspace permissions"
[1404]: https://docs.langchain.com/langsmith/smithdb-sdk-migration-runs "Official asynchronous run retrieval migration"
[1405]: https://docs.langchain.com/langsmith/evaluate-llm-application "Official application evaluation with the SDK"
