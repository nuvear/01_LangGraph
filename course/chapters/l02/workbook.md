# L02 — Hello World and personalized compliment

## Task and source

Build a deterministic personalized-compliment graph with one working node. The input dictionary contains one field, `message`, holding a person's name. The output uses that same field for the completed compliment. Do not add a model, provider key, tool, second node, conversation history, randomness, or a saved file.

This task preserves the exercise introduced at [00:32:22 in the source video](https://youtu.be/jGg_1h0qzaM?t=1942), inside L02's 00:18:39–00:33:07 window. The supplied whole-track review confirms its slide at 00:32:30. Exact spelling, validation, padded-name handling, and executable acceptance checks below are **added course requirements**, not claims about source notebook punctuation. Plan about 20 minutes of independent work after guided practice.

Start with `exercises/starters/l02.py`. It is a separate scaffold, not an import of the answer. Implement only the three marked functions and retain the supplied checks. After your attempt, compare with the independent reference at `exercises/solutions/l02.py`. The greeting demonstration is `course_lessons/l02.py`; do not simply submit its greeting as your compliment exercise.

## Exact acceptance contract

Keep `MessageState` with the one string field `message`. Register your node as `compliment` and connect START → compliment → END. `build_graph` must return the compiled graph rather than the builder. Use `execution_config()` at invocation, as the scaffold does.

For `{"message": "Bob"}`, the final `message` must be exactly:

```text
Bob, you're doing an amazing job learning LangGraph.
```

For any other valid name, use that original name followed by the identical suffix. Check `Ada Lovelace`, `Zoë`, and `  Bob  ` as well. The padded example contains two spaces before and two after Bob; those characters must remain before the comma is appended. Do not replace a person's name with a constant and do not normalize a valid name. This simple exercise tests state transformation, not a production name-cleaning policy.

Missing `message` or a non-string value must raise `TypeError`. Empty or whitespace-only strings must raise `ValueError`. A valid node call returns a new dictionary without assigning into the supplied one. The name is preserved as part of the output sentence, not as a separate field or durable memory. A fresh invocation with Bob must give the same single compliment, not add another compliment to a previous result.

## Work in small steps

1. Activate the prepared Python 3.12 environment and work from the project root. Run the demonstration to remind yourself what a successful one-node graph does:

   ```bash
   python -m course_lessons.l02 --backend none
   ```

2. Run the untouched starter:

   ```bash
   python -m exercises.starters.l02
   ```

   It should exit normally and print `STARTER_NOT_COMPLETED`. That message is a checkpoint, not success. The first reported unfinished function may be `build_graph`, since the acceptance harness builds before invoking.

3. Implement TODO 1, `read_name`. Decide how to distinguish a missing or non-string value from a blank string. Use blankness checking without changing valid text.

4. Implement TODO 2, `compliment_node`. Call your helper, construct the required string, and return a fresh one-field update. Compare the incoming dictionary before and after a direct node call.

5. Implement TODO 3, `build_graph`. Pass the callable to `add_node`, not the result of calling it. Add both boundaries, then return compilation. Keep exactly one registered working node.

6. Rerun the starter without changing its acceptance harness. Its completed path checks the four valid names, repeated invocations, purity, invalid inputs, and the two boundary edges. An assertion failure is not another TODO; investigate the stated property.

7. After your own result is complete, run the independent reference and focused tests:

   ```bash
   python -m exercises.solutions.l02 --backend none
   python -m pytest tests/lessons/test_l02.py -q
   ```

   These tests validate the shipped demonstration/reference and starter harness. They do not replace evidence from your completed starter. No `--live`, environment-file inspection, or tracing dashboard is needed for any step.

## Three progressive hints

### Hint 1: inspect the input before formatting

`TypedDict` does not enforce runtime values. Get the incoming field, check that it is a string, then check whether it contains any non-whitespace characters. Preserve the original string after those checks.

### Hint 2: distinguish an update from mutation

A fresh dictionary containing the new `message` is enough. The default state behavior replaces that channel; it does not automatically append the old value. Your formatting expression must include the checked name explicitly.

### Hint 3: separate topology from execution

The builder needs one registration and two edges. Compile only after wiring the path. Invoke the returned executable with a name dictionary and the shared configuration. A helper called by a node does not need its own graph registration.

## Record observed results

Use brief notes from your actual run, not predictions presented as evidence.

- Command and interpreter/environment used: ______
- Bob output and one additional valid-name output: ______
- Padded-name and unchanged-input observations: ______
- Invalid cases tried, observed exception types, and starter completion status: ______

Keep these notes beside your exercise; screenshots and handbook production are handled separately. Do not invent a pass if dependencies or imports prevent execution.

## Completion and stretch

You are finished when all three TODOs are independently implemented, the starter reports `completed`, every acceptance case holds, and you can explain builder → compilation → invocation. Explain why one ordinary Python node needs no AI service and why successful compilation alone cannot prove correct wording.

For an optional stretch, write an additional local test using a hyphenated name or a name with an apostrophe. Keep the original characters and the required suffix unchanged. Do not add input prompts, a second state field, or a model to solve the baseline task. Compare your reasoning with the student chapter's three knowledge checks before advancing to multiple-input processing in L03.

## References

Current patterns were verified on 3 November 2026 against the official [LangGraph Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api), [Graph API usage guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api), and [Python TypedDict specification](https://typing.python.org/en/latest/spec/typeddict.html). The video uses historical mutation and entry/finish presentation; this workbook uses returned updates and explicit START/END edges.
