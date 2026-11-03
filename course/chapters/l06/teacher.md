# L06 — Bounded loops and automatic higher/lower game

## Explain: teaching purpose and preparation

This 110-minute lesson completes the deterministic foundations. After L05's conditional routing, the new idea is revisiting a node. Assess whether learners connect changing state to an explicit stopping rule, not whether they reproduce a random sequence. Assign the student/workbook automatic midpoint game without human prompts or a model.

Before class, select the prepared Python 3.12 environment and open `course_lessons/l06.py`, `exercises/starters/l06.py`, and the workbook. Keep `exercises/solutions/l06.py` for the debrief. Work from the repository root so imports resolve. Use installed course dependencies; provider keys are unnecessary. The shared runtime imports foundation packages but never requests configuration here.

Allocate 15 minutes to explanation, 10 to illustration, 10 to the demonstration, 25 to guided practice, 40 to independent work, and 10 to review.

## Illustrate: make the stopping rule visible

In minutes 0–15, ask, “What state changes when a node runs for the second time?” Expected response: it receives accumulated updates, not the original input. Sketch the greeting reset followed by generation and conditional return. Define a back-edge as graph control flow, not Python call-stack recursion. Have learners identify the progress value, its increment, its initial value, and the comparison that ends the loop.

In minutes 15–25, use the original diagram and the conceptual figure separately. The first explains our implementation; the second explains the conceptual loop. Do not imply that a conceptual figure is an execution screenshot of adapted code.

<!-- ORIGINAL_DIAGRAM -->

<!-- CONCEPT_FIGURE -->

Ask why resetting only the counter is incomplete. Expected response: stale values in the list would still appear in a new run, even if the number of new generations were correct. The implementation clears both derived fields and preserves `name` in a separate field. Explain that current LangGraph partial updates replace ordinary list-valued keys unless a reducer is supplied. Here the node explicitly builds the complete new list; no accumulator reducer is present.

## Demonstrate: a ten-minute bounded run

In minutes 25–35, run:

```bash
python -m course_lessons.l06 --backend none
```

Spend two minutes locating reset and progress updates, three tracing the conditional path map, three examining the returned summary, and two distinguishing the safety limit from the loop rule. Expected stable properties are counter five, list length five, every integer within 0–10, a Student greeting, and repeatability across fresh runs. Do not grade the exact random list or narrate unrecorded service evidence.

The local `Random(seed + counter)` policy provides deterministic instruction. It neither uses a global random seed nor leaves a mutable generator advancing between runs. Random generation makes graph repetition visible; its exact output is not the goal. Explicit `START` edges and dictionary updates support the current Graph API semantics described in the [Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api).

<!-- EXECUTION_FIGURES -->

## Guided practice: diagnose state rather than guess

In minutes 35–60, have pairs follow the student chapter's four steps. They should predict generation counters one through five, then stream updates using `execution_config()` inside `tracing_context(enabled=False)`. Expect one greeting update and five generation updates. The old `999` must not survive the reset. Repeat on the same compiled graph to demonstrate independence from previous invocation history.

Ask learners to point to a node return and a route return. A correct explanation names dictionaries as state updates and strings as labels translated by a path map. If someone proposes an ordinary loop edge plus conditional routing, ask what would cancel the ordinary edge when the condition says stop. Nothing does: remove the unconditional edge. Do not “repair” this by increasing `recursion_limit`.

For the game, identify the additional distinction: `guess_node` chooses a candidate without reading the target, while `feedback_node` compares it with the target. The target is visible synthetic state, not a security boundary. Separating responsibilities demonstrates algorithmic discipline, not secret-information protection.

## Independent exercise and solution walkthrough

In minutes 60–100, assign the workbook task exactly. Learners implement three functions in the independent starter: configuration validation and reset; midpoint guessing and counting; comparison, narrowing, and terminal status. Wiring and the read-only router are supplied. Until unfinished TODOs are replaced, the starter must print `STARTER_NOT_COMPLETED` rather than claim success.

Require target 17 with budget seven, target 20 with budget two, and target 15 with budget two. The first should use guesses `10, 15, 18, 16, 17` and win after five attempts. The second should use `10, 15`, finish with hint `higher`, and lose normally at two. The third proves equality takes priority over exhaustion. Also require every target 1–20 to win under the default budget, invalid configuration to raise `ValueError`, and dirty derived input to be reset without changing the caller's list.

The reference solution is independent of the demonstration. `new_game` creates a full input dictionary. `reset_game` validates integer targets 1–20 and budgets 1–7, explicitly rejecting booleans; Python otherwise treats booleans as integers. It also rejects blank or non-string names. Only derived fields are replaced. `guess_node` appends a floor midpoint through list construction and increments attempts exactly once. `feedback_node` handles equality first, then excludes a missed candidate with `guess + 1` or `guess - 1`, and finally classifies a miss as `playing` or `lost`. The router returns `again` only for `playing`; both terminal statuses map to `END`.

Every correct miss leaves the target within the remaining inclusive interval and strictly shrinks that interval. These invariants explain the behavior better than memorizing a trace. With deterministic midpoint guessing, the default interval does not naturally need all seven guesses, so the smaller budget intentionally exposes the exhaustion route without introducing a bad strategy.

<!-- SOLUTION_CODE -->

Run the independent reference and focused tests from the repository root:

```bash
python -m exercises.solutions.l06 --backend none
python -m pytest tests/lessons/test_l06.py -q
```

The pytest file checks the delivered demo and reference solution, not the learner's edited starter. The starter's self-check invokes the learner's functions. Tests use real local LangGraph execution, deny network/configuration/model access, and do not substitute canned model responses. No model exists in this lesson.

## Review: exact knowledge-check answers

Use minutes 100–110 to collect explanations, not just final numbers.

1. **The baseline receives counter `-12` and numbers `[999]`. Why must the greeting reset both fields, and what should the final counter and list length be?** Resetting the counter establishes the intended five-visit schedule instead of counting from a negative value. Resetting the list removes earlier output. The final counter and list length must both be five, with no stale `999`. A learner who says only “counter five” has missed the data-isolation requirement.
2. **In the automatic game, a guess is 10 and the target is higher. What exact bound update prevents repetition, and why is assigning `lower = 10` insufficient?** Set `lower = 11`, expressed generally as `guess + 1`. Ten has already been ruled out, so retaining it leaves a known miss in the inclusive interval and can permit repeated guesses when the interval becomes small. The answer must explain exclusion, not merely say “increase the bound.”
3. **A game uses budget two and target 15. What should happen after guesses 10 and 15? Explain why the budget check must not override success, and why a recursion-limit exception is not a normal `lost` result.** The second guess is correct, so hint is `correct`, status is `won`, and attempts is two. Equality is checked before a missed-guess budget check. A recursion error counts graph execution super-steps, not attempts, and reports failure to complete within an execution guard; it is not the game's explicit exhaustion outcome.

## Marking, misconceptions, and recovery

Award ten marks: two for validation/reset and preserving configuration, two for midpoint/counter/list updates, two for correct strict bounds and hints, two for both terminal paths with final-attempt success priority, one for automated full-range checks, and one for explanation of recursion limits. Require both exit paths and the maximum budget for completion regardless of total. Do not award marks for adding a model, user prompts, or a clever interface outside scope.

If history is truncated, inspect singleton list replacement. If guesses repeat, inspect inclusive bounds. If the attempt count is inflated, locate duplicate increments; feedback must not count an extra attempt. If stale state leaks, inspect reset updates. If import errors occur, return to the repository root and the prepared environment rather than running lesson files directly. If `GraphRecursionError` occurs in an ordinary run, recover the intended state rule and edges first. Shared configuration uses 40 super-steps as a guard, not seven attempts as a default.

## References

The [official Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api) and [loop/control guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api) support the current state-update, compilation, conditional-edge, and recursion-error teaching points. Parent-managed rendering, screenshots, integration, and any later platform validation remain separate from this offline lesson.
