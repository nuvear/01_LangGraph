# LangGraph Python Training

## Exercise Workbook

**Version 1.1 · 3 November 2026 · Author: Manus AI**

A self-contained, step-by-step Python course for learners who know basic Python and are new to LangGraph. Course repository: https://github.com/nuvear/01_LangGraph.

Work in exercises/starters, record observations, and use the progressive hints before opening exercises/solutions. Acceptance criteria describe behavior rather than a single wording from a language model. This workbook accompanies the Student Handbook; it is not a substitute for the explanations or complete examples.

The course progresses through eleven core lessons, preparation P00, durable memory U1, safe approval/state U2, LangSmith S1, LangWatch S2, and capstone C01. The estimated full teaching track is 29 hours 55 minutes excluding breaks, combining explanation, demonstration, guided practice, independent work, and assessment.

**Validation and platforms.** Delivered demonstrations and independent reference solutions are executed and recorded in the validation appendix. Model-based checks use the real configured Anthropic API; offline tests use explicitly identified test doubles. macOS/Python 3.12 is the actual execution platform. Windows commands are supplied but Windows execution is untested. Dashboard visual inspection is not implied by API ingestion checks.

**Credentials and data.** Keep `ANTHROPIC_API_KEY` in the local ignored `.env` and select the model with `ANTHROPIC_MODEL`. Do not put keys in state, prompts, source files, screenshots, traces, or submissions. Tracing sends synthetic lesson data to the selected service. A local embedding model requires a first download but no additional paid embedding API key. Examples are teaching applications, not production-security certifications.

**How to run the code.** Commands assume the repository root and an activated Python 3.12 virtual environment. Start with P00. Without activation, substitute `.venv/bin/python` on macOS or `.\.venv\Scripts\python.exe` in PowerShell for `python`. `--live` is an explicit opt-in to paid model calls; it is never a fake-response switch. Use a new `--output-dir` when repeating a save exercise because file writes do not silently overwrite existing work.

<!-- PAGEBREAK -->

# Contents

Use these links in HTML/Markdown and Word’s linked contents or Navigation Pane. Module IDs remain the same in all three manuals.

- [P00 — Setup and safe service checks](#p00)
- [L01 — Python types and graph elements](#l01)
- [L02 — Hello World and personalized compliment](#l02)
- [L03 — Multiple inputs and one-node arithmetic](#l03)
- [L04 — Three-node sequential profile](#l04)
- [L05 — Conditional routes and two independent calculations](#l05)
- [L06 — Bounded loops and automatic higher/lower game](#l06)
- [L07 — Anthropic stateless bot](#l07)
- [L08 — Conversation history and logging](#l08)
- [L09 — ReAct arithmetic tool loop](#l09)
- [L10 — Human–AI Drafter collaboration](#l10)
- [L11 — Local-embedding Chroma RAG](#l11)
- [U1 — Thread memory and durable SQLite checkpoints](#u1)
- [U2 — Safe draft state and human approval/resume](#u2)
- [S1 — LangSmith observability and evaluation](#s1)
- [S2 — LangWatch observability and comparison](#s2)
- [C01 — Document-grounded drafting capstone](#c01)
- [Appendices: commands, versions, validation, and sources](#appendices)



<!-- PAGEBREAK -->
<a id="p00"></a>
# P00 — Setup and safe service checks

## Your independent task

**SUPPLEMENTARY PRACTICE.** Build an offline public-profile readiness checker. Use basic Python dictionaries, functions and conditionals. The graph wrapper is supplied so you can focus on safe validation. No account, key, `.env`, model invocation or tracing export is part of this task.

Edit only `exercises/starters/p00.py`. Complete its three TODO functions without importing the demonstration or reference solution. Keep the supplied fixtures and graph wiring. The independent teacher reference is `exercises/solutions/p00.py`; the demonstration is `course_lessons/p00.py`.

From the project root, with the prepared Python 3.12 environment selected:

```bash
python -m course_lessons.p00 --backend none
python -m exercises.starters.p00
```

Before editing, the starter must exit successfully with `STARTER_NOT_COMPLETED`. This means work remains; it does not mean the exercise passed. Dependency installation belongs to preparation, not this offline activity.

## Step 1: implement `validate_endpoint`

Accept `service` and an optional string `value`, defaulting to blank. The starter's ORIGINS contains the exact supported hosts: Anthropic's API origin; the US, EU, APAC and AWS US LangSmith API origins; and LangWatch's cloud origin. An unsupported service raises `ValueError`.

Strip surrounding whitespace. Blank uses the first host for that service. Accept HTTPS, no port or literal `:443`, and either no path or one trailing slash. Reject unknown or lookalike hosts, credentials, other paths, malformed or other ports, dangling colons, backslashes, embedded control characters/whitespace, and any `?` or `#`, even when its component is empty. Return `https://HOST` without a port or slash. Use fixed exception text that does not echo the input.

For example, ` https://eu.api.smith.langchain.com:443/ ` canonicalizes to the EU API origin. `https://smith.langchain.com` and `https://app.langwatch.ai?token=sample` must fail. The former is a dashboard host; the latter is not a bare origin. See the official [LangSmith regional list](https://docs.langchain.com/langsmith/cloud).

## Step 2: implement `check_profile`

Accept a mapping and return exactly `status`, `issues`, `endpoints`, and `remote_checked`. Do not mutate or return the input. `remote_checked` is always false. Status is `ready` when there are no issues, otherwise `needs_attention`.

Only the six PUBLIC_FIELDS from the starter are allowed. Unknown keys produce only `unsupported_fields` with an empty endpoint map. Otherwise any non-string value produces only `invalid_value_type`, also with an empty map. Do not echo unknown keys or values, even in exceptions.

For an ordinary public profile, append issues in this exact order:

1. Append `model_invalid` unless the model fully matches `claude-[A-Za-z0-9_.:-]+`. Missing model is invalid. This is syntax only, not availability.
2. Append `backend_invalid` unless the backend is `none`, `langsmith`, `langwatch`, or `both`. A missing backend defaults to `none`.
3. Validate LangSmith then LangWatch origins, even when the proposed backend is `none`. Missing endpoint values default to blank. Retain only valid canonical origins; append `langsmith_endpoint_invalid` or `langwatch_endpoint_invalid` for failures.
4. Only for proposed `langwatch` or `both`, validate key kind: missing defaults to `project`; allowed kinds are `project`, `service`, and `personal`. Invalid kind appends `langwatch_key_kind_invalid`. Otherwise service/personal kind with a missing or whitespace-only project ID appends `langwatch_project_required`. Project-bound kind needs no explicit ID in this exercise.

The [LangWatch guide](https://langwatch.ai/docs/integration/python/guide) explains project scope. Your function does not examine a real key. The supplied wrapper validates before invoking its graph; only the safe report enters graph state. Proposed backend data never turns on tracing.

## Step 3: implement `classify_failure`

Return these exact fixed strings for simulated status inputs; perform no request, sleep or retry:

- `None`: `Check network, DNS, proxy and TLS; never disable certificate checks.`
- `401`: `Verify or rotate the key privately; do not print it.`
- `403`: `Check organization/workspace permissions and model access.`
- `404`: `Check the configured model ID and API resource path.`
- `429`: `Check rate and spend limits; honor Retry-After when present.`
- `529`: `Wait and retry within a bounded backoff budget.`
- Any other status: `Record a sanitized status and request ID; consult official errors.`

These teaching mappings are not a complete SDK error handler. Consult the [official Anthropic error reference](https://platform.claude.com/docs/en/api/errors) for other statuses.

## Run and observe

```bash
python -m exercises.starters.p00
python -m pytest tests/lessons/test_p00.py -q
# Teacher reference, after your attempt:
python -m exercises.solutions.p00 --backend none
```

The starter's self-checks assess your edited functions. The focused pytest file checks the demonstration/reference and starter scaffolding; its passing does not replace inspecting your implementation. Do not run the whole course suite.

READY_PROFILE must produce `ready`, no issues, and the canonical EU LangSmith/default LangWatch origins. REPAIR_PROFILE must produce exactly `model_invalid`, `langsmith_endpoint_invalid`, `langwatch_project_required`, in that order. Its status is `needs_attention`, and its endpoint map contains only LangWatch. The graph messages are respectively `Local profile ready.` and `Repair public settings.` Both reports retain `remote_checked: false`.

Record four concrete observations: your Python minor version and isolation result; the two ordered demonstration graph checks; the repaired profile's exact issue list before repair; and the reason a locally ready profile cannot prove authentication. Include sanitized values only.

## Three progressive hints

1. Start with unknown-field/type rejection. It prevents configuration data from leaking into a report or graph before detailed validation begins.
2. `urlsplit` separates components, but parsing is not validation. Inspect the exact host, raw delimiters, user information, path and port; catch malformed-port errors without echoing input.
3. Build one issue list in the specified order. Keep valid endpoints separately and derive status from whether that list is empty. A small dictionary can implement the fixed failure mappings.

## Completion and stretch

Completion requires three implemented functions, passing starter self-checks, both exact fixture outcomes, unchanged input profiles, secret-free errors, and no file/environment access or remote calls. Until completion retain the honest unfinished behavior; never replace TODOs with unconditional success. P00 rejects `--live` and actual non-none tracing options.

For a stretch, add your own offline assertions for a lookalike host, embedded tab, unknown credential field and personal key with blank project scope. Explain why a proposed `both` profile is not permission to export data. Do not turn the stretch into a real connection check: the separate shared CLI reads private configuration and makes actual requests only after instructor authorization.


<!-- PAGEBREAK -->
<a id="l01"></a>
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


<!-- PAGEBREAK -->
<a id="l02"></a>
# L02 — Hello World and personalized compliment

## Task

Build a deterministic personalized-compliment graph with one working node. The input dictionary contains one field, `message`, holding a person's name. The output uses that same field for the completed compliment. Do not add a model, provider key, tool, second node, conversation history, randomness, or a saved file.

The exact spelling, validation, padded-name handling, and executable acceptance checks below define the exercise contract. Plan about 20 minutes of independent work after guided practice.

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

Current patterns use the official [LangGraph Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api), [Graph API usage guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api), and [Python TypedDict specification](https://typing.python.org/en/latest/spec/typeddict.html). Use returned updates and explicit START/END edges.


<!-- PAGEBREAK -->
<a id="l03"></a>
# L03 — Multiple inputs and one-node arithmetic

## Task: finish one calculator node

Build one compiled LangGraph graph that receives an integer list, a name, and an operation. Select addition or multiplication with Python logic inside one node. Strict validation, exact output formatting, numeric outputs, and empty-list rules below define the assessment contract.

Start from `exercises/starters/l03.py`. Implement its three TODO functions, not a new script. Do not import `exercises.solutions.l03` or `course_lessons.l03` into your submission. The independent reference, for review after your attempt, is `exercises/solutions/l03.py`.

### Exact input and output agreement

The required inputs are `values`, `name`, and `operation`. `values` must be a list containing only actual integers; booleans and floats are invalid. Empty lists are valid. `name` must be a string containing at least one non-whitespace character. Preserve the supplied valid name exactly rather than trimming it. `operation` must be the string `+` or `*`. Missing or invalid required inputs must raise `ValueError`.

The node returns exactly two fields: `answer`, an integer, and `result`, formatted exactly as `Hi {name}, your answer is {answer}.` Include the comma and final period. Do not modify the supplied dictionary or its list. The final graph state must retain the three input fields and include the two outputs. If old outputs were supplied, replace them with the new calculation.

Use exactly one work-performing node named `calculator`. Connect START to that node and the node to END with ordinary edges. Return the compiled graph from `build_graph`. Do not create separate addition/multiplication nodes or use graph-level conditional edges.

## Work in three passes

1. Implement `validate_inputs`. Check all required fields explicitly; type hints alone are not runtime validation. Test a valid request, a missing operation, a blank name, and `[True]` before attempting the graph.
2. Implement `process_values`. Call validation first. Use an `if` for `+` and multiplication for `*`. Return only the two computed fields. Check the function directly so arithmetic mistakes are separate from graph-building mistakes.
3. Implement `build_graph`, compile it, and run the starter checks. Keep `execution_config()` in the supplied invocation calls. Stay offline and do not enable a tracing backend.

From the repository root, using the activated Python 3.12 environment:

```bash
python -m exercises.starters.l03
```

Before implementation, expect `STARTER_NOT_COMPLETED`. That message is deliberately not success evidence. After all TODOs are complete and checks pass, expect `STARTER_CHECKS_PASSED`. A failed assertion or exception means there is still a concrete issue to fix; do not remove the check to obtain the message.

After your attempt, compare with the independent reference and run the focused delivered-code tests:

```bash
python -m exercises.solutions.l03 --backend none
python -m pytest tests/lessons/test_l03.py -q
```

These pytest tests validate the delivered demo/reference and the starter's checker, not every line of your edited implementation. Your starter command and a review of the three functions establish your own completion. No `--live` flag or model connection belongs in this task.

## Record observed behavior

Use Jack Sparrow and `[1, 2, 3, 4]` first. With `*`, the expected answer is 24 and the expected message is `Hi Jack Sparrow, your answer is 24.` With `+`, the expected answer is 10. Then test Mei with `[-3, 0, 5]`: addition should give 2 and multiplication should give 0. Test `[-2, 3]` with `*` for a negative product, and `[7]` with `+` for a singleton.

Empty addition must return 0; empty multiplication must return 1. Try `/`, a tuple instead of a list, `[2.5]`, and a missing name. Each must raise `ValueError`, not calculate silently.

Write the observations rather than copying these expectations:

- Starter status and command used: __________
- Jack Sparrow multiplication answer and exact message observed: __________
- Addition and signed/zero results observed: __________
- Empty `+` and empty `*` results observed: __________
- Invalid request tested and exception type observed: __________
- Evidence that input fields survived and the original list did not change: __________

## Three progressive hints

### Hint 1: inspect actual values

Use dictionary `.get` to inspect fields that might be absent. A `NotRequired` output may be missing; that says nothing about runtime validation of required inputs. Check `type(item) is int` if you need to exclude booleans.

### Hint 2: choose the arithmetic identity

`sum` naturally begins at 0. `math.prod`, already imported in the starter, begins at 1. If you write multiplication manually, think about the starting value before processing an empty list. Validate operation tokens before allowing an `else` to mean multiplication.

### Hint 3: separate update from final state

Return only `answer` and `result` from the node. LangGraph retains input fields that were not updated. The builder must register `process_values` once and return the compiled executable, not itself.

## Completion criteria and stretch

You are finished when the starter prints its checked-success message, both operations satisfy all listed cases, invalid/missing inputs raise `ValueError`, the node returns only computed fields, the final state retains the inputs, and the topology has exactly one arithmetic node. Explain why no model call or graph-level branch was needed.

For an optional stretch, add your own test cases for large integers and names containing non-ASCII characters without changing the accepted operations or adding nodes. Verify exact preservation of the name. This is additional practice, not a new required task.

## References

- [Official Graph API state/update guidance](https://docs.langchain.com/oss/python/langgraph/graph-api).
- [Python 3.12 TypedDict and NotRequired](https://docs.python.org/3.12/library/typing.html#typing.TypedDict).
- [Python 3.12 math.prod and its starting value](https://docs.python.org/3.12/library/math.html#math.prod).


<!-- PAGEBREAK -->
<a id="l04"></a>
# L04 — Three-node sequential profile

## Task: build a profile in three ordered updates

Complete `exercises/starters/l04.py` after studying the two-node demonstration. Build the three-node name/age/skills exercise with the supplied validation and boundary cases. Do not use a model or tracing service.

The starter supplies the state schema, input validation, graph builder, and local checks. Your implementation work is confined to three TODO functions: `welcome`, `describe_age`, and `describe_skills`. Do not replace the graph with a single function or import the demonstration or reference solution. Keep the supplied edges and explain them below.

### Required behavior

1. `welcome` returns only `result` and `visited`. Start `result` with `<name> welcome to the system.` and reset `visited` to `["welcome"]`, even when stale generated values are present.
2. `describe_age` retains the welcome and appends ` You are <age> years old` without a final period. For age 1, use `year`. Extend the visited list with `"age"` by creating a new list.
3. `describe_skills` retains both earlier components and appends ` and you have skills in <formatted skills>.` For an empty list, append ` and you have no listed skills.` Extend the visited list with `"skills"`.
4. Preserve skill order and duplicates. One item stands alone. Two items use ` and `. Three or more use commas between earlier items and ` and ` before the last item, with no Oxford comma. Do not sort or normalize the input.
5. Never mutate the dictionary or lists passed to a node. Every node returns only the two generated keys. The final graph state must retain the original `name`, `age`, and `skills` values.

The target for Linda, 31, and `["Python", "machine learning", "LangGraph"]` is exactly:

```text
Linda welcome to the system. You are 31 years old and you have skills in Python, machine learning and LangGraph.
```

The final visited list must be `["welcome", "age", "skills"]`. There are exactly three work nodes, four total edges, and two edges between work nodes. Input validation is already complete: names must be nonblank strings, ages nonnegative integers excluding booleans, and skills a list of nonblank strings. An empty list is valid. Do not weaken those rules to make an example pass.

## Work sequence and commands

Use the prepared environment and repository-root module commands. Do not install packages or modify shared runtime files.

1. Run the baseline and record why its two results differ:

   ```bash
   python -m course_lessons.l04 --backend none
   ```

2. Run your starter once before editing:

   ```bash
   python -m exercises.starters.l04
   ```

   `STARTER_NOT_COMPLETED` is expected at this stage. A successful process exit does not mean the task passed.

3. Implement the TODO functions in order, rerunning after each change. Unfinished later functions still report incomplete work. After all checks pass, the starter prints `STARTER_CHECKS_PASSED` and the Linda message. If an assertion fails, repair your implementation, not the assertion.
4. After an independent attempt, compare with the separate reference:

   ```bash
   python -m exercises.solutions.l04 --backend none
   python -m pytest tests/lessons/test_l04.py -q
   ```

   The focused tests exercise the delivered demonstration and reference solution. They do not automatically assess edits to your starter. Use your starter checks, recorded cases, and teacher inspection as your own evidence.

## Three progressive hints

### Hint 1: inspect the prior value

List exactly which keys each function reads and writes. The age node needs the previous `result` as well as `age`. Returning only an age sentence cannot preserve the welcome, regardless of the edges.

### Hint 2: build a new value, not an in-place change

A partial update replaces each key it supplies. Construct the whole next string from the existing string plus the new clause. For the visited list, think of list concatenation producing a fresh list. The welcome node is intentionally different: it starts fresh rather than carrying stale generated data forward.

### Hint 3: separate list formatting from sentence assembly

Inside the skills node, determine the skills phrase before adding it to the existing result. Distinguish zero items, one item, and at least two items. For the last case, a slice of all but the final item and a lookup of the final item let you place `and` exactly once. This `if` belongs inside the node, not in graph routing.

## Observed results and explanations

Record actual values rather than writing “worked.” Keep these notes next to your starter or in your submitted workbook.

- **Baseline broken final:** record the complete string and identify the missing component.
- **Baseline corrected final:** record the complete string and the visited order.
- **Linda profile:** record the complete result and final visited list.
- **Ari, age 0, no skills:** record the complete result; check the `no listed skills` ending.
- **Jo, age 1, Python only:** record the complete result; check singular `year` and no extra `and` within the skill phrase.
- **Bo, age 2, Python and SQL:** record the complete result; check that no comma is needed between two skills.
- **Input preservation:** record before/after values for `name`, `age`, and `skills`; explain how you avoided list mutation.
- **Edge explanation:** write all four connections, identify the two work-node connections, and explain what would go wrong if the skills node ran before the welcome node.

## Completion criteria and stretch

You are finished when all three nodes return nonmutating partial updates, all recorded cases match the wording rules, input fields remain unchanged, the visited list proves the required sequence, and you can explain why default replacement caused the baseline bug. Inspect each function: a hard-coded Linda sentence does not meet these criteria.

Optional stretch: run a second profile through the same compiled graph, and then invoke it using a previous output as input. Predict whether any old generated text or visited items will leak. Record your prediction and actual result. Keep the same three-node topology, avoid persistence or model calls, and explain why resetting generated fields in `welcome` matters.

For API clarification, consult the official [partial-update explanation](https://docs.langchain.com/oss/python/langgraph/graph-api) and [sequential graph guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api). Their shorthand sequence builder is not required for this explicit-edge exercise.


<!-- PAGEBREAK -->
<a id="l05"></a>
# L05 — Conditional routes and two independent calculations

## Task: connect two conditional sections

Build a deterministic graph that accepts four integers and two operation strings, then returns two independent pairwise answers. The sections execute in sequence, but the second calculation must never use the first answer as an operand. Validation and branch evidence below support careful verification.

Use `exercises/starters/l05.py`. Complete exactly three focused functions: `route_first`, `route_second`, and `build_graph`. The starter already provides `PairState`, validation, four arithmetic nodes, the second router node, and acceptance checks. Do not replace the graph with one Python calculator function, import the solution, or hard-code the sample answers.

Your input fields are `number1`, `number2`, `number3`, `number4`, `operation1`, and `operation2`. Only the exact strings `+` and `-` are supported. Keep the supplied validation: actual integers are accepted, including zero and negatives, while numeric strings, floats, booleans, missing inputs, and unsupported operation tokens are rejected.

Section one computes `result1` from the first two numbers. Section two computes `result2` from the last two numbers. Preserve both results, all original input fields, and a `visited` list naming the four executed work nodes. Routing functions return labels; arithmetic nodes return update dictionaries. Current official documentation describes the conditional edge's source, path callable, and optional label-to-node map [507].

## Prepare and predict

1. Activate the P00 Python 3.12 environment and open a terminal at the repository root. Inspect the starter before editing. Run it once to confirm that unfinished work is honestly reported:

   ```bash
   python -m exercises.starters.l05
   ```

   Expected initial status: `STARTER_NOT_COMPLETED`, with a next-step message. A normal exit here does not mean the exercise passed.

2. Sketch the topology. START reaches `router1`; exactly one first arithmetic node reaches `router2`; exactly one second arithmetic node reaches END. Name the six registered work nodes on your sketch. Do not draw an ordinary outgoing edge and a conditional edge from the same router.

3. Before coding, predict the results and path for `10 - 5` followed by `7 + 2`. Record your prediction in one sentence in your notes. Then identify which input field each routing function should inspect. The two sections may reuse route labels but must have different destination maps.

## Implement and gather observations

4. Implement the two routing functions and connect the graph. Preserve the provided arithmetic and validation code. Return a compiled graph rather than the mutable builder. Use explicit START/END edges and explicit path maps.

5. Run the starter again. After every TODO is implemented correctly, the built-in checks should report `COMPLETED`, four checked operation combinations, successful independence checks, rejected unsupported operations, and a zero/negative check. A traceback or assertion failure is evidence to investigate, not a result to hide.

6. Inspect your own graph output, not just the reference solution. In a Python session, import `build_graph` from `exercises.starters.l05`, `execution_config` from `course_support.runtime`, and `graph_tracing` from `course_support.observability`. Inside `with graph_tracing("none"):` invoke your compiled graph with the required input dictionary and `config=execution_config()`. Print the returned state. To confirm executed nodes, stream the same input with `stream_mode="updates"` inside that context and record the update keys.

Use these short evidence fields; each should contain a concrete observation rather than “it worked”:

- **Baseline observation:** both result values and the exact four-name `visited` list from your implementation.
- **Combination observation:** result pairs for `++`, `+-`, `-+`, and `--`, using operands `10`, `5`, `7`, and `2` throughout.
- **Independence observation:** result pairs after changing only `number1` to `100`, then after separately changing only `number3` to `-7` in the original baseline.
- **Edge/failure observation:** the zero/negative case results, plus the exception type and field named when either operation is `*`.

7. After collecting your own evidence, compare with the independent reference and run only this lesson's focused regression tests:

   ```bash
   python -m exercises.solutions.l05 --backend none
   python -m pytest tests/lessons/test_l05.py -q
   ```

The reference source is `exercises/solutions/l05.py`; the baseline demonstration is `course_lessons/l05.py`. Pytest checks the demonstration/reference, not the correctness of your edited starter. Submit your starter and observations together. No API key, live request, dashboard, or remote trace is needed.

## Three progressive hints

### Hint 1: separate the decisions

The first routing callable reads `operation1`; the second reads `operation2`. Each returns `"addition"` or `"subtraction"`, not a dictionary or an arithmetic function call. Keep explicit rejection for any other token.

### Hint 2: map labels to the right section

The first path map targets nodes whose names end in `1`. The second targets nodes ending in `2`. The keys match routing return labels, not state keys. If a branch is unknown, check the keys first, then registered node names.

### Hint 3: preserve the middle connection

Both possible first arithmetic nodes need their own ordinary edge to `router2`. Only the second pair's arithmetic nodes finish at END. Keep result updates separate so computing `result2` does not overwrite `result1`.

## Completion criteria and stretch

The baseline must return `(5, 9)` and `visited=["router1", "subtract1", "router2", "add2"]`. With the same operands, `++`, `+-`, `-+`, and `--` must return `(15, 9)`, `(15, 5)`, `(5, 9)`, and `(5, 5)`. Changing only the first number to `100` must return `(95, 9)`; separately changing only the third number to `-7` must return `(5, -5)`. The zero/negative check uses `0 - 5` and `-7 + 0`, returning `(-5, -7)`. Both invalid-operation positions must be rejected before arithmetic. Your starter must report `COMPLETED`, retain inputs, and show exactly one selected branch in each section.

**Optional stretch:** sketch multiplication as a third route in both sections using the [official routing reference][507]. Explain which callable labels, maps, nodes, edges, and tests change. Preserve required plus/minus behavior; this extension is not assessed.



[507]: https://reference.langchain.com/python/langgraph/graph/state/StateGraph/add_conditional_edges "Official conditional-edge reference, verified 3 November 2026"


<!-- PAGEBREAK -->
<a id="l06"></a>
# L06 — Bounded loops and automatic higher/lower game

## Your task: automatic guessing, not human input

Build a LangGraph game that finds a synthetic target between 1 and 20 using automatic higher/lower feedback. The default maximum is seven guesses. The graph must also stop honestly when a smaller allowed budget is exhausted. Deterministic midpoints, validation, and a reduced-budget test are required teaching conditions; exact random output is not an acceptance criterion.

Use the separate starter at `exercises/starters/l06.py`. It does not import the answer. The reference solution is `exercises/solutions/l06.py`; consult it after attempting the task. The demonstration at `course_lessons/l06.py` teaches five bounded generations, not this game's solution. No model, API key, tracing service, `input()`, or additional package installation is needed for this prepared environment.

Run these commands from the repository root:

```bash
python -m course_lessons.l06 --backend none
python -m exercises.starters.l06
```

The unfinished starter should print `STARTER_NOT_COMPLETED` and exit successfully. That message means work remains; it is not a pass. After your three functions work, its self-check should print `STARTER_CHECKS_PASSED`. Do not replace the status message or remove assertions to make the command appear successful.

## Implement three focused functions

1. **Validate and reset in `reset_game`.** Accept a nonblank string `player_name`, an integer `target` from 1 through 20, and an integer `max_attempts` from 1 through 7. Reject booleans for the two integer fields. Invalid configuration must raise `ValueError` before any guessing. Preserve these three configuration values. Reset `lower=1`, `upper=20`, `guesses=[]`, `attempts=0`, `hint=""`, and `status="playing"`, even if stale derived values were supplied.
2. **Guess in `guess_node`.** Compute the integer floor midpoint of the inclusive bounds. Do not consult the target to choose it. Return a new guesses list with that midpoint appended and increase attempts by one. Do not mutate the incoming list, change bounds, or increment attempts elsewhere.
3. **Compare in `feedback_node`.** Read the latest guess. Equality means hint `correct` and status `won`. A smaller guess means hint `higher` and the new lower bound is the failed guess plus one. A larger guess means hint `lower` and the new upper bound is the failed guess minus one. After a miss, status is `lost` if attempts has reached the budget, otherwise `playing`. Correctness takes priority even on the last allowed attempt.

Keep the supplied topology: `START → reset → guess → feedback`, with a conditional route from feedback back to guess only while status is `playing`. Both `won` and `lost` route to `END`. Do not add an unconditional feedback-to-guess edge. The provided route returns labels; your node functions return partial update dictionaries.

## Run and record observable results

Rerun `python -m exercises.starters.l06` after each TODO. For additional experiments, import your starter's `build_graph` and `new_game`. Pass `config=execution_config()` to `invoke` or `stream`. Wrap interactive experiments in `with tracing_context(enabled=False):` using the import from `langsmith`, so ambient tracing remains disabled.

Record the following fields using observed state, not copied expected text:

- Target 17, budget seven: guesses ___; attempts ___; final hint ___; status ___. Explain one bound change: ___.
- Target 20, budget two: guesses ___; final inclusive bounds ___; hint ___; status ___. Did a third guess run? ___.
- Target 15, budget two: attempts ___; final status ___; why success takes priority ___.
- Every target 1–20, default budget: number successful ___; maximum attempts observed ___; any repeated guess within one game ___ .
- Dirty input with target 10, guesses `[999]`, attempts `-8`, and wrong bounds: final guesses ___; attempts ___; original caller list unchanged ___ .
- Invalid target 0 and invalid budget 8: exception type ___; why neither should start guessing ___ .

For the first case, expect `10, 15, 18, 16, 17` and a five-attempt win. For the two-attempt exhaustion case, expect `10, 15`, bounds 16–20, hint `higher`, and `lost`. The final-attempt case must win. These are predictions of the specified algorithm, not execution evidence.

## Three progressive hints

### Hint 1: isolate fresh-run fields

Configuration identifies the game; derived fields describe its progress. Reset only the derived fields. Use exact integer type checks where accepting `True` as target one would be misleading.

### Hint 2: separate choosing from judging

The midpoint needs only `lower` and `upper`. The feedback node needs the target. Exclude a missed midpoint from the next inclusive interval; otherwise the same candidate can survive narrowing.

### Hint 3: classify success before exhaustion

Write the equality branch first. Only a miss should be classified by the attempt cap. The router then reads status without changing it. A recursion-limit exception is not an alternative way to report a loss.

## Completion criteria and comparison

Your implementation must pass the starter self-check without deleting checks, win for all 20 valid targets within seven guesses, produce both required exit reasons, and preserve input lists. For each miss, the new bounds must still contain the target, exclude that guess, and strictly shrink. Check this by streaming updates if your result is unexpected. Invalid configuration must fail before guessing. An ordinary run must not end with `GraphRecursionError`.

After your attempt, compare with:

```bash
python -m exercises.solutions.l06 --backend none
python -m pytest tests/lessons/test_l06.py -q
```

Those focused tests validate the delivered demonstration and reference solution, not your edited starter. Record one difference between your implementation and the reference, with its behavioral effect: ___.

## Optional design extension — not part of the validated execution set: make narrowing inspectable

Without changing required behavior, record each pre-guess interval and post-feedback interval in your own notes or a separate in-memory history field. Assert that every miss shrinks the interval and retains the target. Do not add network calls, an interactive player, or a larger budget. Explain why the execution safety guard counts graph super-steps rather than game guesses. The [official loop guide](https://docs.langchain.com/oss/python/langgraph/use-graph-api), verified on 3 November 2026, explains that distinction.


<!-- PAGEBREAK -->
<a id="l07"></a>
# L07 — Anthropic stateless bot

## Assignment: a stateless help-desk session

Build a bounded session controller around a single-node model graph. Your goal is to prove which messages are sent, not to obtain a particular Claude sentence. Allow approximately 20 minutes after the guided practice.

Work in `exercises/starters/l07.py`. The baseline demonstration is `course_lessons/l07.py`; the teacher reference is `exercises/solutions/l07.py`. Do not import either implementation into your starter. You may use shared runtime helpers. Use synthetic data only; credentials do not belong in state, worksheets, or screenshots.

Start from the repository root in the prepared environment:

```bash
python -m exercises.starters.l07
python -m pytest tests/lessons/test_l07.py -q
```

The starter initially reports `STARTER_NOT_COMPLETED`. Its exit code is not a passing grade. The focused test file checks the delivered demo and reference solution with explicit offline doubles; it does not automatically assess your modified starter. Use the learner-side harness below for that.

## Required functions and behavior

1. Implement `classify_entry(raw)`. Reject non-string entries with `TypeError`. Return `exit` when `raw.strip().casefold()` is `exit`, `skip` for whitespace-only text, and `send` otherwise. Normalize only for these decisions; preserve original submitted text.
2. Implement `build_bot(model)`. Create `START → respond → END`, without history, tools, or a checkpointer. Its input is `{'prompt': raw}`. Reject blank/exit prompts even if someone bypasses the session controller. Construct exactly one new `HumanMessage`; invoke the injected model with the node's `config`. Require an `AIMessage` with nonempty displayable text. Return `reply`, `sent_messages` containing just the original prompt, and `usage` from `usage_metadata`, using `{}` if absent. Use `message_text`, not a dump of all content blocks.
3. Implement `run_session(graph, entries, *, max_entries=6)`. Return a dictionary containing `turns`, `skipped`, `inspected`, and `stop_reason`. Reject noninteger or nonpositive budgets with `ValueError`, including booleans. Inspect at most that many raw entries; blank and exit entries consume budget. Count each inspected entry, skip blanks, and stop before invoking on exit. Invoke with fresh state and `execution_config()` for each sent prompt. Store results only for the report, never as later input. Stop reasons are `exit`, `limit` when budget is reached, and `exhausted` when the source ends earlier. Reaching the budget takes precedence over detecting coincident source exhaustion.

Use exactly this assessment sequence:

```python
entries = [
    "  ",
    "My name is Mira. Say hello briefly.",
    "What is my name?",
    " ExIt ",
    "This must never be sent.",
]
```

## Check your starter without a paid request

After completing the TODOs, paste the following into a Python shell from the repository root. This is an explicit offline double, not a live provider and not evidence of live integration. It supplies test responses only; it does not contain your solution's graph or controller logic.

```python
from langchain_core.messages import AIMessage, HumanMessage
from exercises.starters import l07 as learner

class OfflineWorkbookModel:
    def __init__(self):
        self.requests = []

    def invoke(self, messages, config=None):
        assert len(messages) == 1
        assert isinstance(messages[0], HumanMessage)
        assert config["recursion_limit"] == 40
        self.requests.append([m.content for m in messages])
        return AIMessage(content="OFFLINE TEST response")

entries = ["  ", "My name is Mira. Say hello briefly.",
           "What is my name?", " ExIt ", "This must never be sent."]
model = OfflineWorkbookModel()
graph = learner.build_bot(model)
report = learner.run_session(graph, entries)
assert model.requests == [[entries[1]], [entries[2]]]
assert report["inspected"] == 4 and report["skipped"] == 1
assert report["stop_reason"] == "exit" and len(report["turns"]) == 2
assert all(t["reply"].strip() and t["usage"] == {} for t in report["turns"])
assert [t["sent_messages"] for t in report["turns"]] == model.requests
```

Also test `[]` for `exhausted`, two blanks with `max_entries=2` for `limit`, and `"  Hello  "` for preservation of spaces. Check that a zero budget raises `ValueError`. Explain why reusing the same `graph` in these tests does not introduce context into its requests.

## Three progressive hints

### Hint 1: separate decisions from payloads

Use a normalized temporary value to recognize exit. Keep `raw` unchanged for `HumanMessage(content=raw)`. Do not make a model call to decide whether an entry is blank.

### Hint 2: separate configuration from state

Accept `config: RunnableConfig` in the nested node and pass it to `model.invoke`. The session invokes the graph with `execution_config()`. A key, model object, or callback is not a state field.

### Hint 3: bound consumption, not just successful turns

`islice(entries, max_entries)` can cap inspected entries without consuming an extra iterator item. Increment `inspected` before handling skip/exit. A loop `else` can distinguish normal exhaustion/budget completion from an exit `break`.

## Record observed results

Record the actual request lists, inspected count, skipped count, turn count, and stop reason from your harness in a short paragraph. Then record your empty-source and budget-limit observations. State explicitly that these are offline-double results. Add one sentence predicting the second live request's context without predicting its exact answer.

For an authorized real comparison, the delivered implementations are runnable with:

```bash
python -m course_lessons.l07 --live --backend none
python -m exercises.solutions.l07 --live
```

Both make two logical model calls using synthetic prompts. Their output validates those delivered implementations, not your starter. Record whether you actually ran them, any real error, and available usage metadata; do not invent a passed live result. See [ChatAnthropic](https://docs.langchain.com/oss/python/integrations/chat/anthropic) for message/usage representation and [Anthropic's stateless contract](https://platform.claude.com/docs/en/build-with-claude/working-with-messages).

## Completion criteria and stretch

Completion requires all three functions implemented independently; exact two one-message payloads for the assessment sequence; one skip, four inspected entries, two turns, and exit; no processing after exit; correct blank/limit/exhausted handling; preserved raw text; callback forwarding; nonempty textual replies; and no history or credentials in state. Demonstrate these with recorded evidence rather than changing the starter's status string.

For a stretch task, add learner-owned offline tests for a non-string entry, an empty `AIMessage`, a simulated provider exception, and a source iterator whose unread tail remains untouched after the cap. Keep all failures honest: no canned answer fallback in production. Do not add memory; that deliberately changes the problem and belongs to L08/U1.


<!-- PAGEBREAK -->
<a id="l08"></a>
# L08 — Conversation history and logging

## Your task: bounded prompt, complete transcript

Build a text-chat graph that sends a bounded recent window to the model while retaining a complete process-local transcript. Use Anthropic through the shared runtime, not an OpenAI client or a canned live response.

Work in `exercises/starters/l08.py`. The independent instructor reference is `exercises/solutions/l08.py`; consult it only after attempting the task. Do not import either that reference or `course_lessons/l08.py` to replace your implementation. The delivered demonstration and reference have different state-update strategies, even though both carry history between calls.

Before editing, run:

```bash
python -m exercises.starters.l08
```

Expect `STARTER_NOT_COMPLETED` and a successful process exit, with no model construction. This indicates an unfinished scaffold, not a passed exercise. Implement only the three TODO functions; the provided runner contains the acceptance scenario and safe file-writing behavior.

## Implement the three functions

1. **Select model input.** `select_prompt(history, max_pairs=1)` must accept alternating human/AI pairs followed by one pending human. Return a new list with the newest `max_pairs` complete pairs plus that human, without mutating the input. Zero keeps just the pending human. Raise `ValueError` for negative, Boolean, or noninteger limits; empty/even/nonalternating histories; and AI tool calls. This intentionally excludes system/tool conversations.
2. **Build the graph.** `build_graph(model, max_pairs=1)` must validate the limit at construction, compile `START → respond → END` with `MessagesState`, and invoke the injected model only inside the node. Forward the node's config. Return only the new `AIMessage` as a delta. Reject a wrong response role or tool call with `TypeError`, and empty visible text with `ValueError`. Do not use checkpoints or mutate state. Compilation with `model=None` must work for the starter readiness check.[809]
3. **Export full history.** `format_transcript(history)` must format every message as `<role>:\n<text>\n`, using `Human` or `AI`, and join entries with one extra newline. Return an empty string for an empty list; raise `TypeError` for other roles. Use `message_text` without correcting spelling or stripping stored content. Do not open files inside this function.

## Follow the fixed scenario

The provided runner introduces `Hi, my name is Mira. Please acknowledge briefly.` Its second human input is exactly:

```text
gud morning!
What name did I give you?
```

The third is `Reply with one short greeting.` Keep `max_pairs=1`. The runner should send 1, 3, then 3 messages, while retaining 2, 4, then 6. Its separate fourth call starts with no prior history, yielding two messages. Do not include that fresh conversation in the six-message log.

The second answer must mention Mira. Wording otherwise varies. The third prompt must exclude the first human message by ID, but you must not claim this guarantees forgetting: a retained AI answer can repeat Mira. A pair cap is not a token cap, nor a bound on full-history memory or log size.[810] Anthropic content can be block-structured, so use the shared text helper for display/export.[811]

## Test and record observations

For a small offline check, start `python` and paste this probe after implementing the TODOs. `WorkbookChatDouble` is explicitly a test double, not Anthropic evidence:

```python
from langchain_core.messages import HumanMessage, AIMessage
from langsmith import tracing_context
from exercises.starters import l08

class WorkbookChatDouble:
    def __init__(self):
        self.calls = []
    def invoke(self, messages, config=None):
        self.calls.append(list(messages))
        return AIMessage(content="offline reply")

model = WorkbookChatDouble()
graph = l08.build_graph(model, max_pairs=1)
history = []
with tracing_context(enabled=False):
    for text in ["first", "gud morning!\nraw", "third"]:
        history = l08.run_turn(graph, history, text)
assert [len(call) for call in model.calls] == [1, 3, 3]
assert len(history) == 6
assert "Human:\ngud morning!\nraw\n" in l08.format_transcript(history)
```

Exit the interpreter. Run the focused delivered-code tests:

```bash
python -m pytest tests/lessons/test_l08.py -q
```

Those checks validate the delivered demo/reference and starter status; they do not automatically grade your edited TODOs. When authorized for paid calls, validate your implementation:

```bash
python -m exercises.starters.l08 --live --backend none
```

For comparison, the instructor reference command is:

```bash
python -m exercises.solutions.l08 --live --backend none
```

Record actual observations, not invented replies: prompt counts **[observed]**; full-state counts **[observed]**; second answer **[observed]**; exact two-line input preserved **[yes/no and location]**; reported `log_path` **[observed]**; fresh-history count **[observed]**. Open `bounded-conversation.txt` at that path and verify three human and three AI entries. Default output directories are unique; a reused directory must not silently overwrite an existing log.

## Three progressive hints

### Hint 1: count the pending turn separately

An input window has `2 * max_pairs + 1` entries at most. Before selecting, validate the full input's shape. Python's `bool` is an `int` subclass, so an integer check alone accepts `True` accidentally.

### Hint 2: separate invocation input from node update

Without checkpoints, every invocation needs the caller's carried history. Within that invocation, `MessagesState` already preserves it through its reducer. Return only the new reply from the node; do not rebuild old messages with new IDs.

### Hint 3: choose the correct source for the log

The prompt window and full returned history are different lists. Export the full list and preserve the raw human string. Validation can inspect stripped text without storing the stripped version.

## Completion and stretch

Complete the task only when the implemented starter demonstrates the required counts, full six-message export, exact raw input, role labels, two-message reset simulation, and honest error behavior. Explain why no saved transcript is automatically reloaded. U1 is the separate durable-checkpoint lab; do not add persistence here.

For a stretch task, compare `max_pairs=0` and `2` using the offline double. Predict the three prompt counts before running, then discuss how a token-aware policy would also preserve valid message structure. Do not invoke a remote token-counting API as an “offline” check or claim trimming erases information from retained replies.

## References


- [809: LangGraph Graph API: MessagesState and reducer updates](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [810: LangGraph memory: trimming model input versus retained state](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [811: ChatAnthropic: messages, content blocks, and token counting](https://docs.langchain.com/oss/python/integrations/chat/anthropic)

[809]: https://docs.langchain.com/oss/python/langgraph/graph-api "LangGraph Graph API: MessagesState and reducer updates"
[810]: https://docs.langchain.com/oss/python/langgraph/add-memory "LangGraph memory: trimming model input versus retained state"
[811]: https://docs.langchain.com/oss/python/integrations/chat/anthropic "ChatAnthropic: messages, content blocks, and token counting"


<!-- PAGEBREAK -->
<a id="l09"></a>
# L09 — ReAct arithmetic tool loop

## Your task: an audited arithmetic runner

Build a small, bounded tool-using agent and prove what it executed. Use L08 message concepts and the baseline demonstration before starting. Plan approximately fifty minutes for the independent implementation within the lesson's broader practice allocation.

Your editable starter is `exercises/starters/l09.py`. The independent reference is `exercises/solutions/l09.py`; keep it closed until review. The baseline is `course_lessons/l09.py`, and focused offline tests are `tests/lessons/test_l09.py`. Do not solve the task by importing either completed implementation. The starter already provides the integer tools, state schema, prompt, error-observation handler, CLI readiness probe, and three-case acceptance harness.

An unchanged starter must print `STARTER_NOT_COMPLETED` and exit successfully. That message is intentionally not a passing exercise result. The readiness probe detects unfinished TODOs without making model calls; it is not a substitute for testing your implementation.

## Implement three focused functions

1. Complete `route_next(state)`. Require the last message to be an `AIMessage`. Reject a different role with `TypeError`, malformed `invalid_tool_calls` with `ValueError`, and a batch above three calls with `AuditLimit`. Return `"tools"` for valid calls, otherwise END. Routing must not execute arithmetic.
2. Complete `make_agent(model, *, max_model_calls=4)`. Accept budgets from one to ten, rejecting values outside that range. Bind the supplied tools to the injected model. Build `START → model`, a conditional tools/END route, and `tools → model`. The model node must prepend the system instruction, include accumulated messages, forward its `RunnableConfig`, return only the new reply and incremented count, and raise `AuditLimit` before any invocation beyond the budget. Use `ToolNode` with the supplied validation handler. Request invocation already uses `execution_config()`; preserve it.
3. Complete `collect_audit(state)`. Return `model_calls`, `tool_calls`, `audit`, and `final_text`. Each audit row must contain `call_id`, `tool`, `args`, `result`, and `status`. Match results by call ID, even if a batch's results arrive in reverse order. Keep error results marked as errors. Raise `ValueError` for empty/duplicate call IDs, orphan/missing results, a non-tool message interrupting a pending batch, or a missing, empty, or still-tool-calling final AI answer. Never generate a result because you know the expected arithmetic.

## Run and record the three exact cases

From the repository root, with the project environment active:

```bash
python -m exercises.starters.l09
python -m pytest tests/lessons/test_l09.py -q
```

The supplied focused tests validate the baseline and independent reference solution with explicit offline model doubles. They do **not** automatically grade your edited starter. Inspect their scripted message sequences and apply the same cases to your injected-model builder during review. No API key is needed for this offline inspection; do not replace the actual live model factory with a canned responder.

After instructor authorization, run your implemented starter:

```bash
python -m exercises.starters.l09 --live --backend none
```

This makes real paid Anthropic requests. Without `--live`, a completed model-based starter should refuse model creation rather than claim an offline success. The provided harness checks these exact requests:

- **Compound:** “Subtract 5 from 18. After seeing the result, multiply that result by 4.” Observe successful results `13` then `52`, in separate tool rounds. The first call must be `subtract(a=18, b=5)`. The later multiplication must use `13` and `4`, and the final answer must include `52`.
- **Independent:** “Compute 9 + 6 and separately 8 * 3.” Observe successful results `15` and `24` from add and multiply. One shared batch or separate valid batches are both acceptable within four model calls. The final answer must include both results.
- **Greeting:** “Say a friendly hello. Do not calculate anything.” Observe a nonempty final answer, zero tools, and one model call.

Record evidence, not private reasoning. For the compound case, note both call IDs, their matching result IDs, and the multiplication arguments: ______. For the independent case, note the chosen batching pattern and model-call count: ______. For the greeting, record the tool count and final-message role: ______. For an offline failure case, record whether it produced an error observation or a budget exception, and why: ______.

## Three progressive hints

**Hint 1 — control flow:** inspect structured `tool_calls`, not message text. The route returns a label; `ToolNode` executes the registered functions. The model must receive each observation on its next turn.

**Hint 2 — state updates:** `add_messages` merges the new message update. Return `[response]`, not a rebuilt history. Initialize the counter at zero and check it before each model invocation, not after an unwanted fifth call.

**Hint 3 — auditing:** keep a dictionary of pending calls keyed by ID and a set of IDs already used. Remove a pending call when its result arrives. A later AI message is invalid while any pending entries remain. Keep failed observations in your rows instead of converting them into numeric successes.

## Completion, review, and stretch

Complete only when all three live cases satisfy the harness and an instructor has reviewed offline malformed-call, unknown-tool, missing-result, reversed-batch, and repeating-model behavior. A repeating double must stop at the configured model-call budget; a tool error may be explained or corrected, but must never be counted as a successful calculation. Exact model sentences and independent batching need not match the reference.

After assessment, compare with:

```bash
python -m exercises.solutions.l09 --live
```

For a stretch, test negative and zero operands through your injected-model interface. Demonstrate that three minus eight returns a negative result and that a product with zero stays zero. Do not add division or new external services.

## Reference to consult

The [official graph quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart) explains the tool loop, while the [Graph API message guide](https://docs.langchain.com/oss/python/langgraph/graph-api) explains ID-aware updates. These current-API references support the exercise; the stricter audit and execution budgets are part of this course.


<!-- PAGEBREAK -->
<a id="l10"></a>
# L10 — Human–AI Drafter collaboration

## Your task: workshop notice and honest save recovery

This task applies a drafting workflow in which a complete email is revised through human feedback and saved only after an authorized successful write. Prerequisite: L09. Allow 90 minutes including guided practice; use synthetic data only.

Build a process-local Drafter that revises a complete email, fails safely on an occupied filename, then saves after new human feedback. Assess orchestration and file evidence, not exact wording. Persistence, voice, GUI, retrieval, and durable interrupts are outside this task; U2 adds safer state and approval/resume.

Implement `exercises/starters/l10.py` without importing the baseline `course_lessons/l10.py` or reference `exercises/solutions/l10.py`. Leave the reference closed during your first attempt.

## Exact scenario and implementation boundary

The supplied runner already provides the following human turns. Keep the scenario and its acceptance checks intact.

1. Draft an email to **Elena** postponing the training workshop. Initially propose `17 November at 09:00 Singapore time` and sign **Arun**. Call `update` with the entire email, then show the draft without saving.
2. Revise the schedule to the literal phrase `18 November at 14:30 Singapore time`. Remove `17 November` and `09:00`; preserve Elena and Arun. Put a blank line before the closing. Update the entire document again and wait.
3. The runner creates `workshop_taken.txt` with the exact text `Existing classroom file: preserve me.` followed by a newline. Request a save to this occupied name. It must fail without changing that file, revising the document, or claiming completion. Explain the failure and wait rather than choosing a new filename automatically.
4. After new human feedback, save the unchanged reviewed email as `workshop_notice.txt`. End immediately after the successful save tool result. Start a separate empty session with `write an email`; obtain clarification without a tool call, document update, or file write.

Implement only the three marked functions. In `make_tools`, define decorated `update(content: str)` and `save(filename: str)` tools closed over the supplied session. Reject blank drafts, finished sessions, unauthorized saves, and empty-document saves. Count successful updates only. Use the shared `safe_write_text` helper; set `saved_path` only after it returns.

In `after_tools`, return `end` when a real saved path exists or the four-model-call budget is exhausted; otherwise return `agent`. In `build_graph`, bind the tools, implement agent and tools nodes, preserve callbacks/configuration, and compile conditional routes. Reject unexpected multi-call batches without executing any member, but return an error for every call ID. Convert expected validation and filesystem exceptions into error `ToolMessage` results. The supplied host driver resets save permission and reports budget exhaustion.

Current model documentation distinguishes requesting a tool from executing it. A `ToolMessage` must match the request ID; tool availability does not force use. [1021]

## Run commands and collect evidence

From the repository root, with the prepared environment activated:

```bash
python -m exercises.starters.l10
python -m pytest tests/lessons/test_l10.py -q
```

The untouched starter prints `STARTER_NOT_COMPLETED` and exits successfully without a model request or fake pass. Focused tests validate the demonstration/reference using named offline doubles, not your edited starter.

After implementation, run your starter with authorized real calls:

```bash
python -m exercises.starters.l10 --live --backend none
```

For comparison after your attempt:

```bash
python -m course_lessons.l10 --live --backend none
python -m exercises.solutions.l10 --live
```

Use the default unique directory or a fresh `--output-dir`. Never disable collision protection to repeat a run. Inspect facts and state rather than exact prose. `--backend none` still sends model input to Anthropic.

Record these observed results in your working notes:

- **Draft revision:** record the initial and revised schedule, retained recipient/sender, revision count, and whether the closing has a preceding blank line.
- **Collision:** record the error type, `saved_path` value after failure, and the unchanged contents of `workshop_taken.txt`.
- **Recovery:** record the actual final path and the result of comparing its complete UTF-8 text with the revised in-memory document.
- **Clarification:** record the assistant's question, tool-result count, content length, and saved-path state for the new empty session.

## Three progressive hints

### Hint 1: separate history from the draft

`messages` is reducer-managed graph state, while the document is in the supplied process-local session. Return only new messages from nodes. At the next host invocation, pass the previous returned history once. Replacing a complete document is easier to verify than applying an ambiguous prose patch.

### Hint 2: implement truth before routing

Make the file writer the authority. A `FileExistsError` must reach the tools node, which produces `status="error"` with the same call ID. Do not set the path in advance, in `finally`, or in an exception branch. Then let the router inspect actual session state, not words such as “saved” in the assistant response.

### Hint 3: inspect the last message

After `agent`, route to tools only if the newest `AIMessage` has tool calls. After a successful save, do not call the model again. After an update or expected error, another model response can show the draft or explain the error. Forward the received `RunnableConfig` to both model and tool invocation; use `execution_config()` when entering the graph.

## Completion and stretch

You are complete when the three functions are implemented independently; two successful whole-document updates retain the required facts; the occupied file remains byte-for-byte unchanged; failed saving leaves `saved_path=None`; a new human request saves the latest draft to `workshop_notice.txt`; execution stops on that successful tool result; and the separate vague request uses no tool. Also demonstrate rejection of an unsafe basename or missing save permission, and explain why this process-local session is not durable interrupt/resume. Preserve your notes and actual artifacts as evidence.

For a stretch task, drive exactly three manually entered feedback turns through `take_turn`, displaying `session.content` after each. Keep the turn count bounded and retain the same save guards. Do not add an unbounded terminal loop or claim checkpoint persistence. Report which behavior depends on the model and which behavior is enforced by Python.

## References


- [1021: Official LangChain tool requests, execution loops, and matching result IDs](https://docs.langchain.com/oss/python/langchain/models)

[1021]: https://docs.langchain.com/oss/python/langchain/models "Official LangChain tool requests, execution loops, and matching result IDs"


<!-- PAGEBREAK -->
<a id="l11"></a>
# L11 — Local-embedding Chroma RAG

## Your task: produce an evidence-gated answer card

This exercise develops a simpler retrieve-first topology than the model-selected retrieval loop. Build `START → retrieve → generate or abstain → END`. Explain why this guarantees a search happens without asking a model to select a tool. Budget approximately 45 minutes for implementation, followed by evidence review.

Use the original synthetic teaching document `data/rag_teaching_handbook.pdf`. Read its three pages first. Your supported question is: **“How long is the equipment loan, and what renewal is allowed? Use digits.”** Your unsupported question is: **“What is the exact equipment late fee in dollars?”** Do not invent any amount, substitute an external policy, or answer from general knowledge. Source/page citations must refer to the actual teaching PDF.

Start in `exercises/starters/l11.py`. It contains three independent TODO functions and no import of the reference implementation. The reference is `exercises/solutions/l11.py`; use it after making your own attempt. The demonstration in `course_lessons/l11.py` is a different architecture, not your exercise solution.

## Implement three functions

1. **`format_evidence(hits)`** returns a string. For each hit, write `[source p.page]`, a newline, and its text. Separate hits with blank lines. Return an empty string for no hits. Use the already 1-based `page`; never derive it from the chunk position.
2. **`build_graph(model, store, *, search_fn=search)`** returns a compiled graph. Validate a nonblank string question before searching. Retrieve the original question with `k=3`. Route empty hits to an abstain node that sets `answer="NOT_IN_DOCUMENT"`, `status="not_in_document"` and `sources=[]`, without invoking the model. Route nonempty hits to generation. Pass labeled evidence and the question to the injected model, instructing it to use only that evidence, cite `[rag_teaching_handbook.pdf p.N]`, use digits, and output exactly `NOT_IN_DOCUMENT` for an unspecified fact. Forward the runnable config to `model.invoke`. Both branches end at END.
3. **`validate_card(result)`** returns only `question`, `answer`, `status` and `sources`. Accept only `grounded` or `not_in_document`. An abstention needs the exact sentinel and no sources. A grounded answer needs nonempty evidence and at least one citation; every cited source/page must exist among retrieved hits. Its sources must be the sorted, deduplicated inventory of retrieved source/page pairs. This inventory lists available evidence, not proof every page was used. Reject uncited or fabricated-page answers.

Keep raw hits in graph state so you can inspect them before producing the small public card. You may reuse `course_support.retrieval`; do not replace its real ONNX embedding with a fake vector or keyword search. For normal runs, obtain the real Anthropic model from the shared runtime. Explicitly named doubles are for offline tests only.

## Run and record meaningful observations

From the repository root in the prepared Python 3.12 environment:

```bash
python -m exercises.starters.l11
python -m pytest -q tests/lessons/test_l11.py
python -m course_lessons.l11 --live --backend none
python -m exercises.solutions.l11 --live
```

The starter initially exits successfully with `STARTER_NOT_COMPLETED`; that is a deliberate unfinished state, not a pass. The delivered test file checks the demonstration and reference, not your edited starter automatically. Add equivalent learner checks that import your starter's functions. To run your own completed graph, use `get_model(live=True)`, `output_directory`, `prepare_store`, and `execution_config()` in a small local harness, following the demonstration's CLI pattern. Do not paste credentials into the starter or hardcode a model name.

The live commands incur real Anthropic usage. Initial embedding computation can download the local model. An offline test pass does not verify embedding quality or Anthropic access. Chroma telemetry is disabled; retain the default no-tracing backend until you deliberately choose a synthetic-data tracing exercise.

Record these observations in concise sentences, not just “worked”: **Supported evidence:** the actual supporting sentence and page. **Supported card:** durations found, citation accepted, and the source inventory. **Missing fact:** why the nearest returned passages do not provide a dollar amount. **Empty branch:** model invocation count observed with an explicitly named empty-store double. **Failure check:** exception observed for an uncited answer or page 99. Include your commands and test count without including secrets.

## Three progressive hints

### Hint 1 — keep labels attached

The retrieval helper returns dictionaries with `id`, `text`, `source` and `page`. Build formatting from those fields directly. An empty iterable joined with a separator already gives an empty string. Avoid a hardcoded citation unrelated to the hit.

### Hint 2 — route before generating

After the retrieve node, a conditional route can examine `state["hits"]`. Only the nonempty branch should contain `model.invoke`. Test the empty branch with a named model double that records calls, then assert that its call list remains empty. A nonempty list alone cannot establish answerability.

### Hint 3 — compare pairs, not prose

Build a set of `(source, page)` pairs from hits. Extract citations from the answer and compare every pair against that set. Sort and deduplicate sources deliberately so repeated chunks from one page produce one inventory entry. This checks provenance, not semantic entailment.

## Completion criteria and stretch

Complete means both branches terminate, a blank question is rejected, empty evidence skips the model, the supported answer contains **7**, **3** and a page-2 citation, the fee answer is exactly `NOT_IN_DOCUMENT`, and fabricated/absent citations are rejected. Your card has exactly four public keys and truthful status. Show offline evidence for routing and validation plus human inspection of a real generated answer. Do not replace variable wording with a memorized exact supported sentence.

For a stretch task, try three paraphrases of the supported question and one catering question. Record retrieved pages before judging answers, then compare `k=1` and `k=3` in your own harness. Explain one observed trade-off without claiming a universal optimal k. Do not alter the shared index specification mid-run or claim these few questions establish production reliability.

## Reference

The [official recursive splitter guide](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter) explains character sizing. The [Chroma embedding guide](https://docs.trychroma.com/docs/embeddings/embedding-functions) explains the real local default model and its initial download. Use the student chapter for the full implementation notes and troubleshooting.


<!-- PAGEBREAK -->
<a id="u1"></a>
# U1 — Thread memory and durable SQLite checkpoints

## Your task: recover three travel notebooks

**SUPPLEMENTARY PRACTICE.** This exercise extends the conversation-history concepts from L08 with durable SQLite checkpoints. Allow about 18 minutes for the first implementation, then use review time to investigate failed assertions.

Build a small travel notebook that stores three logically isolated conversations in one local SQLite file. The important outcome is not a polished answer: it is recovery after a real connection close, with evidence that each thread receives only its own human inputs. Use synthetic destinations only. A checkpoint database contains conversation data and needs protection even when tracing is off.

Your starter is `exercises/starters/u1.py`. Your teacher's independent reference is `exercises/solutions/u1.py`; do not import it or the demonstration into your work. The three TODOs are deliberately separated so you can test graph construction, invocation, and persistence orchestration independently.

## Commands and baseline observations

From the repository root, with the prepared environment active:

```bash
python -m exercises.starters.u1
python -m pytest -q tests/lessons/test_u1.py
python -m course_lessons.u1 --live --backend none
```

The unmodified starter must exit successfully with `STARTER_NOT_COMPLETED`. That message is not a passing assessment. After implementing its TODOs, rerun the same starter command: it exercises your functions with the explicitly named `StarterDestinationDouble` in a temporary SQLite file and labels its output `OFFLINE_SELF_CHECK_ONLY`. The temporary file is removed afterward; use the live reference for a retained comparison artifact. The focused tests exercise the delivered demonstration and reference solution, not your edited starter. The live reference command, for comparison after attempting the task, is:

```bash
python -m exercises.solutions.u1 --live
```

This reference makes five real Anthropic calls. The project-code demonstration makes four. Neither command should be described as offline. If the optional SQLite dependency is skipped, arrange environment setup before claiming persistence completion.

## Implement the three functions

1. Complete `build_notebook(model, checkpointer)`. Use `MessagesState`, one response node, and explicit `START`/`END` edges. Pass `NOTEBOOK_RULE` followed by the restored messages to the injected model, forwarding `config`. Require an `AIMessage` response. Return only that new message and compile with the supplied checkpointer.
2. Complete `ask(graph, thread_id, text)`. Reject non-string or whitespace-only IDs and text with `ValueError`, before graph invocation. For valid text, preserve its exact characters. Submit one new `HumanMessage` with `config=execution_config(thread_id)`; do not resubmit the existing history.
3. Complete `run_lab(model, database)`. Require a new database path, raising `FileExistsError` for an existing file. Create its parent directory. Import `SqliteSaver` from `langgraph.checkpoint.sqlite`, then use its `from_conn_string` context manager for both connection lifetimes.[1221]

In the first context, send `My destination is Kyoto. Remember it.` to `trip-a` and `My destination is Oslo. Remember it.` to `trip-b`. After each turn, require two messages and a completed snapshot. Save the snapshot's checkpoint ID. Exit the context completely.

In the second context, reopen the **same file** and build a **new graph**. Before recall, require each thread to have its original two messages, no pending work, and its original checkpoint ID. Ask `What is my destination?` in `trip-a`, `trip-b`, and new `trip-c`. Do not seed the third thread with a city.

Require the first two answers to include their own city and exclude the other city. Require the third to include `UNKNOWN` and neither city. Generated wording may vary: compare case-insensitive city inclusion, not an entire model sentence. Verify `trip-a`'s human texts are exactly its Kyoto introduction and question; `trip-b`'s are exactly its Oslo introduction and question; `trip-c` has only the question. Final total-message counts must be `{"trip-a": 4, "trip-b": 4, "trip-c": 2}`.

Return a JSON-serializable dictionary with `database`, `closed_and_reopened`, `recovered_checkpoint_ids_match`, `thread_isolation`, `message_counts`, `answers`, and `model_calls` equal to 5. Set success flags only after assertions pass. Keep model construction out of these functions so offline tests can inject a double.

## Three progressive hints

### Hint 1: separate responsibilities

The reducer merges messages, the saver stores state, and configuration selects the thread. A global conversation list would defeat this separation. Look at the type of the node's output: it is an update dictionary, not a replacement graph or a text answer alone.

### Hint 2: prove restoration before another call

Use `graph.get_state(execution_config(thread_id))` inside the reopened context. Its `values`, `next`, and `config` let you inspect the state without another model request. Check the saved checkpoint ID before sending a new question, because a completed new call creates newer checkpoints.[1222]

### Hint 3: isolate inputs as well as answers

Select human messages by `isinstance(item, HumanMessage)` and compare their text to the exact expected list. Count both human and AI messages. If an unrelated city appears, investigate reused IDs, shared lists, or manually supplied history before blaming SQLite.

## Record evidence and check completion

Record your database path and the two recovered checkpoint-ID comparisons. Note the final counts for `trip-a`, `trip-b`, and `trip-c`, and describe the exact human inputs seen in each thread. Record whether your evidence used offline doubles or real Anthropic, including the command used; do not treat one as proof of the other.

Completion requires all three functions, an actual closed/reopened file, matching pre-recall snapshot IDs, counts 4/4/2, no crossed facts, third-thread unknown behavior, rejection of blank inputs and pre-existing databases, and a truthful returned summary. Explain why an isolated thread is not a security boundary. Preserve a failed database for diagnosis instead of hiding an API failure behind a manufactured response.

## Optional design extension — not part of the validated execution set

Add a fresh-interpreter checkpoint read between the contexts without invoking a model. Pass only the database path and thread ID to the worker, and compare the saved human inputs. Explain why this strengthens restart evidence but still does not test power-loss recovery, backup restoration, or authorization. Do not weaken the core acceptance conditions to finish the extension.

## References


- [1221: File-backed SqliteSaver context-manager usage](https://reference.langchain.com/python/langgraph.checkpoint.sqlite/SqliteSaver/from_conn_string)
- [1222: Inspecting checkpoints and StateSnapshot fields](https://docs.langchain.com/oss/python/langgraph/checkpointers)

[1221]: https://reference.langchain.com/python/langgraph.checkpoint.sqlite/SqliteSaver/from_conn_string "File-backed SqliteSaver context-manager usage"
[1222]: https://docs.langchain.com/oss/python/langgraph/checkpointers "Inspecting checkpoints and StateSnapshot fields"


<!-- PAGEBREAK -->
<a id="u2"></a>
# U2 — Safe draft state and human approval/resume

## Task: approve exact content, repair a filename once

This is supplementary practice for about 30 minutes within the 90-minute U2 lab. Complete L10 and U1 first. You are extending the safety protocol, not writing a GUI or adding another provider.

Your fictional workshop assistant must generate each thread's notice once, pause before writing, and bind approval to the exact draft. If the first write fails, offer one filename-repair opportunity. Never regenerate or edit the text during repair. A second failed write must stop rather than create a retry loop.

Edit `exercises/starters/u2.py`. It is independent of the demonstration and has three focused TODO functions. Read `course_lessons/u2.py` for the baseline pattern. Consult `exercises/solutions/u2.py` only after attempting the task or during teacher review. The reference uses direct state updates and an additional hash/repair protocol; it is not an import of the baseline.

## Establish the starting behavior

From the repository root with the prepared environment active, run:

```bash
python -m exercises.starters.u2
python -m pytest -q tests/lessons/test_u2.py
```

The untouched starter prints `STARTER_NOT_COMPLETED` and exits successfully without loading credentials, invoking a model, or claiming a pass. The offline suite validates the demonstration and reference with named model doubles. Its completed-starter acceptance cases are explicitly skipped until your TODO functions exist; a skip is not exercise completion.

When authorized for real model use, the supplied reference commands are:

```bash
python -m course_lessons.u2 --live --backend none
python -m exercises.solutions.u2 --live --backend none
```

After completing your starter, run `python -m exercises.starters.u2 --live --backend none`. Do not modify the shared runtime, load credentials into graph state, or replace the real CLI model with canned output. Each live harness generates two notices and supplies scripted decisions; the approval protocol is real, but a separate human is not being simulated as evidence.

## Implement the three functions

1. **`approval_update`:** accept only a dictionary containing the actual boolean `True` under `approve` and a `draft_hash` matching the exact current draft and stored fingerprint. Reject malformed, missing, negative, or stale decisions. Clear any saved path. During repair, require a nonblank string filename, increment `repairs` once, and copy the filename only on valid approval. Never change `draft`.
2. **`attempt_save`:** require approved status and an approval fingerprint matching current content. Raise `ValueError` if that guard fails. Then call `safe_write_text`, returning `saved` and the actual path only after success. A writer `OSError` or `ValueError` must return `save_failed`, an empty path, and a useful error. Preserve any existing file.
3. **`build_graph`:** register the supplied nodes and compile with the supplied checkpointer or a new `InMemorySaver`. Route `START → generate → review`. Approved review goes to save; rejection ends. Successful save ends; first failure goes to repair. Approved repair goes to retry_save; rejection ends. retry_save always ends, including on failure. There must be no back edge.

Resume a pending ordinary review on the same thread with `Command(resume={"approve": True, "draft_hash": paused["draft_hash"]})`. Resume a repair with the same keys plus `"filename": "recovered.txt"`. Reject using `{"approve": False}`. Do not use an empty `Command(resume=None)` as rejection: the installed runtime does not treat it as a valid decision.

The SHA-256 digest fingerprints exact UTF-8 bytes, including whitespace. It detects stale approval; it does not authenticate a person. A server would separately authorize thread access. Keep the same graph/checkpointer instance for in-process resume; this lab does not promise restart persistence.

## Three progressive hints

### Hint 1: separate decision and effect

An interrupt payload is a request for a decision, not permission to write. The review node may replay. Return state updates after the decision; keep the writer in its later node. Use `is True`, not a generic truthiness test.

### Hint 2: compare the right hashes

Compare the submitted hash to the digest of current text, and ensure the stored fingerprint is also current. Before saving, compare `approved_hash` to the text again. A stale decision must never be repaired by silently changing its hash.

### Hint 3: bound recovery structurally

Use a separate `retry_save` node with an edge directly to END. Reusing the Python save function is fine; routing retry failure back to repair is not. Validate malformed repair names before approval, and let the safe writer reject traversal and collisions.

## Record concrete observed results

Record the command used and whether the evidence came from an offline double or a real Anthropic run: __________.

Record Cedar's thread ID, Orchid's different thread ID, and the two pending node names before either write: __________.

Record the first failed filename, failure status, empty saved-path value, and error class: __________.

Record the final artifact path and whether its exact text equals the original paused draft: __________.

Record the model-call count across repair, final repair count, and Orchid's unchanged pending draft before rejection: __________.

Record the stale-hash result and the terminal result after a second unsafe filename: __________.

These fields require observations, not predicted screenshots. Model wording can vary; do not require a particular greeting.

## Completion criteria and stretch

Run `python -m pytest -q tests/lessons/test_u2.py -k completed_starter` after implementation. All completed-starter acceptance cases must run rather than skip. Also run the full focused U2 test file, not the whole course suite.

Completion requires no write before approval; isolated pending drafts; rejection of stale approval; an unchanged existing file after collision; exactly one repair; unchanged content and no extra generation during repair; and a terminal honest failure if the repaired name remains unsafe. A fresh successful output must contain the exact approved bytes. Only authorized parent or classroom live validation establishes real model behavior; offline doubles cannot do so.

As a stretch, design a reconciliation policy for a crash after file creation but before checkpoint confirmation. Describe how to inspect the existing artifact without overwriting it or falsely declaring exactly-once delivery. Implementation is optional and must not weaken the required bounded workflow.

## Reference

The current [LangGraph interrupt documentation](https://docs.langchain.com/oss/python/langgraph/interrupts) explains same-thread `Command` resume and replay rules.


<!-- PAGEBREAK -->
<a id="s1"></a>
# S1 — LangSmith observability and evaluation

## Task: audit synthetic shipping receipts

**SUPPLEMENTARY practice · Allow 25 minutes of independent work.** Complete three functions that calculate a synthetic shipping quote, decode the model's receipt, and score actual output. The supplied graph and report writer remain unchanged. Your implementation must not import the demonstration or teacher solution.

Start in `exercises/starters/s1.py`. The independent reference is `exercises/solutions/s1.py`; consult it only after attempting the task. The separate demonstration is `course_lessons/s1.py`. Required background is L09 and the S1 guided trace inspection. All data are invented teaching values, not shipping prices or customer information.

Run the starter from the repository root:

```bash
python -m exercises.starters.s1
```

Initially, it must print `STARTER_NOT_COMPLETED` and exit successfully without contacting services. This status does not pass the task. After implementation, use its live command only with instructor approval:

```bash
python -m exercises.starters.s1 --live
```

S1 defaults to LangSmith. `--backend none` can disable tracing for diagnosis, but `--live` still authorizes a real Anthropic request. Never include keys or configuration dictionaries in code, state, prompts, metadata, reports, or screenshots.

## Implement the three functions

1. Implement `shipping_quote(region, weight)`. Local costs `3 + 2 * weight` credits; regional costs `5 + 3 * weight`. Weight must be an integer from one through ten inclusive. Reject booleans, floats, strings, out-of-range weights, and unsupported region names with `ValueError`. Return exactly `total`, `unit` equal to `credits`, and `source` equal to `shipping-policy-v1`.
2. Implement `decode_receipt(text)`. Accept only a JSON object with exactly `total`, `unit`, and `source`. Require an integer total excluding booleans, the unit `credits`, and a nonblank string source. Return `{}` for invalid JSON/schema, including arrays, missing/extra fields, or Markdown fences. Keep a schema-valid wrong amount or wrong nonblank source unchanged; do not copy the correct values into it.
3. Implement `evaluate_receipt(outputs, reference_outputs)`. Decode `outputs.get("raw", "")`. Return exactly five named booleans. `schema_ok` means decoding succeeded. `amount_ok` compares the decoded total to the reference total. `source_ok` compares its source to the reference source. `bounded_attempts` requires an integer attempt count of one or two. `tool_evidence` requires the tool result's source to equal `shipping-policy-v1` and exactly one `quote` entry in `trace_log`. Missing raw text or tool evidence must fail the relevant metrics, not produce a guessed pass.

The fixed dataset has local/two kilograms → seven credits, regional/three → fourteen, and local/one → five. These references are used by the evaluator, not added to graph input. The formatter receives the tool's result as factual task input.

The supplied graph invokes the tool once, formats a receipt, and checks schema. A malformed first response allows one additional formatting attempt. After the second attempt it terminates even if schema is still invalid. A schema-valid wrong amount fails evaluation without triggering a formatting retry.

## Verify without mislabeling evidence

Run the focused suite:

```bash
python -m pytest tests/lessons/test_s1.py -q
```

The suite tests both demonstration and reference solution using an explicitly named offline chat-model double. It also contains a completed-starter contract check: while TODOs remain, that check is skipped rather than falsely passing. Inspect the skip reason. After implementation, the starter contract check must run and pass. Passing only the reference tests is not evidence that your functions work.

For instructor-approved live comparison, run:

```bash
python -m course_lessons.s1 --live
python -m exercises.solutions.s1 --live
```

Each command performs three to six graph-level model invocations; SDK retries can add requests. The starter saves `s1-starter-evaluation.txt`, the demo saves `s1-demo-evaluation.txt`, and the solution saves `s1-solution-evaluation.txt`, each beneath its run directory. Use `report_path` rather than assuming the current directory. Each file is a JSON report, not an uploaded LangSmith experiment [1421].

## Progressive hints

### Hint 1: separate calculation from formatting

Represent each region with a base charge and a per-kilogram charge. Validate weight before arithmetic. Remember that `isinstance(True, int)` is true in Python; decide how to reject that input explicitly.

### Hint 2: parse before comparing

Use `json.loads` and verify the object type before inspecting keys. An invalid schema returns `{}`. The decoder does not know the expected amount; that belongs to the evaluator. Whitespace and JSON key order should not affect acceptance.

### Hint 3: use the actual model output

Read `raw`, not merely the tool's correct calculation. A valid receipt can still have the wrong amount. Keep the five metric results separate so a failure explains what went wrong. A single `quote` visit is local execution evidence, not remote-ingestion proof.

## Record observed results

Record your offline command, test counts, and whether the completed-starter check ran: **Command and result:** ______.

Record the three observed totals and their five metric results: **local/two:** ______; **regional/three:** ______; **local/one:** ______. Note whether the evidence used a test double or real Anthropic calls: ______.

Record one report path, assigned run ID, and observed node path: ______. Separately record **remote payload read-back:** verified / failed / not checked; and **dashboard hierarchy:** observed / unavailable / not checked. Add the evidence identifier or reason: ______. A flush or local UUID alone cannot fill either field as verified.

## Completion criteria and stretch

Completion requires three passing dataset rows, a strict decoder that rejects malformed schema, a failing amount score for a valid receipt containing eight instead of seven, correct weight/region rejection, and no more than two formatter invocations per example. The report must be a new file, preserve raw model output, and leave dashboard verification false unless separate inspection is genuinely recorded outside the program. Explain why the local report does not prove trace persistence.

For a stretch task, propose a fourth independent case and a failure-specific metric, without changing the required three-case baseline. Explain whether a deterministic rule or a reviewed LLM-judge rubric is appropriate. Do not upload a dataset or enable another tracing service as part of this stretch.

## Reference


- [1421: Official datasets, experiments, and evaluator concepts](https://docs.langchain.com/langsmith/evaluation-concepts)

[1421]: https://docs.langchain.com/langsmith/evaluation-concepts "Official datasets, experiments, and evaluator concepts"


<!-- PAGEBREAK -->
<a id="s2"></a>
# S2 — LangWatch observability and comparison

## Exercise: trace a handout lookup without overstating evidence

**Supplementary practice · 25 minutes within the 90-minute module.** Complete the S2 guided arithmetic demonstration first. You will build a handout lookup workflow with real model, tool, and retriever operations, plus two small privacy/evidence helpers. This is a tracing fixture, not a replacement for L11 vector retrieval.

Your starter is `exercises/starters/s2.py`; the independent reference is `exercises/solutions/s2.py`. Do not import the solution into the starter. The supplied `HandoutRetriever` returns one document for `TRACE-101` and no documents for `MISSING-999`. Its original text explains that flush does not prove acknowledgment or dashboard visibility. A found document has ID `TRACE-101`, source `synthetic-s2-handout`, page 1, and text in `DOCUMENT_TEXT`.

Run from the repository root with the prepared environment:

```bash
python -m exercises.starters.s2
python -m pytest tests/lessons/test_s2.py -q
```

Initially the starter must exit successfully with `STARTER_NOT_COMPLETED`. It must not claim a pass or make requests. The supplied focused tests exercise the demonstration and reference solution using named offline doubles; passing them alone does not assess your edited starter. Redirect or add equivalent local tests for your implementation before claiming completion.

## Implement exactly three functions

1. Complete `privacy_plan(backend)`. Accept only `none`, `langsmith`, `langwatch`, and `both`; reject unknown names with `ValueError`. Return `backend`, `telemetry_recipients`, `model_recipient`, `payload`, `root_capture_is_child_redaction`, and `plan_only`. Recipients are respectively an empty list, `["LangSmith"]`, `["LangWatch"]`, and `["LangSmith", "LangWatch"]`. Use the model-recipient text `Anthropic when --live is used`. Set the last two fields to `False` and `True`. Describe synthetic messages, state, tool arguments/results, and retrieved text in `payload`. This is a routing plan, not a redaction guarantee.
2. Complete `classify_ingestion(report)`. Acknowledge only a record with `service="langwatch"`, `status="passed"`, `http_status=200`, `ingestion_acknowledged` equal to boolean `True`, and `rejected_spans` equal to integer zero. Missing fields, string zero, boolean false, partial rejection, or failures must not pass. Return `checker_ingestion` as `acknowledged` or `not_established`; always leave `lesson_trace_ingestion` and `dashboard_visibility` as `not_checked`. Never create a success record merely because your graph finished.
3. Complete `build_graph(model)`. Make a `HandoutRetriever` and a tool named `lookup_handout`. The tool accepts `document_id` and the injected `RunnableConfig`; invoke the retriever with that config. Return JSON with `found` and `documents`, where each document contains `id`, `source`, `page`, and `text`. Bind this tool for the first model call with `tool_choice="auto"`, explicitly request its use in the prompt, and disable parallel tool calls. Validate that exactly the intended call actually occurred; automatic selection is not a guarantee. Use the unbound model for the second call.
4. Inside that builder, register `prepare`, `agent`, `tools`, and `finish`. Connect `START → prepare → agent`, route `agent` to `tools` if a call is present or to `finish` otherwise, connect `tools → agent`, and connect `finish → END`. Preserve the config on model/tool invocations and pass the entire tool-call dictionary into the tool. Reject blank document IDs, absent/multiple first calls, unknown tools, changed requested IDs, more than two model calls, further second-turn tool requests, and empty final text.
5. Return partial state updates and append events. A successful case must visit `prepare, agent, tools, agent, finish`, make two model calls, and set status to `supported` or `no_evidence` from the retrieved payload in Python. Require nonempty model text, but do not compare an exact sentence. Manually review whether it respects retrieved evidence.
6. After all TODOs are implemented and locally checked, replace the bottom `main()` call with `run_cli("S2", run_demo)`. With authorization, run `python -m exercises.starters.s2 --live`. The supplied runner checks both IDs and writes a new report; it makes four real Anthropic calls. S2 defaults to LangWatch. Use a fresh output directory when repeating a run.

## Three progressive hints

**Hint 1 — separate responsibilities.** Privacy mapping and checker interpretation are ordinary Python functions. Test these without a model. An HTTP status code alone cannot tell you how many spans were rejected.

**Hint 2 — preserve the nested operation.** The graph receives runtime callbacks through `execution_config()`. Nodes receive `config`; carry that same config into the model, tool, and retriever. Use the existing demonstration's message-ID handling as a pattern, not its arithmetic tool as the answer.

**Hint 3 — make absence deterministic.** Parse the tool's JSON into `evidence`. Derive the final status from `evidence["found"]`; do not ask the model to invent a missing handout or trust a generated “success” label. Force one first tool call, then reject additional rounds instead of looping indefinitely.

## Observe the result and compare destinations

After authorization, use the reference and service checker separately:

```bash
python -m exercises.solutions.s2 --live
python -m exercises.solutions.s2 --live --backend both
python -m course_support.check_connections --service langwatch
```

The `both` command routes one execution to two telemetry services; it does not double the model calls. Inspect actual corresponding operations in each authorized project. A checker acknowledgment belongs to its own check, not automatically to the lesson run.

Record concise observations: your command and report path; status and document count for each ID; source/page for the found document; model-call count and event order; selected telemetry destinations and the remaining Anthropic destination; checker status/rejected count; and whether you personally inspected the lesson's model/tool/retriever tree. Mark unperformed checks `not_checked`. Do not record keys, real personal information, fabricated trace IDs, or invented screenshots.

## Completion criteria and stretch

Complete means all three functions are implemented, known/missing cases have the specified evidence and statuses, callbacks reach model/tool/retriever, call IDs match, budgets and invalid-input cases fail honestly, and the report is written without overwriting. Distinguish offline-double evidence, local application success, separate checker acknowledgment, and actual dashboard inspection. Passing local assertions alone is not proof of remote visibility.

**Stretch:** add an offline test in your own implementation that emits a second-turn tool request and proves termination before a third model call. Then write a short comparison of one genuinely inspected `both` execution, noting unavailable fields rather than assuming identical tree layout or timing.

## References

Use the verified official [LangWatch graph callback guide](https://langwatch.ai/docs/integration/python/integrations/langgraph) and [OTLP partial-success specification](https://opentelemetry.io/docs/specs/otlp/) to justify callback placement and evidence handling. The current online setup examples may use arguments absent from installed LangWatch 1.4.0; keep using the supplied shared runtime instead of replacing its configuration.


<!-- PAGEBREAK -->
<a id="c01"></a>
# C01 — Document-grounded drafting capstone

## Independent task: approve the current draft, not an earlier version

**SUPPLEMENTARY · 180-minute capstone session.** This added exercise combines drafting and retrieval ideas with explicit approval and bounded execution. Complete L01–L11, U1–U2 and S1–S2 before starting.

Your client wants a short teammate briefing based only on the supplied L11 synthetic teaching document, `data/rag_teaching_handbook.pdf`. A reviewer may ask for one revision, reject the draft or approve its current contents. Saving must require explicit approval of the current draft. The finished file must include a reproducible inventory of the evidence the assistant retrieved. Do not add another knowledge base, paid provider, global draft buffer or unbounded tool loop.

Use `exercises/starters/c01.py`. The independent instructor reference is `exercises/solutions/c01.py`; compare it only after your attempt. The baseline demonstration is `course_lessons/c01.py`. Keep the provided scaffold and implement its three TODO functions instead of importing another implementation.

## Establish the baseline

From the repository root with the prepared Python environment active:

```bash
python -m exercises.starters.c01
python -m pytest tests/lessons/test_c01.py -q
```

Before implementation, the starter must report `STARTER_NOT_COMPLETED` and exit successfully without paid calls or model downloads. The test suite checks the complete baseline and reference using named offline doubles; the dedicated learner-acceptance test skips while TODOs remain. This is not a completed capstone or proof of live services.

## Implement the three functions

1. **`assess_citations(draft, hits)`.** Return false for blank text, any case-insensitive occurrence of `INSUFFICIENT_EVIDENCE`, or no citation markers. Collect markers matching `r"\[[^\[\]\n]+ p\.\d+\]"`. Every collected marker must be exactly `citation(hit)` for one of the retrieved records. At least one is required. Preserve the helper's source and one-based page. This function checks reference integrity, not semantic truth.

2. **`decide_review(payload, draft, revisions)`.** Always return the keys `approved`, `feedback` and `status`. The default is `False`, an empty string and `invalid_review`. Non-dictionaries remain invalid. An `approve` action requires `payload['fingerprint'] == fingerprint(draft)`; only then return `approved=True` with status `approved`. A `reject` action returns `rejected`, without approval. A `revise` action allows stripped string feedback of 1–500 characters when `revisions < 1`, returning `revision_requested` and that feedback. If a revision already occurred, return `revision_limit`. All malformed decisions must fail closed.

3. **`render_artifact(draft, hits)`.** Start with `draft.strip()`, then a blank line and the literal heading `Evidence inventory`. Deduplicate tuples `(source, page, id)` from every retrieved chunk, sort those tuples and format each line as `- [SOURCE p.PAGE] (chunk ID)`. End with a newline. Include retrieved chunks even when the model did not cite them; distinguish available evidence from evidence actually used. Do not change save behavior to overwrite an existing file.

The scaffold already performs actual L11 retrieval, checks tool IDs and metadata, isolates state with checkpoint thread IDs, interrupts for clarification/review, resets approval after revision and limits successful threads to three model calls. Leave these controls intact.

## Three progressive hints

**Hint 1:** Turn both citation collections into Python sets. Check that the found set is nonempty before using `issubset`. Otherwise an uncited draft could pass because the empty set is a subset of every set.

**Hint 2:** Construct the default review dictionary first. Return a new update only when one of the allowed decisions is validated. Do not use truthiness such as `bool(payload)` as approval, and do not reuse the pre-revision fingerprint.

**Hint 3:** Build an inventory set of tuples before sorting. Sorting strings containing page numbers can order page 10 before page 2; keep the page as an integer in the sorting tuple. Formatting belongs after sorting.

## Check your completed starter

```bash
python -m exercises.starters.c01
python -m pytest tests/lessons/test_c01.py -q -k implemented_starter_acceptance
python -m pytest tests/lessons/test_c01.py -q
```

The targeted acceptance test must **pass, not skip**. It checks your three functions, the approved save, the revision limit and stale approval using explicit offline dependencies. After completing the functions and receiving live-call authorization, run your actual starter and the separate instructor reference:

```bash
python -m exercises.starters.c01 --live
python -m exercises.solutions.c01 --live
```

Each needs L11's actual helper, local embeddings and Anthropic access. Use a fresh output directory for each run. Neither command should silently replace a failed live call with scripted output. The teaching driver supplies explicit review decisions; inspect the draft yourself rather than treating the script as an authenticated human interface.

## Record observed results

Record your targeted-test outcome and whether it passed or skipped: __________. Record the actual fixture source/page you inspected and a supported claim: __________. Record the real saved artifact path and verify its fingerprint-approved draft plus inventory: __________. Record the status returned for stale approval, a second revision and an unsafe filename: __________.

Run the same synthetic scenario with each configured tracing backend separately. Record the backend, server-side trace identifier and where the retrieval/tool result appears: __________. If unavailable, write the concrete blocker rather than inventing an identifier. Never record credentials.

## Completion criteria and stretch task

Completion requires a passing learner-acceptance test; real retrieval and an Anthropic tool round trip; inspectable valid citations; no saved file before approval; stale-approval rejection; one bounded revision; two-thread isolation; a correctly formatted new file inside the allowed directory; and documented failure behavior. Submit the actual artifact and test/live evidence, not an exact expected model sentence. Explain why an in-memory checkpoint does not survive restart and why citation formatting alone cannot establish grounding.

For a stretch task, design an authenticated review interface that displays the current fingerprint and requires a named reviewer to confirm it. Sketch how a durable checkpoint backend and crash-recovery policy would prevent confusing a pre-existing artifact with a newly completed save. Do not implement unattended approval or introduce private documents. Use the [official interrupt semantics](https://docs.langchain.com/oss/python/langgraph/interrupts) and [Anthropic client-tool protocol](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) when explaining the design.


<!-- PAGEBREAK -->
<a id="appendices"></a>
# Appendices

## A. Execution command reference

Run commands from the repository root, not from inside a lesson folder. Starters intentionally report `STARTER_NOT_COMPLETED` until edited; that is not a successful completed exercise. The matching instructor solution is the executable acceptance reference.

```bash
python -m course_lessons.p00
python -m exercises.starters.p00
python -m course_lessons.l01
python -m exercises.starters.l01
python -m course_lessons.l02
python -m exercises.starters.l02
python -m course_lessons.l03
python -m exercises.starters.l03
python -m course_lessons.l04
python -m exercises.starters.l04
python -m course_lessons.l05
python -m exercises.starters.l05
python -m course_lessons.l06
python -m exercises.starters.l06
python -m course_lessons.l07 --live
python -m exercises.starters.l07
python -m course_lessons.l08 --live
python -m exercises.starters.l08
python -m course_lessons.l09 --live
python -m exercises.starters.l09
python -m course_lessons.l10 --live
python -m exercises.starters.l10
python -m course_lessons.l11 --live
python -m exercises.starters.l11
python -m course_lessons.u1 --live
python -m exercises.starters.u1
python -m course_lessons.u2 --live
python -m exercises.starters.u2
python -m course_lessons.s1 --live --backend langsmith
python -m exercises.starters.s1
python -m course_lessons.s2 --live --backend langwatch
python -m exercises.starters.s2
python -m course_lessons.c01 --live --backend both
python -m exercises.starters.c01
python -m pytest -q
```

## B. Reproducible setup and versions

For a fresh checkout, first install Git and Python 3.12, then obtain the course branch. Skip cloning when you already have this repository open:

```bash
git clone --branch course/anthropic-observability-2026-11-03 https://github.com/nuvear/01_LangGraph.git
cd 01_LangGraph
```

macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock.txt
test -f .env || cp .env.example .env
chmod 600 .env
```

Windows PowerShell, without activation or execution-policy changes:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -m examples.observability_demo --backend none
```

Privately edit `.env` in a local text editor: set `ANTHROPIC_API_KEY` to your own Anthropic Console key and keep or replace the configurable `ANTHROPIC_MODEL`. The supplied example uses `claude-opus-5-5`, which passed this project's real connection check; your account must have access to the selected model. LangSmith and LangWatch fields are needed only for the corresponding tracing modules or a command selecting both. Choose the LangSmith endpoint for your actual account region. Close the file before screen sharing and never paste its contents into a terminal command. These guarded copy commands preserve an existing `.env`; do not replace them with an unconditional overwrite.

Install the locked runtime before trying the per-lesson commands. Authoring/rendering tools are separated in `requirements-docs.txt`; students do not need Mermaid, LibreOffice, Playwright, or Word-building tools to run ordinary lessons.

Actual validation interpreter: `3.12.13`. Runtime package versions:

- `anthropic==2.4.0`
- `langgraph==1.2.19`
- `langchain-core==1.7.4`
- `langchain-anthropic==1.7.9`
- `langgraph-checkpoint-sqlite==3.1.3`
- `langchain-text-splitters==1.1.3`
- `chromadb==1.5.9`
- `onnxruntime==1.31.1`
- `pypdf==6.21.4`
- `reportlab==5.1.0`
- `langsmith==0.14.17`
- `langwatch==1.4.0`
- `python-dotenv==1.2.4`
- `pytest==9.2.0`

The complete transitive pins are in `requirements.lock.txt`. Platform-specific wheels and native libraries can differ; a successful macOS install is not a Windows test. The first local-embedding run downloads model weights; offline tests do not stand in for that real download/indexing check.

## C. Actual execution and test results

The validation harness recorded **34/34 successful demonstration/reference-solution executions**. It records command, UTC time, duration, exit code, backend, code hash, log hash, and screenshot path in `course/validation/execution_manifest.json`.

Offline test result: **860 passed**, **0 failed**, **9 skipped**. Offline model doubles validate orchestration deterministically; the separate `--live` runs validate actual provider behavior. Each screenshot in the two handbooks is captured from a browser displaying the actual stdout/stderr produced by the indicated process. It is explicitly labeled rather than made to resemble a native Terminal application. A viewport can show only part of a long log; complete text logs are supplied alongside images.

[Full validation report](../course/validation_report.md). [Machine-readable execution manifest](../course/validation/execution_manifest.json).

The local supplied Anthropic model is configurable; exact model wording and latency are not guaranteed. Independent exercises have executable reference solutions. Optional design extensions are not additional validated software deliverables unless their solution is explicitly implemented and tested.

## D. Troubleshooting map

A missing module normally means the environment or working directory is wrong: verify the selected interpreter, install the lock, and run a module command from the repository root. A graph-build error should be diagnosed before adding an LLM. A recursion-limit failure means the loop did not terminate as intended; inspect state, routing labels, and tool results instead of increasing the limit blindly.

HTTP 401 indicates a credential/authentication problem, not proof of an unavailable graph. Model access, usage limits, network errors, and regional tracing endpoints are separate checks. Never paste a key into an exception report. A missing trace can result from a wrong backend, key scope, endpoint, or unflushed exporter; verify ingestion independently from callback completion. No-tracing mode should remain available for privacy and debugging.

For file-save errors, check the explicitly selected output directory and filename. A rejected traversal, symlink, or overwrite is an intended safety check. For SQLite persistence, keep the same database and thread ID when testing recovery, and use different IDs when testing isolation. For RAG, inspect pages, chunks, collection path, embedding identity, and retrieved evidence before judging the generated answer.

## E. Original illustrations and technical references

The concept illustrations and flowcharts are original diagrams created for this course. Editable Mermaid sources are supplied under `assets/diagrams`. Concept diagrams explain data flow and mental models; complete implementation flowcharts include more detailed guards and error paths.

Execution screenshots are separate evidence of actual runs, not conceptual mockups. Chapter-specific official technical documentation is retained beside the material it supports. Source/page citations in retrieval exercises refer to the supplied synthetic teaching dataset and must remain inspectable.

## F. Delivery and classroom use

The Student Handbook, Teacher Handbook, and Exercise Workbook share the same identifiers and sequence. Runnable baselines live in `course_lessons`, unfinished tasks in `exercises/starters`, instructor answers in `exercises/solutions`, and regression tests in `tests/lessons`. Directory separation is not an access-control boundary: instructors should omit solutions when distributing a learner-only package.

Word contains embedded images. HTML embeds its images for standalone reading. Markdown keeps relative links and should be distributed with the supplied asset folders or complete course archive.

## G. Working glossary

**State** is the graph's structured working data. A **partial update** contains only the state fields a node changes. A **TypedDict** describes expected dictionary keys for type checking; it does not automatically validate arbitrary input at runtime.

A **node** is a named processing step. An **edge** schedules a next step. A **conditional edge** chooses a destination from state. **START** and **END** are graph boundaries, not work-performing business functions. A **compiled graph** is the executable produced by the builder; compilation does not prove its answers are correct.

A **reducer** defines how an update combines with an existing state field. Without an accumulating reducer, a later update commonly replaces an earlier value. **MessagesState** supplies a message channel with **add_messages**, which handles message identity as well as appending new turns.

A **tool schema** describes an available function. A **tool call** is the model's request to use it, not the function's execution. The application executes the tool and returns a **tool result** linked to that call. A **ReAct-style loop** alternates model and tool steps until an exit condition is reached.

A **thread ID** selects a unit of conversation/checkpoint history; it is not an operating-system thread. A **checkpoint** records graph execution state. **Durable persistence** survives the process only when the chosen storage backend actually retains the data. An **interrupt** pauses execution at an explicit point, and a resume command supplies the human decision to the persisted workflow.

**Retrieval** selects passages relevant to a query. An **embedding** maps text to a numeric vector; the index and query must use compatible embeddings. A **vector store** such as Chroma stores and searches vectors with their document metadata. **RAG**, retrieval-augmented generation, supplies retrieved evidence to a model; it does not guarantee that every generated claim is correct. A **citation** should lead to inspectable source/page evidence.

A **trace** records an execution; a **span** records an operation within it. Traces can expose inputs and outputs, so they require deliberate data selection. **Latency** is elapsed time, and **token usage** measures provider-accounted input/output units. Neither tracing nor a token count reveals private model chain-of-thought.
