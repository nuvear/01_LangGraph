# L03 — Multiple inputs and one-node arithmetic

## Task: finish one calculator node

Build one compiled LangGraph graph that receives an integer list, a name, and an operation. Select addition or multiplication with Python logic inside one node. Strict validation, exact output formatting, numeric outputs, and empty-list rules below define the assessment contract.

Start from `exercises/starters/l03.py`. Implement its three TODO functions, not a new script. Do not import `exercises.solutions.l03` or `course_lessons.l03` into your submission. The independent reference, for review after your attempt, is `exercises/solutions/l03.py`.

### Exact input and output agreement

The required inputs are `values`, `name`, and `operation`. `values` must be a list containing only actual integers; booleans and floats are invalid. Empty lists are valid. `name` must be a string containing at least one non-whitespace character. Preserve the supplied valid name exactly rather than trimming it. `operation` must be the string `+` or `*`. Missing or invalid required inputs must raise `ValueError`.

The node returns exactly two fields: `answer`, an integer, and `result`, formatted exactly as `Hi {name}, your answer is {answer}.` Include the comma and final period. Do not modify the supplied dictionary or its list. The final graph state must retain the three input fields and include the two outputs. If old outputs were supplied, replace them with the new calculation.

Use exactly one work-performing node named `calculator`. Connect START to that node and the node to END with ordinary edges. Return the compiled graph from `build_graph`. Do not create separate addition/multiplication nodes or use graph-level conditional edges.

## Work in three passes

1. Implement `validate_inputs`. Check all required fields explicitly; type hints alone are not runtime validation. Test a valid request, a missing operation, a blank name, and `[True]` before attempting the graph.
2. Implement `process_values`. Call validation first. Use an `if` for `+` and multiplication for `*`. Return only the two computed fields. Check the function directly so arithmetic mistakes are separate from graph-building mistakes.
3. Implement `build_graph`, compile it, and run the starter checks. Keep `execution_config()` in the supplied invocation calls. Stay offline and do not enable a tracing backend.

From the repository root, using the activated Python 3.12 environment:

```bash
python -m exercises.starters.l03
```

Before implementation, expect `STARTER_NOT_COMPLETED`. That message is deliberately not success evidence. After all TODOs are complete and checks pass, expect `STARTER_CHECKS_PASSED`. A failed assertion or exception means there is still a concrete issue to fix; do not remove the check to obtain the message.

After your attempt, compare with the independent reference and run the focused delivered-code tests:

```bash
python -m exercises.solutions.l03 --backend none
python -m pytest tests/lessons/test_l03.py -q
```

These pytest tests validate the delivered demo/reference and the starter's checker, not every line of your edited implementation. Your starter command and a review of the three functions establish your own completion. No `--live` flag or model connection belongs in this task.

## Record observed behavior

Use Jack Sparrow and `[1, 2, 3, 4]` first. With `*`, the expected answer is 24 and the expected message is `Hi Jack Sparrow, your answer is 24.` With `+`, the expected answer is 10. Then test Mei with `[-3, 0, 5]`: addition should give 2 and multiplication should give 0. Test `[-2, 3]` with `*` for a negative product, and `[7]` with `+` for a singleton.

Empty addition must return 0; empty multiplication must return 1. Try `/`, a tuple instead of a list, `[2.5]`, and a missing name. Each must raise `ValueError`, not calculate silently.

Write the observations rather than copying these expectations:

- Starter status and command used: __________
- Jack Sparrow multiplication answer and exact message observed: __________
- Addition and signed/zero results observed: __________
- Empty `+` and empty `*` results observed: __________
- Invalid request tested and exception type observed: __________
- Evidence that input fields survived and the original list did not change: __________

## Three progressive hints

### Hint 1: inspect actual values

Use dictionary `.get` to inspect fields that might be absent. A `NotRequired` output may be missing; that says nothing about runtime validation of required inputs. Check `type(item) is int` if you need to exclude booleans.

### Hint 2: choose the arithmetic identity

`sum` naturally begins at 0. `math.prod`, already imported in the starter, begins at 1. If you write multiplication manually, think about the starting value before processing an empty list. Validate operation tokens before allowing an `else` to mean multiplication.

### Hint 3: separate update from final state

Return only `answer` and `result` from the node. LangGraph retains input fields that were not updated. The builder must register `process_values` once and return the compiled executable, not itself.

## Completion criteria and stretch

You are finished when the starter prints its checked-success message, both operations satisfy all listed cases, invalid/missing inputs raise `ValueError`, the node returns only computed fields, the final state retains the inputs, and the topology has exactly one arithmetic node. Explain why no model call or graph-level branch was needed.

For an optional stretch, add your own test cases for large integers and names containing non-ASCII characters without changing the accepted operations or adding nodes. Verify exact preservation of the name. This is additional practice, not a new required task.

## References

- [Official Graph API state/update guidance](https://docs.langchain.com/oss/python/langgraph/graph-api).
- [Python 3.12 TypedDict and NotRequired](https://docs.python.org/3.12/library/typing.html#typing.TypedDict).
- [Python 3.12 math.prod and its starting value](https://docs.python.org/3.12/library/math.html#math.prod).
