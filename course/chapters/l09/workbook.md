# L09 — ReAct arithmetic tool loop

## Your task: an audited arithmetic runner

Build a small, bounded tool-using agent and prove what it executed. Use L08 message concepts and the baseline demonstration before starting. Plan approximately fifty minutes for the independent implementation within the lesson's broader practice allocation.

Your editable starter is `exercises/starters/l09.py`. The independent reference is `exercises/solutions/l09.py`; keep it closed until review. The baseline is `course_lessons/l09.py`, and focused offline tests are `tests/lessons/test_l09.py`. Do not solve the task by importing either completed implementation. The starter already provides the integer tools, state schema, prompt, error-observation handler, CLI readiness probe, and three-case acceptance harness.

An unchanged starter must print `STARTER_NOT_COMPLETED` and exit successfully. That message is intentionally not a passing exercise result. The readiness probe detects unfinished TODOs without making model calls; it is not a substitute for testing your implementation.

## Implement three focused functions

1. Complete `route_next(state)`. Require the last message to be an `AIMessage`. Reject a different role with `TypeError`, malformed `invalid_tool_calls` with `ValueError`, and a batch above three calls with `AuditLimit`. Return `"tools"` for valid calls, otherwise END. Routing must not execute arithmetic.
2. Complete `make_agent(model, *, max_model_calls=4)`. Accept budgets from one to ten, rejecting values outside that range. Bind the supplied tools to the injected model. Build `START → model`, a conditional tools/END route, and `tools → model`. The model node must prepend the system instruction, include accumulated messages, forward its `RunnableConfig`, return only the new reply and incremented count, and raise `AuditLimit` before any invocation beyond the budget. Use `ToolNode` with the supplied validation handler. Request invocation already uses `execution_config()`; preserve it.
3. Complete `collect_audit(state)`. Return `model_calls`, `tool_calls`, `audit`, and `final_text`. Each audit row must contain `call_id`, `tool`, `args`, `result`, and `status`. Match results by call ID, even if a batch's results arrive in reverse order. Keep error results marked as errors. Raise `ValueError` for empty/duplicate call IDs, orphan/missing results, a non-tool message interrupting a pending batch, or a missing, empty, or still-tool-calling final AI answer. Never generate a result because you know the expected arithmetic.

## Run and record the three exact cases

From the repository root, with the project environment active:

```bash
python -m exercises.starters.l09
python -m pytest tests/lessons/test_l09.py -q
```

The supplied focused tests validate the baseline and independent reference solution with explicit offline model doubles. They do **not** automatically grade your edited starter. Inspect their scripted message sequences and apply the same cases to your injected-model builder during review. No API key is needed for this offline inspection; do not replace the actual live model factory with a canned responder.

After instructor authorization, run your implemented starter:

```bash
python -m exercises.starters.l09 --live --backend none
```

This makes real paid Anthropic requests. Without `--live`, a completed model-based starter should refuse model creation rather than claim an offline success. The provided harness checks these exact requests:

- **Compound:** “Subtract 5 from 18. After seeing the result, multiply that result by 4.” Observe successful results `13` then `52`, in separate tool rounds. The first call must be `subtract(a=18, b=5)`. The later multiplication must use `13` and `4`, and the final answer must include `52`.
- **Independent:** “Compute 9 + 6 and separately 8 * 3.” Observe successful results `15` and `24` from add and multiply. One shared batch or separate valid batches are both acceptable within four model calls. The final answer must include both results.
- **Greeting:** “Say a friendly hello. Do not calculate anything.” Observe a nonempty final answer, zero tools, and one model call.

Record evidence, not private reasoning. For the compound case, note both call IDs, their matching result IDs, and the multiplication arguments: ______. For the independent case, note the chosen batching pattern and model-call count: ______. For the greeting, record the tool count and final-message role: ______. For an offline failure case, record whether it produced an error observation or a budget exception, and why: ______.

## Three progressive hints

**Hint 1 — control flow:** inspect structured `tool_calls`, not message text. The route returns a label; `ToolNode` executes the registered functions. The model must receive each observation on its next turn.

**Hint 2 — state updates:** `add_messages` merges the new message update. Return `[response]`, not a rebuilt history. Initialize the counter at zero and check it before each model invocation, not after an unwanted fifth call.

**Hint 3 — auditing:** keep a dictionary of pending calls keyed by ID and a set of IDs already used. Remove a pending call when its result arrives. A later AI message is invalid while any pending entries remain. Keep failed observations in your rows instead of converting them into numeric successes.

## Completion, review, and stretch

Complete only when all three live cases satisfy the harness and an instructor has reviewed offline malformed-call, unknown-tool, missing-result, reversed-batch, and repeating-model behavior. A repeating double must stop at the configured model-call budget; a tool error may be explained or corrected, but must never be counted as a successful calculation. Exact model sentences and independent batching need not match the reference.

After assessment, compare with:

```bash
python -m exercises.solutions.l09 --live
```

For a stretch, test negative and zero operands through your injected-model interface. Demonstrate that three minus eight returns a negative result and that a product with zero stays zero. Do not add division or new external services.

## Reference to consult

The [official graph quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart) explains the tool loop, while the [Graph API message guide](https://docs.langchain.com/oss/python/langgraph/graph-api) explains ID-aware updates. These current-API references support the exercise; the stricter audit and execution budgets are part of this course.
