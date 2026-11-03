# L03 — Multiple inputs and one-node arithmetic

## Explain: several inputs, one processing step

A graph invocation can receive more than one value. In this lesson, one state dictionary carries a person's name and a list of integers. One ordinary Python function calculates a sum and returns a formatted result. The independent exercise adds an operation field so that the same node can add or multiply. Nothing here needs a language model, an API key, or a paid request.

**Prerequisite:** L02, including dictionaries, functions, compilation, and invocation. Allow approximately 75 minutes. By the end, you should be able to describe mixed-type state, return only computed fields, distinguish optional keys from nullable values, and test two arithmetic paths without adding graph branches.

**Video-backed material:** the source window is [00:33:07–00:44:29](https://youtu.be/jGg_1h0qzaM?t=1987). Coding begins at [00:34:02](https://youtu.be/jGg_1h0qzaM?t=2042); the addition/multiplication exercise begins at [00:43:27](https://youtu.be/jGg_1h0qzaM?t=2607). The presenter explicitly keeps this section non-LLM. The supplied whole-track visual review confirms the multiple-input exercise slide at 00:43:35. Figures below are reserved for parent-captured source and execution images, not invented evidence.

<!-- VIDEO_FIGURE -->

### Mixed types belong in named fields

Our baseline `SumState` has required inputs `values: list[int]` and `name: str`. Derived fields are `total: NotRequired[int]` and `result: NotRequired[str]`. A schema describes the intended keys and their types. Here, `values` is a list, while `name` and `result` are strings. Different fields do not need the same type.

`total` is useful for checking arithmetic without parsing a sentence. `result` is useful for displaying that arithmetic to a person. Separating them is an **added teaching adaptation**; it does not make the graph more intelligent. Both outputs are produced by the same node.

Python's [TypedDict documentation](https://docs.python.org/3.12/library/typing.html#typing.TypedDict) explains that a typed dictionary remains a plain dictionary at runtime. An annotation is a description for tools and readers, not an automatic input validator. A caller can still supply a float, a boolean, or a missing field. Our explicit validation rejects those mistakes with `ValueError` before calculating.

### Absent does not mean None

`NotRequired[str]` permits a key to be absent. It does not promise to insert that key or initialize it to `None`. Conversely, `str | None` permits a present value to be either a string or `None`; it does not, by itself, make a typed-dictionary key optional. The [Python typing reference](https://docs.python.org/3.12/library/typing.html#typing.NotRequired) documents this distinction.

The baseline therefore supplies only `values` and `name` when invoking the graph. The node computes outputs without reading a previous `result`. Do not write a placeholder empty string just to satisfy a misleading assumption about required outputs. Do not add to an absent result before creating it.

## Illustrate: input, update, and final state

Imagine the input is `{"values": [1, 2, 3, 4], "name": "Steve"}`. `process_values` validates those two fields, uses Python's `sum`, and returns only `total` and `result`. The expected total is 10 and the exact baseline result is `Hi there Steve! Your sum = 10.`

A **partial update** is a dictionary containing only fields the node writes. The [LangGraph Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api) describes how these updates are applied to graph state. With no custom reducers in this lesson, an updated field is replaced; fields not updated remain available. Consequently, the final state retains `values` and `name` and includes the two outputs. Returning only outputs does not erase inputs.

Our node neither assigns into the supplied dictionary nor changes its list. This makes it easier to compare the input with the final state. If callers supply an old `total` or `result`, the newly calculated values replace them rather than accumulating text.

The original diagram shows the exercise topology. Validation and the Python `if` happen inside the one calculator node. START and END mark boundaries; they are not two additional arithmetic workers. The baseline uses the same shape with its node named `processor`.

<!-- ORIGINAL_DIAGRAM -->

## Demonstrate: run the complete sum example

From the repository root, use the Python 3.12 environment prepared in P00. The commands below use its activated `python`; do not execute a nested file directly.

```bash
python -m course_lessons.l03 --backend none
```

The tested source for that command is included here:

<!-- EXAMPLE_CODE -->

Read `build_graph` in order: make `StateGraph(SumState)`, register `processor`, connect START to the node, connect the node to END, and return `builder.compile()`. The [StateGraph reference](https://reference.langchain.com/python/langgraph/graph/state/StateGraph) states that `StateGraph` is a builder, not the executable graph. Invoke the compiled object, not the builder.

The program returns a small JSON summary. Look for `node_update`, `final_state`, and `selected_result`. They illustrate three different views of the same calculation. `selected_result` is simply `answer["result"]`, not another graph execution. Expect `model_used` to be false. The built-in assertions also check an empty sum, signed integers, and preservation of the supplied input.

`--backend none` makes the demonstration explicitly untraced. Do not add `--live`; it contributes nothing to arithmetic. The shared CLI may prepare an output directory, but this example writes no answer files. Any execution figures inserted below will be produced from actual runs by the parent workflow.

<!-- EXECUTION_FIGURES -->

## Guided practice: inspect before extending

1. Open `course_lessons/l03.py` and identify the required inputs and optional outputs. Explain why `total` is an integer while `result` is a string. Predict the node update before running the command.
2. Compare the printed `input`, `node_update`, and `final_state`. Confirm that the update has two keys and the final state has four. Locate the assertion that checks the input was not mutated. A full-state return and a partial update are different objects with different responsibilities.
3. In a Python session started at the repository root, call the compiled graph with a new list. Keep the invocation configuration rather than bypassing the shared runtime:

   ```python
   from course_lessons.l03 import build_graph
   from course_support.runtime import execution_config

   graph = build_graph()
   answer = graph.invoke(
       {"values": [-3, 0, 5], "name": "Mei"},
       config=execution_config(),
   )
   print(answer["total"])
   print(answer["result"])
   ```

   Before this interactive step, ensure tracing is disabled as established in P00; the CLI command above already disables it. Expect total 2 and a sentence containing Mei. Then try an empty list: the baseline sum is 0.
4. Try `[True]` and then `[2.5]` as `values`. Expect `ValueError`, not a successful arithmetic answer. Python treats booleans as integer subclasses, so our strict check uses `type(item) is int`. This validation policy is deliberate; it is not provided automatically by `list[int]`.

## Independent task: one-node arithmetic

Implement the three TODO functions in `exercises/starters/l03.py`: `validate_inputs`, `process_values`, and `build_graph`. The workbook contains the same task and an observation record. Keep one work-performing node named `calculator`, with ordinary START and END edges. The Python conditional belongs inside `process_values`; do not use `add_conditional_edges` or separate operation nodes.

Require `values` to be a list of actual integers excluding booleans, `name` to be a nonblank string, and `operation` to be exactly `+` or `*`. Missing or invalid required inputs must raise `ValueError`. Preserve valid input fields exactly, including the supplied name. Return only `answer` and `result` from the node, with the exact message `Hi {name}, your answer is {answer}.`

For Jack Sparrow, `[1, 2, 3, 4]` and `*`, the answer must be 24. The same list with `+` must produce 10. Accept negative values and zero. Define empty addition as 0 and empty multiplication as 1. Python's [math.prod](https://docs.python.org/3.12/library/math.html#math.prod) starts with 1, which explains the latter identity. Reject `/` rather than accidentally treating every non-plus token as multiplication.

Run `python -m exercises.starters.l03`. Before implementation, it exits normally with `STARTER_NOT_COMPLETED`, which is not a pass. After implementation, `STARTER_CHECKS_PASSED` means its arithmetic, preservation, topology, and rejection checks completed. The independent reference is `exercises/solutions/l03.py`; use it after making your attempt.

## Review: three knowledge checks

1. For the baseline input Steve and `[1, 2, 3, 4]`, what exact update should `process_values` return? Which fields should the final graph state retain, and why need the update not repeat them?
2. What does `result: NotRequired[str]` allow, and how does it differ from a required `result: str | None`? Will either annotation alone reject `[True]` or `[2.5]` as `values`?
3. Does the exercise's `if` create graph-level routing? State the required empty-list answers for `+` and `*`, and the required behavior for `/`.

## Troubleshooting and current-API differences

If the builder has no `invoke` method, use the value returned by `compile`. If a key is missing, check the actual invocation dictionary; do not assume TypedDict inserted `None`. If a graph node returns an integer or string directly, wrap outputs in the specified update dictionary. If every product is zero, check whether a hand-written accumulator incorrectly starts at zero.

The source uses historical entry/finish helpers and in-place state mutation. This adaptation uses explicit START/END edges and partial updates, following current official guidance. The source's discussion of an omitted result is not a general initialization guarantee. Strict validation, exact punctuation, the numeric output, and empty-list rules are added here to make the exercise assessable. Graph-level conditional routing belongs to L05, not this task.

## References

[Video intro](https://youtu.be/jGg_1h0qzaM?t=1987) · [Original exercise](https://youtu.be/jGg_1h0qzaM?t=2607) · [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api) · [StateGraph](https://reference.langchain.com/python/langgraph/graph/state/StateGraph) · [TypedDict](https://docs.python.org/3.12/library/typing.html#typing.TypedDict) · [math.prod](https://docs.python.org/3.12/library/math.html#math.prod).
