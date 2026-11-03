# Foundation and training-index validation

Validated on 3 November 2026 on macOS 26.6.2 / arm64, Python 3.12.13.

## Passed

- After the user replaced the rejected key locally, the actual Anthropic Messages request returned exactly `ANTHROPIC_CONNECTION_OK` using the configured `claude-opus-5-5` model (39 input and 20 output tokens).
- A real ChatAnthropic call inside a compiled LangGraph returned `LANGGRAPH_ANTHROPIC_OK`, retained two messages, and reported 41 input plus 22 output tokens. Both tracing callbacks were enabled.
- LangSmith acknowledged the synthetic trace and the current asynchronous API retrieved and matched the stored synthetic input/output. The configured APAC endpoint was used.
- LangWatch acknowledged an actual synthetic OTLP ingestion request with HTTP 200 and no rejected spans. The checker validates the response, rather than claiming that an empty local queue proves delivery.
- The deterministic two-node graph passed with `none`, `langsmith`, `langwatch`, and `both` backend selections.
- Nineteen offline regression tests passed. They cover deterministic graph behavior, supported official HTTPS endpoints, invalid endpoints, configuration failure, and credential-safe error reports.
- A clean native Python virtual environment installed `requirements.lock.txt`, ran the offline graph, and passed all nineteen tests independently of the original uv environment.
- The working environment passed the dependency consistency check. Optional Word-build dependencies are separate from the runtime lock.
- The complete 03:09:51 caption track was reviewed in eleven sections. Thirty-six timestamped source-video frames were inspected across the runtime; both apparent caption-boundary truncations were resolved against the continuous track.
- The 10-page Word training index was rendered through LibreOffice. All pages were checked as image contact sheets; dense pages were also inspected at readable size. A cover-formatting defect found during QA was corrected and the cover was re-rendered.

## Tested runtime versions

- `anthropic==2.4.0`
- `langgraph==1.2.19`
- `langchain-anthropic==1.7.9`
- `langchain-core==1.7.4`
- `langwatch==1.4.0`
- `langsmith==0.14.17`
- `python-dotenv==1.2.4`
- `pytest==9.2.0`

`requirements.lock.txt` pins the full runtime environment; `requirements-docs.txt` pins the additional Word builder. The clean runtime reinstall and current workspace both passed the foundation tests.

## Security

Keys remain only in the local ignored `.env`. That file has owner-only 0600 permissions on macOS. Reports do not record credential values. Traces contain synthetic teaching data. The downloaded full source video, captions, complete service reports, working logs, virtual environments, and task metadata are not intended repository deliverables and are ignored by Git. Only an empty-secret `.env.example` is published.

## Explicit limits

This is the index-and-foundation phase, not a completed course. No full student/teacher/workbook documents, completed lesson exercise set, RAG implementation, durable-checkpoint lab, or capstone are claimed. Their code, acceptance tests, and genuine execution screenshots will be produced after scope approval. The source-video visual checks are not screenshots of executed adapted Python code.

Dashboard pages for LangWatch and LangSmith were not visually inspected. Ingestion/read-back API checks and graph callback completion do not substitute for dashboard-layout checks or prove every future span relationship.

Windows setup instructions are documented but were not executed on Windows. Windows dependency wheels, filesystem behavior, and the final commands must be tested separately or remain explicitly marked untested.

The local embedding model, original RAG PDF availability/rights or labeled replacement, and exact durable-checkpoint/tool-runtime package choices remain implementation decisions. A text log is not durable graph state; an in-memory checkpoint does not survive process restart.
