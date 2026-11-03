# L11 — Local-embedding Chroma RAG

## Explain: give the model evidence it can inspect

**Video-aligned lesson:** 02:52:09–03:09:51, approximately 160 teaching minutes including practice. Prerequisites are L09's tool-call loop and L10's distinction between a draft and a saved artifact. Start with the [RAG introduction](https://youtu.be/jGg_1h0qzaM?t=10329), then inspect the [document walkthrough](https://youtu.be/jGg_1h0qzaM?t=10381). The independent answer-card task below is **added practice**, not an original video assignment.

By the end, you should be able to extract PDF pages, split text without losing provenance, explain local embeddings, build a persistent Chroma collection, follow a retrieval-tool loop, and distinguish an answer with evidence from plausible unsupported wording. You will also build a simpler retrieve-first graph and explain why it need not let a model decide whether to search.

Retrieval-augmented generation, or **RAG**, supplies relevant document passages to a language model at question time. Retrieval selects evidence; generation writes an answer from that evidence. This does not train Claude on the PDF or guarantee truth. A correct answer can still be omitted if retrieval misses the right passage. A retrieved passage can be irrelevant, incomplete or wrong. A fluent answer can misrepresent a correct passage. Inspect all three stages separately.

An **embedding** is a numeric vector representing text. Similarity search compares the query's vector with stored passage vectors to find nearby meanings. Chroma's `DefaultEmbeddingFunction` uses the real local all-MiniLM-L6-v2 model, implemented through ONNX in the installed package. It can download model files automatically on first use [1101]. This is not keyword matching and is not a paid embedding API. Claude generation is a separate real Anthropic request; it still needs the setup from P00.

## Illustrate: follow text and provenance together

The source video uses a stock-market PDF. That original file is available in its repository, but this lesson deliberately uses `data/rag_teaching_handbook.pdf`: an **original synthetic teaching replacement** about fictional Harbor Learning Lab policies. Its three pages describe an open day, equipment loans, and practice-record handling. It is neither the original finance document nor a nine-page copy. The editable text, rebuild script and decision record live in `data/rag_teaching_handbook.json`, `data/rag_build_pdf.py` and `data/rag_provenance.md`.

<!-- VIDEO_FIGURE -->

<!-- ORIGINAL_DIAGRAM -->

During ingestion, `load_chunks` reads each actual PDF page with `pypdf`, then splits each page separately. Each chunk receives an ID, text, a source filename and a **1-based page**. Page 2 remains page 2 even when it becomes two chunks. A chunk number is not a page number. File names are portable provenance; an absolute machine path is not needed in the answer.

The recursive splitter tries paragraph, line, word and character boundaries. Our explicit `length_function=len` makes `chunk_size=650` a character limit; `chunk_overlap=90` is a target overlap, not a token budget [1102]. Overlap can preserve a sentence crossing a split, but repeated text costs storage and model context. The ONNX model has its own input limit, independent of Python character counts. These short English passages keep the teaching example small; a production corpus needs token-aware inspection and retrieval evaluation rather than assuming every 650-character chunk is always safe.

`prepare_store(directory: Path)` creates or reopens a collection under `directory/chroma`. Chroma's embedded persistent client writes to that selected local directory [1103]. The collection name fingerprints the PDF bytes and index specification. Changing the source, splitter policy or declared embedding model selects a new collection rather than silently appending incompatible vectors. Reopening the same data does not duplicate records. Do not mix embeddings from different models, even if their vector dimensions happen to match. For an embedding-package/model change, bump the index specification or choose a fresh run directory and re-index.

## Demonstrate: a bounded retrieval-tool loop

The demonstration starts at `agent`, invokes a tool-bound model, routes tool calls to `retrieve`, and loops back to the model. A response without tool calls ends the graph. `MessagesState` accumulates messages through its reducer, while nodes return only their new messages [1104]. Every `ToolMessage` must carry the ID of the tool call it answers. Inspect public tool arguments and returned evidence, not private reasoning.

This adaptation requests retrieval using `tool_choice="auto"` and an explicit prompt. The configured model rejected forced named-tool selection during live validation, so the course does not rely on that option. A missing actual retrieval fails the acceptance check rather than being silently treated as success. Later turns may search again or answer. The prompt restricts answers to supplied passages, treats document text as untrusted data, and requires citations such as `[rag_teaching_handbook.pdf p.2]`. Three model turns and two tool calls per turn bound the loop. Budget exhaustion raises an error; it does not become a fabricated successful answer. `execution_config()` retains the selected tracing callbacks and the separate recursion guard. Anthropic supports tool binding through `bind_tools` [1105].

<!-- EXAMPLE_CODE -->

After activating the prepared Python 3.12 environment, run from the repository root:

```bash
python -m course_lessons.l11 --live --backend none
```

This command can incur real Anthropic usage. On first ingestion, allow time and internet access for the ONNX model download. Chroma product telemetry is explicitly disabled by the helper [1106]. `--backend none` disables the course's optional tracing backend; it does not turn paid generation into an offline operation. Use only synthetic data if you later select `langsmith`, `langwatch` or `both`.

The run checks three stable behaviors. A supported equipment question must include the durations 7 and 3 and a page-2 citation. The exact late-fee question must produce `NOT_IN_DOCUMENT`, because no amount is specified. A separate, genuinely empty local collection must also produce that sentinel with no hits. We do not require identical prose for supported answers. These are acceptance properties, not claims that a live run has already succeeded on your machine.

<!-- EXECUTION_FIGURES -->

## Guided practice: inspect evidence before accepting an answer

1. Open the teaching PDF and find the sentence establishing a 7-calendar-day loan and one possible 3-day renewal. Note the qualification: renewal is conditional on no reservation and must be requested before the due date. An answer giving only the durations can answer our narrow question without describing the full policy.
2. Run `python -m pytest -q tests/lessons/test_l11.py`. These are offline tests with explicitly named model and collection doubles. They exercise control flow and data contracts, not semantic embedding quality or a paid API.
3. Read the demo summary's `hits` before its `answer`. Confirm that the supporting text is actually present, the citation's page matches it, and any unsupported information is absent. The `search` helper always returns nearest chunks for a nonempty collection; “nearest” does not mean “answers the question.”
4. Compare the unsupported case with the empty case. The former may contain several real but insufficient hits. The latter contains none. Both can justify abstention, but they diagnose different failures.
5. Reuse the same output directory deliberately with `--output-dir .work/student-runs/l11-repeat`. Verify the chunk count remains stable. Inspect only your own run directory; do not delete another learner's index. The index is storage, not conversation memory or a checkpoint.

## Independent task: an evidence-gated answer card

Build the workbook's **retrieve-first answer-card graph** in `exercises/starters/l11.py`. It is intentionally different from the demonstration: `START → retrieve → generate or abstain → END`. Search the original nonblank question with `k=3`. Empty evidence must skip the model. Nonempty evidence goes to the injected model with source/page labels. Missing facts require exactly `NOT_IN_DOCUMENT`.

Return an answer card containing only `question`, `answer`, `status` and `sources`. Status is `grounded` or `not_in_document`. For grounded cards, `sources` is the sorted, deduplicated inventory of retrieved source/page pairs; it is not a claim that every retrieved page was cited. For abstention, it is empty. Reject missing or fabricated citations. The workbook specifies the exact questions and acceptance checks. Use the independent reference only after attempting the three TODO functions:

```bash
python -m exercises.starters.l11
python -m exercises.solutions.l11 --live
```

A citation validator can check that page 2 was retrieved. It cannot prove every sentence is entailed by page 2. Human evidence review remains part of completion. This distinction matters especially when tracing records both the query and retrieved passages.

## Review: three knowledge checks

1. With `length_function=len`, what does `chunk_size=650` measure, and why is it not the embedding model's token limit?
2. Why must ingestion and query embeddings use the same model, and what should you do after changing that model or the chunking policy?
3. If Chroma returns three chunks for a late-fee question, can you conclude the document contains a fee? Explain the different checks for empty retrieval and insufficient nonempty evidence.

## Troubleshooting and source/current differences

A missing PDF should raise a file error, not silently create an empty index. A scanned, textless PDF needs OCR; our helper rejects it. A model-download failure is an embedding setup issue, not evidence that Claude rejected your key. Preserve the error and fix connectivity/cache access; never replace embeddings with a keyword fallback. A collection compatibility error calls for a fresh run directory, not disabling checks. A citation failure means inspect the retrieved pages and prompt before relaxing acceptance. Do not use the offline test doubles in the live CLI.

The video demonstrates a Windows persistence path, OpenAI chat/embeddings and `k=5`; this lesson uses portable run directories, Anthropic generation, a real local embedding model and `k=3`. The splitter's character/token distinction is corrected. Direct `chromadb` avoids requiring `langchain-chroma`. Current upstream RAG source has a valid tool-name comprehension; an earlier review's variable-warning is not a current defect to reproduce [1107]. The [testing section](https://youtu.be/jGg_1h0qzaM?t=11175) supports the grounding discussion, while the [outro](https://youtu.be/jGg_1h0qzaM?t=11344) suggests future projects, not another detailed exercise. This lesson's new policy dataset and deterministic acceptance checks are adaptations.

## References

[1101]: https://docs.trychroma.com/docs/embeddings/embedding-functions "Chroma embedding functions and local default model"
[1102]: https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter "Recursive splitting and character sizing"
[1103]: https://cookbook.chromadb.dev/core/clients/ "Chroma embedded persistent client"
[1104]: https://docs.langchain.com/oss/python/langgraph/graph-api "LangGraph messages state and graph routing"
[1105]: https://docs.langchain.com/oss/python/integrations/chat/anthropic "ChatAnthropic integration and tool calls"
[1106]: https://cookbook.chromadb.dev/core/configuration/ "Chroma telemetry configuration"
[1107]: https://raw.githubusercontent.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp/main/Agents/RAG_Agent.py "Original course RAG implementation"
