# L05 — Conditional routes and two independent calculations

## Explain: establish the decision boundary

Teach this lesson after L04. Allocate 115 minutes: minutes 0–12 explain the decision boundary; 12–22 interpret the diagram; 22–40 demonstrate the baseline; 40–65 guide practice; 65–100 run the independent exercise; and 100–115 assess and recover. Learners need dictionary access, return values, `TypedDict`, and ordinary sequential edges. Do not introduce model credentials, tools, reducers, or checkpointing as requirements.

<!-- CONCEPT_FIGURE -->

Ask: “Where was L03's decision made?” Expect “inside its one processing node.” Then ask: “What changes today?” Expect “the next graph node is selected.” A student who says only “we add another if statement” has missed the orchestration distinction. Explain that ordinary nodes return update dictionaries, whereas this conditional-edge callable returns a label. Current documentation explicitly separates the two mechanisms [504].

## Illustrate: trace only one outgoing branch

Use the diagram below to predict the independent exercise. With `operation1="-"` and `operation2="+"`, learners should trace `router1`, `subtract1`, `router2`, and `add2`. Emphasize that the convergence at `router2` does not require both first arithmetic branches. One branch is selected on each run.

<!-- ORIGINAL_DIAGRAM -->

Clarify the word “independent.” The sections run sequentially; their operand pairs are independent. The first calculation uses `number1` and `number2`, while the second uses `number3` and `number4`. Graph state is shared forward so both answers survive, but `result1` is never substituted for an input to section two. Ask a learner to point to the second pair before any coding begins.

## Demonstrate: an eighteen-minute baseline walkthrough

In minutes 22–26, inspect `course_lessons/l05.py`: identify required inputs, optional computed outputs, and the explicit integer/operation checks. Explain why `type(value) is int` rejects booleans, which Python otherwise treats as integer instances. This restriction is an added exercise policy, not a LangGraph requirement.

In minutes 26–31, contrast `validate_inputs`, `choose_route`, and `add_numbers`. The first returns `{}` after successful validation. The second returns `"addition"` or `"subtraction"`. The third returns computed state fields. Point out that the callable is passed without parentheses to `add_conditional_edges`; LangGraph calls it after the source node completes.

In minutes 31–36, inspect registration and run:

```bash
python -m course_lessons.l05 --backend none
```

Expected properties are four successful checked cases, a selected arithmetic node per case, rejection of `*`, and `model_calls=0`. Do not describe this as an Anthropic or tracing test. In minutes 36–40, inspect local update streaming and compare its actual node keys with the selected-node field. This is stronger evidence than reading a label alone.

<!-- EXECUTION_FIGURES -->

The current API accepts an explicit path map and uses return hints/map information to constrain visualization [505]. `set_entry_point` is still documented as equivalent to an explicit START edge [506]. Retain explicit boundaries here for consistency. Prefer partial updates and label return annotations over full-state mutation and an incorrect router-state annotation.

## Guided practice: check predictions before execution

Follow the student's five steps in order. First elicit `"subtraction"` and `"subtract"` as different answers to different questions. Next ask learners to identify the source, callable, and map in the conditional-edge call. Require an explanation rather than accepting a copied expression.

For `2 - 9`, expect result `-7` and updates from `router`, then `subtract`. For `2 + 9`, expect `11` and the `add` branch. For `*`, expect a `ValueError`, not an automatic subtraction fallback. Keep local interactive runs inside `graph_tracing("none")` if ambient tracing flags might be present; the supplied CLI and tests disable tracing explicitly.

If a learner adds ordinary edges from the router to both branches, stop and ask what ordinary outgoing edges mean. Both destinations can execute; they do not describe alternatives [504]. Remove the ordinary outgoing edges rather than masking the problem with a reducer. Compilation checks topology, not the intended answer.

## Independent exercise: reference solution walkthrough

Learners edit only `exercises/starters/l05.py`, completing `route_first`, `route_second`, and `build_graph`. Arithmetic, validation, and checks are supplied so the task focuses on routing. The starter is independent of the solution. Its untouched CLI returns `STARTER_NOT_COMPLETED` without claiming a pass.

The first routing function reads only `operation1`; the second reads only `operation2`. Each returns `"addition"` for `+` and `"subtraction"` for `-`, rejecting anything else. The path maps bind those common labels to different destination nodes in each section. Registering six work nodes is not enough: START must reach `router1`; either first arithmetic branch must reach `router2`; and either second arithmetic branch must reach END. Neither router also receives an ordinary outgoing edge.

The validation node checks all four operands and both operations before either calculation begins. It initializes `visited` with `router1`. Arithmetic nodes return a new list containing their name and only their own result key. The second gate appends `router2`. There is no list reducer: each sequential node deliberately constructs the complete next list. Returning only `result2` and the new `visited` value preserves `result1` automatically.

Run the separate reference solution when reviewing, not as the learner's implementation:

```bash
python -m exercises.solutions.l05 --backend none
python -m pytest tests/lessons/test_l05.py -q
```

The reference `run_demo` asserts all four operation combinations, the exact visited paths, two independence mutations, preserved inputs, and invalid operations in either field. Focused tests additionally inspect actual update-stream node names, negative/zero operands, missing and invalid inputs, repeated-run isolation, and non-mutating node updates. Tests block networking and credential loading. They test the reference modules; learners must separately run their completed starter's checks and show their own observed state.

The complete independent reference source is inserted here:

<!-- SOLUTION_CODE -->

## Review: full knowledge-check answers

### 1. Routing label, mapped destination, and update

For `operation="+"`, `choose_route` returns the string `"addition"`. The path map selects the registered node `"add"`. With inputs `10` and `5`, that node returns `{"result": 15, "selected_node": "add"}`. Credit requires all three parts. The string selects control flow; the dictionary changes state. Treating them as interchangeable causes routing or node-return errors.

### 2. Ordinary edges versus alternatives

Ordinary edges from `router` to both arithmetic nodes schedule both destinations, rather than selecting exactly one. A conditional edge calls the routing function and maps its selected label to one destination in this lesson. Observe actual executed node keys with `graph.stream(..., stream_mode="updates")`; `selected_node` is also useful local evidence, but inspecting streamed node keys confirms which work ran. Do not accept “the diagram has two arrows” as execution evidence.

### 3. Two results and independence

The required input produces `result1=5`, `result2=9`, and `visited=["router1", "subtract1", "router2", "add2"]`. If only `number1` becomes `100`, `result1` becomes `95`, while `result2` remains `9`. The second section reads `7` and `2`, not `result1`. A learner who answers `97` has accidentally made a chained calculator. For fixed original operands, `++`, `+-`, `-+`, and `--` produce `(15, 9)`, `(15, 5)`, `(5, 9)`, and `(5, 5)`.

### Marking and recovery

Award ten points: two for correct independent routing functions; two for correct label-to-destination maps; two for all boundary and inter-section edges; two for separate results and demonstrated operand independence; one for retaining fail-fast validation; and one for exact path evidence plus successful starter checks. Require the independence and validation criteria for completion, even if the numerical score is otherwise high. The stretch is optional.

For mismatched labels, compare callable return strings against map keys, then map values against registered names. For a lost first result, inspect updates for accidental reuse of the same result key. For both branches firing, remove mixed ordinary/conditional routing at that source. For repeated path entries, check for in-place list mutation or unintended loops. For a bad operation silently succeeding, replace a broad `else` fallback with explicit validation. Restart from the supplied starter if the graph has drifted beyond recognition; keep one known passing example while repairing one connection at a time.

## References

Official sources searched and fetched on 3 November 2026. The repeated value near the exercise represents the pair `7` and `2`; do not introduce a fifth operand.

[504]: https://docs.langchain.com/oss/python/langgraph/graph-api "LangGraph Graph API: state updates and routing mechanisms"
[505]: https://reference.langchain.com/python/langgraph/graph/state/StateGraph/add_conditional_edges "Conditional-edge callable and path-map reference"
[506]: https://reference.langchain.com/python/langgraph/graph/state/StateGraph/set_entry_point "Documented entry-point helper equivalence"
