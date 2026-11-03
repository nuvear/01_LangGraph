# L04 — Three-node sequential profile

## Task: build a profile in three ordered updates

Complete `exercises/starters/l04.py` after studying the two-node demonstration. This is the source video's three-node name/age/skills exercise, with explicitly added validation and boundary cases. The source lesson runs [00:44:29–00:55:36](https://youtu.be/jGg_1h0qzaM?t=2669); the exercise chapter begins [00:54:04](https://youtu.be/jGg_1h0qzaM?t=3244). Do not use a model or tracing service.

The starter supplies the state schema, input validation, graph builder, and local checks. Your implementation work is confined to three TODO functions: `welcome`, `describe_age`, and `describe_skills`. Do not replace the graph with a single function or import the demonstration or reference solution. Keep the supplied edges and explain them below.

### Required behavior

1. `welcome` returns only `result` and `visited`. Start `result` with `<name> welcome to the system.` and reset `visited` to `["welcome"]`, even when stale generated values are present.
2. `describe_age` retains the welcome and appends ` You are <age> years old` without a final period. For age 1, use `year`. Extend the visited list with `"age"` by creating a new list.
3. `describe_skills` retains both earlier components and appends ` and you have skills in <formatted skills>.` For an empty list, append ` and you have no listed skills.` Extend the visited list with `"skills"`.
4. Preserve skill order and duplicates. One item stands alone. Two items use ` and `. Three or more use commas between earlier items and ` and ` before the last item, with no Oxford comma. Do not sort or normalize the input.
5. Never mutate the dictionary or lists passed to a node. Every node returns only the two generated keys. The final graph state must retain the original `name`, `age`, and `skills` values.

The target for Linda, 31, and `["Python", "machine learning", "LangGraph"]` is exactly:

```text
Linda welcome to the system. You are 31 years old and you have skills in Python, machine learning and LangGraph.
```

The final visited list must be `["welcome", "age", "skills"]`. There are exactly three work nodes, four total edges, and two edges between work nodes. Input validation is already complete: names must be nonblank strings, ages nonnegative integers excluding booleans, and skills a list of nonblank strings. An empty list is valid. Do not weaken those rules to make an example pass.

## Work sequence and commands

Use the prepared environment and repository-root module commands. Do not install packages or modify shared runtime files.

1. Run the baseline and record why its two results differ:

   ```bash
   python -m course_lessons.l04 --backend none
   ```

2. Run your starter once before editing:

   ```bash
   python -m exercises.starters.l04
   ```

   `STARTER_NOT_COMPLETED` is expected at this stage. A successful process exit does not mean the task passed.

3. Implement the TODO functions in order, rerunning after each change. Unfinished later functions still report incomplete work. After all checks pass, the starter prints `STARTER_CHECKS_PASSED` and the Linda message. If an assertion fails, repair your implementation, not the assertion.
4. After an independent attempt, compare with the separate reference:

   ```bash
   python -m exercises.solutions.l04 --backend none
   python -m pytest tests/lessons/test_l04.py -q
   ```

   The focused tests exercise the delivered demonstration and reference solution. They do not automatically assess edits to your starter. Use your starter checks, recorded cases, and teacher inspection as your own evidence.

## Three progressive hints

### Hint 1: inspect the prior value

List exactly which keys each function reads and writes. The age node needs the previous `result` as well as `age`. Returning only an age sentence cannot preserve the welcome, regardless of the edges.

### Hint 2: build a new value, not an in-place change

A partial update replaces each key it supplies. Construct the whole next string from the existing string plus the new clause. For the visited list, think of list concatenation producing a fresh list. The welcome node is intentionally different: it starts fresh rather than carrying stale generated data forward.

### Hint 3: separate list formatting from sentence assembly

Inside the skills node, determine the skills phrase before adding it to the existing result. Distinguish zero items, one item, and at least two items. For the last case, a slice of all but the final item and a lookup of the final item let you place `and` exactly once. This `if` belongs inside the node, not in graph routing.

## Observed results and explanations

Record actual values rather than writing “worked.” Keep these notes next to your starter or in your submitted workbook.

- **Baseline broken final:** record the complete string and identify the missing component.
- **Baseline corrected final:** record the complete string and the visited order.
- **Linda profile:** record the complete result and final visited list.
- **Ari, age 0, no skills:** record the complete result; check the `no listed skills` ending.
- **Jo, age 1, Python only:** record the complete result; check singular `year` and no extra `and` within the skill phrase.
- **Bo, age 2, Python and SQL:** record the complete result; check that no comma is needed between two skills.
- **Input preservation:** record before/after values for `name`, `age`, and `skills`; explain how you avoided list mutation.
- **Edge explanation:** write all four connections, identify the two work-node connections, and explain what would go wrong if the skills node ran before the welcome node.

## Completion criteria and stretch

You are finished when all three nodes return nonmutating partial updates, all recorded cases match the wording rules, input fields remain unchanged, the visited list proves the required sequence, and you can explain why default replacement caused the baseline bug. Inspect each function: a hard-coded Linda sentence does not meet these criteria.

Optional stretch: run a second profile through the same compiled graph, and then invoke it using a previous output as input. Predict whether any old generated text or visited items will leak. Record your prediction and actual result. Keep the same three-node topology, avoid persistence or model calls, and explain why resetting generated fields in `welcome` matters.

For API clarification, consult the official [partial-update explanation](https://docs.langchain.com/oss/python/langgraph/graph-api) and [sequential graph guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api), verified on 3 November 2026. Their shorthand sequence builder is not required for this explicit-edge exercise.
