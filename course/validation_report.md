# Complete LangGraph course — validation report

Validated on **3 November 2026**, using Python **3.12.13** on **macOS/arm64**. This report supersedes the earlier index-and-foundation status; the original training index and its source-review records remain preserved.

## Delivery and scope

The complete sequence is P00, L01–L11, U1–U2, S1–S2, and C01: **17 modules**, including the capstone. All three matched chapter sets, complete demonstrations, separate learner starters and instructor solutions, test files, original diagrams, attributed video illustrations, and execution records are delivered. Added teaching material is distinguished from original video assignments and source timestamps.

| Word document | Actual rendered pages | Embedded images |
| --- | ---: | ---: |
| Student Handbook | 141 | 62 |
| Teacher Handbook | 140 | 62 |
| Exercise Workbook | 50 | 0 |

Both handbooks contain all **34 actual execution screenshots**, 11 timestamped source-video stills, and 17 original teaching/overview diagrams. Editable detailed Mermaid flowcharts remain available; compact overviews improve the printed readability of dense workflows. The workbook contains concrete tasks, progressive hints, expected behavior, observed-result fields, and completion criteria. The teacher edition includes independent solutions and reasoned answers to the corresponding knowledge checks.

The three editions also have editable Markdown and self-contained HTML versions. The complete export preserves relative code/data/asset links; the ZIP excludes local credentials and working environments.

## Execution: 34 of 34 passed

Every module’s baseline demonstration and independent instructor reference were executed successfully: **34/34 passed**. Fourteen runs were deterministic/model-free; **20 runs used real Anthropic-enabled implementations**. Live execution never substitutes an offline model double.

The [execution manifest](validation/execution_manifest.json) records exact commands, UTC times, exit codes, selected backends, source hashes, logs and screenshots. Each current demonstration/solution file was checked against its recorded hash. The complete captured stdout/stderr is retained in `assets/execution`; screenshots are genuine browser captures of that actual stdout, explicitly labeled as such—not simulated terminal windows or fabricated model replies. The figures link to their full recorded output.

The runs cover stateless and history-based chat, real model-requested arithmetic tools, iterative drafting and saving, local ONNX embeddings with persistent Chroma retrieval, supported/unsupported/empty evidence, SQLite close/reopen and fresh-interpreter reading, actual interrupt/resume mechanics, bounded approval/revision paths, LangSmith/LangWatch callbacks, and both capstone implementations.

The enhanced capstone returned `saved`, retrieved three chunks, completed the real tool-result continuation, used three model calls, made one revision, verified thread isolation and current-draft fingerprint approval, rejected unsafe/duplicate saves, and produced an actual 1,742-byte cited artifact. Its finite command-line harness scripts clarification/revision/approval decisions; that is explicitly disclosed rather than presented as independent human review.

## Offline tests and clean setup

**860 passed; 9 intentionally skipped; no failures.** The identical result passed in a clean native Python virtual environment installed from the platform-aware runtime lock.

The nine skips are unfinished **learner-starter acceptance** cases: C01 one, S1 one, and U2 seven. They are not claimed passes. Corresponding reference behavior is exercised separately. Untouched starter commands honestly report `STARTER_NOT_COMPLETED`; workbook instructions explain how to assess edited starters instead of treating reference tests as evidence of learner completion.

The [test summary](validation/test_summary.json) and [environment record](validation/environment.json) give the exact result and installed versions. `requirements.txt` pins top-level runtime dependencies; `requirements.lock.txt` retains complete runtime pins and platform markers. Optional authoring dependencies are separate in `requirements-docs.txt`, with the complete tested authoring environment in `requirements-docs.lock.txt`.

Real Chroma default ONNX embeddings were downloaded/used; retrieval was not replaced by a keyword or fake-embedding fallback. The clearly labeled original three-page synthetic teaching PDF is supplied with editable data, a rebuild script, and [provenance](../data/rag_provenance.md). It is not misrepresented as the original video’s finance PDF.

## Current integrations and resolved compatibility issues

The saved configurable model, `claude-opus-5-5`, passed a real Messages API check returning `ANTHROPIC_CONNECTION_OK`. Model/account availability is not assumed for other students. The earlier rejected credential was replaced privately; no key value appears in the materials.

LangSmith acknowledged a synthetic check trace, and the current asynchronous retrieval API read back and matched its stored inputs/outputs at the configured APAC endpoint. LangWatch acknowledged a separate real OTLP check with **HTTP 200 and zero rejected spans**. See [service-check evidence](validation/service_checks.json). A check trace is not proof that every lesson trace is visible in a dashboard.

Live testing identified rejection of forced named-tool selection by the configured model. L11 and S2 now use supported automatic tool choice, explicit prompts, and strict checks that the intended actual calls occurred. The model was not silently changed and a missing tool call is not accepted as a success.

The integration review also found and closed two reference-integrity gaps: U1 now inspects **both** recovered snapshots before either recall, with an ordering regression; L11 rejects a fabricated non-PDF source/page marker even when accompanied by a valid PDF citation. Added regression tests pass. Current official-source references and video-versus-current differences appear in the matched chapters.

## Word rendering and visual inspection

All **331 actual PDF-proof pages** were rendered from the final DOCX files through LibreOffice. All page contact sheets were visually reviewed, with covers, dense code, diagrams, and warning pages also inspected at readable size. Targeted corrections removed orphaned reference-only pages, obsolete production wording, and duplicated bibliography headings. Dense original diagrams retain detailed editable sources and use more readable printed overviews where appropriate.

The final [document-layout record](validation/document_layout.json) records DOCX/PDF hashes, actual PDF page counts, image counts, and page-bound checks. Final automated checks found **no overflow candidates and no sparse-page warnings**. Draft page images are cleared before inspection so old pages cannot inflate counts. DOCX packages were reopened and checked for corruption and unresolved insertion markers. PDFs and page proofs are working QA artifacts, not additional promised course deliverables. Microsoft Word may repaginate according to its fonts/printer configuration; inspection here used LibreOffice rendering.

## Source review and attribution

The complete **03:09:51** caption track was reviewed across eleven sections. The index phase checked 36 timestamped video frames; handbook production added visual selection and eleven attributed stills. Continuous-caption checks resolved the apparent memory/tools and Drafter/RAG chapter-boundary issues. This is a complete content review supported by sampled visuals, **not** a claim that every video frame was watched in real time.

See the [timestamped source map](video_source_map.md), [visual review](video_visual_review.md), and chapter-level current official references. Video excerpts credit Vaibhav Mehra/freeCodeCamp with exact timestamps and source URLs; rights in those excerpts remain with their owners. The supplementary labs, synthetic dataset, original diagrams, and additional exercises are identified as adaptations, not publisher-endorsed source material.

## Security and explicit limits

The private `.env` stays ignored and owner-readable/writable only on macOS. `.env.example` contains blank secret placeholders and safe public configuration defaults. The exporter checks known local secret values and high-confidence key patterns, including the XML inside DOCX packages, before copying tracked files. No full source video/caption download, private task metadata, working logs, virtual environment, or credential file belongs in the delivery archive or commit. Synthetic data only was used for model calls and selected telemetry.

Windows setup is documented using Python 3.12, the platform-aware lock, and direct virtual-environment interpreter commands. **Windows installation, filesystem/symlink behavior, and execution were not tested.** No Windows pass is claimed.

LangSmith/LangWatch **dashboard pages were not visually inspected**. Submission, HTTP acknowledgment, stored API read-back, callback ancestry, and local flush are distinguished; none is mislabeled as dashboard verification or proof of all remote span relationships.

Optional stretch/design prompts are not additional validated implementations unless explicitly identified. U2/C01 checkpoints are in-process; U1 separately covers durable SQLite state. Thread IDs are not authentication. Fingerprint approval and safe file creation are classroom patterns, not authenticated production authorization, transactional exactly-once saving, crash/power-loss recovery, or production security certification. Citation integrity is not semantic entailment; human evidence review remains required.

## Repository and reuse

Canonical materials are published on **`course/anthropic-observability-2026-11-03`** in [nuvear/01_LangGraph](https://github.com/nuvear/01_LangGraph/tree/course/anthropic-observability-2026-11-03). Existing foundation examples, source-review records, and the original Word training index are retained. The open index file is not replaced by a handbook. The README contains exact setup, module execution, authoring, and evidence-regeneration commands.
