# L04 — Three-node sequential profile

## Explain: why the second node can erase the first

A graph can run in the correct order and still produce the wrong answer. In this lesson, a first node writes a greeting and a second node writes an age sentence. If both write the same key without preserving its previous value, the age sentence replaces the greeting. Your job is to separate two questions: **Which node runs next?** and **What value does that node return?** An edge answers the first question; the node's Python code answers the second.

By the end, you should be able to build a directed sequence, predict intermediate state, distinguish a partial update from the accumulated state, and extend the sequence to produce a complete profile. Prerequisites are L03, dictionaries, lists, f-strings, and ordinary Python functions. Allow about 80 minutes, including guided practice and the independent exercise. No model, credentials, paid API, or tracing backend is needed.

**Video-backed content:** the source section is [00:44:29–00:55:36](https://youtu.be/jGg_1h0qzaM?t=2669). It demonstrates two name/age nodes, introduces the overwrite mistake around [00:48:00](https://youtu.be/jGg_1h0qzaM?t=2880), then assigns a three-node profile exercise in the chapter beginning [00:54:04](https://youtu.be/jGg_1h0qzaM?t=3244). The reviewed exercise uses Linda, age 31, with Python, machine learning, and LangGraph skills. Exact punctuation here is an adaptation, not a transcription of a low-resolution frame.

**Added practice and current-API update:** this version uses integer ages, explicit input validation, partial updates, a visited-node list, and defined empty-skill behavior. These additions make correctness observable and testable without changing the source exercise's purpose.

## Illustrate: state, updates, and directed edges

The demonstration state has input keys `name` and `age`, plus generated keys `final` and `visited`. A `TypedDict` describes the expected dictionary shape to readers and type-checking tools. `NotRequired` means a key need not exist initially. It does not mean LangGraph invents a useful value for it. The greeting node creates the generated keys before the age node reads them.

A **partial update** is a dictionary containing only the keys a node wants to change. The accumulated state is the current collection of input and generated values after LangGraph applies that update. The official [Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api) documents that, without a custom reducer, a new value replaces the previous value for the same key. Keys omitted from an update retain their existing values.

For Charlie, age 20, the greeting node returns `{"final": "Hi Charlie.", "visited": ["greet"]}`. The buggy age node returns a new `final` containing only `You are 20 years old.` The greeting disappears, but `name` and `age` do not: that node never replaced those keys. The corrected node constructs its new string from `state["final"]` followed by the age sentence. It still replaces `final`; the replacement simply includes the old text deliberately.

The same rule applies to `visited`. Writing `["age"]` would replace `["greet"]`. Returning `state["visited"] + ["age"]` constructs a new list preserving the earlier item. Neither strings nor lists accumulate automatically in this lesson. A **reducer** is a rule that can combine old and new values for a key; configuring one is not necessary here.

The original diagram below shows the two-node demonstration and its three-node extension. Boundary labels mark entry and termination; they do not perform profile work.

<!-- ORIGINAL_DIAGRAM -->

An edge from one node to another makes the destination wait for that source to finish, as specified in the official [add_edge reference](https://reference.langchain.com/python/langgraph/graph/state/StateGraph/add_edge). Merely registering functions with `add_node` does not establish their order. The exercise needs `START → welcome → age → skills → END`: four edges in total, with two edges between work nodes.

<!-- VIDEO_FIGURE -->

Source figure context: the supplied visual review confirms the sequential-profile exercise title at [00:54:10](https://youtu.be/jGg_1h0qzaM?t=3250). A source frame illustrates the original lesson; it is not evidence that this adapted code executed.

## Demonstrate: run the tested baseline

From the repository root, with the course virtual environment active, run:

```bash
python -m course_lessons.l04 --backend none
```

The complete demonstration source belongs here for reading alongside the explanation.

<!-- EXAMPLE_CODE -->

The module builds the same topology twice: once with the intentionally broken age function and once with the corrected function. Internal assertions check both actual results. Expected stable properties are a broken result containing only the age sentence, a corrected result containing both greeting and age, and node order `["greet", "age"]`. The returned summary also includes three details worth inspecting: `updates`, `inputs_unchanged`, and `model_calls`.

The `updates` list comes from a separate, fresh streaming invocation using `stream_mode="updates"`. It contains each node's returned changes, not the whole accumulated state. This second run is harmless here because nodes have no external side effects. Do not assume repeating a graph is equally harmless when later lessons introduce model costs or file writes.

`run_demo` accepts the course-standard `live` and `workdir` arguments but does not need them for its calculations. Leave `--live` off. The shared CLI may create an empty run directory; L04 itself does not write files. Keep `--backend none` for this offline lesson. The parent project handles optional service verification and screenshots separately.

<!-- EXECUTION_FIGURES -->

## Guided practice: predict before rerunning

1. Read `greet`, `overwrite_age`, and `append_age` in `course_lessons/l04.py`. On paper, write the value of `final` after each function. Include the initial state, in which `final` is absent. Identify which function first creates it.
2. Run the demonstration and compare the two final strings. Explain why both versions can report the same visited-node order. Correct control flow is necessary but does not prove correct string construction.
3. Inspect the first streaming update. Find the two keys it contains and the input keys it omits. Explain why omission is not deletion. Then locate the second update and identify where it carries the earlier greeting forward.
4. Trace the four construction stages: define the state, register nodes, connect edges, and compile. Invocation uses the compiled graph, not the builder. Compilation checks structure, not whether your sentence has the right words.
5. Predict the age wording for 0 and 1. This adaptation uses `0 years old` and `1 year old`. Input validation rejects negative ages, strings such as `"31"`, and booleans. Python treats `bool` as related to `int`, so the supplied validator deliberately requires `type(age) is int`.

These are reading and prediction activities. You do not need to alter another lesson or the shared runtime. The official [sequential graph guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api) also shows `add_sequence`, but explicit edges are retained here so you can explain every transition.

## Independent exercise: welcome, age, and skills

Open `exercises/starters/l04.py`; the full task and recording fields are in `course/chapters/l04/workbook.md`. Complete exactly three TODO functions: `welcome`, `describe_age`, and `describe_skills`. Validation, graph registration, and all four edges are supplied. Explain the edges in the workbook rather than hiding the entire calculation in one function.

Each node must return only `result` and `visited` updates without mutating its input dictionary or lists. `welcome` starts a fresh message and sets `visited` to `["welcome"]`, even if stale generated fields were supplied. The age node preserves that message, adds age without a trailing period, and extends the list with `"age"`. The skills node preserves both earlier components, finishes the sentence, and adds `"skills"`.

For Linda, the exact target is:

```text
Linda welcome to the system. You are 31 years old and you have skills in Python, machine learning and LangGraph.
```

Keep skill order and duplicates. One skill is printed alone; two use ` and `; three or more use commas between earlier items and ` and ` before the last item, without an Oxford comma. With an empty list, end with ` and you have no listed skills.` Use singular `year` only for age 1. Preserve the original `name`, `age`, and `skills` values in the returned graph state. No normalization, sorting, model call, file write, conditional graph route, or reducer is required.

Run `python -m exercises.starters.l04`. Before implementation it must print `STARTER_NOT_COMPLETED`, not pretend to pass. After completing all nodes, its checks cover Linda, an empty list, one skill, and two skills. The independent reference is `python -m exercises.solutions.l04 --backend none`; use it after attempting the task. The focused maintainer tests are `python -m pytest tests/lessons/test_l04.py -q`. They test delivered demonstration and reference solution behavior; they do not automatically grade your edited starter.

## Review: three knowledge checks

1. After `welcome`, `result` contains `Linda welcome to the system.` and `visited` is `["welcome"]`. Suppose the age node returns `{"result": "You are 31 years old", "visited": ["age"]}`. What disappears, what happens to `name`, `age`, and `skills`, and why?
2. Write the exercise's four `add_edge` connections. Which two connect work nodes, and why does calling `add_node` three times not guarantee this sequence?
3. The corrected skills node returns only `result` and `visited`. Why do the input fields still appear in final state? Must the node mutate state or return the entire dictionary to retain them?

## Troubleshooting and completion

A missing greeting usually means a later node constructed a replacement without reading the old string. A missing visited item has the same cause for lists. Fix the update expression, not the edge order. A `KeyError` for `result` suggests that an earlier node did not create it or that the graph was rewired incorrectly; do not cover this up with an empty-string default.

A skills list printed with brackets means Python's list representation was used instead of formatting its items. An extra comma before the last skill fails this exercise's chosen punctuation contract. A successful compilation with a wrong message means structural validation worked but the application logic still needs testing. If imports fail, activate the prepared course environment and run module commands from the repository root; no API key can repair a Python import error.

Completion means you can predict the overwrite, explain each edge, produce the exact Linda message and boundary cases, and show unchanged input values. The learner result is a deterministic profile builder, not an autonomous agent.

## References and source differences

The [source video](https://youtu.be/jGg_1h0qzaM?t=2669) supplies the overwrite demonstration and three-node exercise. The [Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api), [usage guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api), and [edge reference](https://reference.langchain.com/python/langgraph/graph/state/StateGraph/add_edge) were verified by search and fetch on 3 November 2026. This implementation uses explicit `START`/`END` boundaries and returned partial updates rather than reproducing historical mutation-style examples. Historical entry/finish terminology remains conceptually useful; it is not a requirement to use those convenience methods. No LLM integration is added to this deterministic source section.
