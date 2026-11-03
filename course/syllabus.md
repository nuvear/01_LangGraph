# Syllabus: LangGraph from basic Python to tool-using workflows

**Updated approval draft:** [complete training index](training_index.md). The later [whole-track visual-review record](video_visual_review.md) resolves the apparent L08/L10 caption-boundary truncations and documents 36 visual checks across the full source. The original section-review caveats below describe the earlier review stage, not missing video access. The index adds a 60-minute preparation module, uses C01 for the capstone, and plans local non-OpenAI embeddings rather than requiring another paid embedding API key.

## Course design and status

**Audience:** students comfortable with basic Python who have not used LangGraph. **Core structure:** 11 lessons following the original video sequence, from Python/state foundations through deterministic graphs, chat, memory, tools, collaborative drafting, and RAG. **Source:** [freeCodeCamp course video](https://youtu.be/jGg_1h0qzaM) and [original code repository](https://github.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp).

This is a project foundation and teaching plan, not a completed learner handbook or a claim that code, exercises, integrations, or assessments have been delivered. The accompanying [video source map](video_source_map.md) is the detailed provenance contract.

The plan uses **only the supplied reviewed transcript evidence and its inherited repository/API notes**. Transcript review is represented in those reviews; **video-frame/visual review is not yet completed**. No new documentation research, repository execution, or model testing is asserted here. “Current-API update” means guidance supplied with the reviews, to be pinned and tested against the eventual implementation environment; it is not a fresh compatibility audit.

### What belongs to which layer

| Layer | Meaning in this syllabus |
|---|---|
| VIDEO-BACKED | Narrated topics, demonstrations, and explicitly assigned original exercises. |
| CURRENT-API UPDATE | Clearly identified changes for the adapted implementation; not attributed to the original presenter. |
| ADDED PRACTICE | New instructional work used to make an outcome assessable; not original video homework. |
| SUPPLEMENTARY | LangSmith/LangWatch observability and capstone work outside the original 11 lessons. Advanced current-API memory/state labs are also scheduled outside core lesson time. |

The adapted course uses **Anthropic for every chat-model call**. Original OpenAI code is documented historically where supported, not reproduced as the adapted provider. L01–L06 stay deterministic: they require no model call or paid model account. L11 needs a separately chosen **non-OpenAI embedding provider**; do not assume Anthropic chat models provide embeddings.

## Entry prerequisites and preparation

Learners should be able to define and call a function, pass a dictionary/list, use an `if` statement and a loop, read an f-string, and run a Python file or notebook. Type annotations, graph vocabulary, message objects, reducers, tools, and retrieval are taught in the sequence. There is no prerequisite knowledge of agents, vector databases, LangChain, or LangGraph.

Before L02, provide a working Python environment and a way to run scripts/notebooks. Before L07, provide a pinned, tested dependency environment, an approved Anthropic account/model choice, and instructions for setting `ANTHROPIC_API_KEY` without placing its value in source files, screenshots, logs, or submissions. Before L11, verify access to the source PDF, a portable local persistence directory, and the embedding provider. Optional tracing labs require separate account/configuration preparation and a data-sharing/redaction decision.

Allow an additional **45–75 minutes of setup support** if needed; it is not included in the teaching totals. This is an estimate, not a claim that setup has been done. Use synthetic names and documents. Keep file-writing exercises in an explicitly selected output directory, and do not use real personal correspondence for tracing.

## Course-level learning outcomes

By the end of the proposed core sequence, a learner should be able to:

1. Define typed graph state and explain the distinct roles of nodes, ordinary edges, conditional routes, START/END boundaries, and compiled execution.
2. Implement and test one-node, sequential, branching, and bounded-loop graphs without an LLM.
3. Integrate an Anthropic chat model while distinguishing a stateless wrapper from a tool-using agent and from a memory-enabled application.
4. Manage human/AI/tool messages and explain overwrite versus reducer-based updates, process-local history versus durable persistence, and valid tool-call/result pairing.
5. Build a tool loop and an iterative document assistant with explicit termination and controlled file side effects.
6. Build a retrieval-backed graph, inspect retrieved evidence and citations, and test answers to both document-supported and out-of-domain questions.
7. Identify where historical examples need modernization and state which behavior remains unverified rather than treating old code as a production guarantee.

Observability and cross-project synthesis are outcomes of the **supplementary track**, not claims about the video curriculum.

## Sequence, duration, and scheduling

Each core lesson retains its original video window. The video itself spans **3h 09m 51s**; source viewing or selected clips are included in guided instruction below, not added on top. Guided instruction includes explanation and labeled API comparisons. Practice includes coding/debugging. Checks include reflection and evidence review. Breaks, setup, and optional labs are excluded.

| Lesson | Topic in original order | Source window | Guided | Practice | Check | Total |
|---|---|---|---|---|---|---|
| L01 | Python foundations and LangGraph elements | 00:00:00–00:18:39 | 45 min | 45 min | 10 min | 100 min |
| L02 | Hello World Graph | 00:18:39–00:33:07 | 25 min | 35 min | 10 min | 70 min |
| L03 | Graph II: Multiple Inputs | 00:33:07–00:44:29 | 25 min | 40 min | 10 min | 75 min |
| L04 | Sequential graph with multiple nodes | 00:44:29–00:55:36 | 25 min | 45 min | 10 min | 80 min |
| L05 | Graph 4: Conditional Graphs | 00:55:36–01:14:14 | 40 min | 60 min | 15 min | 115 min |
| L06 | Graph 5: Loops and Conditional Routing | 01:14:14–01:31:01 | 35 min | 60 min | 15 min | 110 min |
| L07 | First AI agent: simple bot | 01:31:01–01:42:54 | 30 min | 40 min | 10 min | 80 min |
| L08 | Conversation memory | 01:42:54–02:03:20 | 45 min | 65 min | 15 min | 125 min |
| L09 | ReAct agent with tools | 02:03:20–02:28:46 | 50 min | 80 min | 20 min | 150 min |
| L10 | Drafter collaboration | 02:28:46–02:52:09 | 50 min | 90 min | 20 min | 160 min |
| L11 | RAG and course outro | 02:52:09–03:09:51 | 45 min | 95 min | 20 min | 160 min |

**Core total: 1,225 minutes / 20h 25m.** Longer lessons can be split into two meetings without reordering their material. Optional update/observability/capstone labs add up to **510 minutes / 8h 30m** if all are selected. The core plus every optional lab totals **1,735 minutes / 28h 55m**, excluding setup and breaks. These are teaching estimates including practice, not guarantees of learner speed.

## L01 — Python foundations and LangGraph elements

**Prerequisite:** basic Python functions, collections, and control flow. **Time:** 45 minutes guided + 45 practice + 10 check. **Video:** [00:00:00–00:18:39](https://youtu.be/jGg_1h0qzaM?t=0s).

**VIDEO-BACKED focus:** course scope (00:00:02–00:01:21); typed dictionaries and annotations (00:01:24–00:04:20); `Union`, `Optional`, `Any`, and lambda/map (00:04:24–00:08:33); state/nodes/graphs (00:08:36–00:11:34); edges/boundaries (00:11:35–00:13:59); tools/state graphs/runnables/messages (00:14:01–00:18:39).

**Learning outcomes:** define a typed state with string and integer fields; annotate a function with a union and an optional return; distinguish a node from a tool; draw and narrate a graph with a conditional branch.

**Practice:** there is **no original hands-on assignment** in this source window. ADDED PRACTICE: create a small profile-state schema, write two deterministic state functions, and draw a two-node workflow with a branch and explicit stopping point. Explain the difference between a type annotation and runtime validation; do not make a model call.

**CURRENT-API UPDATE:** introduce `StateGraph(State)`, ordinary function nodes, explicit START/END edges, and compilation as the implementation vocabulary. START/END are sentinels, not work nodes. Mark the historical function-message explanation as legacy/imprecise; use human/system/AI/tool terminology for later implementation.

**Check / planned learner evidence:** a typed-state snippet, graph sketch, and a short explanation matching each edge to its routing condition. Check whether the learner can distinguish control flow from the data carried in state.

**Source caveat:** noisy captions and a repeated outro/next-section boundary; no original model/provider implementation is established. No frame review has been completed.

## L02 — Hello World Graph

**Prerequisite:** L01. **Time:** 25 guided + 35 practice + 10 check. **Video:** [00:18:39–00:33:07](https://youtu.be/jGg_1h0qzaM?t=18m39s).

**VIDEO-BACKED focus:** minimal graph objectives (00:19:53–00:20:56); message state and greeting function (00:21:11–00:26:10); graph registration/boundaries (00:26:13–00:29:34); compile/visualize/invoke (00:29:39–00:31:59).

**Learning outcomes:** define one state field and one processing node; register the node and compile the graph; invoke the compiled graph with a name; inspect a returned message and explain why compilation alone does not prove correct behavior.

**Original exercise, 00:32:03–00:33:07:** make a personalized compliment graph. Preserve the supplied name through concatenation rather than replacing it. Use Bob and the intended output “Bob, you're doing an amazing job learning LangGraph.” First reproduce the deterministic greeting baseline; then attempt the compliment task before consulting the repository answer.

**CURRENT-API UPDATE:** teach explicit START → greeter → END edges and a partial state-update dictionary, comparing them with the historical entry/finish and in-place mutation style. No LLM is introduced. IPython graph rendering is optional if the environment does not support it; a manually drawn topology can check understanding without claiming a visual review of the source video.

**Check / planned learner evidence:** runnable graph and two input/output cases showing name preservation. Ask the learner to point to builder creation, compilation, and invocation separately.

**Source caveat:** exact historical import source is not recoverable from captions. The supplied review identifies `Graphs/Hello_Word.ipynb`; no execution or code-screen verification is claimed.

## L03 — Graph II: Multiple Inputs

**Prerequisite:** L02; lists and arithmetic. **Time:** 25 guided + 40 practice + 10 check. **Video:** [00:33:07–00:44:29](https://youtu.be/jGg_1h0qzaM?t=33m7s).

**VIDEO-BACKED focus:** mixed state fields (00:33:09–00:36:08); summing and greeting in one processor (00:36:10–00:37:56); compiled app invocation (00:38:00–00:41:33); before/after state and omitted-result discussion (00:41:38–00:43:14).

**Learning outcomes:** define list/string state fields; read several inputs in one node; derive and select a formatted result; choose addition or multiplication with a Python `if` while retaining one graph node.

**Original exercise, 00:43:20–00:44:29:** accept a name, list of integers, and an operation. Add all values for `+` or multiply all values for multiplication. Keep the conditional **inside the same node**; do not add an extra graph node yet. Preserve the example Jack Sparrow with `[1, 2, 3, 4]` producing 24 for multiplication. Explicitly document the adapted input contract as `+`/`*`, since exact source tokens are unclear.

**CURRENT-API UPDATE:** use partial updates and explicit boundaries. Initialize required input/output expectations deliberately; do not teach that every omitted `TypedDict` field automatically becomes `None`. The graph builder is not the compiled executable. Input/output/context-schema features can be named as later options but are not required here.

**Check / planned learner evidence:** one-node topology; one addition and one multiplication test; clean access to `result`. ADDED PRACTICE: reject an unsupported operation with a documented error instead of silently selecting a branch.

**Source caveat:** captions omit roughly the first two seconds. The presenter's `None` explanation is not a universal current-runtime guarantee. No model is involved.

## L04 — Sequential graph with multiple nodes

**Prerequisite:** L03; string formatting. **Time:** 25 guided + 45 practice + 10 check. **Video:** [00:44:29–00:55:36](https://youtu.be/jGg_1h0qzaM?t=44m29s).

**VIDEO-BACKED focus:** shared name/age/final state and two nodes (00:44:33–00:47:50); intentional overwrite and concatenation fix (00:48:00–00:49:35); directed topology and invocation with Charlie, age 20 (00:49:38–00:52:52); repeated-update recap (00:52:53–00:54:06).

**Learning outcomes:** connect sequential nodes with directed edges; inspect state after each update; explain why a later write replaces an earlier string; preserve earlier output while extending the workflow.

**Original exercise, 00:54:09–00:55:34:** create three nodes for the person's name, age, and skills. Welcome the person, describe their age, list skills, and combine the pieces into one result. Retain Linda, age 31, with Python/machine learning/LangGraph skills as the example. Use two connecting `add_edge` calls between nodes plus boundary connections. The review identifies `Exercises/Exercise_Graph3.ipynb` as the answer cross-reference.

**CURRENT-API UPDATE:** use partial updates and START/END edges. Teach overwrite as default behavior without a reducer; manually preserving a string is not the same as automatic reducer accumulation. Use explicit edges rather than a sequence shorthand for the first implementation.

**Check / planned learner evidence:** three-node diagram and output containing all three profile components in order. Before fixing the example, have the learner predict the overwrite result; then show a test that catches the lost greeting.

**Source caveat:** exact separators, f-string punctuation, and historical final-key spelling are uncertain. This is the course's third graph, but lesson L04; do not renumber the sequence to match graph labels.

## L05 — Graph 4: Conditional Graphs

**Prerequisite:** L04; returning values from conditional functions. **Time:** 40 guided + 60 practice + 15 check. **Video:** [00:55:36–01:14:14](https://youtu.be/jGg_1h0qzaM?t=55m36s).

**VIDEO-BACKED focus:** arithmetic state and separate adder/subtractor nodes (00:56:41–01:00:00); route labels (01:00:00–01:02:42); routing result versus state update (01:03:21–01:05:54); START, path map, conditional edges, END, compilation and invocation (01:06:02–01:11:51).

**Learning outcomes:** separate routing from arithmetic processing; return a route label instead of a state dictionary from the routing callable; use a path map; combine two conditional sections while preserving both results.

**Practice:** first rebuild the demonstrated two-number graph using `number1`, `operation`, `number2`, and `finalNumber`. **Original exercise, 01:13:11–01:14:14:** accept four numbers and two operations, chain two conditional sections, and output both pairwise results. Preserve 10 − 5 = 5 and 7 + 2 = 9. The second pair is independent arithmetic, not an instruction to apply the next operation to the first answer.

**CURRENT-API UPDATE:** retain explicit START/END edges; use partial updates and a correct route return annotation or path map. Entry/finish helpers remain documented alternatives; do not describe them as removed. Fix the historical route function's state-return annotation when the actual return is a string.

**Check / planned learner evidence:** a path-map explanation, tests for addition/subtraction, and a two-section result showing both answers. ADDED PRACTICE: validate unsupported operations before routing. Ask the learner to compare this graph-level branch with L03's within-node `if`.

**Source caveat:** a caption says “7 + 7 + 2”; inherited repository corroboration establishes 7 + 2. The diagram has not been visually verified.

## L06 — Graph 5: Loops and Conditional Routing

**Prerequisite:** L05; counters and random-number generation. **Time:** 35 guided + 60 practice + 15 check. **Video:** [01:14:14–01:31:01](https://youtu.be/jGg_1h0qzaM?t=1h14m14s).

**VIDEO-BACKED focus:** graph blueprinting (01:15:49–01:18:09); name/list/counter state and greeting/random nodes (01:18:09–01:22:25); loop condition/five-pass goal (01:22:31–01:25:28); construction and robustness check (01:25:29–01:28:42).

**Learning outcomes:** implement a conditional back-edge; reset/normalize an initial counter; stop after exactly five number generations; use bounded state to implement an automatic feedback game.

**Practice:** rebuild START → greeting → random with a random-to-random or random-to-END condition. Initialize an empty number list and verify five entries, including a negative initial counter that is normalized by greeting. **Original exercise, 01:29:22–01:31:01:** automatic higher/lower game with player name `Student`, empty guesses, attempts 0, bounds 1–20, hint-based bound updates, and no more than seven guesses. It must run without human intervention.

**CURRENT-API UPDATE:** return state updates, make termination explicit, and use a suitable recursion limit as a safety net. Explain that a recursion-limit exception is not the intended normal termination. Do not accidentally combine competing static and conditional outgoing paths from the same source.

**Check / planned learner evidence:** loop diagram, five-number assertions, and game traces for early success and maximum-attempt exit. ADDED PRACTICE: control randomness/guess choices in tests so both paths are exercised reliably rather than waiting for chance.

**Source caveat:** exact random output, route name, annotation syntax, and edge-map syntax are uncertain. Do not use a specific caption-rendered random sequence as an expected result. This exercise is not human-in-the-loop and does not use an LLM.

## L07 — First AI agent: simple bot

**Prerequisite:** L01–L06; prepared Anthropic environment. **Time:** 30 guided + 40 practice + 10 check. **Video:** [01:31:01–01:42:54](https://youtu.be/jGg_1h0qzaM?t=1h31m1s).

**VIDEO-BACKED focus:** AI section objectives and integration setup (01:31:04–01:34:37); message state/model setup (01:35:32–01:37:26); process node and single-node graph (01:37:29–01:39:20); input loop and Bob/name test (01:39:25–01:42:05); explicit “not yet an agent” and no-exercise outro (01:42:00–01:42:53).

**Learning outcomes:** invoke a chat model from a graph node; construct a human message; run a shell loop with an exit sentinel; prove from the submitted message payload that repeated fresh invocations carry no conversation history.

**Exercise status:** the original assigns **no exercise**. ADDED PRACTICE: rebuild START → process → END with ChatAnthropic, send “my name is Bob,” then ask for the name in a separate invocation containing only that new user message. Inspect inputs to establish absent memory; do not require a specific model sentence or assume a model cannot coincidentally guess the name.

**CURRENT-API UPDATE:** original ChatOpenAI/GPT-4o is replaced with `langchain-anthropic` / `ChatAnthropic` and `ANTHROPIC_API_KEY`. Select a supported Claude model and omit unsupported sampling overrides. Introduce message-state/reducer vocabulary carefully, but retain the stateless baseline. Do not add a checkpointer yet and accidentally remove the contrast that L08 needs.

**Check / planned learner evidence:** redacted invocation inputs, two outputs, and a short explanation of why a Python `while` loop is not memory and why a single model wrapper is not the tool-loop agent of L09.

**Source caveat:** historical cost claims are not current pricing guidance; exact responses are not guaranteed or newly tested. Provider/model evidence is inherited from transcript and repository review, not code execution here.

## L08 — AI agent with conversation memory

**Prerequisite:** L07; message lists and text-file I/O. **Time:** 45 guided + 65 practice + 15 check. **Video:** [01:42:54–02:03:20](https://youtu.be/jGg_1h0qzaM?t=1h42m54s).

**VIDEO-BACKED focus:** human/AI-message union (01:44:05–01:46:38); invoke/append/history loop (01:47:49–01:51:54); Steve recall and predict-the-state prompt (01:52:00–01:55:53); restart and text logging (01:55:59–02:00:57); history/token growth and trimming heuristic (02:00:59–02:03:01).

**Learning outcomes:** send accumulated human/AI turns; predict the next message list; distinguish process-local memory from restoration after restart; preserve raw human text in a labeled log; describe a bounded-history policy and its trade-offs.

**Source-backed walkthrough practice:** build human/AI history, send “my name is Steve,” predict state after another such turn, restart and inspect the cleared process-local history, and write role-labeled turns to `logging.txt`. Include a deliberate spelling mistake and verify the stored user text remains unchanged. These are narrated activities, not a claim that a separate original homework assignment exists.

**CURRENT-API UPDATE:** adapt all model calls to Anthropic. Compare the manual-history demonstration with `MessagesState`/`add_messages` updates, avoiding duplicate appends. Explain ID-aware message updates. Treat `logging.txt` as a prototype log, not resumable or concurrency-safe persistence. Replace the arbitrary “remove the oldest human message after five” idea with an explicitly labeled improved policy that preserves valid turn structure; no production guarantee follows from a five-message threshold.

**Check / planned learner evidence:** before/after message snapshots, a synthetic labeled log, and a memory comparison covering fresh calls, process history, logs, and checkpoints. Have the learner explain why deleting a human message alone can leave an invalid or misleading conversation. Durable restart behavior is reserved for U1.

**Source caveat:** exact historical GPT-4 variant and some state-assignment details are unclear. The recap ends mid-sentence at 02:03:20; no missing instruction is invented.

## L09 — AI Agent 3: ReAct agent with tools

**Prerequisite:** L08; typed functions, docstrings, and conditional routing. **Time:** 50 guided + 80 practice + 20 check. **Video:** [02:03:20–02:28:46](https://youtu.be/jGg_1h0qzaM?t=2h3m20s).

**VIDEO-BACKED focus:** ReAct and typing (02:03:26–02:08:18); roles/reducers (02:08:22–02:13:25); tools/binding/model node (02:13:28–02:18:21); `ToolNode` and conditional loop (02:18:28–02:22:12); docstring failure and single/multiple/sequential/no-tool tests (02:22:16–02:28:46).

**Learning outcomes:** define typed tools with usable docstrings; bind tool schemas to a model; route based on tool calls; connect tool results to the requesting call; stop when the model returns without further tools.

**Source-backed lab:** rebuild the add-tool graph, then add subtract and multiply. Test 3 + 4, 34 + 21, two additions, and “add 40 + 12 then multiply the result by 6” with the demonstrated final result 312. Include a no-tool request and a mixed request to inspect end/loop behavior. This follows the demonstration; do not label it as independently confirmed original homework.

**CURRENT-API UPDATE:** use Anthropic and `bind_tools`. Explain that binding provides tool schemas but does not execute functions or force tool use; the application executes requests and returns matching tool results. Contrast LangChain message abstractions with Anthropic `tool_use`/`tool_result` blocks. Explain that `add_messages` includes message-ID handling rather than just appending blindly.

**Check / planned learner evidence:** tool definitions, route diagram, and structured call/result records for one call and sequential calls. ADDED PRACTICE: verify matching tool-call IDs and a bounded loop/error path. Inspect observable actions/results, not private chain-of-thought. Trace-service integration is optional S1/S2, not a source topic or core requirement.

**Source caveat:** exact historical model string and output helper are uncertain; narration mentioning streaming does not identify a verified current streaming API. The email example is not evidence of an implemented validator.

## L10 — Drafter: human–AI document collaboration

**Prerequisite:** L09; exceptions, files, and user input. **Time:** 50 guided + 90 practice + 20 check. **Video:** [02:28:46–02:52:09](https://youtu.be/jGg_1h0qzaM?t=2h28m46s).

**VIDEO-BACKED focus:** requirements and save termination (02:28:48–02:31:05); global buffer, state, update/save tools (02:31:08–02:36:31); input/model/routing (02:36:31–02:43:15); graph/runner and caveats (02:43:19–02:45:51); live email revisions/save and clarification behavior (02:45:53–02:51:24).

**Learning outcomes:** maintain a draft through revisions; build update/save tools; return to human feedback when appropriate; terminate after a successful save; explain why a global document buffer is unsafe for concurrent users.

**Source-backed lab:** draft an email to Tom, add meeting time, revise sender/name/location/time, request formatting, and save. Use `Unable_to_Attend_Meeting_Email.txt` as the source-demo filename example. Start from an existing document and try “write an email” without details, observing whether the model asks clarifying questions rather than assuming every prompt requires a tool call.

**CURRENT-API UPDATE:** replace repository-confirmed GPT-4o/ChatOpenAI with ChatAnthropic. Explain the original global-buffer workaround without endorsing it for production. Save within a controlled output directory and validate intended file names in the adaptation. Core study may use a single-session prototype with explicit limitations; ToolRuntime/injected state and a checkpointer/store belong to advanced lab U2. Do not label the source's terminal input loop as an implemented durable `interrupt`/resume system.

**Check / planned learner evidence:** draft/revision sequence, synthetic saved file, successful-save exit, and an explanation of clarification without tools. ADDED PRACTICE: deliberately fail a save and verify that failure does not masquerade as a successful terminal state. Multi-user isolation is assessed in U2, not silently claimed here.

**Source caveat:** homework ends as a truncated sentence at 02:52:08.800; no missing homework is reconstructed. Exact model setup is inherited repository evidence. The narrated file verification is not independently checked against frames or disk.

## L11 — Retrieval-Augmented Generation graph and course outro

**Prerequisite:** L09–L10; tool loops and file paths. **Time:** 45 guided + 95 practice + 20 check. **Video:** [02:52:09–03:09:51](https://youtu.be/jGg_1h0qzaM?t=2h52m9s).

**VIDEO-BACKED focus:** RAG/model/embedding introduction (02:52:11–02:55:01); PDF loading and page count (02:55:01–02:56:33); splitting (02:56:33–02:57:59); Chroma/retrieval (02:57:59–03:00:39); retrieval tool, grounding prompt, nodes, and loop (03:00:39–03:06:35); supported/out-of-domain tests (03:06:35–03:09:11); nontechnical outro (03:09:12–03:09:51).

**Learning outcomes:** describe retrieval plus generation; inspect PDF pages and chunks; create a persistent vector collection with a consistent embedding choice; invoke a retrieval tool from a model loop; inspect citations and recognize an answer unsupported by the document.

**Source-backed lab:** use the source's nine-page Stock Market Performance 2024 PDF; load/check page count; split at the reviewed configuration of size 1000 and overlap 200; persist Chroma; retrieve `k=5`; build model/retriever nodes with a conditional loop. Ask how the S&P 500 performed in 2024, inspect retrieved passages and cited answer, then ask about OpenAI performance in 2024 outside the PDF. The expected assessment is document-grounded support or an explicit lack-of-information response, not memorizing an exact model sentence.

**CURRENT-API UPDATE:** use ChatAnthropic plus a separately selected non-OpenAI embedding provider. Use appropriate separate Chroma/splitter integration packages. Teach the shown default splitter sizes as **characters**, not tokens, unless an explicit token length function is added and labeled. Correct the original nonportable Windows path and undefined `our_tool` in the reviewed tool dictionary. Do not blindly copy `temperature=0` into models that reject sampling overrides. Retain consistent embedding configuration for persisted collections.

**Check / planned learner evidence:** verified input asset/page count, chunk/retrieval metadata, portable collection path, one supported answer with inspectable citations, and one out-of-domain response. The narrated approximate 23% S&P result is a source-demo reference to check against the PDF, not a newly verified financial fact. ADDED PRACTICE: test an empty-retrieval path and explain why retrieval reduces but does not eliminate hallucinations.

**Source caveat:** the first roughly two seconds are absent from captions; full numeric output is incomplete; PDF availability/content and citations have not been independently verified. If the original PDF cannot be obtained, label any replacement as an adaptation and do not claim the source page count or example answer applies to it. The outro is not a capstone assignment.

## Optional current-API update labs — outside core time

These labs extend modern implementation skills while preserving the original 11-lesson sequence. They are not original video lessons or assignments, and have no source-video timestamp.

### U1 — Thread memory and persistence comparison

**Placement/prerequisite:** after L08. **Estimate:** 15 minutes guided + 35 practice + 10 check = **60 minutes**.

**Outcomes:** use a message reducer with a checkpointer and stable thread ID; distinguish same-thread continuity from different-thread isolation; explain the restart limits of an in-memory saver; identify what durable persistence needs.

**Practice and evidence:** repeat the name test within one thread and across two threads. Inspect isolation. Use an in-memory checkpointer for the continuity example, then design or implement a separately labeled durable checkpointer/restoration path if supported by the selected environment. Never call an in-memory saver restart-durable. Provide a short comparison table and test evidence for whichever persistence behavior is actually implemented.

**Reviewed reference:** [LangGraph memory](https://docs.langchain.com/oss/python/langgraph/add-memory). Backend/version choices remain to be checked before coding.

### U2 — Safe Drafter state and isolation

**Placement/prerequisite:** after L10; L09 tools. **Estimate:** 20 guided + 55 practice + 15 check = **90 minutes**.

**Outcomes:** replace a global draft with runtime-injected state; keep two sessions isolated; separate the editable draft from saved output; explain which state is persisted and where.

**Practice and evidence:** adapt the reviewed ToolRuntime/injected-state direction to the pinned package versions, add a checkpointer or store, run two synthetic document sessions, and verify that one cannot overwrite the other's draft. Check save-failure behavior and document any remaining concurrency limits. A durable interrupt/resume workflow is an additional design choice, not something to attribute to L10.

**Reviewed references:** [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents).

## SUPPLEMENTARY observability and capstone track

The video does **not** teach LangSmith or LangWatch. These labs are optional course additions without video timestamps. Choose one tracing platform or study both comparatively; do not require double transmission of the same learner data. Use Anthropic model calls throughout. Treat setup and exact SDK signatures as implementation checks, not verified integrations in this document.

### S1 — LangSmith graph, model, and tool observability

**Placement/prerequisite:** after L09; working model/tool graph and approved tracing setup. **Estimate:** 20 guided + 55 practice + 15 check = **90 minutes**.

**Outcomes:** inspect a graph run and its node/model/tool structure; identify a failed tool or unexpected loop; attach non-sensitive metadata; define a small, repeatable evaluation set.

**Practice and evidence:** trace an arithmetic graph and the ReAct loop, inspect a deliberate tool failure, and compare observable paths. After L11, optionally reuse the technique for retrieval/citation checks. Submit redacted span evidence and a short evaluation checklist covering output correctness, expected tool use, and failure handling. Tracing is not itself an evaluation pass and does not require exposing private model reasoning.

**Reviewed references:** [LangSmith observability](https://docs.langchain.com/langsmith/observability), [trace LangGraph](https://docs.langchain.com/langsmith/trace-with-langgraph). Review environment configuration and avoid logging API-key values or sensitive prompts.

### S2 — LangWatch callback-based observability

**Placement/prerequisite:** after L09; working graph and approved LangWatch setup. **Estimate:** 20 guided + 55 practice + 15 check = **90 minutes**.

**Outcomes:** connect the reviewed callback approach at graph invocation; inspect deterministic node steps as well as model/tool spans; compare normal and failure paths; explain consent/redaction and data boundaries.

**Practice and evidence:** instrument a deterministic loop and the Anthropic tool graph. Check that graph/node transitions are visible rather than assuming only LLM calls are traced. Optionally extend to RAG after L11. Provide redacted span evidence and an explanation of where callbacks/configuration are attached. State any missing spans or unsupported SDK behavior rather than claiming successful coverage without inspection.

**Reviewed references:** [LangWatch LangGraph integration](https://langwatch.ai/docs/integration/python/integrations/langgraph), [LangWatch LangChain integration](https://langwatch.ai/docs/integration/python/integrations/langchain).

### S3 — Capstone: grounded drafting assistant

**Placement/prerequisite:** after L11; preferably U1/U2 and at least one tracing lab. **Estimate:** 25 minutes design review + 130 practice + 25 evidence review = **180 minutes**. Larger deployments require additional time and are outside this estimate.

**Status:** entirely SUPPLEMENTARY. This is not a twelfth source lesson, the video's final homework, or a reconstruction of truncated captions.

**Brief:** combine the RAG evidence workflow with a document-drafting workflow over synthetic/local approved content. Keep retrieval, human revision, safe save, and termination explicit; use Anthropic for chat and a documented non-OpenAI embedding choice. Decide the required memory/isolation behavior before building.

**Expected evidence:** a state/topology design; an implementation with declared dependency/model choices; tests for one grounded question, one unsupported question, a revision, a successful save, a failed save, and bounded termination; and redacted traces from at least one chosen observability platform. Document limitations and distinguish observed behavior from intended behavior. Do not claim multi-user durability unless implemented and tested. A GUI, voice interface, or additional knowledge base is an optional stretch, not a required source exercise.

## Assessment approach

For L02–L06, assess deterministic outputs and state/route invariants rather than polished prose. Require learners to attempt the original exercise before using the source answer. For L07–L11, inspect message payloads, call/result structure, state transitions, citations, and failure handling in addition to the final model response; avoid asserting that an exact model sentence or tool choice is guaranteed on every run.

A core lesson's planned evidence should establish three things: the intended state/control flow, a successful representative run or clearly stated implementation blocker, and an explanation of the relevant limitation. Optional labs add isolation/persistence and observability evidence. These criteria are a proposed assessment design; they do not certify that any learner or implementation has passed.

## Source and uncertainty register

| Area | Teaching/publication rule |
|---|---|
| Transcript versus visuals | Attribute narrated material to reviewed captions. Visual review of frames, diagrams, on-screen imports, and outputs remains pending. |
| Missing/garbled captions | Retain the L03/L11 opening gaps, L08 cut-off recap, and L10 incomplete homework. Do not invent missing instruction. |
| Original provider history | L01–L06 have no model calls. L07 uses GPT-4o in the source; L08's exact GPT-4 variant is unclear; L09's exact model string is unclear; L10/L11 provider details inherit repository confirmation. All adapted model calls use Anthropic. |
| API guidance | Supplied current-API notes are modernization inputs, not proof of present package compatibility. Pin and test imports, runtime state, model/tool support, sampling rules, and callback APIs later. |
| State and memory | Do not universalize omitted-key-to-`None` behavior; do not call a log or an in-memory saver durable; do not call a global buffer multi-user safe. |
| RAG | Verify the source asset and nine-page count; correct character/token terminology and inherited code/path defects; check citations against retrieved pages. The approximate stock-return demo is not independent financial research. |
| Supplementary scope | LangSmith, LangWatch, advanced persistence/state labs, and the capstone have no original lesson timestamps. Keep their time and attribution separate. |

The detailed [source map](video_source_map.md) contains per-lesson source links, timestamp anchors, inherited corroboration, and unresolved evidence items. These two foundation files should guide future authoring and verification; they do not imply that visual review, handbooks, runnable examples, or optional integrations are complete.
