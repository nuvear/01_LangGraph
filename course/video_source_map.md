# Video source map: LangGraph course

**Whole-track update, 3 November 2026:** after these initial caption-section reviews, the parent review inspected 36 timestamped video frames across the complete source and checked the captions across chapter boundaries. See [visual-review record](video_visual_review.md) for the evidence and corrections. L08's recap and L10's homework invitation continue into the next editorial windows; the underlying caption track is not truncated there. The current approval draft is [the complete training index](training_index.md). Its capstone identifier C01 supersedes the initial planning label S3 below. Foundation code and the three service connections have now been tested separately; this does not establish completion of the lesson exercises or handbooks.

## Purpose and evidence boundary

This project foundation maps the source course into **11 lessons in the original video order** for students who know basic Python and are new to LangGraph. It establishes what later teaching material may attribute to the video, what needs a current-API rewrite, and what must be labeled supplementary. It is not a finished handbook, an executed implementation, or a declaration that the course has been completed.

**Primary sources:** [source video](https://youtu.be/jGg_1h0qzaM) and [original course repository](https://github.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp). The contiguous editorial windows below cover 00:00:00–03:09:51, including transitions and the final outro. These are lesson boundaries from the supplied review, not a claim that the video has exactly these chapter labels.

**Evidence used:** only the supplied structured reviews L01–L11. Their listed review artifacts are `.work/source-review/reviews/L01.md` through `L11.md`, relative to the project root. This editing pass did not independently reopen those artifacts, inspect source notebooks, execute code, research documentation, or view video frames. Repository corroboration and API guidance below are inherited from those reviews, not newly verified here. The supplied review-failure list was empty; that does not establish visual verification or runtime correctness.

### Attribution labels

- **VIDEO-BACKED / TRANSCRIPT:** concepts, narrated demonstrations, and explicitly identified exercises supported by the reviewed captions. Statements about code visible on screen remain unverified unless described as repository corroboration inherited from a review.
- **CURRENT-API UPDATE:** modernization guidance included in the supplied reviews. This is not a claim that the original presenter taught the newer pattern. Package versions, imports, model availability, and compatibility still need verification during implementation.
- **ADDED PRACTICE:** a new teaching activity based on the lesson, not original video homework.
- **SUPPLEMENTARY:** LangSmith/LangWatch observability, advanced persistence/runtime-state labs, and capstone work. These are not additional original lessons and must not be presented as material taught in this video.

**Review status:** transcript evidence has been reviewed in the supplied material; **frame-by-frame/video visual review has not been completed**. Auto-captions frequently duplicate lines and misrecognize names and code terms. Timestamps locate narrated material; they are not guarantees of exact on-screen code. Current-API recommendations retain their provenance as reviewed guidance rather than a fresh November 2026 compatibility audit.

## Sequence and pacing at a glance

Source duration is the length of each editorial window. Teaching estimates include source viewing or selected clips within guided instruction, explanation, API comparisons, hands-on practice, and checks; do not add source runtime again. They assume a working Python environment. Breaks, installation troubleshooting, account setup, and supplementary labs are excluded. See [syllabus](syllabus.md) for the instructional plan and assessment criteria.

| ID | Original-order lesson | Video window | Source duration | Guided / practice / check | Teaching total |
|---|---|---|---|---|---|
| L01 | Python foundations and LangGraph elements | 00:00:00–00:18:39 | 18m 39s | 45 / 45 / 10 min | 100 min |
| L02 | Hello World Graph | 00:18:39–00:33:07 | 14m 28s | 25 / 35 / 10 min | 70 min |
| L03 | Graph II: Multiple Inputs | 00:33:07–00:44:29 | 11m 22s | 25 / 40 / 10 min | 75 min |
| L04 | Sequential graph with multiple nodes: the third graph | 00:44:29–00:55:36 | 11m 07s | 25 / 45 / 10 min | 80 min |
| L05 | Graph 4: Conditional Graphs | 00:55:36–01:14:14 | 18m 38s | 40 / 60 / 15 min | 115 min |
| L06 | Graph 5: Loops and Conditional Routing | 01:14:14–01:31:01 | 16m 47s | 35 / 60 / 15 min | 110 min |
| L07 | First AI agent: simple bot | 01:31:01–01:42:54 | 11m 53s | 30 / 40 / 10 min | 80 min |
| L08 | AI agent with conversation memory | 01:42:54–02:03:20 | 20m 26s | 45 / 65 / 15 min | 125 min |
| L09 | AI Agent 3: ReAct agent with tools | 02:03:20–02:28:46 | 25m 26s | 50 / 80 / 20 min | 150 min |
| L10 | Drafter: human–AI document collaboration | 02:28:46–02:52:09 | 23m 23s | 50 / 90 / 20 min | 160 min |
| L11 | RAG graph and course outro | 02:52:09–03:09:51 | 17m 42s | 45 / 95 / 20 min | 160 min |

The source windows total **3h 09m 51s**. The proposed core teaching plan totals **1,225 minutes / 20h 25m**, including practice and checks. Estimates are editorial planning judgments, not source claims or learner-performance guarantees. Original graph numbering does not match lesson IDs: Graph II is L03, the third graph is L04, Graph 4 is L05, and Graph 5 is L06.

## L01 — Python foundations and LangGraph elements

**Source:** [video from the beginning](https://youtu.be/jGg_1h0qzaM?t=0s), 00:00:00–00:18:39. **Prerequisite:** basic variables, functions, lists, dictionaries, and `if` statements. **Teaching estimate:** 100 minutes including 45 minutes of practice.

### VIDEO-BACKED / TRANSCRIPT

| Time | Supported content |
|---|---|
| 00:00:02–00:01:21 | Course scope, audience assumptions, theory-first pacing, and promise of later exercises. |
| 00:01:24–00:04:20 | Type-annotation rationale; dictionaries and typed dictionaries. |
| 00:04:24–00:06:58 | `Union`, `Optional`, and `Any`. |
| 00:07:00–00:08:33 | Lambda and map example. |
| 00:08:36–00:11:34 | State, nodes, and graphs through conceptual analogies. |
| 00:11:35–00:13:59 | Ordinary/conditional edges and start/end boundaries. |
| 00:14:01–00:17:42 | Tools, tool nodes, state graphs, and runnable versus node. |
| 00:17:45–00:18:39 | Message-role terminology and closing/boundary material. |

**Exercise fidelity:** no hands-on exercise occurs in this window. The presenter promises later exercises and repository answers. A TypedDict task or graph sketch belongs under ADDED PRACTICE, not original homework.

**Actionable outcomes:** define a small typed state; distinguish state, node, edge, conditional edge, and tool; sketch a two-node workflow; explain why a message role matters.

### CURRENT-API UPDATE / ADDED PRACTICE

Teach `StateGraph(State)`, ordinary Python node functions, explicit `START`/`END` edges, conditional edges, and compilation. START and END are graph sentinels, not work-performing nodes; runs can also stop when no active work remains. Contrast modern `HumanMessage`, `SystemMessage`, `AIMessage`, and `ToolMessage` with the transcript's legacy/imprecise function-message description. Introduce `MessagesState` only as a preview. Added practice: type string/integer state fields, annotate `Union`/`Optional` functions, and draw a branch without calling an LLM.

**Uncertainties:** typed-dictionary wording and the state-graph phrase around 00:15:50 are garbled. The repeated outro/next-section opening near 00:18:32–00:18:39 is a boundary artifact. OpenAI is mentioned as a familiar API example, not evidence of an actual call or model in this lesson. No visual review is available.

**Reviewed references:** [Graph API usage](https://docs.langchain.com/oss/python/langgraph/use-graph-api), [quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart), [messages](https://docs.langchain.com/oss/python/langchain/messages).

## L02 — Hello World Graph

**Source:** [video at 00:18:39](https://youtu.be/jGg_1h0qzaM?t=18m39s), 00:18:39–00:33:07. **Prerequisite:** L01 state/node vocabulary and Python functions/dictionaries. **Teaching estimate:** 70 minutes including 35 minutes of practice.

### VIDEO-BACKED / TRANSCRIPT

| Time | Supported content |
|---|---|
| 00:18:39–00:20:56 | First coding graph; agents intentionally deferred; start/node/end objectives. |
| 00:21:11–00:24:25 | Imports, one-field `AgentState`, and a greeting-node function. |
| 00:24:31–00:26:10 | Docstring, message transformation, and state return. |
| 00:26:13–00:29:34 | `StateGraph`, `add_node`, entry point, and finish point. |
| 00:29:39–00:30:50 | Compilation versus logical correctness and IPython visualization. |
| 00:30:50–00:31:59 | Invoke with Bob and inspect the returned message. |
| 00:32:03–00:33:07 | Personalized compliment exercise and transition. |

**Original exercise:** build a one-node personalized compliment graph; concatenate with the supplied name rather than replacing it. The example intent is “Bob, you're doing an amazing job learning LangGraph.” Retain the deterministic greeting graph as the baseline.

**Actionable outcomes:** register and compile a Python node, invoke the compiled graph, inspect one result field, and preserve an existing state value when constructing an output.

### CURRENT-API UPDATE

Show `add_edge(START, 'greeter')` and a greeter-to-END edge alongside historical entry/finish terminology. Return a partial update such as `{'message': ...}` rather than mutate and return the entire input state. Compilation checks graph construction, not correctness of the greeting. No model is needed; an Anthropic extension would be extra, not the original task.

**Uncertainties:** exact `typing` versus `typing_extensions` imports are not established by captions. The review reports repository identity `Graphs/Hello_Word.ipynb` and exercise notebooks but does not establish execution. No original provider, model, or credentials are evident. Visualization is narrated, not visually verified.

**Reviewed references:** [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [Graph API usage](https://docs.langchain.com/oss/python/langgraph/use-graph-api), [original repository](https://github.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp).

## L03 — Graph II: Multiple Inputs

**Source:** [video at 00:33:07](https://youtu.be/jGg_1h0qzaM?t=33m7s), 00:33:07–00:44:29. **Prerequisite:** L02; lists and simple arithmetic. **Teaching estimate:** 75 minutes including 40 minutes of practice.

### VIDEO-BACKED / TRANSCRIPT

| Time | Supported content |
|---|---|
| 00:33:09–00:36:08 | Multiple-input objectives, imports, arbitrary state-class naming, and `values`, `name`, `result` fields. |
| 00:36:10–00:37:56 | One processor sums the list and formats a greeting; explicitly no LLM. |
| 00:38:00–00:40:16 | Build/compile; invoke the compiled app rather than the builder. |
| 00:40:20–00:41:33 | Steve with `[1, 2, 3, 4]`, sum 10; select `answers['result']`. |
| 00:41:38–00:43:14 | Print state before/after; discussion of omitted result and `None`. |
| 00:43:20–00:44:29 | Addition/multiplication exercise and transition. |

**Original exercise:** one graph, **one node**, a list of integers, a name, and an operation. Use an `if` inside that same node to add or multiply all elements. Example: Jack Sparrow and `[1, 2, 3, 4]` with multiplication produce an answer of 24. Do not move this exercise's branching into extra graph nodes.

**Actionable outcomes:** design mixed-type state, derive a result from several inputs, distinguish builder from compiled executable, and test both operation paths.

### CURRENT-API UPDATE

Use explicit START/END edges and partial updates. Do not generalize the presenter's omitted-result explanation into a guarantee that every missing typed key becomes `None`; initialize deliberately or define optionality explicitly in the implementation. More advanced input/output/context schemas are not required for the original exercise. The reviewed API guidance notes `config_schema` deprecation, but teaching it here would add unnecessary scope.

**Uncertainties:** captions start at 00:33:09.669, leaving roughly two seconds of the window unrepresented. Exact operation tokens are not fully specified; the adaptation should document its accepted `+` and `*` inputs as an implementation decision. The missing-result behavior is not independently tested. No model/provider is involved.

**Reviewed references:** [source notebook](https://github.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp/blob/main/Graphs/Multiple_Inputs.ipynb), [StateGraph reference](https://reference.langchain.com/python/langgraph/graph/StateGraph), [quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart).

## L04 — Sequential graph with multiple nodes: the third graph

**Source:** [video at 00:44:29](https://youtu.be/jGg_1h0qzaM?t=44m29s), 00:44:29–00:55:36. **Prerequisite:** L03; f-strings and string concatenation. **Teaching estimate:** 80 minutes including 45 minutes of practice.

### VIDEO-BACKED / TRANSCRIPT

| Time | Supported content |
|---|---|
| 00:44:33–00:46:06 | Sequential workflow goal, imports, and name/age/final state fields. |
| 00:46:08–00:47:50 | First node writes a greeting; second writes an age sentence. |
| 00:48:00–00:49:35 | Deliberate overwrite bug, then preservation/concatenation fix. |
| 00:49:38–00:52:22 | Node registration, directed edge, entry/finish connections, and narrated topology. |
| 00:52:24–00:54:06 | Charlie, age 20; combined output and recap. |
| 00:54:09–00:55:34 | Three-node exercise and two connecting-edge hint. |

**Original exercise:** accept a name, age, and skill list. Create three sequential nodes: welcome the person, describe their age, then format skills. Combine the pieces into one result. Retain the Linda example: age 31, Python/machine learning/LangGraph skills. Use two node-to-node `add_edge` calls, in addition to boundary connections. The review associates the answer with `Exercises/Exercise_Graph3.ipynb`.

**Actionable outcomes:** build and explain a linear topology, reproduce the overwrite bug, fix it deliberately, and extend the two-node graph to three nodes.

### CURRENT-API UPDATE

Use partial state updates and explicit START/END edges. Explain default overwrite behavior: concatenation here is manual preservation, not an automatic reducer. Reducers or separate intermediate keys are alternative designs, not hidden original behavior. Prefer explicit edges over `add_sequence` while teaching topology.

**Uncertainties:** exact f-string punctuation and the historical final-key spelling cannot be reliably recovered from captions. Exact legacy entry/finish method syntax is not audible with confidence. Narrated topology has not been checked against frames. No model/provider is used.

**Reviewed references:** [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [sequential graph guidance](https://docs.langchain.com/oss/python/langgraph/use-graph-api), [original repository](https://github.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp).

## L05 — Graph 4: Conditional Graphs

**Source:** [video at 00:55:36](https://youtu.be/jGg_1h0qzaM?t=55m36s), 00:55:36–01:14:14. **Prerequisite:** L04; Python conditional functions and return values. **Teaching estimate:** 115 minutes including 60 minutes of practice.

### VIDEO-BACKED / TRANSCRIPT

| Time | Supported content |
|---|---|
| 00:55:36–00:58:40 | Graph-level branching goal, imports, and arithmetic state schema. |
| 00:58:40–01:02:42 | Adder/subtractor nodes and routing function returning route labels. |
| 01:03:21–01:05:54 | Route result versus state update; pass-through `lambda state: state`. |
| 01:06:02–01:09:34 | START-to-router edge, `add_conditional_edges`, and label-to-node path map. |
| 01:09:38–01:11:51 | Branches to END, compilation, narrated visualization, and 10 − 5 invocation. |
| 01:11:56–01:14:14 | Recap and exercise chaining two conditional sections. |

**Demonstrated lab:** state carries `number1`, `operation`, `number2`, and `finalNumber`; route addition to an adder and subtraction to a subtractor. **Original exercise:** chain a second conditional section: four numbers, two operations, and two pairwise outputs. Preserve the intended example 10 − 5 = 5 and 7 + 2 = 9. Do not silently change it into applying the second operation to the first result.

**Actionable outcomes:** distinguish a routing label from a state update, build a path map, test both branches, and connect two branching sections sequentially.

### CURRENT-API UPDATE

Use explicit START/END edges, partial updates, and a routing return hint such as `Literal[...]` or an explicit path map. Current guidance still documents entry/finish helpers: do not repeat the presenter's stronger claim that they are no longer used. Without a map, route results should name destinations. Correct the inherited notebook annotation that identifies the route return as `AgentState` despite returning strings.

**Uncertainties:** captions around 01:13:42 say “7 + 7 + 2”; the supplied review reports repository corroboration of 7 + 2. The diagram is inferred from narration and inherited repository corroboration, not frame review. No LLM call appears.

**Reviewed references:** [conditional-edge reference](https://reference.langchain.com/python/langgraph/graph/state/StateGraph/add_conditional_edges), [source notebook](https://raw.githubusercontent.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp/main/Graphs/Conditional_Agent.ipynb), [exercise answer](https://raw.githubusercontent.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp/main/Exercises/Exercise_Graph4.ipynb).

## L06 — Graph 5: Loops and Conditional Routing

**Source:** [video at 01:14:14](https://youtu.be/jGg_1h0qzaM?t=1h14m14s), 01:14:14–01:31:01. **Prerequisite:** L05; counters, lists, random-number generation, and termination conditions. **Teaching estimate:** 110 minutes including 60 minutes of practice.

### VIDEO-BACKED / TRANSCRIPT

| Time | Supported content |
|---|---|
| 01:14:15–01:18:09 | Loop objective, blueprinting, greeting/random design, and pedagogical rationale. |
| 01:18:09–01:22:25 | State, greeting/counter reset, random append, and increment. |
| 01:22:31–01:25:28 | Conditional loop routing and intended five-pass trajectory. |
| 01:25:29–01:28:42 | Graph construction/compilation, demonstration, and robustness check. |
| 01:28:42–01:29:22 | Wrap-up. |
| 01:29:22–01:31:01 | Automatic higher/lower exercise; transition to AI agents. |

**Demonstrated lab:** START → greeting → random; random conditionally loops to itself or ends. State holds name, numbers, and counter; greeting resets the counter, random appends an integer and increments, and the loop ends after five generations. The reviewed summary describes random bounds of 0–10, but exact source syntax has not been visually checked.

**Original exercise:** an **automatic**, non-human-in-the-loop higher/lower game. Initialize `player_name='Student'`, `guesses=[]`, `attempts=0`, bounds 1–20; update bounds from hints; stop on success or after at most seven guesses. Retain these settings rather than replacing the task with interactive user guessing.

**Actionable outcomes:** draw and implement a loop, normalize initial counters, produce exactly five numbers, and test success and maximum-attempt exits in the game.

### CURRENT-API UPDATE

Return partial updates; make loop termination explicit and configure a suitable recursion limit as a safeguard rather than a substitute for correct stopping logic. Avoid combining ordinary and dynamic routing from the same source in a way that unintentionally schedules both paths. Use test control of randomness to exercise both game exit paths; that test technique is added pedagogy.

**Uncertainties:** routing function name, precise annotation syntax, edge-map syntax, and exact random outputs are not reliably recoverable from captions. One narrated loop count is inconsistent, but the surrounding explanation establishes five generations. Do not claim an exact random output sequence. No model is used.

**Reviewed references:** [Graph API usage](https://docs.langchain.com/oss/python/langgraph/use-graph-api), [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [exercise answer](https://github.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp/blob/main/Exercises/Exercise_Graph5.ipynb).

## L07 — First AI agent: simple bot

**Source:** [video at 01:31:01](https://youtu.be/jGg_1h0qzaM?t=1h31m1s), 01:31:01–01:42:54. **Prerequisite:** L01–L06; environment-variable concepts and access to an approved Anthropic account for the adaptation. **Teaching estimate:** 80 minutes including 40 minutes of practice.

### VIDEO-BACKED / TRANSCRIPT

| Time | Supported content |
|---|---|
| 01:31:04–01:34:37 | AI section objectives; simple topology; LangChain integration, dotenv, and keys. |
| 01:35:32–01:37:26 | Message state and original model setup/provider discussion. |
| 01:37:29–01:39:20 | `llm.invoke` inside a process node; graph edges and compilation. |
| 01:39:25–01:41:25 | One-shot invocation and Python input loop with exit sentinel. |
| 01:41:25–01:42:53 | Bob/name test, lack of memory, distinction from an agent, and no-exercise outro. |

**Original behavior:** a single START → process → END LLM wrapper, repeatedly invoked with a fresh human-message list. The source uses ChatOpenAI/GPT-4o according to transcript and inherited repository confirmation. The presenter explicitly says this is not yet a true agent. A Python input loop is not conversation memory.

**Exercise fidelity:** no original exercise is assigned. Rebuilding the bot and running the Bob/name test are ADDED PRACTICE based on the demonstration.

**Actionable outcomes:** place a chat call inside a graph node, explain message input/output, exit the shell loop, and demonstrate that fresh invocations do not remember a name.

### CURRENT-API UPDATE

Replace the original provider with `langchain-anthropic` / `ChatAnthropic` and `ANTHROPIC_API_KEY`; select a supported Claude model at implementation time. Retain statelessness first. Explain `MessagesState`/`add_messages` without silently adding a checkpointer and erasing the demonstration. Checkpointer/thread-ID memory belongs to the separately labeled update lab. Do not reproduce historical token-price claims or unsupported sampling settings.

**Uncertainties:** model responses were not independently executed; price claims are historical and approximate. The graph is repository/narration-corroborated, not frame-verified.

**Reviewed references:** [source program](https://raw.githubusercontent.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp/main/Agents/Agent_Bot.py), [Anthropic integration](https://docs.langchain.com/oss/python/integrations/chat/anthropic), [memory guidance for the separate update lab](https://docs.langchain.com/oss/python/langgraph/add-memory).

## L08 — AI agent with conversation memory

**Source:** [video at 01:42:54](https://youtu.be/jGg_1h0qzaM?t=1h42m54s), 01:42:54–02:03:20. **Prerequisite:** L07; lists, message roles, loops, and text-file writing. **Teaching estimate:** 125 minutes including 65 minutes of practice.

### VIDEO-BACKED / TRANSCRIPT

| Time | Supported content |
|---|---|
| 01:42:55–01:46:38 | Memory motivation, imports, and human/AI message union state. |
| 01:46:40–01:49:50 | Framework-control discussion; model invocation and appending an AI message. |
| 01:49:52–01:52:45 | Same graph shape, external history, full-history invocation, and Steve recall. |
| 01:52:57–01:55:53 | Message-state printout and learner prediction prompt. |
| 01:55:59–02:00:57 | Restart loses memory; text-file prototype, role labels, and preserved raw misspelling. |
| 02:00:59–02:03:20 | History growth/token cost, arbitrary five-human-message trimming idea, and cut-off recap. |

**Source-backed practice:** construct a human/AI-message history, invoke with all turns, predict the state after another “my name is Steve,” restart to observe lost memory, and write labeled turns to `logging.txt`. These are walkthrough activities and a pause/predict prompt, not evidence of a separate completed homework assignment. Design a bounded-history policy in response to the discussed growth problem.

**Actionable outcomes:** contrast stateless calls with process-local history, preserve original user text, explain why a log alone does not restore memory, and identify context/cost growth.

### CURRENT-API UPDATE

Use Anthropic rather than the original ChatOpenAI/GPT-4 references; the exact original GPT-4 variant is uncertain. Teach `MessagesState` or an `add_messages` channel without duplicating history through both manual append and reducer updates. `add_messages` also handles IDs and deserialization. A text log is not a production persistence system. Checkpointers/thread IDs are a separate extension; in-memory checkpoints do not survive restarts. Improve trimming while preserving valid human/AI/tool turn structure; deleting one oldest human message is not a general production policy.

**Uncertainties:** exact imports, state replacement code, and use of reducers in the historical code are not fully audible. `logging.txt` is disambiguated by the inherited repository review. The transcript stops mid-sentence at 02:03:20; do not reconstruct the missing ending. No frame review has been done.

**Reviewed references:** [original repository: Memory_Agent.py and logging.txt](https://github.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp), [memory guidance](https://langchain-ai.github.io/langgraph/concepts/memory/), [low-level state/message concepts](https://langchain-ai.github.io/langgraph/concepts/low_level/), [Anthropic integration](https://python.langchain.com/docs/integrations/chat/anthropic/).

## L09 — AI Agent 3: ReAct agent with tools

**Source:** [video at 02:03:20](https://youtu.be/jGg_1h0qzaM?t=2h3m20s), 02:03:20–02:28:46. **Prerequisite:** L08; typed functions, docstrings, conditionals, and message histories. **Teaching estimate:** 150 minutes including 80 minutes of practice.

### VIDEO-BACKED / TRANSCRIPT

| Time | Supported content |
|---|---|
| 02:03:26–02:08:18 | ReAct definition/topology, `Annotated`, and sequence annotations. |
| 02:08:22–02:13:25 | Message roles, reducers, `add_messages`, and state. |
| 02:13:28–02:18:21 | Add tool, original OpenAI model, tool binding, and system/model node. |
| 02:18:28–02:22:12 | Tool-call conditional route, `ToolNode`, agent loop, and compilation. |
| 02:22:16–02:25:47 | Single/multiple tool tests, docstring failure, and model-selected arguments. |
| 02:25:50–02:28:46 | Subtract/multiply, sequential result 312, no-tool path, and outro. |

**Source-backed lab:** rebuild the arithmetic tool loop, then add subtract and multiply. Test 3 + 4, 34 + 21, two additions, and “add 40 + 12 then multiply the result by 6.” Test a non-tool request and mixed input to inspect the exit branch. These follow demonstrated work; do not assert a separate original homework assignment. Tool-call ID inspection is added assessment practice.

**Actionable outcomes:** define documented typed tools, bind tool schemas, route on tool calls, return matching tool results, and explain repeated agent/tool transitions without confusing a tool request with tool execution.

### CURRENT-API UPDATE

Use Anthropic-only model calls, `bind_tools`, and valid tool-call/result pairing. At the direct Anthropic API layer these are `tool_use`/`tool_result` blocks connected by IDs; LangChain presents provider-neutral messages. `add_messages` is more than blind list concatenation. Tracing tools does not mean exposing private chain-of-thought: inspect observable calls, results, routes, and timing instead.

**Uncertainties:** original OpenAI/GPT-4o-like naming is clear in context, but exact model string, imports, output-formatting helper, and a specific streaming API are not recoverable. The email example does not establish a real validator implementation. The statement that an LLM “does not know math” is pedagogical shorthand, not a guarantee. Frames were not reviewed.

**Reviewed references:** [LangGraph quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart), [models and tool binding](https://docs.langchain.com/oss/python/langchain/models), [Anthropic tool use](https://docs.anthropic.com/docs/en/agents-and-tools/tool-use/overview).

## L10 — Drafter: human–AI document collaboration

**Source:** [video at 02:28:46](https://youtu.be/jGg_1h0qzaM?t=2h28m46s), 02:28:46–02:52:09. **Prerequisite:** L09; file writing, exceptions, user input, and side-effect awareness. **Teaching estimate:** 160 minutes including 90 minutes of practice.

### VIDEO-BACKED / TRANSCRIPT

| Time | Supported content |
|---|---|
| 02:28:48–02:32:17 | Requirements/topology; save must end; imports and global buffer workaround. |
| 02:32:21–02:36:31 | State, update/save tools, `.txt` handling, errors, model, and tool binding. |
| 02:36:31–02:43:15 | Agent system prompt/input, returned state, conditional termination, and formatting helper. |
| 02:43:19–02:45:51 | Build/compile/runner; global-variable caveat and advanced alternatives. |
| 02:45:53–02:49:24 | Email to Tom, iterative human revisions, save, and narrated file verification. |
| 02:49:24–02:51:24 | Existing-document initialization and clarifying question without tool use. |
| 02:51:34–02:52:08 | Voice/GUI/knowledge-base suggestions; truncated homework sentence. |

**Source-backed lab:** create Drafter's agent/tools graph and update/save tools. Draft an email, add meeting time, revise sender/name/location/time, request formatting, then save. Preserve the demonstrated filename `Unable_to_Attend_Meeting_Email.txt` as an example, not a mandatory model-generated output. Try an underspecified “write an email” request and observe clarification without a tool call. Homework wording is incomplete and must not be reconstructed.

**Actionable outcomes:** maintain an editable document, incorporate human revisions, distinguish tool binding from mandatory invocation, and end after a successful save. This is a human-feedback workflow, not evidence that a durable LangGraph `interrupt`/resume workflow was implemented.

### CURRENT-API UPDATE

Replace repository-confirmed `ChatOpenAI(model='gpt-4o')` with ChatAnthropic. The global document buffer is a beginner workaround, not safe multi-user state or durable persistence. Explain this limitation in the core lesson; implement ToolRuntime/injected state and a checkpointer or store in a separate advanced update lab. Adapt imports to the target package versions. Save only within an explicitly chosen working/output directory in the adaptation; this safeguard is added implementation policy.

**Uncertainties:** exact historical model setup comes from inherited repository corroboration, not clear audio. The supplied captions stop at 02:52:08.800 during “if you want a homework for this”; no full homework instruction is available. Later captions begin with a homework invitation, but its full content is still not established. Frames and saved files have not been independently inspected.

**Reviewed references:** [source program](https://raw.githubusercontent.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp/main/Agents/Drafter.py), [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents), [Anthropic integration](https://docs.langchain.com/oss/python/integrations/chat/anthropic).

## L11 — Retrieval-Augmented Generation graph and course outro

**Source:** [video at 02:52:09](https://youtu.be/jGg_1h0qzaM?t=2h52m9s), 02:52:09–03:09:51. **Prerequisite:** L09–L10; tool loops, file paths, basic documents, and willingness to learn retrieval terminology. No prior vector-database knowledge is assumed. **Teaching estimate:** 160 minutes including 95 minutes of practice.

### VIDEO-BACKED / TRANSCRIPT

| Time | Supported content |
|---|---|
| 02:52:11–02:55:01 | Transition/homework invitation, RAG topology, imports, original model and embeddings discussion. |
| 02:55:01–02:57:59 | Nine-page Stock Market Performance 2024 PDF, loading/page count, chunk size 1000, overlap 200. |
| 02:57:59–03:00:39 | Split pages, persistent Chroma collection, and similarity retrieval with `k=5`. |
| 03:00:39–03:03:31 | Retrieval tool, empty-result behavior, binding, message state, routing, grounding/citation prompt. |
| 03:03:31–03:06:35 | Model node, retrieval/tool-call handling, graph loop, compilation, interactive runner. |
| 03:06:35–03:09:11 | Vector-store creation; S&P 500 question; out-of-domain OpenAI question; conclusion. |
| 03:09:12–03:09:51 | Nontechnical course farewell and future-project encouragement. |

**Source-backed lab:** load the source nine-page PDF, split it, build/persist Chroma, expose top-five retrieval as a tool, and compile a two-node model/retriever loop. Ask about S&P 500 performance in 2024, inspect passages and citations, then ask about OpenAI performance in 2024 outside the PDF and inspect the absence-of-information response. “OpenAI” here is the subject of a test question, not permission to use an OpenAI model in the adaptation. The review reports approximately 23% in the narrated S&P example; treat it as source-demo content to check against the PDF, not independently researched market data.

**Actionable outcomes:** explain retrieval versus generation, inspect page/chunk metadata, create a portable vector store, connect retrieval tool results to generation, and evaluate grounded versus unsupported answers.

### CURRENT-API UPDATE

Replace original GPT-4o with ChatAnthropic and original `text-embedding-3-small` with a separately selected **non-OpenAI embedding provider**. Do not assume the chat provider supplies embeddings or that chat and embedding models must share a provider. Keep embedding choice/re-indexing policy explicit. Use `langchain-chroma` and `langchain-text-splitters` as appropriate to the target version. The shown default recursive splitter is **character-based**, despite the transcript saying “tokens”; token-based sizing requires an explicit token length function. Correct the inherited repository's nonportable Windows persistence path and undefined `our_tool` in `tools_dict`; do not copy those defects. Omit sampling overrides unsupported by the selected Claude model.

**Uncertainties:** captions start at 02:52:11.269, leaving roughly two seconds unrepresented. The chunk-unit statement conflicts with the reviewed code. Full numeric financial output and benchmark wording are incomplete. PDF availability/content, page count, citations, and runtime outputs have not been independently verified here. No frame review is complete.

**Reviewed references:** [source program](https://raw.githubusercontent.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp/main/Agents/RAG_Agent.py), [Chroma integration](https://docs.langchain.com/oss/python/integrations/vectorstores/chroma), [splitters](https://docs.langchain.com/oss/python/integrations/splitters), [Anthropic integration](https://docs.langchain.com/oss/python/integrations/chat/anthropic).

## Cross-course adaptation rules

1. **Preserve the deterministic runway.** L01–L06 do not need an LLM; do not replace state/routing exercises with chatbot prompts. Introduce model calls in L07, memory in L08, tool loops in L09, collaborative drafting in L10, and retrieval in L11.
2. **Preserve original exercise semantics.** L02 compliments; L03 same-node arithmetic; L04 three sequential profile nodes; L05 two pairwise conditional calculations; L06 automatic bounded guessing. L01 and L07 have no original assigned exercise. L08–L11 primarily supply walkthrough/demonstration practice, and L10's homework is incomplete.
3. **Anthropic-only adapted model calls.** Original OpenAI usage may be documented historically, never copied into adapted executable examples. Use supported Claude models through the reviewed integration guidance. Model IDs, cost, sampling controls, and dependency versions must be checked later; no fixed “latest” model is asserted here.
4. **Modernize without rewriting history.** Compare partial updates, START/END edges, proper routing types, message reducers, and safe tool results with historical patterns. Entry/finish helpers are not declared removed. Keep manual string preservation distinct from reducer accumulation.
5. **Separate memory levels.** Fresh calls, process-local message history, append-only logs, thread checkpoints, durable checkpoints, and cross-thread stores are different concepts. Avoid claims that a text log or in-memory saver survives restart without restoration/durable storage.
6. **Do not treat tracing as a source topic.** LangSmith/LangWatch work below is supplementary; logs/traces must not expose secrets, personal conversations, or unrestricted document contents.

## SUPPLEMENTARY material, outside the original 11 lessons

These items are course-design additions. They have **no video timestamp** and must remain outside the original lesson count and original source-runtime total. The syllabus allocates 510 optional minutes across these additions.

| Add-on | Placement and prerequisite | Purpose | Estimate |
|---|---|---|---|
| U1 — Current-API memory lab | After L08 | Contrast `MessagesState`/`add_messages`, thread IDs, in-memory checkpoints, and a durable persistence design; do not claim restart durability for an in-memory saver. | 60 min |
| U2 — Current-API safe Drafter state | After L10; L09 tools | Replace the global buffer with runtime-injected state and a checkpointer/store; test isolation. Advanced implementation choice, not original video code. | 90 min |
| S1 — LangSmith observability | After L09; may trace earlier graphs too | Trace graph/model/tool transitions, inspect tool failures and loops, attach non-sensitive run metadata, and design a small evaluation set. | 90 min |
| S2 — LangWatch observability | After L09; may trace earlier graphs too | Attach the reviewed callback pattern at graph invocation and inspect node/model/tool/retrieval spans with appropriate redaction. | 90 min |
| S3 — Capstone | After L11; preferably U1/U2 and at least one tracing lab | Combine a grounded assistant with a drafting workflow, bounded tools, tests, safe saves, and trace evidence. This synthesis is not the original RAG lesson or an inferred missing homework task. | 180 min |

**Reviewed supplementary references:** [LangSmith observability](https://docs.langchain.com/langsmith/observability), [LangSmith with LangGraph](https://docs.langchain.com/langsmith/trace-with-langgraph), [LangWatch LangGraph integration](https://langwatch.ai/docs/integration/python/integrations/langgraph), [LangWatch LangChain integration](https://langwatch.ai/docs/integration/python/integrations/langchain). Exact SDK APIs and trace payload policies remain implementation checks. A learner may choose one tracing platform; both are separate options, not a requirement to transmit the same data to two services.

## Open verification register

| Item | Known evidence | Remaining work before publication or runnable delivery |
|---|---|---|
| Visual/code-screen review | Transcript and inherited repository corroboration only | Inspect frames for diagrams, exact imports, code, and outputs; record visual evidence separately from captions. |
| Caption boundaries | Repeated outros; short gaps at L03 and L11; truncated L08/L10 endings | Preserve gaps; do not invent missing exercise text. Check source media if a later task authorizes it. |
| Historical notebook behavior | Reviewed descriptions, not new execution | Confirm exact source names/annotations and run adapted tests separately. |
| Modern APIs/models | Guidance already supplied with the reviews | Pin/test dependency versions; confirm supported Claude/tool behavior and sampling rules. |
| RAG asset and provider | Named nine-page PDF; original OpenAI embeddings identified | Verify asset availability/page count and usage rights; choose non-OpenAI embeddings, indexing policy, portable paths, and citation behavior. |
| Memory and tool state | Known limitations of logs/global buffers | Test restart behavior, thread isolation, tool-call/result integrity, and bounded loops. |
| Observability | Supplementary reference guidance only | Verify callback/configuration, consent/redaction, secrets exclusion, and evaluation design before sending traces. |

This source map authorizes no completion claim about handbooks, implementations, visual review, tests, or service integrations. It supplies the provenance and scope contract for that future work.
