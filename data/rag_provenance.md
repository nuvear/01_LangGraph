# L11 retrieval asset provenance

Checked 3 November 2026. The source PDF **is available** at https://raw.githubusercontent.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp/main/Agents/Stock_Market_Performance_2024.pdf . The upstream tree lists that file at blob `4a1bdd198dc903e3c591da7fa2ce01cf6a8ff5ba` in commit `9f172bf8ae6f3cc5094b0905d843f792266619af` (https://api.github.com/repos/iamvaibhavmehra/LangGraph-Course-freeCodeCamp/git/trees/main?recursive=1). The document was opened through fetch and its text inspected. We do not redistribute it or use its finance answers: financial assertions and incomplete source references have not been independently validated, and the course needs explicitly synthetic, inspectable evidence safe to trace.

`rag_teaching_handbook.pdf` is therefore an **original synthetic teaching replacement**, not the video's Stock Market Performance PDF. It has three pages, fictional Harbor Learning Lab policies, and no real personal or financial information. Every page carries the replacement label. `rag_teaching_handbook.json` is the original editable page text; `rag_build_pdf.py` rebuilds the portable PDF with ReportLab. Citation pages are the actual PDF's 1-based pages. The baseline and exercise use these exact facts, not the original S&P 500 question or a nine-page assertion.

## Official API sources verified with search and fetch

- https://docs.trychroma.com/docs/embeddings/embedding-functions — DefaultEmbeddingFunction uses all-MiniLM-L6-v2 locally and may automatically download model files. Installed Chroma 1.5.9 source inspection confirms its default delegates to ONNXMiniLM_L6_V2 and advertises a 256-token input limit.
- https://cookbook.chromadb.dev/core/clients/ — PersistentClient writes to its selected local path.
- https://cookbook.chromadb.dev/core/configuration/ — Settings/anonymized telemetry opt-out; helper explicitly disables anonymized telemetry and does not configure Chroma tracing.
- https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter — recursive splitting defaults to character sizing and targets overlap rather than guaranteeing exact overlap.
- https://docs.langchain.com/oss/python/integrations/chat/anthropic — bind_tools, tool choices and normalized tool_calls. No temperature override is needed here.
- https://docs.langchain.com/oss/python/langgraph/graph-api — MessagesState, partial updates, explicit boundary edges, conditional routes, recursion config.
- https://raw.githubusercontent.com/iamvaibhavmehra/LangGraph-Course-freeCodeCamp/main/Agents/RAG_Agent.py — source concepts and historical paths/imports; the upstream current comprehension is valid, so the old review's undefined-variable warning is not reproduced as a present-source defect.

The helper talks to an embedded local Chroma client, not a paid embedding endpoint. First-use embedding model download requires internet. Generation still requires real Anthropic calls in the parent's authorized live validation. Offline tests explicitly use named model and collection doubles; they are not retrieval-quality or paid-model validation.
