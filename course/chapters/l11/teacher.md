# L11 — Local-embedding Chroma RAG

## Explain: establish what the evidence can prove

Allow **160 minutes**: explanation 20, illustration 15, timed demonstration 25, guided practice 35, independent answer-card work 45, and review 20. Prerequisites are message/tool routing from L09 and controlled outputs from L10. Learners should know Python functions, dictionaries and partial graph updates.

Open with a question: “If an assistant cites a page, what have we established?” Expect “there is a source,” then refine it: citation presence is weaker than citation provenance, which is weaker than semantic support. Today's code checks provenance and known teaching facts. It does not provide a general entailment proof. Make this distinction before anyone sees a fluent generated answer.

Define RAG as retrieving passages at question time and passing them to generation. Explain that embeddings are numeric text representations, not hidden copies of every fact. Local embedding computation does not make Claude generation local. The first ONNX download still requires connectivity; subsequent inference uses the downloaded model. Chroma documents its default all-MiniLM-L6-v2 embedding behavior [1111]. Have participants point to the separate embedding and chat-model boxes.

## Illustrate: source identity and page identity

Open the delivered synthetic PDF and establish its role as inspectable evidence and safe tracing. Use an original three-page fictional policy handbook rather than treating unrelated financial assertions as course evidence. Do not teach an external finance answer as the replacement's answer, and do not report a different page count.

<!-- CONCEPT_FIGURE -->

<!-- ORIGINAL_DIAGRAM -->

On page 2, identify 7 calendar days and one possible 3-day renewal. Read the conditional qualification aloud. The narrow demonstration asks for durations; it is not an exhaustive policy summary. Page 2 also states that no late-fee amounts are specified. This makes the unsupported question an assessment of abstention rather than general financial knowledge.

Walk a page through `load_chunks`. A 1-based page number survives splitting; chunk IDs distinguish passages. Ask whether a second chunk on page 2 becomes page 3. Expected response: no. Then contrast `len` with model tokenization. The recursive splitter documents character sizing and target overlap [1112]. Our short chunks are a teaching choice, not a universal optimum for every language or embedding input limit.

## Demonstrate: a 25-minute controlled live walkthrough

Before class, obtain authorized live validation on the configured Anthropic model and cache the real embedding download if appropriate. Verify the PDF, dependency versions and a writable output directory. Do not open credentials on screen. If access fails, teach with the PDF, code and clearly identified offline tests; do not present scripted doubles as a live substitute.

1. **Minutes 0–5:** run `python -m pytest -q tests/lessons/test_l11.py`. Explain that explicit named doubles check orchestration without contacting services. Distinguish this from both embedding-quality evaluation and a paid model run.
2. **Minutes 5–12:** run `python -m course_lessons.l11 --live --backend none`. Narrate ingestion, persistence and the first requested retrieval call. Explain automatic selection plus explicit validation: the configured model rejected a forced named-tool choice during live testing. A missing actual retrieval is still an error. Anthropic tool binding and normalized `tool_calls` are current integration APIs [1113]. No temperature override is added.
3. **Minutes 12–17:** inspect the supported result's actual hits, then the answer. Require durations 7 and 3 and `[rag_teaching_handbook.pdf p.2]`; allow variable wording. Explain how a `ToolMessage` uses the incoming call ID. Inspect the visible evidence, not private reasoning.
4. **Minutes 17–22:** compare the late-fee case and the real empty-collection case. Both should return exactly `NOT_IN_DOCUMENT`. The former can still retrieve nearby chunks. The latter has no passages. Ask learners which stage they would investigate in each case.
5. **Minutes 22–25:** show the bounded turn budget and `execution_config()`. Three model turns limit normal work, while the recursion limit is a separate safety backstop. Explain why a raised retrieval or budget error must not be reclassified as an answer.

<!-- EXECUTION_FIGURES -->

Expected behavior here is an acceptance target, not a record of a completed live run. Chroma paths stay inside the selected run directory. Its product telemetry is explicitly disabled; optional course tracing is selected separately. PersistentClient and telemetry configuration are documented independently [1114] [1115]. Changing the embedding model requires re-indexing; persistence is not permission to reuse incompatible vectors.

## Guided practice: diagnose the right layer

Give pairs 35 minutes. One learner reads the source text while the other traces the graph; switch halfway. Ask them to locate each returned source/page pair, compare blank-search behavior with unsupported questions, and rerun against the same output directory to examine idempotent ingestion. A collection should not grow merely because it is reopened.

Watch for four misconceptions. “Top three means relevant” confuses nearest neighbors with answerability. “A citation proves truth” confuses provenance with entailment. “Local embeddings means no data leaves the machine” ignores the generation request and optional traces. “A persistent vector index remembers my conversation” confuses document storage with checkpointed state. Correct each with the actual code path rather than an abstract warning.

The fingerprint includes document bytes, splitter settings and the declared model tag. Explain its boundary: it does not automatically detect every future model/package behavior change. A package upgrade that alters embedding behavior requires a deliberate index-spec revision or a fresh directory. Avoid concurrent writes to one teaching index; the helper is not a multi-writer migration service.

## Independent task: solution walkthrough and marking

The workbook requires a **retrieve-first answer card**, not another copy of the model-selected retrieval loop. The three starter functions are `format_evidence`, `build_graph` and `validate_card`. Keep the reference hidden during the first implementation attempt. The starter's successful exit only means it displayed `STARTER_NOT_COMPLETED`; it is not an exercise pass.

`format_evidence` labels every passage with its actual source/page and joins them with blank lines; empty input becomes an empty string. `build_graph` validates the question, retrieves with `k=3`, then routes by whether hits exist. Empty hits produce deterministic abstention without any model invocation. Nonempty hits reach generation, which passes labeled evidence and an abstention instruction to the injected model with the current runnable config. This architecture guarantees the search occurs before the model but still needs semantic review when irrelevant hits are nonempty.

`validate_card` checks the status, the abstention sentinel, and provenance of every citation. For grounded cards it checks that `sources` is the sorted deduplicated inventory of retrieved evidence pages. Explain that this inventory is not the set of pages the answer necessarily cites. The public card returns only question, answer, status and sources, keeping raw evidence in graph state for inspection. The solution invokes the shared execution config and never imports the demonstration.

Run the independent reference with:

```bash
python -m exercises.solutions.l11 --live
```

<!-- SOLUTION_CODE -->

Award 10 points: 2 for faithful source/page formatting; 3 for correct retrieval and empty/nonempty routing, including skipping the model when empty; 2 for truthful status and deduplicated source inventory; 2 for rejection of absent/fabricated citations; 1 for offline tests plus actual evidence review. Full completion also requires nonblank-question rejection, a supported card with 7 and 3 plus page 2, and a late-fee abstention. Do not award grounding points solely for the presence of a bracketed string. A stretch paraphrase experiment should report observations, not claim statistical retrieval performance from a few examples.

## Review: exact knowledge-check answers

**1. What does 650 measure, and why not the token limit?** With `length_function=len`, 650 measures Python characters. Tokenization is model-dependent; the embedding model's own input limit is a separate constraint. Even overlap is targeted around separators rather than guaranteed to be exactly 90 characters. Reasoning must distinguish the splitter's unit from the model's unit.

**2. Why use the same embedding model, and what after a change?** Stored vectors and query vectors must occupy the same learned representation space. Equal vector length alone is insufficient. Rebuild under a new model/index specification or a fresh run directory after changing the embedding or chunking policy. Never append mixed vectors to an old index and hope proximity remains meaningful.

**3. Do three late-fee hits establish a fee?** No. Top-k retrieves nearest candidates even when none answers the question. Empty retrieval can skip generation and abstain deterministically. Nonempty insufficient evidence needs evidence inspection and model abstention; here the exact missing-fee response is `NOT_IN_DOCUMENT`. A real retrieval exception must propagate as a failure, not be renamed “empty.”

## Recovery and current implementation notes

For a missing or textless PDF, repair the asset/OCR stage first. For failed ONNX downloads, diagnose connectivity and cache access; never silently switch embeddings. For wrong citations, compare each cited page to returned hits and the actual PDF. For Anthropic failures, return to P00's safe checks without showing secrets. If the turn budget is exhausted, inspect visible tool calls before changing the limit. Use a fresh output directory for collection incompatibility and preserve evidence before deleting an index.

Use Anthropic generation, local embeddings, portable persistence and `k=3` for this lesson. Keep tool names consistent between the registry and dispatch lookup. LangGraph conditional routing and reducers are the relevant graph concepts [1116]. U1/U2 and C01 add checkpointing and approval behavior; this lesson does not claim to implement them.

## References

**Official guidance:** [embeddings][1111] · [text splitting][1112] · [Anthropic tools][1113] · [persistence][1114] · [telemetry][1115] · [graph API][1116].

<!-- REFERENCES_INLINE -->

[1111]: https://docs.trychroma.com/docs/embeddings/embedding-functions "Chroma default embedding function"
[1112]: https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter "Recursive character splitting"
[1113]: https://docs.langchain.com/oss/python/integrations/chat/anthropic "Anthropic tool binding"
[1114]: https://cookbook.chromadb.dev/core/clients/ "Chroma persistent client"
[1115]: https://cookbook.chromadb.dev/core/configuration/ "Chroma anonymized telemetry opt-out"
[1116]: https://docs.langchain.com/oss/python/langgraph/graph-api "LangGraph graph and message-state APIs"
