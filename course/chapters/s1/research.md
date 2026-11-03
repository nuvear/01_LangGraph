# S1 — Official-source verification

Verified on 3 November 2026 by search followed by page extraction. No service requests, credentials, or dashboard access were used.

- https://docs.langchain.com/langsmith/trace-with-langgraph — LangGraph and LangChain runnable tracing; parent/child graph/model/tool relationships; workspace identifier and region-specific API endpoints. Official snippets use another provider and ambient tracing variables; S1 deliberately uses the existing explicit callback runtime and Anthropic instead. New agent-based workspaces require an agent/environment compatibility project name; the existing course helper uses `LANGSMITH_PROJECT`, so provisioning remains the instructor's responsibility.
- https://docs.langchain.com/langsmith/smithdb-sdk-migration-runs — `await client.runs.retrieve(...)` replaces synchronous `read_run` guidance; `project_id` is required, `start_time` is optional, and field projection defaults to ID only. Request `INPUTS` and `OUTPUTS` explicitly. The existing safe checker already uses `await client.aread_project(...)`, bounded retries, and `selects=["ID", "INPUTS", "OUTPUTS"]`. A synthetic persisted read-back is not proof that a later graph trace is visible in a dashboard.
- https://docs.langchain.com/langsmith/evaluation-concepts — deterministic code evaluators enforce fixed rules; model-based evaluators add judgment and cost. A local evaluation report is not automatically a LangSmith experiment.
- https://docs.langchain.com/langsmith/create-account-api-key — key permissions and workspace scope must match the intended operation; never include a key in prompts or metadata.
- https://docs.langchain.com/langsmith/evaluate-llm-application — SDK evaluation can run a target over examples and attach evaluators. S1 keeps its three-example evaluation set in Python and writes a local report; no automatic dataset upload is claimed.

Locally inspected without model/network activity: Python environment contains langgraph 1.2.19, langchain-anthropic 1.7.9, langchain-core 1.7.4, langsmith 0.14.17, pytest 9.2.0. These observations describe the authoring environment, not a cross-platform guarantee or a dependency-file change.
