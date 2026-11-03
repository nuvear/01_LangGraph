# C01 — Document-grounded drafting capstone

## Build a draft that can be inspected and safely approved

**SUPPLEMENTARY CAPSTONE · 180 minutes.** Complete L01–L11, U1–U2 and S1–S2 first. This capstone combines drafting and retrieval concepts with current checkpointed approval, isolated threads and acceptance tests.

You will combine those ideas into a document-grounded briefing assistant. A successful run retrieves actual teaching-document passages, completes an Anthropic tool round trip, drafts with inspectable citations, accepts one revision and pauses before saving. You must also explain why a plausible sentence is not evidence. Your final product is a new text file beneath the chosen output directory, not a model message saying “saved.”

Use only L11's `data/rag_*` teaching fixtures. The integrated `rag_teaching_handbook.pdf` is an explicitly labeled original synthetic teaching document. Do not replace it with personal documents or customer data. The source filename and one-based PDF page must travel with each retrieved passage. Model wording varies, so assess stable properties—tool messages, citations, thread state, approval and file contents—instead of memorizing an example paragraph.

## Understand the graph before running it

A retriever returns passages selected by similarity. An embedding is a numerical representation used for that comparison. L11's helper owns the Chroma store and local `all-MiniLM-L6-v2` embedding model; C01 imports the helper only when needed. Its first run may download embedding-model files. This is separate from the paid Anthropic request that writes the briefing. Keep the same embedding configuration for indexing and querying; rebuild an index deliberately when its model or chunking changes. [Chroma's embedding documentation](https://docs.trychroma.com/docs/embeddings/embedding-functions) describes the default model and download behavior.

The model first receives a retrieval-tool schema. Search uses automatic tool choice with an explicit instruction to call the tool; the graph rejects a missing or unexpected call rather than inventing one. Drafting retains the schema but disables further tools using `tool_choice={"type": "none"}`, as documented in [Anthropic's tool-choice guide](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools). Its response asks for `retrieve_passages`, but that response does not execute Python. The graph checks that there is exactly one permitted call, invokes the actual retrieval tool, and returns its JSON result in a `ToolMessage` bearing the matching call ID. The next model invocation receives that result. This is the round trip; merely calling a search function before an unrelated prompt would not demonstrate the same message protocol. [ChatAnthropic's integration guide](https://docs.langchain.com/oss/python/integrations/chat/anthropic) documents these standardized messages.

The graph branches on evidence and validation results. Empty retrieval ends as `no_evidence`. An explicit insufficient-evidence response ends as `unsupported`. Missing or unknown citation markers produce `citation_failed`. Only a structurally acceptable draft reaches review. One requested revision returns to review; a second ends as `revision_limit`. There is no open-ended agent loop, and the successful path makes three model calls: tool selection, initial drafting and one revision. The recursion limit is an emergency ceiling, not the normal stopping condition.

<!-- ORIGINAL_DIAGRAM -->

An interrupt suspends graph execution and exposes a serializable question to the caller. A checkpointer stores the state needed to resume. The caller supplies `Command(resume=...)` using the same thread ID. Importantly, an interrupted node starts again from its beginning on resume. Our review node therefore contains neither a model call nor a file write. A separate save node performs the side effect only after approval. See the [official interrupt guide](https://docs.langchain.com/oss/python/langgraph/interrupts).

## Inspect the complete baseline

The demonstration is `course_lessons/c01.py`. Its builder accepts an injected model and retriever for tests, but `run_demo(live=True)` obtains the real Anthropic model and L11 store. Without `--live`, it refuses to pretend that scripted output is a model response. The ordinary CLI has an intentionally scripted teaching driver: it supplies clarification, revision and approval decisions itself. It demonstrates the boundary, but it is not an authenticated human-approval interface.

<!-- EXAMPLE_CODE -->

## Guided practice

1. **Start offline.** From the repository root, activate the prepared Python environment and run:

   ```bash
   python -m pytest tests/lessons/test_c01.py -q
   python -m exercises.starters.c01
   ```

   The unfinished starter must exit successfully with `STARTER_NOT_COMPLETED`, not claim completion. One learner-acceptance test is skipped until the TODOs are implemented. Other tests exercise the demonstration and reference solution using explicitly named offline doubles. These checks do not establish that Anthropic, Chroma downloads or tracing services work.

2. **Find the actual retrieval boundary.** Read `load_retriever`. It lazily imports `course_support.retrieval`, prepares a store under the run's `chroma` directory and calls `search(store, query, k=3)`. Read the L11 fixture description before drawing conclusions about its contents. If the sibling helper is absent during integration, stop at its clear dependency error; do not fabricate a replacement store or assume that a particular document and answer were reproduced.

3. **Run the real demonstration when authorized.** The shared runtime handles local credentials; never copy them into code or state.

   ```bash
   python -m course_lessons.c01 --live --backend none
   ```

   The driver opens two fresh thread IDs. Both initially pause for clarification. Thread A then receives a briefing request, retrieves evidence and reaches review. Thread B still has no draft or model calls. A receives one concise-revision request, reaches review again and is explicitly approved by the script. B receives an empty clarification and ends as `clarification_failed`. The summary reports stable assertions, not a predetermined model paragraph.

4. **Inspect the artifact, not just the summary.** Locate `saved_path` in the returned JSON. It must be beneath that run's `artifacts` directory, contain the reviewed draft and retain source/page markers. The driver also attempts an unsafe filename and an existing filename; both must be rejected without changing the saved content. Use a fresh output directory for another run. An existing file is not silently overwritten.

5. **Read the failure branches.** Find the tests for absent tools, multiple tool calls, invalid metadata, empty retrieval, unsupported requests, rejected review and failed writes. These are deliberate offline scenarios; a similarity retriever may return some passages even for an unrelated question. A nonempty top-k result is not proof that a request is supported. Citation validation likewise checks reference integrity, not whether every sentence follows from the passage. Compare the actual claim with its PDF page before approving.

6. **Inspect trace structure after local behavior works.** With synthetic fixture data only, repeat the same scenario with each backend separately:

   ```bash
   python -m course_lessons.c01 --live --backend langsmith
   python -m course_lessons.c01 --live --backend langwatch
   ```

   Identify the retrieval tool, matched result, two drafting calls, interrupt/resume and save node. Record genuine server-side trace identifiers when available. A printed summary is not proof that either service ingested a trace. Model prompts, passages and drafts may leave the machine when tracing is enabled.

<!-- EXECUTION_FIGURES -->

## Independent task: fingerprint-bound approval and an evidence inventory

Complete exactly three functions in `exercises/starters/c01.py`: `assess_citations`, `decide_review` and `render_artifact`. Keep the supplied retrieval, tool and graph scaffold. Do not import the solution. Your assistant must reject empty, insufficient or uncited drafts and markers outside the retrieved source/page set. Approval must contain the SHA-256 fingerprint of the current draft. A hash is a content identifier, not an approver's signature; real applications also need authorization.

Return the specified review status with `approved=False` by default. Permit one revision with stripped feedback of 1–500 characters, reject malformed decisions and stop a second revision. Save the approved draft followed by an `Evidence inventory` containing sorted, de-duplicated `(source, page, id)` entries for every retrieved chunk. An inventory documents what was available, not what was necessarily used or proven. The workbook gives exact formatting and completion checks; the independent reference is `exercises/solutions/c01.py`.

## Three knowledge checks

1. Why do a nonempty retrieval result and valid citation markers still not prove that a draft is grounded? What should tests check, and what must a reviewer inspect?
2. Thread A is paused with a draft and thread B is awaiting its first clarification. Why must A resume with A's thread ID, and what happens to these checkpoints after the process exits?
3. A revision changes draft D1 into D2. What happens if approval carries D1's fingerprint? Separately, what happens if D2 is correctly approved but the filename is `../escape.txt`? State the status and expected file behavior for each case.

## Troubleshooting and current-API differences

A missing-helper error means L11 integration is incomplete, not that fake retrieval is acceptable. A first-run embedding download error needs network/cache diagnosis through the parent or instructor. Authentication and model-access errors belong to the shared runtime configuration; never print secrets to troubleshoot them. Inspect `citation_failed` against the exact tool-provided markers before increasing token limits. A save failure must leave `saved_path` empty; do not convert it into success merely because approval was granted.

Current node configuration uses `RunnableConfig`, allowing LangGraph to inject callbacks and thread settings. `invoke` still exposes `__interrupt__` even though current documentation also describes newer streaming APIs. This capstone uses `InMemorySaver`: it demonstrates process-local isolation, not restart durability. Refer back to U1 for a durable backend. Anthropic generation, local embeddings, fail-closed approval and this assessment are implementation choices for this capstone.

## References

The [LangGraph interrupt documentation](https://docs.langchain.com/oss/python/langgraph/interrupts), [ChatAnthropic guide](https://docs.langchain.com/oss/python/integrations/chat/anthropic), [tool-binding reference](https://reference.langchain.com/python/langchain-anthropic/chat_models/ChatAnthropic/bind_tools) and [Chroma embedding documentation](https://docs.trychroma.com/docs/embeddings/embedding-functions) were checked on 3 November 2026. Actual model wording, service availability, live trace ingestion and platform-specific execution still require recorded validation.
