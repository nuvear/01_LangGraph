# Technical sources for the course foundation

Checked on 3 November 2026. These sources support the environment and observability code introduced in the foundation phase. The full lesson source map is maintained separately in `video_source_map.md`.

## Anthropic

The connection checker calls the official Messages API with the model configured in `ANTHROPIC_MODEL`. It uses a single synthetic prompt and a 64-token output limit, with retries disabled. A successful authentication test must return the expected sentinel response; merely finding a non-empty key is not a test. [1] [2]

The initial live request returned HTTP 401. After the user replaced the key locally, the configured `claude-opus-5-5` model returned the exact `ANTHROPIC_CONNECTION_OK` sentinel. A separate real ChatAnthropic call inside LangGraph, with both observability callbacks enabled, returned `LANGGRAPH_ANTHROPIC_OK` and retained the human/AI message pair. These checks establish the basic model and framework path, not the still-unimplemented course tool loops, RAG exercises, or capstone. The supplied local `.env` was preserved and no key values were logged.

## LangGraph

The foundation demo defines a `TypedDict` state, returns partial state updates from two ordinary Python functions, builds a `StateGraph`, and connects `START` and `END`. It compiles before invocation. These choices follow the current graph API; the demo does not make a language-model request. [3]

## LangWatch

The official Python integration attaches the LangChain callback at the graph invocation so graph nodes and model/tool calls can be represented in the trace. The helper in `course_support/observability.py` uses a dedicated OpenTelemetry provider and flushes it before exit. Credentials stay in local configuration rather than graph state or metadata. [4]

The pinned SDK's `setup()` signature does not accept every option shown in the current guide. In particular, the helper sets project scope through `LANGWATCH_PROJECT_ID` during initialization instead of passing `project_id` to `setup()`. The installed client reads that environment variable. The original value is restored afterward. New API keys may need this project scope; legacy project keys carry their scope. [5] [6]

The connection checker sends an actual synthetic OTLP payload to the documented receiver used by the SDK. It checks the HTTP status and acknowledgment rather than treating a successful local queue flush as proof of ingestion. The observed service returned a JSON acknowledgment to an OTLP protobuf request; the checker accepts JSON and protobuf acknowledgments. Dashboard visibility is a separate manual check and has not been claimed.

## LangSmith

The helper supplies an explicit LangChain callback and reads the configured regional endpoint. The user's local configuration selects the APAC endpoint. The example template defaults to US and explains that users must select their own region. Automatic ambient tracing is disabled inside the helper so choosing `--backend none` does not silently export classroom data. [7]

The current `client.runs.retrieve()` method is asynchronous and requires a project UUID. The connection checker awaits it and requests the input/output fields explicitly; this replaces the deprecated `read_run()` path. The trace check compares the stored synthetic inputs and outputs, rather than merely checking that a create call returned. [8]

Choosing `--backend both` intentionally sends the synthetic graph data to both services. This is not anonymization. Use synthetic teaching data and do not put API keys, personal data, or full configuration dictionaries into graph state, prompts, tool arguments, or tracing metadata.

## References

[1]: https://platform.claude.com/docs/en/api/overview "Claude API overview and authentication"
[2]: https://platform.claude.com/docs/en/api/messages/create "Create a message"
[3]: https://docs.langchain.com/oss/python/langgraph/graph-api "LangGraph Graph API"
[4]: https://langwatch.ai/docs/integration/python/integrations/langgraph "LangWatch LangGraph instrumentation"
[5]: https://langwatch.ai/docs/integration/python/guide "LangWatch Python integration guide"
[6]: https://langwatch.ai/docs/platform/api-keys "LangWatch API keys and project scope"
[7]: https://docs.langchain.com/langsmith/trace-with-langchain "Trace LangChain and LangGraph applications with LangSmith"
[8]: https://docs.langchain.com/langsmith/smithdb-sdk-migration-runs "LangSmith run retrieval migration to SmithDB"
