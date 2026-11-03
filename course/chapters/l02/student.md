# L02 — Hello World and personalized compliment

## What you will build

A LangGraph graph does not need an AI model. In this lesson, one ordinary Python function receives a name, formats a greeting, and returns a state update. LangGraph controls when that function runs and when execution finishes. The independent exercise changes the function's job from greeting to personalized compliment. Both programs are deterministic: the same valid name produces the same exact text on every fresh invocation.

Allow 70 minutes. Before starting, complete L01 and be comfortable with dictionary lookup, function calls, string formatting, and `TypedDict`. By the end, you should be able to define a one-field state, register one node, connect START and END, compile the builder, invoke the compiled graph, and inspect its returned `message`. You will also distinguish changing graph state from mutating the caller's input dictionary.

**Video-backed:** the source section runs from [00:18:39](https://youtu.be/jGg_1h0qzaM?t=1119) to 00:33:07. Its coding chapter begins at [00:21:08](https://youtu.be/jGg_1h0qzaM?t=1268), and the personalized-compliment exercise begins at [00:32:22](https://youtu.be/jGg_1h0qzaM?t=1942). The supplied whole-track visual review confirms the exercise slide at 00:32:30. These references identify source teaching, not execution of our adapted files.

<!-- VIDEO_FIGURE -->

## Explain: a state, a function, and a path

Our `MessageState` describes a dictionary containing one key, `message`, whose value is a string. At input, the string is a person's name, such as `Bob`. After the node runs, the same channel contains the full greeting. A **channel** here means one named field that LangGraph tracks in its state. We deliberately reuse one field to stay close to the source exercise; we are not creating chat history.

`TypedDict` helps readers and static type checkers understand that structure. At runtime, the value is still an ordinary dictionary. The annotation does not automatically reject a number or guarantee that a key exists. The [official Python typing specification](https://typing.python.org/en/latest/spec/typeddict.html) explains this distinction. Our explicit `read_name` checks are **added practice**: missing or non-string values raise `TypeError`; empty or whitespace-only strings raise `ValueError`.

A **node** is the callable registered in the graph. Our greeting node reads the name and returns a newly constructed dictionary. It never assigns into the dictionary it receives. `read_name` is a helper function called inside that node; it is not a second graph node. In this lesson the returned update contains the only state field, but it follows the same partial-update pattern that later lessons use with several fields.

An **edge** specifies what runs next. The path is START → greeter → END. START and END are special boundary markers, not two more Python functions to implement. There is exactly one work-performing node, no decision branch, and no loop. The [official Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api) describes nodes that contain ordinary code as well as nodes that call models.

## Illustrate: follow one invocation

The following original diagram shows the common topology. Use the greeter in the demonstration or the compliment node in the exercise; they are alternatives, not two nodes connected together.

<!-- ORIGINAL_DIAGRAM -->

For input `{"message": "Bob"}`, the greeting node returns `{"message": "Hello, Bob! How is your day going?"}`. LangGraph applies the returned update to its state, and `invoke` returns the resulting dictionary. Read `result["message"]` to obtain the string rather than printing the whole dictionary when you only want the greeting.

There is no automatic string concatenation in this state. Without a custom reducer, an update replaces the old value of that channel. Therefore the node must explicitly include the incoming name while building its output. Returning a fixed greeting would erase the personalization even though the graph could compile and execute successfully.

The caller's original dictionary is a different concern. We keep it unchanged by returning a new update instead of doing `state["message"] = ...`. Successful compilation alone cannot establish either the wording or this non-mutation property. Those require checks against actual behavior.

## Demonstrate: build, compile, and invoke

The tested demonstration lives in `course_lessons/l02.py`. Read it before changing anything. Parent handbook integration inserts its complete source at this point.

<!-- EXAMPLE_CODE -->

The `StateGraph(MessageState)` object is a **builder**: it records the state schema, node names, and connections. `add_node("greeter", greeting_node)` associates a graph-visible string with a Python callable. Notice that the function is passed without parentheses. Calling `greeting_node(...)` while registering it would run the function too early instead of handing the graph something to execute later.

`add_edge(START, "greeter")` selects the first node. `add_edge("greeter", END)` establishes the exit. Node names in the edges must match the registration exactly. Then `compile()` produces an executable graph. Finally, `graph.invoke(input_state, config=execution_config())` executes that graph. The shared configuration supplies the course recursion limit and preserves explicitly selected callbacks; it is not the input state.

Run commands from the project root with the prepared Python 3.12 virtual environment active:

```bash
python -m course_lessons.l02 --backend none
```

No `--live` option or model key is needed. The selected `none` backend prevents unrequested tracing. The command's JSON summary should report the Bob greeting, `model_used: false`, and successful deterministic and input-preservation checks. These are expected acceptance properties, not a claim about a screenshot or service dashboard. The wrapper creates its run directory, but this lesson's function writes no data files.

<!-- EXECUTION_FIGURES -->

## Guided practice: inspect the boundaries

1. Locate `MessageState`, `read_name`, `greeting_node`, and `build_graph`. Trace which object is a dictionary, which is a function, and which is a compiled graph. Say the complete runtime path aloud.
2. Predict the greeting for `Ada Lovelace` before trying it. In a Python session, import `build_graph` from `course_lessons.l02` and `execution_config` from `course_support.runtime`; invoke the compiled graph with `{"message": "Ada Lovelace"}` and that configuration. Use backend-none classroom settings, not a tracing-enabled session.
3. Keep an input variable and a copy of it. Call `greeting_node` directly, then compare the original with its copy and inspect the returned dictionary. The original should still contain only the supplied name. This separates node behavior from orchestration.
4. Read the topology in `build_graph`. Removing the END edge is not our requested graph, even if some graph constructions can finish without an explicit END edge. Restore any exploratory change before continuing.
5. Compare the demo command with `python -m pytest tests/lessons/test_l02.py -q`. The command checks a working example; the focused tests also exercise invalid input, the independent solution, and callback forwarding. A passing reference test file does not assess your starter edits.

## Independent exercise: personalized compliment

Open `exercises/starters/l02.py`, not the solution. Implement its three TODO functions: `read_name`, `compliment_node`, and `build_graph`. Keep exactly one state field, `message`, and one registered node named `compliment`. Connect START → compliment → END and return the compiled graph.

For `Bob`, produce exactly `Bob, you're doing an amazing job learning LangGraph.` Use the incoming value rather than hard-coding Bob. Apply the identical suffix to `Ada Lovelace`, `Zoë`, and `  Bob  `. Preserve every character of a valid name, including its spaces; using `.strip()` to test blankness must not change what you return. The name remains present in the output, but the one-field design does not retain a separate raw-name field.

Raise `TypeError` for missing or non-string `message`, and `ValueError` for empty or whitespace-only strings. Return a new update dictionary and do not modify the incoming dictionary. Use only ordinary Python and LangGraph: no model, network, randomness, added nodes, or file saving. Detailed steps, progressive hints, and evidence fields are in the matching workbook.

```bash
python -m exercises.starters.l02
```

The untouched starter exits normally with `STARTER_NOT_COMPLETED`; that is not a pass. Once all TODOs meet its embedded checks, it reports `completed`. Consult `python -m exercises.solutions.l02 --backend none` only after making your own attempt. The reference solution is independent of the greeting demonstration.

## Review: three knowledge checks

1. What are the separate jobs of `StateGraph(MessageState)`, `compile()`, and `invoke({"message": "Bob"}, config=execution_config())`? Does successful compilation prove the greeting text is correct?
2. A compliment node reads `name` from `{"message": "Ada Lovelace"}` and returns `{"message": f"{name}, you're doing an amazing job learning LangGraph."}`. What is the final `message`, and should the caller's original input dictionary have been edited?
3. Why does this graph need no Anthropic key? Under our explicit validation rules, what happens for `{"message": "   "}` and `{"message": 7}`?

## Troubleshooting and current-API differences

If imports fail, check the active virtual environment and run from the repository root with `python -m`, not a direct file path. Do not install a model provider to fix a simple module-path error. If a node name is unknown, compare the exact strings in `add_node` and both edges. If invocation fails, confirm that `build_graph` returns `builder.compile()`, not the builder.

A wrong name usually means a constant was used instead of `state["message"]`. A lost name means the output replaced the channel without incorporating its previous value. A padded name losing spaces means the validation function returned a stripped value. Invalid-input errors are intentional and are not model failures.

**Current-API update:** the video uses entry/finish terminology and mutates its state dictionary. This adaptation uses explicit START/END edges and returns updates, following the [current official usage guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api). Entry-point helpers still appear in current documentation; they are not presented here as removed APIs. Exact punctuation, validation cases, automated tests, and CLI summaries are course additions. Later lessons introduce larger state schemas and real model calls; adding either here would obscure the one-node lesson.

## References

Official references were verified through search and fetch on 3 November 2026: [Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api), [Graph API usage](https://docs.langchain.com/oss/python/langgraph/use-graph-api), and [Python TypedDict specification](https://typing.python.org/en/latest/spec/typeddict.html). Source teaching: Vaibhav Mehra / freeCodeCamp, [first graph](https://youtu.be/jGg_1h0qzaM?t=1119), [coding chapter](https://youtu.be/jGg_1h0qzaM?t=1268), and [compliment exercise](https://youtu.be/jGg_1h0qzaM?t=1942).
