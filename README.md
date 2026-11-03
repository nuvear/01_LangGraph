# 01_LangGraph

A complete, self-contained Python course for learners who know basic Python and are new to LangGraph, with current Anthropic examples, separate student starters and instructor solutions, local-embedding RAG, durable-memory and human-approval labs, LangSmith, LangWatch, and a capstone.

Development and deliverables are on **`course/anthropic-observability-2026-11-03`**. Version 1.1 presents the course as a standalone sequence with original concept illustrations. The full track follows P00 → L01–L11 → U1–U2 → S1–S2 → C01 and is planned for approximately 29h 55m excluding breaks. Chapters point to useful insertion locations for the advanced labs.

## The three complete handbooks

- **Student Handbook:** [Word](docs/LangGraph_Student_Handbook.docx), [self-contained HTML](docs/LangGraph_Student_Handbook.html), [Markdown](docs/LangGraph_Student_Handbook.md).
- **Teacher Handbook:** [Word](docs/LangGraph_Teacher_Handbook.docx), [self-contained HTML](docs/LangGraph_Teacher_Handbook.html), [Markdown](docs/LangGraph_Teacher_Handbook.md).
- **Exercise Workbook:** [Word](docs/LangGraph_Exercise_Workbook.docx), [self-contained HTML](docs/LangGraph_Exercise_Workbook.html), [Markdown](docs/LangGraph_Exercise_Workbook.md).

Both handbooks embed original concept illustrations and flowcharts, the delivered Python examples/solutions, and genuine screenshots of actual captured execution. Screenshots explicitly identify the browser-rendered stdout source; they do not pretend to be a native Terminal window. Full logs and source hashes are supplied alongside them. HTML embeds its illustrations; Markdown needs the relative asset folders. Official technical-documentation references and evidence citations remain intact.

## Fresh checkout and macOS setup

Skip cloning when this repository is already open. Install Python 3.12 and Git first.

```bash
git clone --branch course/anthropic-observability-2026-11-03 https://github.com/nuvear/01_LangGraph.git
cd 01_LangGraph
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock.txt
test -f .env || cp .env.example .env
chmod 600 .env
python -m course_lessons.p00 --backend none
python -m pytest -q
```

The runtime lock was generated with platform markers and installed successfully in a fresh native macOS virtual environment. Python 3.12.13/macOS arm64 was actually tested. Top-level pins are in `requirements.txt`; complete runtime pins are in `requirements.lock.txt`. Existing `.env` files are never overwritten by the guarded copy command.

Privately edit the local `.env` to provide `ANTHROPIC_API_KEY`. The safe example’s configurable `ANTHROPIC_MODEL=claude-opus-5-5` passed real checks on 3 November 2026; account access and billing are your responsibility. Never paste keys into source, chat, terminal commands, logs, traces, screenshots, or Git. Close the file before screen sharing.

## Windows PowerShell setup — documented, not executed on Windows

After checking out the same branch, use the environment interpreter directly; no execution-policy change is needed:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -m course_lessons.p00 --backend none
.\.venv\Scripts\python.exe -m pytest -q
```

Privately edit `.env` before model-based lessons. Substitute `.\.venv\Scripts\python.exe` for `python` in the handbook commands. Windows wheel installation, filesystem/symlink behavior, and execution remain explicitly untested. Platform markers retain Windows-specific dependency choices, but a platform-aware lock is not a Windows validation result.

## Examples, starters, solutions, and tests

`course_lessons/` contains complete baseline demonstrations. `exercises/starters/` contains actionable TODO files, and `exercises/solutions/` contains separate instructor references. `tests/lessons/` tests delivered demonstrations and solutions using actual graphs and explicitly named offline model doubles. Some starters include their own acceptance harnesses; the workbook explains how to assess learner edits. Directory separation is not access control—omit solutions when distributing a learner-only package.

```bash
python -m course_lessons.l02
python -m exercises.starters.l02
python -m exercises.solutions.l02
python -m pytest tests/lessons/test_l02.py -q
```

Untouched starters honestly print `STARTER_NOT_COMPLETED`; they are intentionally not completed exercises. Run all module commands from the repository root, not by executing a nested `.py` file directly.

P00 and L01–L06 require no model request. L07–L11, U1/U2, S1/S2 and C01 require explicit `--live`, which sends actual paid Anthropic requests. No fake model is silently substituted in live execution.

```bash
python -m course_lessons.l07 --live --backend none
python -m course_lessons.l09 --live --backend none
python -m course_lessons.l11 --live --backend none
python -m course_lessons.u1 --live --backend none
python -m course_lessons.u2 --live --backend none
python -m course_lessons.c01 --live --backend both
python -m exercises.solutions.c01 --live --backend both
```

Save exercises use fresh per-run output directories under `.work/student-runs` unless `--output-dir` is specified. Safe writing rejects traversal, symlinks and existing files instead of silently overwriting them. The capstone actually retrieves evidence, performs the model/tool continuation, pauses for review, tests revision/isolation/error paths, and verifies the saved artifact. Its finite CLI harness scripts human decisions; it is not an authenticated approval interface. U1 separately demonstrates SQLite reopen and fresh-process checkpoint reading; U2/C01 use in-process checkpoint state and do not claim restart durability.

## RAG and synthetic teaching data

`course_support/retrieval.py` uses a real local all-MiniLM-L6-v2 ONNX embedding model through Chroma, persistent indexing, compatible index fingerprints, and source/page metadata. The first embedding operation downloads model weights and requires Internet access; no paid embedding key is needed. Anthropic generation and selected tracing still transmit the relevant synthetic lesson text.

The course supplies an **original three-page synthetic Harbor Learning Lab handbook** with fictional, inspectable policy facts and a clearly labeled classroom dataset. See [dataset provenance](data/rag_provenance.md). `data/rag_build_pdf.py` rebuilds the committed PDF from editable JSON. Chroma product telemetry is disabled. A provenance-valid citation is not proof of semantic entailment; inspect the evidence.

## Tracing and service checks

The preserved foundation demos remain available:

```bash
python -m examples.observability_demo --backend none
python -m examples.observability_demo --backend langsmith
python -m examples.observability_demo --backend langwatch
python -m examples.observability_demo --backend both
python -m examples.anthropic_graph --backend both
```

The deterministic two-node demo needs no LLM. The Anthropic demo makes a small paid request. The helper disables ambient implicit tracing and explicitly selects `none`, `langsmith`, `langwatch` or `both`. P00 deliberately rejects live/non-none options. S1 defaults to LangSmith; S2 defaults to LangWatch. Other modules default to no tracing. Selecting `both` intentionally sends synthetic workflow data to both tracing services; it is not redaction or anonymization.

LangSmith needs `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, the correct regional `LANGSMITH_ENDPOINT`, and possibly `LANGSMITH_WORKSPACE_ID`. LangWatch needs `LANGWATCH_API_KEY`, the endpoint, and project scope where required. Enter only your own account values in `.env`.

With authorization for real requests and synthetic telemetry:

```bash
python -m course_support.check_connections --service anthropic
python -m course_support.check_connections --service langsmith
python -m course_support.check_connections --service langwatch
```

LangSmith checks acknowledged submission plus stored input/output read-back. LangWatch checks actual HTTP 200 acknowledgment and zero rejected spans. The check traces are separate from lesson traces. Callback completion and queue flush do not certify every lesson span’s ingestion or dashboard visibility. Dashboard pages were not visually inspected.

The configured model rejected forced named-tool selection during live testing. The affected examples now use supported automatic selection with explicit prompts and strict checks that real tool calls occurred; the configured model was not silently changed.

## Validation

All **34/34 demonstration and independent reference-solution executions** passed, including 20 real Anthropic-enabled cases. There are **860 passed offline tests and 9 intentional skips** for unfinished learner starter acceptance (C01: 1, S1: 1, U2: 7); matching reference behavior is tested. The same result passed in the clean runtime environment.

See the [complete validation report](course/validation_report.md), [execution manifest](course/validation/execution_manifest.json), [test summary](course/validation/test_summary.json), [environment/version record](course/validation/environment.json), [service-check evidence](course/validation/service_checks.json), and [document-layout record](course/validation/document_layout.json). Optional design extensions are not additional validated implementations unless explicitly identified as such.

## Rebuild the manuals and evidence

Students do not need the authoring tools for ordinary lessons. On the tested macOS authoring setup:

```bash
python -m pip install -r requirements-docs.txt
python tools/build_handbooks.py --output-dir docs
```

The three formats are generated from matched chapter sources in `course/chapters`, actual Python sources, original diagrams, and recorded execution evidence. `requirements-docs.lock.txt` preserves the full tested authoring environment in addition to the separate runtime lock.

To regenerate diagrams, install Node and Google Chrome, then:

```bash
npm --prefix .work/tools/diagrams install --no-audit --no-fund --ignore-scripts @mermaid-js/mermaid-cli
python tools/create_concept_diagrams.py
python tools/create_overview_diagrams.py
python tools/render_course_diagrams.py
python tools/render_course_diagrams.py --overview
```

Use `--chrome /path/to/chrome` for another executable location. Editable concept diagrams explain mental models; compact printed overviews keep dense implementation flowcharts readable.

To repeat all actual model/service executions and replace the evidence, explicitly authorize the cost and synthetic tracing, install the authoring dependencies and Chrome, then run:

```bash
python tools/validate_course.py --live --screenshots
```

`--only L02 L07` limits validation to named modules. `tools/inspect_handbooks.py` checks DOCX packaging and rendered page proofs after LibreOffice renders the three Word files into `.work/previews/handbooks`; Poppler creates the page images and text/bounding-box checks. Working proofs are not published as extra course PDFs.

## Course packaging

The course archive preserves the three manual editions, code, data, editable original diagram sources, tests, and current validation records. Historical planning/index artifacts remain in repository history and are excluded from the standalone export.

```bash
python tools/package_course.py --standalone --overwrite
```

Credentials, virtual environments, task metadata, working logs, preview PDFs, and local delivery copies remain ignored. The approval/save examples are classroom patterns, not production authentication, transactional crash recovery, or security certification.
