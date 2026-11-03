# L04 — Three-node sequential profile

## Explain: teaching intent and prerequisites

This 80-minute lesson moves from one-node calculations to ordered state transformations. The central distinction is between control flow and update semantics. Students should leave knowing that correct edges cannot prevent a node from returning the wrong replacement value. They should also recognize that retaining fields does not require mutating or returning the whole input dictionary.

Check dictionary lookups, f-strings, list concatenation, and dictionary returns. Re-establish L03's builder-versus-compiled-graph distinction if necessary. No credentials, Anthropic access, or dashboard is relevant here.

**Video-backed sequence:** [00:44:29–00:55:36](https://youtu.be/jGg_1h0qzaM?t=2669) introduces sequential nodes, demonstrates the overwrite error at about [00:48:00](https://youtu.be/jGg_1h0qzaM?t=2880), fixes preservation, then assigns the three-node profile exercise in the chapter starting [00:54:04](https://youtu.be/jGg_1h0qzaM?t=3244). Whole-track sampled visual review confirms exercise identity at 00:54:10; do not describe that as frame-by-frame viewing or execution of our adaptation.

**Added/current practice:** integer ages, singular-year wording, runtime validation, empty skills, visited lists, and exact acceptance tests are authored teaching decisions. The source's central profile components and Linda example remain intact. Keep this distinction explicit when learners compare punctuation or state annotations with the source.

## Illustrate: make replacement visible

Use the original diagram to distinguish boundary markers from the work nodes. The upper path is the two-node demonstration; the lower path extends that pattern to the independent exercise. There is no branch and no loop.

<!-- ORIGINAL_DIAGRAM -->

Show the source figure only to situate the original exercise. Explain that a source screenshot and an adapted-code execution screenshot have different evidential roles.

<!-- VIDEO_FIGURE -->

The [Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api) explicitly describes partial updates and default per-key replacement. Draw three separate records: input state, node return dictionary, and accumulated state. This prevents students treating a streaming update as if it were the entire state. Ask which record contains the name after a node returns only a new `final` value. Expected response: the accumulated state still contains the name; the update itself does not need to repeat it.

Explain manual preservation precisely: `old_text + new_text` creates the complete next value, which then replaces the earlier value. Likewise, `old_list + [item]` creates a fresh list. Neither operation configures a reducer, and the reference nodes never use in-place `append` on a state list.

## Demonstrate: an 80-minute delivery sequence

### Minutes 0–10: prediction and source context

Introduce the objective and show the source's overwrite moment. Ask, “If both nodes finish successfully, can the final string still be incomplete?” Expected response: yes, the second node can replace the greeting. Have learners predict both the broken string and corrected string before running anything.

### Minutes 10–25: live local demonstration, not a live API call

Run `python -m course_lessons.l04 --backend none` from the prepared environment. Inspect `broken_final`, `corrected_final`, and `node_order` in the summary. Both graph variants must visit `greet` then `age`. Their different results isolate the Python update behavior as the cause. The demonstration's assertions check actual graph outputs, not predetermined printed success text.

Show the separate `updates` run. Its first event carries only `final` and `visited`; after applying it, the accumulated state also retains `name` and `age`. State clearly that streaming here reruns a side-effect-free graph. Do not generalize that as free or safe for future model/tool workflows.

<!-- EXECUTION_FIGURES -->

### Minutes 25–40: guided practice

Follow the student's five numbered activities in order. Expected predictions are absent `final` initially, then a greeting, then either an age-only string or a combined string. For age 1, expect `year`; for age 0, expect `years`. A learner who says TypedDict will reject `"31"` needs the distinction between annotations and the supplied `make_input` checks. Booleans are explicitly rejected despite Python's integer relationship.

Have learners name all construction stages and point to each in code. Emphasize that `add_node` registers a callable, `add_edge` describes transitions, and `compile` produces the runnable graph. The official [edge reference](https://reference.langchain.com/python/langgraph/graph/state/StateGraph/add_edge) says the destination of a single-source edge waits for that source to complete. Registration order is not an execution plan.

### Minutes 40–70: independent three-node exercise

Direct learners to `exercises/starters/l04.py` and the matching workbook. The graph scaffold and validator are supplied; only the three node functions are TODOs. Keep the reference solution closed initially. Check one early return value before allowing students to finish all three functions. This catches mutation, complete-state returns, and a fourth “format everything” node before they become entrenched.

At minute 60, ask learners to test empty and two-skill inputs. An exact Linda result alone is insufficient evidence for general formatting. If time is short, retain these checks and drop the optional stretch, not the distinction between update and accumulated state.

### Minutes 70–80: review and assessment

Use the three exact knowledge checks below and the workbook observations. Demonstrate `python -m exercises.solutions.l04 --backend none` only after independent attempts. Run `python -m pytest tests/lessons/test_l04.py -q` for the delivered reference checks. Explain that these maintainer tests do not automatically grade a learner's edited starter; the starter's own checks plus inspection establish that evidence.

## Full knowledge-check answers with reasoning

### Answer 1: overwritten text and list

The welcome text disappears because the age node supplies an age-only replacement for `result`. The `welcome` item also disappears from `visited`, which becomes `["age"]`. The `name`, `age`, and `skills` fields retain their current values because the update does not write them. Default update behavior operates independently per key: omission preserves a field; an explicit new value replaces it. This is not a graph-order error, because the hypothetical node still follows `welcome`.

### Answer 2: four required connections

The exact connections are `START → welcome`, `welcome → age`, `age → skills`, and `skills → END`. In code, use `builder.add_edge(START, "welcome")`, `builder.add_edge("welcome", "age")`, `builder.add_edge("age", "skills")`, and `builder.add_edge("skills", END)`. The middle two connect work nodes. `add_node` associates names with functions; it does not create these transitions. Three registrations alone do not describe the required sequence.

### Answer 3: retained inputs without mutation

A partial update changes only its supplied keys. After the skills node writes `result` and `visited`, the accumulated state retains `name`, `age`, and `skills` from earlier state. Returning the full dictionary is unnecessary, and mutating it is neither necessary nor permitted by this exercise. Reading the prior result and producing a new combined value provides preservation without hidden in-place changes.

## Reference solution walkthrough

`make_input` rejects blank/non-string names, non-integer or negative ages, booleans, non-list skills, and blank/non-string list items. It copies the list. It does not normalize text, sort items, or remove duplicates. These checks are supplied to students rather than added as extra TODOs.

`welcome` replaces stale generated fields with a new welcome and `["welcome"]`. This makes repeated invocation predictable even when given a previous output. `describe_age` reads that result, appends the age clause with a leading space, and leaves the clause without a period so the next node can finish it. It returns a new visited list ending in `age`.

`describe_skills` selects one of three Python formatting cases inside the same node. Empty lists produce ` and you have no listed skills.` One item uses that item alone. Two or more join all but the last with commas and connect the last with ` and `. It preserves order and duplicates. This local `if` is ordinary formatting, not a conditional graph route. The returned result retains welcome and age, and the final visited list is exactly `["welcome", "age", "skills"]`.

<!-- SOLUTION_CODE -->

## Marking criteria, misconceptions, and recovery

Award 10 points: two for the exact three-node/four-edge topology and explanation; three for nonmutating partial updates that preserve earlier text and reset the welcome; two for exact Linda wording and unchanged inputs; two for empty/one/two/multiple skills and age 0/1; one for accurate workbook evidence and overwrite reasoning. Require all three components and no model dependency for completion, even if the numeric score would otherwise pass.

Common misconceptions are that strings concatenate automatically, lists always append automatically, compilation proves business correctness, and a successful exit proves the unfinished starter passed. Correct the last point by reading the explicit `STARTER_NOT_COMPLETED` message. That exit behavior supports incremental work; it is not a pass.

For a `KeyError`, inspect the previous node's return and edge names before adding fallback defaults. For missing words, compare old and new `result` values. For a mutated input, replace in-place list methods with a new concatenated list. For import errors, verify the active prepared interpreter and repository-root module command. Do not ask students to edit credentials or install packages mid-lesson. If the environment lacks LangGraph, report that setup blocker to the instructor rather than substitute a fake graph.

## References and evidence limits

The [sequential graph guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api), [Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api), and [add_edge reference](https://reference.langchain.com/python/langgraph/graph/state/StateGraph/add_edge) were verified on 3 November 2026. Explicit boundaries and partial updates modernize the video; `add_sequence` is available but intentionally unused. Offline tests do not establish Windows execution or remote dashboard visibility. The embedded figures and validation appendix record actual delivered execution evidence.
