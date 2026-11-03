# L01 — Python types and graph elements

## Prepare: scope and setup

Follow the student sequence Explain → Illustrate → Demonstrate → Guided practice → Independent exercise → Review. Allocate 100 minutes: 20 for Python types, 15 for graph vocabulary, 10 for demonstration, 15 for guided practice, 30 for independent work, and 10 for assessment. P00 should provide an activated Python 3.12 environment. Work from the project root. No credentials, model initialization or tracing service is needed.

The source window is [00:00:00–00:18:39](https://youtu.be/jGg_1h0qzaM?t=0). Select concepts at [00:01:24](https://youtu.be/jGg_1h0qzaM?t=84) and [00:08:35](https://youtu.be/jGg_1h0qzaM?t=515) within the allocated time. The supplied whole-track record includes sampled visual checks, not continuous viewing. No source-assigned exercise occurs here. Label the movie graph, badge exercise, validation rules and conditional sketch as original added practice.

<!-- VIDEO_FIGURE -->

Inspect `course_lessons/l01.py`, `exercises/starters/l01.py`, and `exercises/solutions/l01.py`. Keep backend `none`. Both complete modules have independent `run_demo` entry points. The starter is deliberately incomplete; a successful process exit initially means only that it honestly reported incomplete work.

## Explain: minutes 0–20, types without false guarantees

Begin with a dictionary containing title and year. Ask which value is text and which is an integer. Introduce `TypedDict` as a named contract, not runtime validation. The [Python typing documentation](https://docs.python.org/3.12/library/typing.html) states that instances remain ordinary dictionaries and expected types are not enforced at runtime.

Separate nullable values, missing keys and default arguments. `str | None` allows None. `NotRequired[str]` permits omission of a dictionary key. `name=None` supplies a function-argument default. Ask whether `Optional[str]` alone allows calling a function with no argument. Expected answer: no, a default determines that.

Show `Union[int, float]` beside `int | float`, then `Any`. Neither converts or validates inputs. With lambda/map, ask learners to predict 1, 4, 9, 16 before execution. Explain that `map` produces an iterator and `list` consumes it, using the [built-in reference](https://docs.python.org/3.12/library/functions.html#map). Avoid a functional-programming detour.

## Illustrate: minutes 20–35, graph vocabulary

Use the original diagram to identify two work nodes and two boundary sentinels. START and END do not trim strings or format cards.

<!-- ORIGINAL_DIAGRAM -->

Write the first node's update separately from accumulated state. Ask whether returning only title deletes year. Expected answer: no, untouched state keys remain. Without a custom reducer, an update replaces the value of the key it supplies. Consult the [Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api). Do not imply that lists automatically append or state automatically survives a restart.

Distinguish builder from compiled runnable. Compilation checks structure; assertions and tests check behavior. Nodes perform work, ordinary edges fix the next node, and conditional edges choose from state. An `if` inside a node is not a graph route. A tool is a capability; a tool node executes tool requests. This lesson has neither a tool dispatcher nor an LLM.

## Demonstrate: minutes 35–45

1. For two minutes, read `MovieState` and both node signatures. Predict that `card` can be absent initially, the title will be trimmed, and the caller's dictionary will remain unchanged.
2. For three minutes, run `python -m course_lessons.l01 --backend none`. Inspect actual JSON fields. Expect the card, square list, fallback greeting, and matching hand-authored message IDs.
3. For two minutes, trace `START → normalize_title → describe_movie → END`. Ask which line preserves year. Precise answer: neither node must return it; update application retains untouched state channels.
4. For three minutes, read `message_examples`. System carries instructions/context; human carries user input; AI carries assistant content or requests; tool carries a result. All objects are hand-authored, and `l01-square-1` links request and result. No model generated them.

The [message guide](https://docs.langchain.com/oss/python/langchain/messages) supports AI tool-call requests paired with ToolMessage results. The video's “function message” wording is legacy/imprecise here, not a fifth required role. This course imports `langchain_core.messages`; documentation may use `langchain.messages`. No provider migration is needed because L01 makes no provider request.

<!-- EXECUTION_FIGURES -->

## Guided practice: minutes 45–60

Pairs predict `square(2.5)`, `greet(None)`, and `greet("")`: 6.25, `Hello, visitor!`, and `Hello, !`. Blank is deliberately not normalized in that helper. The badge task applies a different explicit rule; do not “fix” the demo to match it.

Require both the partial title update and the full next state. Explain the strict year check: bool subclasses int, so `isinstance(True, int)` would accept True. Rejecting it is an application rule, not a TypedDict feature. Ask why no model is involved. Accept “ordinary deterministic Python transforms the data, LangGraph schedules the functions, and message objects are constructed locally.”

## Independent exercise: minutes 60–90

Learners implement the workbook's exact badge task in three starter functions. Required topology is linear, including zero sessions. The independent reference follows; the movie demo is not its substitute.

<!-- SOLUTION_CODE -->

`normalize_name` rejects non-string/non-None values, strips surrounding whitespace, and returns only `name`, falling back to Visitor for None or blank text. Internal spaces remain. `make_badge` rejects non-integers, including booleans, with TypeError, rejects negatives with ValueError, and returns only `badge`. Singular applies exactly at one. `build_graph` registers both functions and compiles explicit boundary and connecting edges.

Walk through padded Ada/2 becoming `Ada: 2 sessions`, None/0 becoming `Visitor: 0 sessions`, and whitespace/1 becoming `Visitor: 1 session`. Final state preserves sessions and original inputs remain unchanged. Negative one raises ValueError; `"2"`, True and a numeric name raise TypeError. Missing required keys are outside the task.

Run `python -m exercises.solutions.l01`, then `python -m pytest tests/lessons/test_l01.py -q -p no:cacheprovider`. The suite checks distributed demo/reference behavior, topology, errors, message IDs, CLI defaults and starter honesty. Learners must run their starter command to check their own edits; the reference tests do not grade edited node bodies.

For the paper-only alternative, accept START to normalization, then `sessions == 0` to END or `sessions > 0` to formatting, then END. Assume valid nonnegative counts. Zero receives no badge in that sketch; therefore it cannot replace the required executable graph. Reject unlabeled routes or START depicted as a formatter.

## Review: minutes 90–100, exact assessment answers

### Check 1

**Question:** How do `name: str | None` and `badge: NotRequired[str]` differ? Does either annotation automatically validate runtime values?

**Answer:** Name is required but may contain a string or None. Badge may be omitted; if present, its annotated value is a string, not None. Neither validates runtime values. Explicit checks enforce the solution's rules. Merely saying both are “optional” is insufficient.

### Check 2

**Question:** The movie input is `{"title": "  Example  ", "year": 2024}`. The first node returns `{"title": "Example"}`. What full state reaches the second node, and what determines which node runs next?

**Answer:** `{"title": "Example", "year": 2024}` reaches `describe_movie`; no card exists yet. The ordinary edge from `normalize_title` fixes that next node. The returned dictionary updates state; it neither drops year nor acts as a routing instruction.

### Check 3

**Question:** What do system, human, AI, and tool messages represent? What must match between an AI tool-call request and a tool result, and does constructing these objects prove a model was called?

**Answer:** System carries instructions/context; human carries user input; AI carries assistant content and possibly tool-call requests; tool carries a tool execution result. The request ID must match the result's `tool_call_id`. No: all four objects can be manually constructed. A class name is not evidence of remote generation.

## Marking and recovery

Award ten points: two for normalization including invalid names, two for badge text/count validation, two for topology and partial updates, one for unchanged inputs/counts, one for acceptance cases and starter status, one for the labeled sketch, and one for explaining typing versus runtime checks. All completion criteria remain required; points cannot compensate for skipping the executable zero badge.

For import failures, recover the P00 environment and module invocation rather than editing paths or installing packages. If year disappears in an explanation, separate update from state on paper. If the starter reports TODO 3, finish its builder before debugging nodes. For assertion failures, compare strip behavior, grammar and bool handling. Restore linear edges if learners implemented the paper route. Defer persistence, tools, tracing and model behavior to later lessons.

## References and publication boundary

Official [typing](https://docs.python.org/3.12/library/typing.html), [map](https://docs.python.org/3.12/library/functions.html#map), [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [construction](https://docs.langchain.com/oss/python/langgraph/use-graph-api), and [message](https://docs.langchain.com/oss/python/langchain/messages) pages were searched and retrieved on 3 November 2026. Parent handles figures, rendering and handbook integration. No Windows execution, model request or dashboard inspection is claimed.
