# L01 — Python types and graph elements

## Task: make typed workshop badges

This task applies L01's type and graph vocabulary in a standalone workshop-badge exercise. Allow 30 minutes after guided practice. Use P00's Python 3.12 environment from the project root. No model or credentials are needed.

Starter: `exercises/starters/l01.py`. Instructor reference: `exercises/solutions/l01.py`; try the task first. The demonstration `course_lessons/l01.py` uses movies, not badges, so reproducing its output does not complete this exercise.

The supplied `BadgeState` requires `name: str | None` and `sessions: int`; `badge: NotRequired[str]` may be absent initially. The name key must exist, but may contain None. Type hints do not enforce runtime rules; see the [Python typing reference](https://docs.python.org/3.12/library/typing.html).

## Establish your baseline

1. Run `python -m course_lessons.l01 --backend none`. Find the trimmed movie title, squares and two work-node names.
2. Run `python -m exercises.starters.l01`. Initially it exits successfully but prints `STARTER_NOT_COMPLETED`. That is an incomplete status, not a pass.
3. Locate exactly three TODO functions. Complete them without importing either the demonstration or reference solution; retain the checking harness.

## Implement the exact behavior

### Step 1: normalize the name

Implement `normalize_name(state)`. Return a new dictionary containing only `name`. None, an empty string and whitespace-only text become `Visitor`. Otherwise remove surrounding whitespace, preserving spelling, case and internal spaces. Non-string/non-None values must raise TypeError. Do not mutate the input dictionary.

### Step 2: create a badge update

Implement `make_badge(state)`. Its name has already been normalized. Require an integer sessions count, excluding booleans. Other types, including `"2"`, 2.0, None and True, must raise TypeError; negative integers must raise ValueError. Zero is valid.

Return only `badge`, formatted exactly as `<name>: <sessions> session` for one, or `<name>: <sessions> sessions` otherwise. Do not change or return the count; do not mutate state. These are application rules, not annotation behavior.

### Step 3: assemble the runnable

Implement `build_graph()` using `StateGraph(BadgeState)`. Register functions under the exact node names `normalize_name` and `make_badge`. Connect `START → normalize_name → make_badge → END`, then return the compiled graph. Both nodes execute even for zero sessions. Do not add conditional edges. The [graph guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api) explains explicit edges and partial updates.

### Step 4: check every required case

Run the starter. Its checks expect:

- `{"name": "  Ada  ", "sessions": 2}` becomes `{"name": "Ada", "sessions": 2, "badge": "Ada: 2 sessions"}`.
- `{"name": None, "sessions": 0}` becomes `{"name": "Visitor", "sessions": 0, "badge": "Visitor: 0 sessions"}`.
- `{"name": "   ", "sessions": 1}` becomes `{"name": "Visitor", "sessions": 1, "badge": "Visitor: 1 session"}`.

Each caller input must remain unchanged. Also check name 42 raises TypeError, sessions -1 raises ValueError, and sessions `"2"` or True raises TypeError. Missing required keys are outside this task. A completed starter reports `STARTER_CHECKS_PASSED`; a traceback means a failed check.

## Draw a different route on paper

Sketch a two-work-node alternative: START to normalization; then `sessions == 0` to END or `sessions > 0` to badge formatting, then END. Assume a valid nonnegative count. Label both routes and identify the absent zero-case output: no badge has been generated.

Keep the sketch separate. It previews L05 and intentionally differs from the runnable, where zero still receives a badge. START/END are boundaries, not work functions. The student chapter's concept diagram illustrates the movie demonstration.

## Three progressive hints

1. Distinguish None before calling `.strip()`. A cleaned empty string needs the same fallback as None; a required nullable key is not a missing key.
2. Return only each node's changed field; LangGraph retains other state keys. Remember bool is a subclass of int when validating sessions.
3. If nodes never run, inspect construction first. Register both functions, add boundary and connecting edges, and return `builder.compile()`, not the builder. Compare all three final states before extensions.

## Record observed results

Replace these prompts with evidence from your own run. Do not invent screenshots.

- Movie card and two node names: **Record here.**
- Starter status before and after editing: **Record here.**
- Actual three badge strings: **Record here.**
- Error types for invalid name, negative count, text count and bool count: **Record here.**
- Evidence of unchanged input and preserved sessions: **Record here.**
- What the sketch's zero route omits, and why executable behavior differs: **Record here.**

## Completion and optional stretch

Finish when all TODOs are implemented independently, exact cases and invalid-type checks pass, outputs are partial updates, caller inputs remain unchanged, topology is linear, and the separate sketch has labeled routes. Explain why annotations alone did not validate values.

Compare afterward with `python -m exercises.solutions.l01`. Run `python -m pytest tests/lessons/test_l01.py -q -p no:cacheprovider` to validate distributed demo/reference artifacts. That file does not grade your edited starter; use its own command. Keep backend `none`; no `--live` is needed.

For a stretch, check `"  Mei Lin  "/1` and an empty-string name/3 without changing required rules. Predict both badges first. Explain why constructing an AIMessage does not prove an API call. Consult the [message guide](https://docs.langchain.com/oss/python/langchain/messages), typing reference, and graph guide when reviewing the relevant concepts.
