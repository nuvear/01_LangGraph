# L05 — Conditional routes and two independent calculations

## Task: connect two conditional sections

Build a deterministic graph that accepts four integers and two operation strings, then returns two independent pairwise answers. The sections execute in sequence, but the second calculation must never use the first answer as an operand. Validation and branch evidence below support careful verification.

Use `exercises/starters/l05.py`. Complete exactly three focused functions: `route_first`, `route_second`, and `build_graph`. The starter already provides `PairState`, validation, four arithmetic nodes, the second router node, and acceptance checks. Do not replace the graph with one Python calculator function, import the solution, or hard-code the sample answers.

Your input fields are `number1`, `number2`, `number3`, `number4`, `operation1`, and `operation2`. Only the exact strings `+` and `-` are supported. Keep the supplied validation: actual integers are accepted, including zero and negatives, while numeric strings, floats, booleans, missing inputs, and unsupported operation tokens are rejected.

Section one computes `result1` from the first two numbers. Section two computes `result2` from the last two numbers. Preserve both results, all original input fields, and a `visited` list naming the four executed work nodes. Routing functions return labels; arithmetic nodes return update dictionaries. Current official documentation describes the conditional edge's source, path callable, and optional label-to-node map [507].

## Prepare and predict

1. Activate the P00 Python 3.12 environment and open a terminal at the repository root. Inspect the starter before editing. Run it once to confirm that unfinished work is honestly reported:

   ```bash
   python -m exercises.starters.l05
   ```

   Expected initial status: `STARTER_NOT_COMPLETED`, with a next-step message. A normal exit here does not mean the exercise passed.

2. Sketch the topology. START reaches `router1`; exactly one first arithmetic node reaches `router2`; exactly one second arithmetic node reaches END. Name the six registered work nodes on your sketch. Do not draw an ordinary outgoing edge and a conditional edge from the same router.

3. Before coding, predict the results and path for `10 - 5` followed by `7 + 2`. Record your prediction in one sentence in your notes. Then identify which input field each routing function should inspect. The two sections may reuse route labels but must have different destination maps.

## Implement and gather observations

4. Implement the two routing functions and connect the graph. Preserve the provided arithmetic and validation code. Return a compiled graph rather than the mutable builder. Use explicit START/END edges and explicit path maps.

5. Run the starter again. After every TODO is implemented correctly, the built-in checks should report `COMPLETED`, four checked operation combinations, successful independence checks, rejected unsupported operations, and a zero/negative check. A traceback or assertion failure is evidence to investigate, not a result to hide.

6. Inspect your own graph output, not just the reference solution. In a Python session, import `build_graph` from `exercises.starters.l05`, `execution_config` from `course_support.runtime`, and `graph_tracing` from `course_support.observability`. Inside `with graph_tracing("none"):` invoke your compiled graph with the required input dictionary and `config=execution_config()`. Print the returned state. To confirm executed nodes, stream the same input with `stream_mode="updates"` inside that context and record the update keys.

Use these short evidence fields; each should contain a concrete observation rather than “it worked”:

- **Baseline observation:** both result values and the exact four-name `visited` list from your implementation.
- **Combination observation:** result pairs for `++`, `+-`, `-+`, and `--`, using operands `10`, `5`, `7`, and `2` throughout.
- **Independence observation:** result pairs after changing only `number1` to `100`, then after separately changing only `number3` to `-7` in the original baseline.
- **Edge/failure observation:** the zero/negative case results, plus the exception type and field named when either operation is `*`.

7. After collecting your own evidence, compare with the independent reference and run only this lesson's focused regression tests:

   ```bash
   python -m exercises.solutions.l05 --backend none
   python -m pytest tests/lessons/test_l05.py -q
   ```

The reference source is `exercises/solutions/l05.py`; the baseline demonstration is `course_lessons/l05.py`. Pytest checks the demonstration/reference, not the correctness of your edited starter. Submit your starter and observations together. No API key, live request, dashboard, or remote trace is needed.

## Three progressive hints

### Hint 1: separate the decisions

The first routing callable reads `operation1`; the second reads `operation2`. Each returns `"addition"` or `"subtraction"`, not a dictionary or an arithmetic function call. Keep explicit rejection for any other token.

### Hint 2: map labels to the right section

The first path map targets nodes whose names end in `1`. The second targets nodes ending in `2`. The keys match routing return labels, not state keys. If a branch is unknown, check the keys first, then registered node names.

### Hint 3: preserve the middle connection

Both possible first arithmetic nodes need their own ordinary edge to `router2`. Only the second pair's arithmetic nodes finish at END. Keep result updates separate so computing `result2` does not overwrite `result1`.

## Completion criteria and stretch

The baseline must return `(5, 9)` and `visited=["router1", "subtract1", "router2", "add2"]`. With the same operands, `++`, `+-`, `-+`, and `--` must return `(15, 9)`, `(15, 5)`, `(5, 9)`, and `(5, 5)`. Changing only the first number to `100` must return `(95, 9)`; separately changing only the third number to `-7` must return `(5, -5)`. The zero/negative check uses `0 - 5` and `-7 + 0`, returning `(-5, -7)`. Both invalid-operation positions must be rejected before arithmetic. Your starter must report `COMPLETED`, retain inputs, and show exactly one selected branch in each section.

**Optional stretch:** sketch multiplication as a third route in both sections using the [official routing reference][507]. Explain which callable labels, maps, nodes, edges, and tests change. Preserve required plus/minus behavior; this extension is not assessed.

<!-- REFERENCES_INLINE -->

[507]: https://reference.langchain.com/python/langgraph/graph/state/StateGraph/add_conditional_edges "Official conditional-edge reference, verified 3 November 2026"
