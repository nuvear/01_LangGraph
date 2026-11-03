# L02 — Hello World and personalized compliment

## Prepare the same learning sequence

Teach Explain → Illustrate → Demonstrate → Guided practice → Independent exercise → Review in 70 minutes. The prerequisite is L01, not access to an AI provider. Learners need dictionary access, functions, f-strings, and the idea that `TypedDict` describes a structure. The observable outcome is a compiled graph with exactly one working node and two explicit boundary edges. Avoid adding messages, tools, history, or model calls to make the lesson appear more sophisticated.

Use the lesson's exact output punctuation and validation requirements as the acceptance contract for the classroom exercise.

<!-- CONCEPT_FIGURE -->

Before teaching, activate the prepared Python 3.12 environment and identify `course_lessons/l02.py`, `exercises/starters/l02.py`, `exercises/solutions/l02.py`, and `tests/lessons/test_l02.py`. Use only synthetic names. Run the following locally with tracing disabled; no model account or credential inspection is needed:

```bash
python -m course_lessons.l02 --backend none
python -m exercises.solutions.l02 --backend none
python -m exercises.starters.l02
python -m pytest tests/lessons/test_l02.py -q
```

The untouched starter must say `STARTER_NOT_COMPLETED`, not `passed`. Distinguish these preparation expectations from actual execution evidence. Treat the command output as execution evidence for the implementation; a prepared example or diagram is not proof that the learner's implementation ran.

## Explain and illustrate: minutes 0–15

During minutes 0–8, establish that the graph schedules ordinary code. Ask learners to identify the Python function that constructs text and the edges that determine execution order. Expected response: the greeting node constructs the greeting; START → greeter → END gives the path. `read_name` is called inside the node, so it does not make this a two-node graph.

During minutes 8–15, walk through the diagram with `{"message": "Bob"}`. Use either the greeter or the compliment as its single middle node; never imply that both run in one invocation.

<!-- ORIGINAL_DIAGRAM -->

Explain that `message` initially carries the name and later carries the formatted result. Name preservation means including the input characters in the output; it does not imply a separate name channel. With no custom reducer, an update replaces that field. The Python expression must explicitly include the incoming name. The [Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api) supports the default-replacement and partial-update explanations.

Separate two objects on screen: the caller's dictionary and the update returned by the function. Returning an update changes graph state without assigning into the caller's dictionary. A correct-looking sentence does not establish purity; compare the original before and after. Likewise, `TypedDict` is not our runtime validator. Show the explicit type and blankness checks rather than attributing their errors to annotations.

## Demonstrate: minutes 15–25

1. Open the demonstration. Identify `MessageState` and `greeting_node`, then read `read_name`. Explain that `.strip()` is used only to detect blankness; a valid string is returned unchanged.
2. Trace `StateGraph(MessageState)`, `add_node("greeter", greeting_node)`, and both boundary edges. Expected response: this is graph construction, not yet execution. Draw attention to passing the function without calling it.
3. Show `builder.compile()` and then `graph.invoke(..., config=execution_config())`. Compilation checks construction; invocation executes the work. Preserve the shared configuration rather than replacing it with an unrelated dictionary.
4. Run the demo command. Find the Bob greeting in the JSON result and the `model_used: false` property. Run the same valid input again and compare text. Explain that this is deterministic formatting, not an LLM memorizing a prompt.
5. Read the actual assertions in `run_demo`. They check several names, unchanged input, repeatability, and exact topology. The wrapper's output directory is not a saved greeting artifact; the lesson function writes no files.

<!-- EXECUTION_FIGURES -->

## Guided practice: minutes 25–40

Have learners predict the Ada Lovelace greeting before invocation, compare a direct node call with a full graph call, and identify the two boundary edges. Circulate for the distinction between a builder and a compiled executable. If someone changes a node name, ask them to trace every edge string instead of immediately supplying the correction.

A useful controlled mistake is a node returning a fixed greeting. It may compile and run yet fail personalization. Restore the demonstration rather than leaving a broken baseline. Ask for evidence of non-mutation: comparing the input dictionary against its saved copy is stronger than saying the function looks pure.

## Independent exercise and solution: minutes 40–60

Assign exactly the workbook's three functions. Learners keep one `message` channel, register `compliment`, and compile START → compliment → END. For each valid name they produce the name followed by `, you're doing an amazing job learning LangGraph.` They must handle Bob, Ada Lovelace, Zoë, and a padded Bob without normalization. Empty or whitespace-only input raises `ValueError`; missing or non-string input raises `TypeError`.

The reference is a complete independent implementation, not an import of the demonstration. Explain its three decisions. First, `read_name` uses a lookup that can detect missing input and performs explicit checks. Second, `compliment_node` returns a fresh one-key dictionary constructed from the checked original name. Third, `build_graph` registers only that callable, adds both edges, and returns the compiled result. No extra graph node is introduced by factoring validation into a helper.

`run_demo` invokes the real graph for the four valid names and checks the original dictionary. It then invokes four invalid cases and requires the specified exceptions. A final fresh Bob invocation verifies repeatability rather than accumulation. Topology assertions exclude an accidental second node or missing boundary. Focused pytest coverage adds `None` and verifies configuration reaches actual node callbacks without using a remote tracer.

<!-- SOLUTION_CODE -->

Do not reward importing the reference solution into the starter. Its embedded checks assess the learner's local functions. The focused pytest file primarily validates the shipped demo/reference and starter harness; passing it alone is not evidence that a learner implemented the TODOs.

## Review and exact knowledge-check answers: minutes 60–70

### 1. Builder, compilation, and invocation

The student's question asks for the jobs of `StateGraph(MessageState)`, `compile()`, and `invoke({"message": "Bob"}, config=execution_config())`, and whether compilation proves text correctness. The builder records the schema and construction. Compilation produces the runnable graph and performs structural checks. Invocation supplies state and executes the connected function. Successful compilation does not prove the greeting wording, name preservation, or non-mutation; behavioral assertions establish those properties.

### 2. Ada Lovelace and the original dictionary

The final message is exactly `Ada Lovelace, you're doing an amazing job learning LangGraph.` The caller's original dictionary should remain `{"message": "Ada Lovelace"}`. The node returns a new update; the graph applies it to its state. Default replacement of the `message` channel does not require editing the caller's original object. Reject an answer that says LangGraph automatically concatenates the name.

### 3. No provider key and the two invalid inputs

No Anthropic key is needed because every node operation is ordinary Python string handling. No model is constructed. `{"message": "   "}` raises `ValueError` because the string is blank after the blankness check. `{"message": 7}` raises `TypeError` because the value is not a string. These outcomes follow from our explicit checks, not `TypedDict` enforcement or provider behavior.

## Marking, misconceptions, and recovery

Use five criteria worth two points each: correct one-node topology and compiled return; exact personalization across all valid names; explicit invalid-input handling; a new update with unchanged input; and runnable starter evidence plus a correct explanation of build/compile/invoke. Give one point for a partially correct criterion. Require independent starter execution before calling the practical task complete. Knowledge-check explanations reveal whether apparent success came from copying.

Common misconceptions include counting START and END as working functions, treating a helper as a registered node, assuming compilation proves semantics, and expecting annotations to reject bad data. A learner who strips a valid name should compare the padded acceptance case character by character. A learner who sees an API-key error should check that they are running L02 with `--backend none`, not a different lesson or an explicitly traced command.

For import recovery, return to the project root and active environment; use module commands. For a missing-node error, compare registration and edge names. For builder invocation, restore the compiled return. For blank-input failures, decide whether the exception is expected before changing the program. Do not fix these problems by installing packages or introducing provider configuration during the lesson.

## Current API and references

Use explicit START/END edges to make the path visible; current documentation still contains entry-point helpers, so do not call them removed. The [official usage guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api) advises returning updates rather than mutating state. The [Python typing specification](https://typing.python.org/en/latest/spec/typeddict.html) supports the ordinary-dictionary explanation. Input validation, exact punctuation, tests, and CLI summaries are teaching safeguards for this lesson. No model request or tracing dashboard is needed for this chapter.
