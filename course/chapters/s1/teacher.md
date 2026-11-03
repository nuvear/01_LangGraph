# S1 — LangSmith observability and evaluation

## Preparation and evidence discipline

**SUPPLEMENTARY · 90 minutes · Prerequisite: L09; L11 for retrieval inspection.** Teach S1 as an observability addition. The student chapter, workbook, starter, and reference solution all use the same shipping-receipt task; the seat-quote demonstration is deliberately separate.

Before class, have the environment owner validate the configured Anthropic model and the correct LangSmith destination using the existing credential-safe checker. Do not project configuration files. Confirm that the credential can both ingest and read traces if read-back is planned. A tracing-only key cannot read stored runs; do not diagnose that as proof that ingestion failed [1411]. For agent-based workspaces, provision the agent/environment and use its tracing-project compatibility name with the course's existing project-based helper.

Prepare a fresh output directory, permission to make real paid calls, and an authorized dashboard session. Run the demo and solution separately during instructor validation. Three examples require three to six graph-level model invocations per command; the shared model's SDK retries can create additional requests. No fixed model wording, token count, latency, or price is an assessment requirement.

## Explain and illustrate: minutes 0–20

Use the first ten minutes to distinguish a run, a trace, and an evaluation. Ask: “If the correct tool result is seven, does that prove the model returned seven?” The expected response is no: the formatter's actual output must be checked independently. Introduce the difference between a deterministic evaluator and an LLM judge. The former uses fixed rules; the latter supplies model-based judgment and needs its own rubric and validation [1412].

During minutes 10–20, draw the graph and the evidence pipeline separately. One tool invocation precedes a formatting loop. Invalid schema can repeat `format` once; the tool does not repeat. A schema-valid incorrect amount ends the graph and fails evaluation. This design isolates formatting recovery from factual grading and provides a comprehensible bounded loop.

<!-- ORIGINAL_DIAGRAM -->

Ask learners to predict the longest path: `quote, format, check, format, check`. Expected reasoning: the counter begins at zero, increases only after model invocation, and the route permits a retry only below two. `recursion_limit=40` is a separate safety cap, not the normal stopping rule.

## Timed demonstration: minutes 20–40

1. During minutes 20–24, show `execution_config()` at graph invocation and `config` forwarding into the tool and model. Explain that callbacks preserve parent/child relationships. The program chooses the tool; this is not model-driven ReAct. Official LangGraph tracing guidance supports nested instrumented operations, but the course uses its explicit helper rather than copying ambient environment examples [1413].
2. During minutes 24–30, execute `python -m course_lessons.s1 --live` after approval. Read the returned report path and inspect its three rows. The expected reference totals are twelve, fourteen, and four. Describe these as expected checks until the run actually establishes them.
3. During minutes 30–35, locate one matching root run in the configured dashboard and expand its node/tool/model hierarchy. Inspect errors, duration, and available usage fields. Never infer zero tokens from a missing field or equate local elapsed time with provider-only latency.
4. During minutes 35–40, inspect the existing service checker source. It awaits `aread_project`, then `client.runs.retrieve`, explicitly selecting stored inputs and outputs. Current retrieval needs `project_id`; `start_time` is a useful optional hint; unselected fields can be absent [1414]. Its successful synthetic read-back would establish that check run's persistence, not every demonstration trace's visibility.

If dashboard access fails, use local reports to continue evaluation teaching and mark remote inspection pending. Do not create illustrative screenshots that appear to prove a live run. The execution figures below are reserved for the parent's actual demo and solution evidence.

<!-- EXECUTION_FIGURES -->

## Guided practice and independent work: minutes 40–75

During minutes 40–50, learners inspect a report's raw receipt and five individual scores. Ask whether key order matters; the expected response is no because JSON is parsed into a dictionary. Ask whether valid JSON guarantees correctness; no, because amount and source are checked separately. For learners who completed L11, discuss retrieved source/page evidence as an additional target, while making clear that S1 itself performs no retrieval.

During minutes 50–75, assign the workbook's three TODO functions in `exercises/starters/s1.py`. Learners should keep supplied graph and reporting plumbing intact. Initial execution prints `STARTER_NOT_COMPLETED` and exits successfully without configuration access. That is an honest placeholder status, not passing evidence. Require function-level reasoning before granting permission for a live run.

The separate solution is `exercises/solutions/s1.py`. `shipping_quote` maps local to base three plus two per kilogram, and regional to base five plus three per kilogram. It explicitly rejects booleans and floats with `type(weight) is int`, because Python booleans are subclasses of integers. One through ten is inclusive. Unsupported region names and invalid weights raise `ValueError`.

`decode_receipt` uses `json.loads`, verifies a dictionary with exactly three keys, and rejects incorrect types, units, or blank sources. It returns `{}` for invalid schema rather than inventing data. It does not compare source or amount to the reference: otherwise schema and correctness failures would be conflated.

`evaluate_receipt` decodes the actual raw model output, compares total and source to reference outputs, checks one or two integer attempts, and checks tool provenance plus one `quote` visit. The known reference outputs stay outside graph input and prompts. The model receives the tool's factual result because this is a receipt-copying task, not because the evaluator leaks an answer key.

The runner evaluates local/two → seven, regional/three → fourteen, and local/one → five. It writes `s1-solution-evaluation.txt` before asserting every row passed. A malformed output gets at most one repair; a schema-valid wrong amount fails without repair. Tool/model exceptions propagate and may prevent report creation. The file writer refuses overwrites.

<!-- SOLUTION_CODE -->

## Review and exact assessment answers: minutes 75–90

**Knowledge check 1.** `amount_ok` must be false when the model returns eight instead of seven. `schema_ok` may still be true if the keys, types, unit, and nonblank source meet the contract. This schema-only retry loop must not retry merely because the amount is wrong. Its purpose is formatting recovery; factual correctness is graded afterward. The overall row fails because all five metrics are required.

**Knowledge check 2.** A flush means submission was attempted, and a local run ID identifies the intended root. Neither proves remote persistence or UI visibility. Read-back with the correct project and explicit input/output selections verifies a particular stored payload. An authorized person must separately open the matching dashboard trace and record what was visible. A successful connection-check read-back is not a blanket guarantee about later graph runs.

**Knowledge check 3.** `project_id` identifies the owning project required by current retrieval. Explicit `INPUTS` and `OUTPUTS` selections request fields that are not returned by the ID-only default. The method is awaited because it is asynchronous. Credentials must remain outside state and metadata because callbacks can export those structures; even synthetic labels do not redact secrets.

## Marking criteria and recovery

Assess four areas: correct shipping arithmetic and validation; strict parsing without fabricated corrections; five correctly separated evaluator booleans; and honest execution/evidence interpretation. Full credit in an area requires both working behavior and a correct explanation. Give partial credit for a sound approach with one edge-case defect; withhold credit when a learner hard-codes row passes, imports the teacher answer, silently overwrites reports, or calls local IDs proof of ingestion.

Run `python -m pytest tests/lessons/test_s1.py -q` for focused offline evidence. The named model double is a test instrument, never a live-call substitute. The suite also checks callback ancestry locally; that is not a remote-storage test. The completed-starter contract check is skipped while TODOs remain, so passing reference tests alone does not certify student completion.

For schema failures, examine raw JSON and types before changing prompts. For wrong totals, inspect tool calculation and compare the actual receipt, not just the tool result. For missing traces, check region, workspace, project name, permissions, time filters, and bounded ingestion delay. Use the safe checker rather than printing SDK exceptions or secrets. If a report filename already exists, choose a fresh run directory.

Close by explaining the scope boundary: this small local evaluation is not a LangSmith experiment or a production benchmark. The official SDK can upload datasets and create experiments through `evaluate`, but that requires a deliberate separate workflow and permissions [1415]. Keep broader dataset design and LLM-judge extensions optional.

## References

[1411]: https://docs.langchain.com/langsmith/create-account-api-key "Official key permissions and tracing-only limitations"
[1412]: https://docs.langchain.com/langsmith/evaluation-concepts "Official deterministic and model-based evaluation concepts"
[1413]: https://docs.langchain.com/langsmith/trace-with-langgraph "Official graph tracing and nested operations"
[1414]: https://docs.langchain.com/langsmith/smithdb-sdk-migration-runs "Official projected asynchronous retrieval API"
[1415]: https://docs.langchain.com/langsmith/evaluate-llm-application "Official SDK experiment workflow"
