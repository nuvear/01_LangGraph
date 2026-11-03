# S1 — LangSmith observability and evaluation

## Task: audit synthetic shipping receipts

**SUPPLEMENTARY practice · Allow 25 minutes of independent work.** Complete three functions that calculate a synthetic shipping quote, decode the model's receipt, and score actual output. The supplied graph and report writer remain unchanged. Your implementation must not import the demonstration or teacher solution.

Start in `exercises/starters/s1.py`. The independent reference is `exercises/solutions/s1.py`; consult it only after attempting the task. The separate demonstration is `course_lessons/s1.py`. Required background is L09 and the S1 guided trace inspection. All data are invented teaching values, not shipping prices or customer information.

Run the starter from the repository root:

```bash
python -m exercises.starters.s1
```

Initially, it must print `STARTER_NOT_COMPLETED` and exit successfully without contacting services. This status does not pass the task. After implementation, use its live command only with instructor approval:

```bash
python -m exercises.starters.s1 --live
```

S1 defaults to LangSmith. `--backend none` can disable tracing for diagnosis, but `--live` still authorizes a real Anthropic request. Never include keys or configuration dictionaries in code, state, prompts, metadata, reports, or screenshots.

## Implement the three functions

1. Implement `shipping_quote(region, weight)`. Local costs `3 + 2 * weight` credits; regional costs `5 + 3 * weight`. Weight must be an integer from one through ten inclusive. Reject booleans, floats, strings, out-of-range weights, and unsupported region names with `ValueError`. Return exactly `total`, `unit` equal to `credits`, and `source` equal to `shipping-policy-v1`.
2. Implement `decode_receipt(text)`. Accept only a JSON object with exactly `total`, `unit`, and `source`. Require an integer total excluding booleans, the unit `credits`, and a nonblank string source. Return `{}` for invalid JSON/schema, including arrays, missing/extra fields, or Markdown fences. Keep a schema-valid wrong amount or wrong nonblank source unchanged; do not copy the correct values into it.
3. Implement `evaluate_receipt(outputs, reference_outputs)`. Decode `outputs.get("raw", "")`. Return exactly five named booleans. `schema_ok` means decoding succeeded. `amount_ok` compares the decoded total to the reference total. `source_ok` compares its source to the reference source. `bounded_attempts` requires an integer attempt count of one or two. `tool_evidence` requires the tool result's source to equal `shipping-policy-v1` and exactly one `quote` entry in `trace_log`. Missing raw text or tool evidence must fail the relevant metrics, not produce a guessed pass.

The fixed dataset has local/two kilograms → seven credits, regional/three → fourteen, and local/one → five. These references are used by the evaluator, not added to graph input. The formatter receives the tool's result as factual task input.

The supplied graph invokes the tool once, formats a receipt, and checks schema. A malformed first response allows one additional formatting attempt. After the second attempt it terminates even if schema is still invalid. A schema-valid wrong amount fails evaluation without triggering a formatting retry.

## Verify without mislabeling evidence

Run the focused suite:

```bash
python -m pytest tests/lessons/test_s1.py -q
```

The suite tests both demonstration and reference solution using an explicitly named offline chat-model double. It also contains a completed-starter contract check: while TODOs remain, that check is skipped rather than falsely passing. Inspect the skip reason. After implementation, the starter contract check must run and pass. Passing only the reference tests is not evidence that your functions work.

For instructor-approved live comparison, run:

```bash
python -m course_lessons.s1 --live
python -m exercises.solutions.s1 --live
```

Each command performs three to six graph-level model invocations; SDK retries can add requests. The starter saves `s1-starter-evaluation.txt`, the demo saves `s1-demo-evaluation.txt`, and the solution saves `s1-solution-evaluation.txt`, each beneath its run directory. Use `report_path` rather than assuming the current directory. Each file is a JSON report, not an uploaded LangSmith experiment [1421].

## Progressive hints

### Hint 1: separate calculation from formatting

Represent each region with a base charge and a per-kilogram charge. Validate weight before arithmetic. Remember that `isinstance(True, int)` is true in Python; decide how to reject that input explicitly.

### Hint 2: parse before comparing

Use `json.loads` and verify the object type before inspecting keys. An invalid schema returns `{}`. The decoder does not know the expected amount; that belongs to the evaluator. Whitespace and JSON key order should not affect acceptance.

### Hint 3: use the actual model output

Read `raw`, not merely the tool's correct calculation. A valid receipt can still have the wrong amount. Keep the five metric results separate so a failure explains what went wrong. A single `quote` visit is local execution evidence, not remote-ingestion proof.

## Record observed results

Record your offline command, test counts, and whether the completed-starter check ran: **Command and result:** ______.

Record the three observed totals and their five metric results: **local/two:** ______; **regional/three:** ______; **local/one:** ______. Note whether the evidence used a test double or real Anthropic calls: ______.

Record one report path, assigned run ID, and observed node path: ______. Separately record **remote payload read-back:** verified / failed / not checked; and **dashboard hierarchy:** observed / unavailable / not checked. Add the evidence identifier or reason: ______. A flush or local UUID alone cannot fill either field as verified.

## Completion criteria and stretch

Completion requires three passing dataset rows, a strict decoder that rejects malformed schema, a failing amount score for a valid receipt containing eight instead of seven, correct weight/region rejection, and no more than two formatter invocations per example. The report must be a new file, preserve raw model output, and leave dashboard verification false unless separate inspection is genuinely recorded outside the program. Explain why the local report does not prove trace persistence.

For a stretch task, propose a fourth independent case and a failure-specific metric, without changing the required three-case baseline. Explain whether a deterministic rule or a reviewed LLM-judge rubric is appropriate. Do not upload a dataset or enable another tracing service as part of this stretch.

## Reference

[1421]: https://docs.langchain.com/langsmith/evaluation-concepts "Official datasets, experiments, and evaluator concepts"
