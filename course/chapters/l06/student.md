# L06 — Bounded loops and automatic higher/lower game

## Explain: why a graph can revisit a node

A graph does not have to travel from left to right once. A **back-edge** sends execution to a node that has already run. The next visit receives the latest state, so it can make progress instead of repeating the same calculation forever. In this lesson, a counter records progress and a conditional route decides whether another visit is allowed. No language model is involved: ordinary Python makes every decision.

After this lesson, you should be able to sketch a bounded loop, reset its working state, return partial updates without mutating an input list, and distinguish normal termination from a recursion-limit error. You should also be able to build an automatic higher/lower game with two valid exit reasons. Prerequisites are L05's route labels and path maps, plus integer arithmetic, lists, dictionaries, and `if` statements. Allow approximately 110 minutes, including practice.

**Video-backed material:** the source window is [01:14:14–01:31:01](https://youtu.be/jGg_1h0qzaM?t=4454). The planning discussion and loop diagram precede the implementation; the [automatic game exercise begins around 01:29:19](https://youtu.be/jGg_1h0qzaM?t=5359). The supplied whole-track review confirms that the exercise guesses automatically, rather than asking a human for guesses. The baseline generates five integers after a greeting.

**Added/current-API adaptation:** our runnable version uses repeatable local random draws, separate name and greeting fields, explicit `START` edges, and returned state updates. The exercise uses integer midpoints, validates configuration, and demonstrates exhaustion with a deliberately smaller budget. These choices make the source concepts testable; they do not reproduce the source notebook's exact random sequence.

## Illustrate: progress and termination

The demonstration follows `START → greeting → generate`. The greeting resets `counter` to zero and `numbers` to an empty list. Each generation returns a new list containing the previous numbers plus one new integer from 0 through 10, and increases the counter once. Only then does the route read the updated state. If the counter is below five, it chooses `again`; otherwise, it chooses `done`, which the path map connects to `END`.

<!-- ORIGINAL_DIAGRAM -->

The original diagram shows both the demonstration and the exercise. Read the back-edge as permission to perform one more unit of work, not as a Python function calling itself. A **termination condition** is the rule that ends this repetition. Here it is the updated counter reaching five. Since every visit increases the counter and the reset begins at zero, the intended path cannot continue indefinitely.

<!-- VIDEO_FIGURE -->

The source loop illustration is a separate attributed video figure. It is not evidence that the adapted program has run. The original demonstration deliberately uses a graph where a Python `for` loop would be simpler. Its purpose is to make state transitions visible before later lessons use similar loops for model/tool workflows.

## Demonstrate: inspect the bounded baseline

From the repository root, in the prepared Python 3.12 environment, run:

```bash
python -m course_lessons.l06 --backend none
```

`none` explicitly disables service tracing. No `--live` flag or API key is needed. The shared command wrapper prints a JSON summary after the module's assertions complete. Expect five numbers, a counter of five, a greeting containing Student, and a repeatability check. An exact random list is not a learning requirement; its length, range, reset behavior, and reproducibility are.

The full tested demonstration belongs here:

<!-- EXAMPLE_CODE -->

`build_graph()` separates construction from execution. `compile()` produces the object with `invoke()` and `stream()` methods; it does not prove that the loop's numerical rule is correct. The current Graph API permits nodes to return only changed keys. Keys without a custom reducer use replacement semantics, so `{"numbers": [new_number]}` would discard earlier draws. We instead return a newly constructed list containing the old values and the new value. See the [official state and reducer explanation](https://docs.langchain.com/oss/python/langgraph/graph-api).

The generation node uses a local `Random(seed + counter)` instance on each visit. This is a specific repeatability policy, not a claim that random numbers are inherently deterministic. It avoids changing Python's global random generator and avoids a mutable generator shared between graph invocations. The greeting resets both the list and the counter, so stale caller values do not become extra work or old output. The incoming name is preserved rather than replaced with the greeting.

<!-- EXECUTION_FIGURES -->

## Guided practice: follow the updates

1. Read `reset_loop`, `loop_route`, and the path map before changing code. Predict the sequence of counter values after generation. Explain why an initial counter of `-12` does not cause seventeen generations: that value is replaced before the first generation runs.
2. In a Python session launched from the project root, import `build_graph` from `course_lessons.l06` and `execution_config` from `course_support.runtime`. Import `tracing_context` from `langsmith` and use `with tracing_context(enabled=False):` around the experiment. Stream `{"name": "Ada", "numbers": [999], "counter": -12}` with `config=execution_config(), stream_mode="updates"`. Print each update inside the context. Expect one greeting update followed by five generation updates; the old `999` must disappear.
3. Invoke the same compiled graph again inside that tracing-disabled context. Use the same name but a different initial counter. Compare the generated lists. They should agree because the seed policy and reset are unchanged. Check that the original input dictionary and its list are unchanged too.
4. Locate the two different return types. A node returns a dictionary such as `{"counter": 1}`. A route returns a label such as `"again"`. The path map translates that label to a destination. Returning a dictionary from this router would confuse state changes with control flow.

Do not add an ordinary `generate → generate` edge as well as conditional routing. The unconditional edge would still schedule work regardless of the route's exit choice. The demonstration needs exactly one kind of outgoing decision at that point. The [official loop guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api) uses conditional termination for this reason.

## Independent task: build the automatic game

Use `exercises/starters/l06.py`, not a copy of the reference solution. It provides graph wiring and three functions to finish: `reset_game`, `guess_node`, and `feedback_node`. Run it with:

```bash
python -m exercises.starters.l06
```

Until implemented, the starter exits successfully with `STARTER_NOT_COMPLETED`; this is an honest incomplete status, not a passing exercise. Work through the exact requirements in the L06 workbook.

The game starts with player Student, bounds 1–20, no guesses, and zero attempts. The target is a fixed synthetic integer in that range. The guesser must use only the bounds to choose `(lower + upper) // 2`; the feedback node compares that guess with the target. A smaller guess means `higher` and raises the lower bound to `guess + 1`. A larger guess means `lower` and lowers the upper bound to `guess - 1`. Excluding the failed guess prevents repeated guesses. Return updated lists rather than calling `append` on state.

A correct guess sets hint `correct` and status `won`. A miss sets status `lost` when the allowed attempt budget is reached; otherwise status remains `playing`. Success must take precedence on the final permitted attempt. The default budget is seven, but accept integer budgets from one through seven so that exhaustion can be tested. Reject invalid targets, invalid budgets, booleans in either integer field, and blank or non-string player names with `ValueError` before guessing. Reset stale bounds, lists, hints, attempts, and status while preserving configuration.

For target 17, predict the midpoint sequence `10, 15, 18, 16, 17`. For target 20 with budget two, predict guesses `10, 15`, hint `higher`, and status `lost`. These are algorithm-derived expectations, not a claim about the video's output. Also check target 15 with budget two: it must win on the final attempt. Verify every target from 1 to 20 using the default budget. The game is automatic: do not add `input()` or an LLM.

## Knowledge checks

1. The baseline receives counter `-12` and numbers `[999]`. Why must the greeting reset both fields, and what should the final counter and list length be?
2. In the automatic game, a guess is 10 and the target is higher. What exact bound update prevents repetition, and why is assigning `lower = 10` insufficient?
3. A game uses budget two and target 15. What should happen after guesses 10 and 15? Explain why the budget check must not override success, and why a recursion-limit exception is not a normal `lost` result.

## Troubleshooting and current API differences

If history contains only one guess, inspect whether each node replaces the list with a singleton. If attempts stop increasing, ensure the increment is in `guess_node`, not in a route or reset node visited on every cycle. If a game never terminates, inspect both the state update and the route label mapping; do not merely raise the recursion limit.

The shared `execution_config()` sets `recursion_limit=40`. This is an execution safety net measured in graph super-steps, not a guess budget. Our game has separate guess and feedback nodes, so one guess is not one super-step. A `GraphRecursionError` indicates an execution limit was reached; it is not evidence that the player used exactly seven guesses. Current documentation describes configurable recursion limits; this lesson deliberately does not depend on a version-specific default.

Compared with historical whole-dictionary mutation and entry-point helpers, this implementation uses partial updates and `START`/`END` with an explicit path map. No Anthropic adaptation is needed for this non-model section. From the repository root, run the focused reference tests with `python -m pytest tests/lessons/test_l06.py -q`; those test the delivered demo and solution, while the starter's self-check tests your own implementation. Rendered figures, Windows checks, and service traces are separate parent-managed evidence.

## References

- [LangGraph Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api): state, default replacement, nodes, edges, and compilation; verified by search and fetch on 3 November 2026.
- [Use the graph API](https://docs.langchain.com/oss/python/langgraph/use-graph-api): loop construction, conditional termination, recursion configuration, and errors; verified on 3 November 2026.
- [Source section](https://youtu.be/jGg_1h0qzaM?t=4454) and [exercise prompt](https://youtu.be/jGg_1h0qzaM?t=5359): attribution follows the supplied caption review and whole-track sampled visual review, not a new viewing claim.
