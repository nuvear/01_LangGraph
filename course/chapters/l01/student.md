# L01 — Python types and graph elements

## Explain: what this lesson lets you do

You will read the typed Python used throughout the course, identify the parts of a LangGraph workflow, and follow a value through two ordinary functions. By the end, you should explain why a graph does not automatically imply artificial intelligence, why a type annotation does not validate incoming data, and why a returned update can contain fewer keys than the accumulated state.

Prerequisites are P00 and basic Python variables, functions, lists, dictionaries, and `if` statements. Allow 100 minutes, including about 45 minutes of practice. Work from the project root with the prepared Python 3.12 environment active. This lesson needs no model, API key, internet connection during execution, or tracing backend.

**Video-backed concepts:** [00:00:00–00:18:39](https://youtu.be/jGg_1h0qzaM?t=0). Type annotations begin at [00:01:24](https://youtu.be/jGg_1h0qzaM?t=84), graph elements at [00:08:35](https://youtu.be/jGg_1h0qzaM?t=515), and message roles at [00:17:45](https://youtu.be/jGg_1h0qzaM?t=1065). The supplied whole-track review confirms the early topic identities through sampled frames. This window contains no original coding assignment. The movie-card demonstration, badge exercise, validation rules, and graph sketch below are **added practice**, not the presenter's homework.

<!-- VIDEO_FIGURE -->

## Explain: type hints describe a contract

A dictionary maps keys to values. `{"title": "The Clockwork Garden", "year": 2025}` is a dictionary containing both a string and an integer. A `TypedDict` describes which keys belong together and what values a static type checker should expect:

```python
from typing import NotRequired, TypedDict

class MovieState(TypedDict):
    title: str
    year: int
    card: NotRequired[str]
```

The class is a schema, meaning a description of the data's shape. Its instances are ordinary dictionaries at runtime. `title` and `year` are required in the typed contract; `card` may be absent because the graph creates it later. Python does not automatically reject a string placed in `year`. Code that receives untrusted values still needs explicit checks. A type checker can flag mistakes before execution, but running Python alone is not running a type checker. See the [Python typing reference](https://docs.python.org/3.12/library/typing.html).

`Union[int, float]` means either numeric type; Python 3.12 also supports the shorter `int | float`. It does not convert a string such as `"3"` into a number. `Optional[str]` means `str | None`, not “the caller can always leave this argument out.” An argument becomes omittable when its function definition supplies a default, such as `name=None`. Likewise, a dictionary key annotated `name: str | None` is still required unless marked `NotRequired`. A missing key and a present key containing `None` are different situations.

`Any` relaxes static checking for a value whose type is not constrained. It is not a validator and does not turn data into a universal safe format. Prefer specific types when you know them. The demonstration's `echo` function accepts `Any` simply to show that the same object can pass through unchanged.

A lambda is a small anonymous function written as one expression. `map(lambda n: n * n, [1, 2, 3, 4])` creates an iterator that will yield squared values. `list(...)` consumes that iterator to produce `[1, 4, 9, 16]`. Consuming the same iterator again yields no items. A list comprehension can express the same calculation more readably; neither form requires LangGraph. The [built-in map documentation](https://docs.python.org/3.12/library/functions.html#map) explains its iterator behavior.

## Illustrate: graph vocabulary without a model

**State** is the current application data. It can carry inputs, intermediate values, and outputs, but is not automatically durable memory across restarts. A **node** is a registered operation, usually a Python function, that reads state and returns updates. In our example, one node trims a movie title and another creates a card. A **graph** specifies how those operations connect.

An ordinary **edge** fixes the next operation. A **conditional edge** calls routing logic to select the next operation based on state. For example, a route might skip formatting when a count is zero. A Python `if` inside a formatting function is not itself a graph-level conditional edge: execution still visits that same node. We only sketch conditional routing here; L05 develops it fully.

`START` and `END` are boundary sentinels, not functions that do useful work. `StateGraph(MovieState)` creates a builder. Adding nodes and edges describes the workflow; `compile()` creates its executable form. The resulting **runnable** supports a standard execution interface such as `invoke`. A runnable is a broader concept than a node: a complete compiled graph is runnable too. Compilation checks structure, not whether your card has correct punctuation or your algorithm produces the intended answer. These concepts follow the [Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api).

Original diagram: the actual movie-card demonstration. Both work nodes run once, in order. The boundaries do not modify state.

<!-- ORIGINAL_DIAGRAM -->

Nodes return partial updates. After `normalize_title` returns only `{"title": "The Clockwork Garden"}`, the graph keeps `year`. When `describe_movie` returns `{"card": "The Clockwork Garden (2025)"}`, the other fields remain. Without a custom reducer, an update replaces the previous value of the key it supplies; it does not erase unrelated keys. Return a new dictionary instead of mutating the incoming one, as recommended in the [current graph guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api).

A **tool** is a capability exposed for use, such as arithmetic or retrieval. A **tool node** is graph structure responsible for executing tool requests. An ordinary node can call a helper function without becoming a model-driven agent or using `ToolNode`. This lesson registers ordinary functions only; tool orchestration arrives in L09.

## Demonstrate: inspect the complete local example

The tested source is `course_lessons/l01.py`. It includes the movie graph, `square`, `greet`, `echo`, lambda/map practice, and explicitly hand-authored message objects.

<!-- EXAMPLE_CODE -->

Run:

```bash
python -m course_lessons.l01 --backend none
```

Expect a JSON summary containing `mode: deterministic_no_model`, a trimmed movie title, the card `The Clockwork Garden (2025)`, squares `[1, 4, 9, 16]`, and checks for preserved input and matching message IDs. These are deterministic acceptance properties, not a claim about a dashboard or generated response. The shared CLI creates a run directory, but this module writes no lesson artifacts there. Do not add `--live`; it is unnecessary. Selecting a tracing backend other than `none` would deliberately enable a separate remote service through shared infrastructure.

### Message objects are not evidence of model calls

`SystemMessage` supplies instructions or context. `HumanMessage` represents user input. `AIMessage` represents an assistant message and can contain tool-call requests. `ToolMessage` carries a tool result, with `tool_call_id` matching the request ID. The demonstration manually constructs all four objects and pairs the ID `l01-square-1`; it does not send them anywhere or run a tool dispatcher. An `AIMessage` constructor is not an API call. Compare the [official message guide](https://docs.langchain.com/oss/python/langchain/messages).

The source video's “function message” wording is legacy or imprecise for this purpose. We teach the current AI-tool-call and tool-result pairing, not a new fifth core role. The guide may show imports from `langchain.messages`; this course uses the installed `langchain_core.messages` classes directly. Provider-specific examples are unnecessary here: Python logic computes values, LangGraph orchestrates functions, and no model behavior is involved.

<!-- EXECUTION_FIGURES -->

## Guided practice: predict, then inspect

1. Read `MovieState` and identify which key can be absent initially. Predict the difference between an omitted `card` and a supplied `card=None` under its annotation.
2. Trace the padded title through `normalize_title`. Write the returned update separately from the full state that `describe_movie` receives. Check that `year` has not disappeared.
3. Run the demonstration and locate its card and role list. Explain why the role `ai` does not prove a model was contacted.
4. Read `square` and `greet`. Predict `square(2.5)`, `greet(None)`, and `greet("")`; the empty string is not `None`, so the last case deliberately produces `Hello, !`.
5. Read the strict year check. Python treats booleans as a subclass of integers; this course explicitly rejects them as year values. That is an application rule, not behavior supplied by `TypedDict`.

## Independent exercise: workshop badges

Complete `exercises/starters/l01.py` without importing the demonstration or solution. Implement its three TODO functions: `normalize_name`, `make_badge`, and `build_graph`. The supplied `BadgeState` requires nullable `name` and integer `sessions`; `badge` may be absent initially.

Normalize `None`, an empty string, or whitespace-only text to `Visitor`; otherwise strip only surrounding whitespace. Reject other name types with `TypeError`. Return only the name update. Validate that sessions is an integer but not a boolean; reject other types with `TypeError` and negative integers with `ValueError`. Return only a badge update using singular `session` for exactly one and plural `sessions` otherwise. Preserve the count and do not mutate inputs.

Compile exactly `START → normalize_name → make_badge → END`. Expected badges are `Ada: 2 sessions` for `"  Ada  "`/2, `Visitor: 0 sessions` for `None`/0, and `Visitor: 1 session` for `"   "`/1. Run `python -m exercises.starters.l01`. Initially it must report `STARTER_NOT_COMPLETED`; after all checks succeed it reports `STARTER_CHECKS_PASSED`.

Also draw a paper-only alternative: after normalization, route zero sessions to END and positive sessions to `make_badge`, then END. Label the branches. Do not implement that alternative: the required executable graph must still create the zero-session badge. The workbook provides observation fields, progressive hints, and completion criteria.

## Review: three knowledge checks

1. How do `name: str | None` and `badge: NotRequired[str]` differ? Does either annotation automatically validate runtime values?
2. The movie input is `{"title": "  Example  ", "year": 2024}`. The first node returns `{"title": "Example"}`. What full state reaches the second node, and what determines which node runs next?
3. What do system, human, AI, and tool messages represent? What must match between an AI tool-call request and a tool result, and does constructing these objects prove a model was called?

## Troubleshooting and next steps

If imports fail, confirm the prepared environment is active and use module commands from the project root, not `python course_lessons/l01.py`. If `KeyError` appears, check required input keys; nullable does not mean missing. If a node returns a string instead of a dictionary, restore its partial-update return. If year or count validation fails, supply an actual integer rather than quoted digits. If the starter still says incomplete, its builder may be unimplemented even when node bodies are finished.

Run `python -m pytest tests/lessons/test_l01.py -q -p no:cacheprovider` to check the distributed demonstration and reference solution offline. These tests do not certify your unfinished starter; its own command checks your edits. Continue to L02 for a slower construction of a minimal graph. Keep your paper conditional route for comparison in L05.

## References

Official documentation was verified through search and retrieval on 3 November 2026: [Python 3.12 typing](https://docs.python.org/3.12/library/typing.html), [map](https://docs.python.org/3.12/library/functions.html#map), [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [graph construction guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api), and [messages](https://docs.langchain.com/oss/python/langchain/messages). Source attribution: Vaibhav Mehra / freeCodeCamp, [LangGraph Complete Course for Beginners](https://youtu.be/jGg_1h0qzaM?t=0), L01 window 00:00:00–00:18:39.
