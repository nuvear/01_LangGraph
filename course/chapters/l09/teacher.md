# L09 — ReAct arithmetic tool loop

## Explain: teaching intent and preparation

Teach this lesson after L08. The tool-definition and graph-building sequence, audit exercise, explicit execution budgets, and automated failure checks are all part of this lesson. The approved teaching allocation is 150 minutes. The core learning distinction is model selection versus deterministic execution versus graph orchestration. Learners should leave able to explain each one without describing a tool call as an already completed action.

Before class, confirm the project Python 3.12 environment and separately authorized service validation. Never display credentials. Use synthetic requests if tracing is enabled. An offline test pass establishes neither live service access nor dashboard ingestion.

Run the focused checks with `python -m pytest tests/lessons/test_l09.py -q`. The model doubles are deliberately named and finite. They execute the real local arithmetic tools and graph routes, but their responses are controlled test inputs. Live evidence and handbook execution figures are recorded separately by the integrating instructor.

## Illustrate: allocate the first thirty minutes

**Minutes 0–15:** ask learners what L08's assistant could do beyond emitting text. Introduce ReAct as an observable action loop, not a request for hidden reasoning. Draw a distinction between a model request for `subtract` and the Python result. Expected response: the model supplies arguments, but our application must execute the function. A final answer can be correct while still failing the requirement to use tools.

**Minutes 15–30:** work through message roles and reducers. Ask what happens if a node replaces the message list with only its newest response. Learners should predict loss of the user request and prior call/result context. Then explain `Annotated` and `add_messages`: new IDs append; an existing ID updates. Contrast a tool-call ID with a message ID. The [Graph API reference](https://docs.langchain.com/oss/python/langgraph/graph-api) supports this distinction.

<!-- ORIGINAL_DIAGRAM -->

Use the concept diagram to trace a greeting and a dependent calculation. Point out that the tool-result edge returns to the model rather than directly to END. A request may stop through an exception when the budget is exhausted; that is not the successful exit branch.

<!-- CONCEPT_FIGURE -->

## Demonstrate: minutes 30–50

Open `course_lessons/l09.py`. Spend the first part on the typed tools and their docstrings. Ask why subtract's argument order is explicit. Expected answer: subtraction is not commutative; `a - b` and `b - a` can differ. Then locate the same `TOOLS` list at binding and at `ToolNode` construction. Binding exposes schemas; registering the node supplies executable functions.

Trace the model node's input. It includes a `SystemMessage` followed by all current messages. Show why omitting the user message would make the graph lose the actual problem. Show the partial update containing one new AI message and the replacement counter value. The [official calculator quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart) confirms the two-node loop, while this course deliberately uses `ToolNode` and the ID-aware reducer.

After authorization, execute:

```bash
python -m course_lessons.l09 --live --backend none
```

Read the checked observations rather than demanding identical assistant wording. Locate addition observations, the subtraction case, the mixed request, and the no-tool case. In the dependent example, look for addition result `52`, a later multiplication call using `52` and `6`, result `312`, and a final AI response. Independent tool calls may share a batch; do not grade a fixed turn count for them. The greeting should have no audit rows and one model call.

<!-- EXECUTION_FIGURES -->

If service access fails, preserve the exception and switch to the clearly labeled offline tests. Do not silently substitute a test double into a live demonstration. Save actual execution figures only after the relevant demo and solution have genuinely run.

## Guided practice: minutes 50–80

Have pairs annotate the sequential and parallel tests in `tests/lessons/test_l09.py`. One student follows messages; the other follows control flow. Expected sequential sequence is human, AI call, tool result, AI call, tool result, final AI. The system instruction is prepended for each invocation rather than repeatedly stored in state.

Ask pairs to reverse the two independent tool results in a written transcript. The audit should still match them by ID. Then discuss the invalid-argument path: a tool error is an observation with status `error`, not a successful result or proof that the model corrected itself. The tests separately exercise correction and repeated-call exhaustion.

The installed ToolNode wraps argument-validation failures in a `ToolException` subtype. Keep the handler narrowly annotated with that supported public base; programming mistakes should remain visible. Verify alternate exception annotations against the installed package before teaching them.

## Independent exercise: minutes 80–130

Assign the workbook's audited runner. Students edit only the three TODO functions in `exercises/starters/l09.py`: `route_next`, `make_agent`, and `collect_audit`. The starter's `BindingOnlyProbe` binds schemas without invoking a model; it detects unfinished TODOs, not correctness. An unchanged starter exits successfully while printing `STARTER_NOT_COMPLETED`. Once implemented, the real run still requires `--live`.

The independent reference is `exercises/solutions/l09.py`, not an import of the demonstration. Its `run_demo` validates exactly the workbook's compound subtraction/multiplication request, independent addition/product request, and greeting. To inspect it live after authorization:

```bash
python -m exercises.solutions.l09 --live
```

Walk through the solution in three stages. First, `route_next` inspects the last AI message, rejects malformed calls and batches above three, and chooses tools or END. Second, `make_agent` binds the tools, creates both nodes and edges, and checks the model-call budget before each invocation. It forwards the node's `RunnableConfig`; invocation uses `execution_config()` so selected callbacks are preserved. Third, `collect_audit` holds pending calls keyed by ID, consumes each result once, and refuses incomplete or interrupted transcripts. Error observations remain in the audit with their original status.

<!-- SOLUTION_CODE -->

The compound task requires observations `13` then `52`, with multiplication after the first observation. It should require at least three model turns. The independent task produces `15` and `24`, with either valid batching pattern accepted within the four-turn budget. The greeting has no tool results. Grade these behavioral properties, not a memorized final sentence.

## Review: minutes 130–150 and assessment answers

**1. With `add_messages`, what should the model node return, and what happens when a later update uses an existing message ID?** It should return only the new reply in a message update, plus its incremented counter. New IDs append, while an existing ID replaces the corresponding message. Resending a reconstructed full history with fresh IDs risks duplicates; the reducer is not blind concatenation.

**2. A tool call has ID `call_a`, name `subtract`, and arguments `a=18, b=5`. What executes it, what `tool_call_id` must the result carry, and why must the model see that result before multiplying by four?** `ToolNode` dispatches to the registered Python subtraction tool, which returns `13`. The result must carry `tool_call_id="call_a"`. The next model turn must receive this observation before requesting multiplication of `13` by `4`; otherwise the model may have calculated an intermediate value itself rather than used the tool result. The later tool returns `52`.

**3. For greeting-only input, which route ends the graph? Why do a final sentence containing `52` and `recursion_limit=40` not by themselves prove the compound task completed correctly?** An AI response with no tool calls routes to END. Correct prose does not prove either tool executed or the IDs matched. A recursion limit bounds graph steps, not arithmetic correctness or the intended model-turn policy. Require both successful observations, correct dependency order and arguments, a complete transcript, and a nonempty final answer within budget.

Award ten marks: two for graph construction and partial updates, two for audit pairing and rejection of incomplete evidence, two for all three exact cases, two for bounded/error behavior, and two for the explanations above. Withhold completion if a student hardcodes results, imports the reference solution, hides errors as success, or omits the no-tool route.

## Recovery and references

If a result is unmatched, inspect `tool_call_id` before modifying arithmetic. If user intent disappears, restore the full current message input. If loops recur, inspect the last error observation and stop retrying identical bad arguments rather than merely raising limits. If imports differ from an old notebook, use the delivered imports and verified local versions.

Current provider behavior is documented in [ChatAnthropic](https://docs.langchain.com/oss/python/integrations/chat/anthropic) and [Anthropic client tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview): LangChain normalizes tool calls, while Anthropic's direct API uses linked `tool_use` and `tool_result` blocks. No division, persistent memory, external side effects, or private chain-of-thought access is required. Official references were checked on 3 November 2026; live and cross-platform outcomes require separate evidence.
