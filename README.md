# 01_LangGraph


## Current stage: training index for approval

This project will become a practical Python course based on [Vaibhav Mehra’s freeCodeCamp LangGraph video](https://youtu.be/jGg_1h0qzaM). The latest request is to review the whole source and approve the complete index **before** further lesson development.

- [Editable Word training index](docs/LangGraph_Training_Index.docx)
- [Index source](course/training_index.md)
- [Detailed video source map](course/video_source_map.md)
- [Whole-track visual-review record](course/video_visual_review.md)
- [Technical documentation sources](course/technical_sources.md)
- [Validation and limitations](course/validation_report.md)

The complete caption track was reviewed across eleven sections, with 36 timestamped visual checks spanning the full 03:09:51 video. Original code: [source course repository](https://github.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp). The planned track includes eleven core lessons, preparation, two modern implementation labs, LangSmith, LangWatch, and a capstone: approximately 29h 55m excluding breaks.

The three full handbooks, complete exercise set, and capstone are **not yet delivered**. This branch contains the draft index and a tested environment/observability foundation. Starter files and instructor solutions will be separated during lesson production.

## macOS setup

Use Python 3.12 from the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock.txt
```

Equivalent `uv` commands were also tested:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.lock.txt
```

Copy `.env.example` to `.env` only if `.env` does not already exist. Preserve supplied credentials. Enter keys directly in that local file; never put them in code, chat, screenshots, logs, or Git. Restrict the macOS file with `chmod 600 .env`.

## Windows setup — documented, not executed on Windows yet

PowerShell commands use the virtual-environment interpreter directly, avoiding execution-policy changes:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -m examples.observability_demo --backend none
.\.venv\Scripts\python.exe -m course_support.check_connections --service all
.\.venv\Scripts\python.exe -m examples.anthropic_graph --backend both
.\.venv\Scripts\python.exe -m pytest -q
```

Windows wheel availability, filesystem behavior, and commands remain to be validated before final publication. The lock was tested on macOS arm64 with Python 3.12.13, including a clean native `venv` reinstall.

## Configuration and live checks

`ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL` are required for model-dependent examples. The configured `claude-opus-5-5` model passed a real connection check and a ChatAnthropic-in-LangGraph invocation on 3 November 2026. Availability/billing are account-specific, so model selection remains configurable.

LangSmith uses `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, and the regional `LANGSMITH_ENDPOINT`; `LANGSMITH_WORKSPACE_ID` may be required by key scope. LangWatch uses `LANGWATCH_API_KEY`, `LANGWATCH_PROJECT_ID` where required, and `LANGWATCH_ENDPOINT`. `.env.example` contains blank secret placeholders, never the local values.

With the environment active:

```bash
python -m examples.observability_demo --backend none
python -m examples.observability_demo --backend langsmith
python -m examples.observability_demo --backend langwatch
python -m examples.observability_demo --backend both
python -m course_support.check_connections --service all
python -m examples.anthropic_graph --backend both
python -m pytest -q
```

The two-node demo needs no LLM. The Anthropic demo sends a small paid request. All tracing inputs are synthetic. The helper disables implicit ambient tracing and explicitly selects `none`, `langsmith`, `langwatch`, or `both`. Selecting both intentionally sends graph inputs/outputs to both services; it is not anonymization.

LangSmith connection validation reads back and compares stored inputs/outputs. LangWatch validation checks its actual HTTP acknowledgment. A completed callback or queue flush alone does not prove a dashboard received a trace. Dashboard visual inspection remains a later validation step.

## Rebuild the Word index

```bash
python -m pip install -r requirements-docs.txt
python tools/build_training_index.py
```

The builder reads `course/training_index.md` and writes `docs/LangGraph_Training_Index.docx`. The delivered index is rendered and inspected, with navigable headings, source timestamps, and page numbers.

Local credentials, virtual environments, downloaded complete source media/captions, working logs, and task metadata are ignored by Git. See the validation report for actual coverage; the foundation is not a claim that every planned lesson, assessment, screenshot, or capstone is complete.
