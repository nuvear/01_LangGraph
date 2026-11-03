# L05 — Conditional routes and two independent calculations

## Explain: choose the next node

In L03, one node used a Python `if` to decide which arithmetic expression to evaluate. The graph still had one processing node. Here the decision changes **which graph node executes next**. Addition and subtraction have separate nodes, and a conditional edge selects exactly one. This distinction matters later when branches perform different work, but no language model is needed to learn it.

Allow 115 minutes, including practice and review. You should already understand L04's sequential edges, dictionary access, Python functions, and partial state updates. By the end, you should be able to return a routing label, map that label to a registered node, explain the executed branch, and connect two conditional sections without mixing their inputs.

<!-- CONCEPT_FIGURE -->

### State updates and route labels do different jobs

A **state** is the dictionary of values available to the graph. Our demonstration requires `number1`, `number2`, and `operation`. An arithmetic node reads those inputs and returns an update such as `{"result": 15, "selected_node": "add"}`. LangGraph merges that update into state. Keys the node does not update remain available. The default behavior replaces an updated key; it does not automatically append to lists or add numbers [501].

A **routing callable** reads the current state and returns a label such as `"addition"`. It does not call the arithmetic function, and its return value is not a state update. The **path map** translates that label to a registered node name: `{"addition": "add", "subtraction": "subtract"}`. The label and node name may differ. Both are strings here, but they serve different purposes [502].

The demonstration's registered `router` node runs `validate_inputs`. It returns `{}` because validation changes no state fields. After that node completes, LangGraph calls `choose_route` through the conditional edge. The node and routing callable are therefore two distinct functions, even though people sometimes loosely call both a “router.” A routing callable is not registered as a work node in this example.

## Illustrate: one branch, then another section

For the single-pair demonstration, the route is START → router → add **or** subtract → END. START and END mark the graph boundaries; they do not calculate anything. The router has conditional outgoing edges, not ordinary edges to both arithmetic nodes. Two ordinary outgoing edges would schedule both destinations rather than implement an either/or decision [501].

The diagram below shows the exercise's extension. Follow one line out of `router1`, then one line out of `router2`. Each run visits four work nodes. The lines converge at the second router, but only one first arithmetic branch is selected, so this is not a parallel join requiring both branches to run.

<!-- ORIGINAL_DIAGRAM -->

The sections execute sequentially, yet their arithmetic is independent. `result1` uses only `number1` and `number2`. `result2` uses only `number3` and `number4`. Passing the accumulated state forward preserves the first answer; it does not make that answer an operand for section two. This is the central exercise constraint.

## Demonstrate: run and inspect the baseline

Use the Python 3.12 environment prepared in P00. Commands below assume it is activated and your terminal is at the repository root. No API key, model, or tracing backend is required.

```bash
python -m course_lessons.l05 --backend none
```

The complete tested demonstration is inserted here:

<!-- EXAMPLE_CODE -->

Read it in this order: schema, validation node, routing callable, arithmetic nodes, graph construction, then `run_demo`. `NotRequired[int]` means callers need not supply the result before the graph computes it. It does not ask LangGraph to create every missing key with `None`. Likewise, `TypedDict` describes expected dictionary shapes for developers and type checkers; our validation code performs the actual runtime checks.

The CLI prints a JSON summary only after assertions succeed. Expect four checked examples: `10 - 5` gives `5`; `7 + 2` gives `9`; `0 - 7` gives `-7`; and `-3 + 0` gives `-3`. Each record identifies the selected arithmetic node. The summary also records rejection of `*` and zero model calls. These are deterministic acceptance properties, not a screenshot or a claim that a remote service was contacted.

Do not add `--live`: it is unnecessary. Keep `--backend none` for this lesson. Other tracing choices belong to later supplementary labs and can send state outside your computer.

<!-- EXECUTION_FIGURES -->

## Guided practice: predict, observe, explain

1. Before running anything again, predict the label returned by `choose_route` for `operation="-"`. Then find the matching destination in the path map. The label is `"subtraction"`; the registered destination is `"subtract"`.
2. Find `add_conditional_edges("router", choose_route, ...)`. Its first argument identifies the node that has just completed. Its second argument is the routing function itself, without parentheses. Its third argument connects possible return labels to destinations.
3. In a Python session from the repository root, import `build_graph` from `course_lessons.l05`, `execution_config` from `course_support.runtime`, and `graph_tracing` from `course_support.observability`. Inside `with graph_tracing("none"):` invoke the compiled graph with `{"number1": 2, "number2": 9, "operation": "-"}` and `config=execution_config()`. Predict `-7`, then inspect `result` and `selected_node`.
4. Inside the same tracing-disabled context, iterate over `graph.stream(initial, config=execution_config(), stream_mode="updates")`, where `graph` is your compiled graph and `initial` is the input dictionary from step 3. The update keys identify `router` and `subtract`; there should be no `add` update. Streaming here is local graph output, not remote tracing.
5. Change only the operation to `"+"` and repeat. You should now see `add`. Finally try `"*"` inside a `try/except ValueError` block. Explain why explicit rejection is safer than using an `else` that silently treats every unfamiliar token as subtraction.

Do not add an unconditional router-to-add edge while keeping its conditional edge. Both routing mechanisms could then schedule work. A graph that compiles is structurally usable, but compilation alone does not prove that its arithmetic or branch selection is correct [501].

## Independent exercise: two pairwise results

Complete `exercises/starters/l05.py`; detailed recording fields and hints are in the L05 workbook. The starter already supplies the state, validation, arithmetic nodes, and local acceptance checks. Your three TODO functions are `route_first`, `route_second`, and `build_graph`. Do not import the solution.

Accept four integer operands and the exact operation strings `+` or `-`. Route `operation1` between `add1` and `subtract1`. Connect either selected first node to `router2`, then route `operation2` between `add2` and `subtract2`. Finish either second node at END. Retain both answers and the four-node `visited` list.

The required example is `number1=10`, `number2=5`, `operation1="-"`, `number3=7`, `number4=2`, `operation2="+"`. It must produce `result1=5`, `result2=9`, and `visited=["router1", "subtract1", "router2", "add2"]`. For these operands, operation combinations `++`, `+-`, `-+`, and `--` must yield result pairs `(15, 9)`, `(15, 5)`, `(5, 9)`, and `(5, 5)` respectively.

Demonstrate independence by changing only `number1` to `100`: section two still returns `9`. Changing only `number3` to `-7` leaves section one at `5` and changes section two to `-5`. Include zero and negative operands. Reject an unsupported operation in either field before arithmetic begins. Preserve the starter's validation rather than converting strings or accepting booleans as integers.

```bash
python -m exercises.starters.l05
python -m pytest tests/lessons/test_l05.py -q
```

An untouched starter exits normally with `STARTER_NOT_COMPLETED`. This is a reminder, not a pass. After you implement all three TODOs, its own checks must report `COMPLETED`. The pytest command tests the supplied demonstration and reference solution, not your unfinished starter; passing those tests alone does not earn exercise credit.

## Review: knowledge checks

1. With `operation="+"`, what does the demonstration's routing callable return, what does the path map select, and what dictionary does the selected arithmetic node return for inputs `10` and `5`?
2. Why are ordinary edges from `router` to both `add` and `subtract` not equivalent to one conditional edge? Name one way to observe which node actually ran.
3. For the required two-section example, what are both answers and the exact `visited` list? If only `number1` changes to `100`, which answer changes, and why?

### Troubleshooting and current-API differences

If you see an unknown route or node error, compare the routing label with the path-map **keys**, then compare map values with registered node names. A state-update dictionary returned from a routing callable is not a valid single route label. A string returned from a normal work node is not a state-update dictionary.

If the second answer depends on the first, inspect the operands in section two and its routing function. If the first answer disappears, use separate result keys and return partial updates. If validation rejects `"7"`, that is intentional: this task accepts integers, not numeric strings.

Historical examples may use names such as `finalNumber` or mutate state in place. Prefer descriptive result keys and fresh update dictionaries. Routing return annotations describe labels with `Literal`, not `AgentState`. The current reference accepts explicit path maps and warns that missing map/type information can make visualizations overly broad [502]. Explicit START/END edges are used here, but `set_entry_point` remains a documented equivalent helper, not a removed API [503]. The second pair is `7` and `2`; the repeated value is not an extra operand.

## References

Official documentation searched and fetched on 3 November 2026.

[501]: https://docs.langchain.com/oss/python/langgraph/graph-api "LangGraph Graph API: state updates, ordinary edges, and conditional edges"
[502]: https://reference.langchain.com/python/langgraph/graph/state/StateGraph/add_conditional_edges "StateGraph add_conditional_edges reference"
[503]: https://reference.langchain.com/python/langgraph/graph/state/StateGraph/set_entry_point "StateGraph set_entry_point remains equivalent to an explicit START edge"
