# LangGraph Python Training

## Complete training index

**Draft v0.1 · 3 November 2026 · For scope approval**

A practical course for learners who know basic Python and are new to LangGraph. The training follows Vaibhav Mehra’s freeCodeCamp video, *LangGraph Complete Course for Beginners – Complex AI Agents with Python*, then adds current implementation practices, LangSmith, LangWatch, and a capstone.

**Source video:** https://youtu.be/jGg_1h0qzaM  
**Source duration:** 3 hours 9 minutes 51 seconds  
**Course repository:** https://github.com/nuvear/01_LangGraph  
**Adapted model provider:** Anthropic; configurable through the local `.env` file.

**Review basis.** The complete timestamped English caption track was reviewed across eleven contiguous sections. Thirty-six timestamped video frames were also inspected across the full runtime to check section identity, exercise slides, graph diagrams, code, demonstrations, and the outro. The linked original code was used to resolve selected ambiguities. This is a full-content review supported by sampled visuals, not a claim that every video frame was watched in real time. Auto-caption errors are not treated as reliable Python syntax.

**Current stage.** This document proposes the complete contents of the training. It is not the three finished handbooks. Detailed lesson writing will follow approval of this index. The environment, service checks, and initial graph examples have already been tested; the remaining course exercises and capstone have not yet been implemented or validated.

<!-- pagebreak -->

# 1. Course structure and learning path

## 1.1 How the index is organized

**P00 — Preparation:** environment setup, credentials, execution checks, and safe use of tracing.

**L01–L06 — Core foundations:** Python annotations, graph vocabulary, a minimal graph, multiple inputs, sequential nodes, conditional routes, and bounded loops. These lessons do not require a language-model call.

**L07–L11 — Core AI workflows:** an Anthropic-backed bot, conversation history, tool-using ReAct loops, collaborative drafting, and retrieval-augmented generation. These preserve the video’s conceptual progression.

**U1–U2 — Current implementation updates:** thread/checkpoint memory and safer draft state. These are added labs, not claims about what the video implements.

**S1–S2 — Observability:** LangSmith and LangWatch, each taught and validated separately before comparing them or enabling both.

**C01 — Capstone:** a document-grounded drafting assistant that combines the main concepts and produces test and trace evidence.

## 1.2 Estimated teaching time

The eleven video-aligned core lessons total **20 hours 25 minutes**, including guided instruction, practice, and review. The source video’s runtime is included in that estimate, not added again.

Preparation adds **1 hour**. The two implementation-update labs add **2 hours 30 minutes**. LangSmith and LangWatch add **3 hours** together. The guided capstone adds **3 hours**. The full proposed track is therefore **29 hours 55 minutes**, excluding breaks and optional extensions. A five-day program with approximately six teaching hours per day is a reasonable planning format; learner pace may vary.

## 1.3 Common lesson pattern

Every lesson in the eventual handbooks will follow **Explain → Illustrate → Demonstrate → Guided practice → Independent exercise → Review**. It will include objectives, prerequisites, source timestamps, runnable Python, exact commands, expected behavior, acceptance criteria, troubleshooting, and knowledge checks.

Student and teacher materials will use matching lesson and exercise identifiers. Video illustrations will have timestamped attribution; original diagrams will be labeled separately. Actual execution screenshots will be embedded in both handbooks after the corresponding delivered code is tested.

<!-- pagebreak -->

# 2. Preparation and foundational graphs

## P00 — Orientation, installation, and connection checks

**Added preparation · 60 minutes · Prerequisite: basic Python**

P00.1 Course goals, repository navigation, student files, and teacher-only solutions.  
P00.2 Python 3.12, virtual environments, and pinned dependencies.  
P00.3 Reproducible macOS and Windows setup and exact execution commands.  
P00.4 Local `.env`, `.env.example`, configurable model selection, and secret exclusions.  
P00.5 Anthropic authentication, model response, and LangChain–LangGraph smoke tests.  
P00.6 LangSmith regional endpoints; LangWatch project scope; synthetic tracing data.  
P00.7 Diagnose missing keys, invalid credentials, model access, rate limits, and network errors.

**Completion evidence:** an offline graph run and service-check results, with no credentials in code, logs, screenshots, or Git.

## L01 — Python refresher and LangGraph elements

**Video 00:00:00–00:18:39 · 100 minutes · Prerequisite: P00**

L01.1 Course introduction and what LangGraph does — 00:00:00.  
L01.2 Type annotations, dictionaries, and `TypedDict` — 00:01:24.  
L01.3 `Union`, `Optional`, `Any`, lambda, and map.  
L01.4 State, nodes, graphs, ordinary edges, and conditional edges — 00:08:35.  
L01.5 START/END, tools, tool nodes, `StateGraph`, and runnables.  
L01.6 Human, system, AI, and tool messages; Python logic versus orchestration versus model behavior.

**Practice:** added typed-state and graph-sketch activities. The source section does not assign an original coding exercise.

## L02 — First graph: Hello World and personalized compliments

**Video 00:18:39–00:33:07 · 70 minutes · Prerequisite: L01**

L02.1 Single-node graph objectives and the START → node → END pattern.  
L02.2 Define message state and an ordinary Python greeting node — code begins 00:21:08.  
L02.3 Register nodes; connect boundaries; distinguish builder, compilation, and invocation.  
L02.4 Inspect returned state and visualize the graph.  
L02.5 Modern partial updates versus historical in-place mutation.  
L02.6 Original personalized compliment exercise — chapter begins 00:32:22.

**Exercise outcome:** preserve the supplied name and produce the personalized compliment. No Anthropic call is needed.

## L03 — Multiple inputs and one-node processing

**Video 00:33:07–00:44:29 · 75 minutes · Prerequisite: L02**

L03.1 Mixed-type state: integer lists, names, operations, and result fields.  
L03.2 Compute a sum and format an answer — code begins 00:34:02.  
L03.3 Inspect input state, returned updates, and selected output fields.  
L03.4 Required and optional fields; why annotations are not runtime validation.  
L03.5 Original addition/multiplication exercise — chapter begins 00:43:27.

**Exercise outcome:** use one graph node and a Python conditional to add or multiply the supplied list. Keep graph-level branching for L05.

<!-- pagebreak -->

# 3. Sequences, conditional routing, and loops

## L04 — Sequential graph with multiple nodes

**Video 00:44:29–00:55:36 · 80 minutes · Prerequisite: L03**

L04.1 Extend a graph from one node to a directed sequence.  
L04.2 Build name and age transformations — code begins 00:45:18.  
L04.3 Observe the deliberate overwrite bug and preserve earlier output.  
L04.4 Separate a partial update from the accumulated state.  
L04.5 Original three-node profile exercise — chapter begins 00:54:04.  
L04.6 Check ordering and the final combined name, age, and skills message.

**Exercise outcome:** connect three nodes and retain all profile components rather than replacing earlier text.

## L05 — Conditional graphs and route maps

**Video 00:55:36–01:14:14 · 115 minutes · Prerequisite: L04**

L05.1 Contrast an `if` inside one node with routing to different graph nodes.  
L05.2 Build arithmetic nodes and a routing function — code begins 00:56:37.  
L05.3 Use `add_conditional_edges`, route labels, and a path map.  
L05.4 Distinguish routing return values from state-update dictionaries.  
L05.5 Handle valid and unsupported operations; inspect the executed branch.  
L05.6 Original two-section conditional exercise — chapter begins 01:13:09.

**Exercise outcome:** accept four numbers and two operations and produce two pairwise results. The second calculation must not accidentally reuse the first answer as its input.

## L06 — Loops, counters, and reliable termination

**Video 01:14:14–01:31:01 · 110 minutes · Prerequisite: L05**

L06.1 Blueprint the greeting/random-node graph before implementation.  
L06.2 Define name, generated numbers, and a counter — code begins 01:15:45.  
L06.3 Add a conditional back-edge and stop after five generations.  
L06.4 Reset counters; distinguish intended termination from recursion-limit failure.  
L06.5 Debug iterative state and control randomness for repeatable tests.  
L06.6 Original automatic higher/lower game — chapter begins 01:29:19.

**Exercise outcome:** narrow bounds from 1 to 20, update hints, and stop on success or after at most seven guesses. The original exercise is automatic, not an interactive human-guessing game.

<!-- pagebreak -->

# 4. Model calls, memory, and tools

## L07 — First Anthropic-backed graph: the stateless bot

**Video 01:31:01–01:42:54 · 80 minutes · Prerequisite: L06 and Anthropic access**

L07.1 Why a model wrapper is not yet a tool-using agent.  
L07.2 Replace the original OpenAI integration with `ChatAnthropic` — code begins 01:32:49.  
L07.3 Read the key and model from `.env`; keep secrets outside graph state.  
L07.4 Invoke the chat model from a graph node; inspect response and usage.  
L07.5 Build a terminal input/exit loop and repeat the name-recall demonstration.  
L07.6 Explain why fresh invocations and a Python loop do not provide memory.

**Practice:** added statelessness checks based on the demonstration. The presenter explicitly assigns no original exercise here. Model responses are assessed by behavior, not an exact memorized sentence.

## L08 — Conversation history and the limits of process-local memory

**Video 01:42:54–02:03:20 · 125 minutes · Prerequisite: L07**

L08.1 Human/AI messages and history state — code begins 01:43:58.  
L08.2 Send accumulated turns and append the new AI response.  
L08.3 Predict message state and demonstrate recall within one process.  
L08.4 Restart the program and distinguish lost history from durable persistence.  
L08.5 Serialize role-labeled text logs without changing the user’s text.  
L08.6 Explain history growth, context limits, token usage, and safe trimming.  
L08.7 Compare manual history with `MessagesState`/`add_messages`, avoiding duplicate appends.

**Practice:** reconstruct the demonstrated history and logging workflow, test restart behavior, and design a bounded-history policy. Durable checkpointing is added separately in U1.

## L09 — ReAct agent with arithmetic tools

**Video 02:03:20–02:28:46 · 150 minutes · Prerequisite: L08**

L09.1 Agent/tool loop and observable reasoning-and-acting workflow.  
L09.2 `Annotated`, sequence types, message roles, and reducers — prerequisite chapter 02:05:00.  
L09.3 Typed tools, useful docstrings, and model tool binding — code begins 02:12:28.  
L09.4 Conditional tool routing, `ToolNode`, and the return to the model.  
L09.5 Matching tool-call IDs to results; Anthropic versus LangChain message representations.  
L09.6 Single, multiple, sequential, and no-tool requests; bounded error paths.  
L09.7 Inspect visible calls and results, not private model chain-of-thought.

**Practice:** reproduce add/subtract/multiply demonstrations, including `(40 + 12) × 6 = 312`, and prove that both loop and exit routes work.

<!-- pagebreak -->

# 5. Collaborative drafting and retrieval

## L10 — Drafter: human–AI document collaboration

**Video 02:28:46–02:52:09 · 160 minutes · Prerequisite: L09**

L10.1 Define the document assistant’s agent/tools topology and successful-save exit.  
L10.2 Add document update and save tools — code begins 02:30:59.  
L10.3 Iterate through human feedback, revised drafts, and clarifying questions.  
L10.4 Save to a controlled output directory; handle file errors honestly.  
L10.5 Understand the original global-buffer workaround and its limitations.  
L10.6 Distinguish terminal feedback from durable `interrupt`/resume behavior.  
L10.7 Source extension suggestions: voice, GUI, and a knowledge base — 02:51:34 onward.

**Practice:** recreate the email-drafting/revision/save workflow, inspect the written file, and test an underspecified request. The brief “homework” invitation continues across the published chapter boundary; it refers back to the suggested extensions, not a separate detailed assignment. Voice and GUI are optional project ideas, not required new platforms or API keys in this course.

## L11 — Retrieval-augmented generation: a document-grounded agent

**Video 02:52:09–03:09:51 · 160 minutes · Prerequisite: L09–L10**

L11.1 Explain RAG from first principles, although the video assumes prior familiarity.  
L11.2 Inspect the PDF/document asset, pages, and metadata — code begins 02:53:01.  
L11.3 Split text into chunks; distinguish character counts from token counts.  
L11.4 Explain embeddings, a Chroma collection, persistence, and top-k retrieval.  
L11.5 Expose retrieval as a tool and loop between model and retriever.  
L11.6 Ground answers in retrieved passages; retain source/page citations.  
L11.7 Test supported, unsupported, and empty-retrieval questions — testing chapter 03:06:15.  
L11.8 Review the course and identify realistic next projects — outro chapter 03:09:04.

**Practice:** reconstruct the RAG demonstration and inspect evidence for answers rather than relying on plausible wording. Anthropic is used for generation. A local, non-OpenAI embedding model is the planned adaptation so no additional paid embedding API key is required. The exact embedding package/model and original PDF availability must be verified during implementation; any replacement document will be explicitly labeled as an adaptation.

**Important correction:** the video’s default recursive splitter configuration uses character-based sizing unless a token-length function is explicitly supplied. Fix nonportable paths and source-code defects rather than reproducing them as teaching requirements.

<!-- pagebreak -->

# 6. Current implementation updates and observability

These additions have **no source-video timestamp**. They preserve the video-backed sequence while teaching modern implementation and debugging practices requested for this project.

## U1 — Thread memory, checkpoints, and persistence

**Added update lab · 60 minutes · Prerequisite: L08**

U1.1 `MessagesState`/`add_messages` and state snapshots.  
U1.2 Checkpointers, thread IDs, repeated invocations, and thread isolation.  
U1.3 In-memory continuity versus restart-durable storage.  
U1.4 A durable local checkpoint example, restart test, and recovery limits.

**Evidence:** same-thread recall, cross-thread isolation, and an explicit restart test for the selected durable backend.

## U2 — Safe draft state, human approval, and file side effects

**Added update lab · 90 minutes · Prerequisite: L10 and U1**

U2.1 Replace shared global draft content with explicit session state.  
U2.2 Current tool-runtime/state-injection patterns, verified against pinned versions.  
U2.3 Introduce a bounded approval/resume pattern before a file-writing action.  
U2.4 Restrict paths; prevent unintended overwrites; test failed-save recovery.  
U2.5 Verify two-session isolation and distinguish graph state from saved files.

**Evidence:** isolated drafts, successful approval/resume, rejected unsafe paths, and no false successful-save state.

## S1 — LangSmith tracing and evaluation

**Added observability module · 90 minutes · Prerequisite: L09; L11 for RAG examples**

S1.1 Configure project/workspace scope, keys, and the correct regional endpoint.  
S1.2 Trace graph nodes, model calls, tools, conditional routes, and loop iterations.  
S1.3 Inspect latency, token usage, errors, and retrieval evidence.  
S1.4 Use current asynchronous run retrieval and verify persisted inputs/outputs.  
S1.5 Build a small evaluation set and explain deterministic versus model-based checks.  
S1.6 Keep secrets out of state, prompts, metadata, screenshots, and evaluation datasets.

**Evidence:** a stored trace with inspectable graph/model/tool relationships and a small evaluation report. Initial synthetic ingestion and API read-back have already passed.

## S2 — LangWatch tracing and comparison

**Added observability module · 90 minutes · Prerequisite: L09; L11 for RAG examples**

S2.1 Configure key, project ID, endpoint, and the supported SDK interface.  
S2.2 Create a parent trace and attach the callback at graph invocation.  
S2.3 Inspect plain Python nodes, model/tool/retrieval spans, and loop behavior.  
S2.4 Flush before exit; distinguish local export completion from server acknowledgment.  
S2.5 Compare one synthetic run across LangWatch and LangSmith.  
S2.6 Choose no tracing, one backend, or both; document what data leaves the process.

**Evidence:** server-acknowledged trace ingestion and a trace-tree inspection. Initial synthetic LangWatch ingestion returned HTTP 200 with no rejected spans; dashboard inspection is still a later validation step.

<!-- pagebreak -->

# 7. Capstone, assessments, and final training materials

## C01 — Document-grounded drafting assistant

**Added capstone · 180 minutes guided implementation · Prerequisite: L01–L11, U1–U2, S1–S2**

C01.1 Read the brief and draw the graph before coding.  
C01.2 Retrieve relevant passages from a small teaching knowledge base.  
C01.3 Use an Anthropic model to answer a grounded request and prepare a draft.  
C01.4 Use tools and conditional routing for clarification, revision, and controlled saving.  
C01.5 Maintain thread-scoped state; bound tool loops; handle missing evidence.  
C01.6 Require approval before the relevant file side effect.  
C01.7 Trace and debug the same scenario with LangSmith and LangWatch.  
C01.8 Run acceptance tests, capture genuine execution screenshots, and explain design choices.

**Acceptance criteria:** a grounded answer with inspectable citations; at least one genuine model/tool round trip; correct branch and termination behavior; two-session isolation; a tested approved save within the output directory; documented failure paths; trace evidence; and no committed credentials. A working instructor reference solution and marking rubric will be supplied.

## 7.1 Student Handbook index

Course orientation and outcomes; P00 setup; L01–L11 in video order; U1–U2 updates; S1–S2 observability; C01 capstone; glossary; troubleshooting; references. Every lesson will include illustrated explanations, complete runnable examples, guided checkpoints, independent practice, review questions, and actual execution screenshots.

**Planned file:** `docs/LangGraph_Student_Handbook.docx`.

## 7.2 Teacher Handbook index

The same identifiers and sequence; preparation checklist; demonstration script; suggested explanations and discussion questions; expected responses; misconceptions; complete solutions; assessment answers with reasoning; marking criteria; recovery procedures; extensions; and genuine demonstration screenshots.

**Planned file:** `docs/LangGraph_Teacher_Handbook.docx`. Teacher solutions will be kept separate from student starter files.

## 7.3 Exercise Workbook index

One matching exercise section per lesson/lab; starter-file locations; prerequisites; step-by-step tasks; progressive hints; expected behavior; completion criteria; observation space; capstone brief; and rubric. Where the video supplies only a demonstration, the workbook’s added exercise will be labeled accordingly.

**Planned file:** `docs/LangGraph_Exercise_Workbook.docx`.

## 7.4 Cross-course appendices

A. macOS and Windows command reference.  
B. Tested versions, lock file, and environment checks.  
C. Original-video versus current-API comparison notes.  
D. State, routing, message, tool, memory, and retrieval glossary.  
E. Anthropic authentication, availability, rate-limit, and token troubleshooting.  
F. LangSmith/LangWatch configuration, privacy, and missing-trace troubleshooting.  
G. Exercise command index and student/teacher file manifest.  
H. Video illustration attribution and execution-screenshot index.  
I. Knowledge-check answers and instructor marking guidance.  
J. Validation report and clearly identified untested platform behavior.

<!-- pagebreak -->

# 8. Original video chapter index

The following are the video publisher’s chapter labels and start times. The adapted lesson IDs group them without changing their order. A chapter boundary can occur during the presenter’s concluding sentence.

**00:00:00** — Introduction  
**00:01:24** — Type Annotations  
**00:08:35** — Elements  
**00:18:39** — Agent 1 Intro  
**00:21:08** — Agent 1 Code  
**00:32:22** — Agent 1 Exercise  
**00:33:07** — Agent 2 Intro  
**00:34:02** — Agent 2 Code  
**00:43:27** — Agent 2 Exercise  
**00:44:29** — Agent 3 Intro  
**00:45:18** — Agent 3 Code  
**00:54:04** — Agent 3 Exercise  
**00:55:36** — Agent 4 Intro  
**00:56:37** — Agent 4 Code  
**01:13:09** — Agent 4 Exercise  
**01:14:14** — Agent 5 Intro  
**01:15:45** — Agent 5 Code  
**01:29:19** — Agent 5 Exercise  
**01:31:01** — AI Agent 1 Intro  
**01:32:49** — AI Agent 1 Code  
**01:42:54** — AI Agent 2 Intro  
**01:43:58** — AI Agent 2 Code  
**02:03:20** — AI Agent 3 Intro  
**02:05:00** — AI Agent 3 Prerequisite  
**02:12:28** — AI Agent 3 Code  
**02:28:46** — AI Agent 4 Intro  
**02:30:59** — AI Agent 4 Code  
**02:52:09** — RAG Agent Intro  
**02:53:01** — RAG Agent Code  
**03:06:15** — RAG Agent Testing  
**03:09:04** — Course Outro  

<!-- pagebreak -->

# 9. Approval and remaining implementation decisions

This draft fixes the proposed sequence and coverage, not the final wording or page count of the three handbooks. The main remaining implementation decisions are the local embedding model/package, availability or replacement of the source RAG document, and the exact durable-checkpoint/runtime patterns that pass tests under the pinned dependencies.

Before publishing the full training, every exercise and the capstone will be run; final execution screenshots will be embedded in both handbooks; dependency and command checks will be recorded; and the rendered Word documents will be inspected for clipping, readable code, image captions, and page flow. Windows instructions will be labeled untested unless a Windows execution environment is actually used.

**Approval requested:** accept this overall sequence and scope, or identify modules to add, remove, shorten, or deepen before detailed handbook and exercise development proceeds.
