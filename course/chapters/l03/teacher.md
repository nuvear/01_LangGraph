# L03 — Multiple inputs and one-node arithmetic

## Explain: teaching intent and preparation

Teach this as deterministic graph programming, not as an AI agent demonstration. Learners bring Python lists, dictionaries, functions, and L02's compile/invoke distinction. The desired transfer is that a node can consume several differently typed state fields and produce a small update without changing graph topology. Keep model access and observability setup out of the lesson.

The core activity uses one node to add or multiply a list. Teach strict validation, separate numeric output, precise punctuation, and empty-list rules as the explicit assessment contract. Current partial-update guidance comes from the [official Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api).

Before class, activate the prepared Python 3.12 environment at the repository root. Have these commands ready:

```bash
python -m course_lessons.l03 --backend none
python -m exercises.starters.l03
python -m exercises.solutions.l03 --backend none
python -m pytest tests/lessons/test_l03.py -q
```

Do not use `--live`. The demo and solution use the real installed LangGraph engine but perform no model requests. The focused tests disable ambient tracing, reject attempted network/configuration access, and do not validate services. Their passing does not establish a Windows run or a dashboard result. Parent-supplied figures are inserted only after actual capture.

## Illustrate: 0–12 minutes

Spend the first five minutes eliciting the inputs and outputs. Ask, “Which field is a list? Which field do we calculate?” Expected responses are `values` and `total`/`result`, respectively. Write `NotRequired` beside derived fields. Explain that it permits absence, whereas `str | None` permits a null value in a present key. The [Python typing reference](https://docs.python.org/3.12/library/typing.html#typing.TypedDict) states that TypedDict does not enforce values at runtime.

At minutes 5–9, compare the baseline schema with the exercise schema. Emphasize that the same node pattern supports several typed inputs and a small partial update. Use the exact Python code supplied in the lesson rather than inferring syntax from a diagram.

<!-- CONCEPT_FIGURE -->

At minutes 9–12, use the concept diagram to ask learners how many work-performing nodes execute. The answer is one. START and END are boundary markers, not extra computation nodes. In the baseline the node is `processor`; in the exercise it is `calculator`. The `if` changes arithmetic inside that node, not the graph's route.

<!-- ORIGINAL_DIAGRAM -->

## Demonstrate: 12–27 minutes

At minutes 12–16, trace `build_graph` line by line: schema, registration, two edges, compile. Point to the distinction between builder and executable documented in the [StateGraph reference](https://reference.langchain.com/python/langgraph/graph/state/StateGraph). Ask which object supports `invoke`. Accept “the compiled graph,” not “the TypedDict” or “the node name.”

At minutes 16–21, predict Steve's result before running the demo command. The exact update is `{"total": 10, "result": "Hi there Steve! Your sum = 10."}`. Compare that with the final dictionary, which also retains `values` and `name`. Explain that updates apply per key: omitting an input from an update does not erase it; writing a new result replaces any old result.

At minutes 21–24, inspect `selected_result` and the input-preservation assertion. The formatted sentence is a projection of the final state, not a second node. Show why assignment to `state["result"]` is unnecessary. Avoid suggesting that all nested dictionaries are automatically immutable; this node simply never mutates its inputs.

At minutes 24–27, show the empty and signed-list checks. If a learner supplies a boolean, explain that Python's integer subclass relationship is why the strict check uses `type(item) is int`. Keep this explanation brief and tied to the exact acceptance policy.

<!-- EXECUTION_FIGURES -->

## Guided practice: 27–42 minutes

Follow the student's four steps in order. First ask partners to identify required and derived fields. Then have them compare the input's two keys, the update's two keys, and the final state's four keys. A common false prediction is that the update replaces the entire dictionary. Recover by looking at one unchanged field, such as `name`, before discussing reducers.

Next, let learners invoke the compiled baseline with Mei and `[-3, 0, 5]`, using `execution_config()` and an offline tracing configuration. Expect total 2. The empty list produces 0. Finally, try `[True]` and `[2.5]`; both should raise `ValueError`. Ask learners to point to the validation that causes rejection, rather than crediting the type annotation.

Use the CLI for a learner whose interactive shell has uncertain tracing settings. Missing imports usually indicate that they started Python outside the repository root or have not activated the prepared environment. Do not fix this by changing shared runtime files during class.

## Independent exercise and solution: 42–67 minutes

Give 18 minutes for the three starter TODOs and seven minutes for review. The exact task requires one `calculator` node, strict `values`/`name`/`operation` validation, outputs named `answer` and `result`, and the message `Hi {name}, your answer is {answer}.` Missing or invalid required inputs raise `ValueError`. Preserve the supplied name and values, including valid whitespace around a nonblank name.

The starter intentionally prints `STARTER_NOT_COMPLETED` and exits successfully before implementation. Distinguish process completion from task completion. Its completed checks test both operations, signed and zero values, singleton input, empty lists, malformed values, missing inputs, and unsupported operations. The repository pytest file tests the delivered demo/reference; it does not silently grade the learner's edited starter. Use the starter's own checker and inspect their functions.

Walk through the independent solution in three parts. `validate_inputs` uses `.get` so absent inputs become a controlled `ValueError`, not an unexplained `KeyError`. It checks the actual list elements, a nonblank name, and exact `+`/`*` tokens. `process_values` validates first, then uses an `if` to select `sum` or `prod`. Because validation has already rejected other tokens, the `else` is safely multiplication. It returns only the two outputs. `build_graph` registers that function once and compiles the fixed topology.

Empty addition is 0. Empty multiplication is 1 because [math.prod](https://docs.python.org/3.12/library/math.html#math.prod) starts at 1. The Jack Sparrow multiplication case yields 24; addition yields 10. Signed tests catch a zero-initialized product or a calculation that accidentally ignores negative inputs. Unsupported `/` must raise; it must never fall into multiplication accidentally.

The complete independent reference source follows. It does not import or delegate to the baseline demonstration.

<!-- SOLUTION_CODE -->

## Review: 67–75 minutes

### Exact knowledge-check answers

1. The update is `{"total": 10, "result": "Hi there Steve! Your sum = 10."}`. The final state additionally retains `values: [1, 2, 3, 4]` and `name: "Steve"`. LangGraph applies updates per field, so the node need only return computed fields. Award reasoning credit only if the learner distinguishes an update from the whole final state.
2. `NotRequired[str]` allows `result` to be absent; a required `str | None` key must be present according to the schema but may contain `None`. Neither validates `values` at runtime. Explicit checks reject booleans and floats. Do not accept “TypedDict converts the inputs” or “missing keys are automatically None.”
3. The `if` selects Python arithmetic inside one node; it is not graph-level routing. Empty addition must be 0; empty multiplication must be 1. `/` must raise `ValueError`. Graph-level conditional edges are deferred to L05.

### Marking and recovery

Use ten marks: two for strict validation including missing fields and unsupported operations; two for correct addition and multiplication; two for zero, negative, singleton, and empty-list behavior; two for the one-node compiled topology; and two for partial outputs, exact formatting, and input preservation. Require all safety/validity criteria to be corrected even if the arithmetic subtotal is high. A product that works only for the slide's positive list is not complete.

For recovery, isolate the earliest failing layer. Test `validate_inputs` directly, then `process_values`, then compilation and invocation. An integer returned by the node must become an update dictionary. A zero product accumulator must become 1 or use `prod`. An accepted `/` requires validation before the conditional. An extra arithmetic node should be removed, not justified as a preview of L05. Re-run only L03 tests after each targeted repair.

## References

- [LangGraph Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api) and [StateGraph reference](https://reference.langchain.com/python/langgraph/graph/state/StateGraph).
- [Python 3.12 TypedDict](https://docs.python.org/3.12/library/typing.html#typing.TypedDict) and [math.prod](https://docs.python.org/3.12/library/math.html#math.prod).
