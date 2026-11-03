# L09 — ReAct arithmetic tool loop

## Explain: from conversation to action

Allow 150 minutes including practice and review. Prerequisites are L08, Python functions and lists, conditional edges, and a working Anthropic setup from P00. U1 is an optional memory update after L08, not a prerequisite for this fresh-request graph.

By the end, you should be able to define documented arithmetic tools, bind their schemas to a model, preserve message history with a reducer, route a model response to a tool node or END, and audit each result against its call ID. You will also distinguish successful termination from a safety limit that stopped an unfinished run.

The previous bot could produce text. This graph can also request that Python perform an operation. ReAct means reasoning and acting, but this lesson examines the **observable action loop**: model request, tool execution, returned observation, and final response. It does not request or display private chain-of-thought. A tool-call record tells us what was requested, not everything happening inside the model.

The model chooses a tool and arguments. Python executes the arithmetic. LangGraph controls the order and stores messages. These are different responsibilities: binding tools does not execute them, and a plausible final answer does not establish that a tool ran. The [official calculator quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart) demonstrates this same model-to-tools-to-model topology.

## Illustrate: the messages that make the loop work

A `HumanMessage` contains the user's request. A `SystemMessage` gives application instructions. An `AIMessage` may contain ordinary text, structured `tool_calls`, or both. A `ToolMessage` contains an execution result. `AnyMessage` describes the supported message variants; `BaseMessage` is their shared base class. These classes let the application inspect roles and tool relationships without parsing an assistant's prose.

Our state declares `messages: Annotated[list[AnyMessage], add_messages]`. `Annotated` associates metadata with a type; it does not validate an email or make a list persistent. LangGraph interprets the attached `add_messages` function as a **reducer**, the rule for combining an existing state value with a node update. New message IDs append. An existing message ID updates the corresponding message. This is more precise than “append every item”; see the [Graph API message-state documentation](https://docs.langchain.com/oss/python/langgraph/graph-api).

The model node returns `{"messages": [reply], "model_calls": count + 1}`. It returns only its new message, not the whole accumulated transcript. `model_calls` uses ordinary replacement because it has no reducer. This contrasts with the message field's merging rule. A type annotation describes intended values; the tools' generated argument schemas provide a separate runtime validation boundary.

Suppose the assistant requests `subtract(a=18, b=5)` with ID `call_a`. `ToolNode` executes the registered function and creates a `ToolMessage` containing `13`, with `tool_call_id="call_a"`. The tool message's own message ID is not the matching key. The next model invocation receives the human request, the AI call, and its tool result. Only then can it request multiplication of the observed result by four. Every call in a batch needs its own matching result before the next assistant response.

Two independent calculations may be requested together. Their results must be paired by ID rather than assumed position. A dependent calculation is different: requesting multiplication in the same batch as subtraction would not prove that the model used the subtraction tool's observation.

<!-- ORIGINAL_DIAGRAM -->

The concept diagram shows both normal routes and explicit failure bounds. Follow its return edge from tools to the model. A tool result is not automatically the final user answer; the model normally needs another turn to interpret it. The no-tool route exits directly after a model response.

<!-- CONCEPT_FIGURE -->

## Demonstrate: run the complete baseline

The demonstration is `course_lessons/l09.py`. Its tools add, subtract, and multiply integers. Useful docstrings describe their purpose, while argument names and annotations form schemas for the model. The [tools guide](https://docs.langchain.com/oss/python/langchain/tools) explains that functions become tools with descriptions and input schemas. Subtraction's description specifically preserves argument order.

1. Open the demonstration and find `TOOLS`, `build_graph`, and `route_after_model`. Predict which function actually executes the arithmetic. It is not the routing function: the route returns a label, and `ToolNode` performs execution.
2. Follow `START → model`. The model input prepends the system instruction to **all** current state messages. Passing only the system instruction would discard the user's actual problem.
3. Follow the conditional edge. Any valid `tool_calls` route to tools; no calls route to END. After tool execution, the ordinary edge returns to the model. The model-call counter starts at zero for every request.
4. In the activated project environment, run the focused offline checks first:

   ```bash
   python -m pytest tests/lessons/test_l09.py -q
   ```

   These checks use explicitly named scripted model doubles. They test real graph execution and real local tools, but do not test Anthropic availability or model judgment.
5. When your instructor authorizes real requests, run:

   ```bash
   python -m course_lessons.l09 --live --backend none
   ```

   This is a paid network run. Without `--live`, model creation is deliberately rejected; there is no canned fallback. The baseline makes seven fresh requests, often requiring multiple model turns each. Do not repeatedly run it while troubleshooting a local syntax error.

<!-- EXAMPLE_CODE -->

Expected stable properties are actual tool results of `7`, `55`, two independent addition results, subtraction result `17`, and the sequential observations `52` then `312`. The final sequential answer should contain `312`. The mixed request combines a calculation with a joke. A plain greeting should produce no tool calls and exactly one model turn. The summary retains observable calls, arguments, results, statuses, and final text. Wording and independent-call batching can vary; these are acceptance expectations, not a claim that a live run has already passed.

<!-- EXECUTION_FIGURES -->

## Guided practice: inspect evidence, not only the answer

1. Locate `inspect_transcript`. Explain why its pending-call dictionary uses call IDs. Compare an `AIMessage.tool_calls` entry with the following `ToolMessage`.
2. Read the sequential offline test. Count three model turns: request addition, request multiplication after seeing the addition result, then answer. The tool executes twice; “three model turns” does not mean “three tool executions.”
3. Read the parallel test. Two independent additions can produce two tool messages between two model turns. Do not require an exact model-turn count for independent live requests because the model may choose separate batches.
4. Inspect the invalid-argument tests and the intentionally repeating model double. A validation error is returned as an error observation, which the next model turn can address. Repetition instead reaches a clear budget exception. Neither path invents a successful arithmetic result.

The demonstration permits at most six model calls per request and four tool calls per batch. A recursion limit of 40 remains a backup graph-step bound. It is not the same unit as model calls and is not a substitute for the explicit budget. A budget exception means the request failed to finish within policy.

## Independent task: build an audited arithmetic runner

Complete `exercises/starters/l09.py` using the exact workbook specification. Implement `route_next`, `make_agent`, and `collect_audit` without importing the demonstration or reference solution. Keep the provided typed tools and acceptance harness.

Use a default limit of four model calls and a maximum of three tools per batch. Produce an audit row for every result with `call_id`, `tool`, `args`, `result`, and `status`. Reject mismatched or missing results instead of fabricating evidence. Validate three requests: subtract five from eighteen and then multiply the observed result by four; independently compute nine plus six and eight times three; and give a greeting with no calculation. The workbook provides progressive hints, failure cases, and completion criteria. The independent solution is `exercises/solutions/l09.py`.

## Knowledge checks

1. With `add_messages`, what should the model node return, and what happens when a later update uses an existing message ID?
2. A tool call has ID `call_a`, name `subtract`, and arguments `a=18, b=5`. What executes it, what `tool_call_id` must the result carry, and why must the model see that result before multiplying by four?
3. For greeting-only input, which route ends the graph? Why do a final sentence containing `52` and `recursion_limit=40` not by themselves prove the compound task completed correctly?

## Troubleshooting and current-API differences

If the model ignores tools, check that the same tool list reaches both `bind_tools` and `ToolNode`, and that your prompt explicitly asks for tool-backed arithmetic. Do not fix this by fabricating calls. If the provider rejects the transcript, check every call/result ID and whether all results precede the next model turn. If a greeting reaches tools, inspect structured calls rather than searching text for arithmetic keywords.

This lesson uses the shared Anthropic factory with locally configured model selection and no temperature override. [ChatAnthropic](https://docs.langchain.com/oss/python/integrations/chat/anthropic) exposes normalized `AIMessage.tool_calls`. At the direct [Anthropic client-tool layer](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview), the corresponding blocks are `tool_use` and `tool_result`, linked by `tool_use_id`. Do not manually mix those wire-format dictionaries into LangChain tool-message construction.

The installed ToolNode wraps schema-validation failures in a `ToolException` subtype. The supplied narrowly typed handler supports that path without swallowing arbitrary programming errors. Empty or malformed call JSON is rejected explicitly. This example does not add durable memory, division, file-writing tools, or private reasoning logs. If execution reaches a safety exception, inspect the last observable call and correct the cause rather than simply raising the limit.

## References

Current official references linked above support the arithmetic-loop progression. The explicit budgets, audit acceptance checks, offline doubles, and independent workbook task are part of this course.
