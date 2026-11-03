# L11 — Local-embedding Chroma RAG

## Your task: produce an evidence-gated answer card

This is **added practice** based on the video's RAG lesson, 02:52:09–03:09:51. The video demonstrates a model/retriever loop; your task deliberately chooses a simpler retrieve-first topology. Build `START → retrieve → generate or abstain → END`. Explain why this guarantees a search happens without asking a model to select a tool. Budget approximately 45 minutes for implementation, followed by evidence review.

Use the original synthetic replacement `data/rag_teaching_handbook.pdf`, not the video's stock-market PDF. Read its three pages first. Your supported question is: **“How long is the equipment loan, and what renewal is allowed? Use digits.”** Your unsupported question is: **“What is the exact equipment late fee in dollars?”** Do not invent any amount, substitute an external policy, or answer from general knowledge. Source/page citations must refer to the actual teaching PDF.

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

The [official recursive splitter guide](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter) explains character sizing. The [Chroma embedding guide](https://docs.trychroma.com/docs/embeddings/embedding-functions) explains the real local default model and its initial download. Use the student chapter for the full source/current-API comparison and troubleshooting.
