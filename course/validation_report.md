# Standalone LangGraph course — validation report

**Edition 1.1, 3 November 2026.** The three matched manuals cover P00, L01–L11, U1–U2, S1–S2 and C01: 17 modules including the capstone. Student, teacher and workbook material is presented as a self-contained course, with the same assessed exercise contracts and official technical-documentation references.

## Document and illustration checks

All 51 lesson chapter files were revised for standalone wording. Eleven new original concept diagrams complement the existing 17 original implementation diagrams/overviews in each handbook. Both handbooks retain all **34 genuine execution screenshots**, giving **62 distinct embedded images** per handbook. The workbook retains its task-focused text, progressive hints, expected results and completion criteria.

The [standalone audit](validation/standalone_handbooks.json) checks the saved DOCX packages, visible HTML and Markdown editions. All three passed the prohibited-reference scan. No retired artwork remains embedded, all eleven new concept diagrams and all 34 current execution captures are verified in each handbook, and all 17 lesson headings remain in the correct sequence. Official technical URLs and embedded fenced example text were compared during editorial integration; assessed contracts were not changed.

The latest saved input Word files were checked against the canonical versions and backed up before rebuilding. They had no intervening edits, comments or pending revisions. Exported files were also checked against the previous delivery manifest before replacement so user changes would not be silently overwritten.

Final DOCX files are rendered through LibreOffice and reopened for verification. Actual page counts, package hashes, image counts and bounding-box checks are recorded in the [document-layout report](validation/document_layout.json). Contact sheets and representative full-size pages are inspected for readability. Microsoft Word may repaginate according to fonts and printer settings. Working PDF/page proofs are not additional promised deliverables.

## Execution evidence

The [execution manifest](validation/execution_manifest.json) contains **34/34 successful demonstration/reference-solution executions**: 14 deterministic cases and 20 Anthropic-enabled cases. Every current demonstration and reference source file matches its recorded SHA-256 hash.

The L06 wording-only docstring change was followed by fresh demonstration and independent-reference executions. The L11 prompt now describes its synthetic teaching fixture directly. Its three-page dataset label was made standalone, while every policy paragraph and page heading was checked against the previous version and remained unchanged. The PDF was rebuilt, and all eight L11, S1, S2 and C01 demonstration/reference cases were rerun successfully with real Anthropic calls and the selected tracing callbacks. Their logs and screenshots were captured again from actual execution, not retouched or reconstructed.

The runs cover model/tool continuation, local ONNX embeddings, Chroma persistence, supported/unsupported/empty retrieval, SQLite reopen and fresh-interpreter reading, real interrupt/resume, bounded revision/approval, safe saving, isolation and error paths. The capstone produced an actual cited artifact after checking approval against the current draft fingerprint. Its finite command-line harness scripts human decisions; it is not an authenticated production approval interface.

Screenshots are explicitly labeled browser captures of actual stdout/stderr. A viewport may show only part of a long log; complete captured logs are supplied under `assets/execution`. Source/page citation integrity is not semantic entailment, so evidence still requires human review.

## Tests and reproducibility

The source environment and the clean native Python runtime both revalidated at **860 passed, 9 intentionally skipped, zero failures**. The nine skips are unfinished learner-starter acceptance cases: C01 one, S1 one and U2 seven. They are not claimed passes. Corresponding reference behavior is tested separately, and untouched starters honestly report `STARTER_NOT_COMPLETED`.

`pytest.ini` limits automatic discovery to the authoritative `tests` directory; generated export copies are not collected as duplicate test modules. The [test summary](validation/test_summary.json) and [environment record](validation/environment.json) retain the actual results and versions. Python 3.12.13/macOS arm64 was tested. Top-level and complete runtime pins remain in `requirements.txt` and `requirements.lock.txt`; optional authoring dependencies are separate.

Current integrations retain the already-verified configurable Anthropic model, supported automatic tool selection and strict checks for actual calls. The [service-check record](validation/service_checks.json) distinguishes Anthropic success, LangSmith acknowledged submission plus stored API read-back, and LangWatch HTTP acknowledgment with zero rejected spans. Check traces are not proof that every lesson trace is visible remotely.

## Security, distribution and explicit limits

Private values stay in the ignored local `.env`. The exporter scans known local secret values and high-confidence key patterns, including XML inside DOCX packages. The standalone archive excludes historical planning artifacts and retired borrowed visual assets while preserving their repository history. It contains the three manual editions, runnable examples, separate learner starters/instructor solutions, synthetic data, original diagram sources, tests and current validation records. The README supplies exact execution and authoring commands.

Windows installation/execution and filesystem behavior remain **untested**, despite documented PowerShell setup and a platform-aware lock. Remote tracing dashboard pages were not visually inspected. Callback completion, local flush, HTTP acknowledgment and stored API read-back are distinguished; none is described as full dashboard verification.

Optional design extensions are not additional validated implementations unless explicitly identified. U2/C01 state is in-process; U1 separately covers durable SQLite checkpoints. Thread IDs are not authentication. Classroom approval and safe-write patterns do not certify transactional exactly-once behavior, crash/power-loss recovery or production security. Only synthetic teaching data was used in model calls and selected telemetry.

## Repository

The canonical course remains on [`course/anthropic-observability-2026-11-03`](https://github.com/nuvear/01_LangGraph/tree/course/anthropic-observability-2026-11-03). Existing planning/index artifacts are preserved separately; they are not part of the standalone manuals or standalone export. Word embeds images, HTML is self-contained, and Markdown uses relative dependencies included in the complete archive.
