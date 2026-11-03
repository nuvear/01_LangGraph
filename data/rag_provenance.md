# L11 retrieval asset provenance

The supplied `rag_teaching_handbook.pdf` is an **original synthetic teaching dataset** with three pages of fictional Harbor Learning Lab policies. It contains no real personal or financial information. `rag_teaching_handbook.json` is the editable page text; `rag_build_pdf.py` rebuilds the portable PDF with ReportLab. Citation pages are the actual PDF's 1-based pages. The baseline and exercise use these inspectable facts, allowing supported, unsupported and empty-evidence cases to be tested without sending private documents to a model or tracing service.

## Official API sources verified with search and fetch

- https://docs.trychroma.com/docs/embeddings/embedding-functions — DefaultEmbeddingFunction uses all-MiniLM-L6-v2 locally and may automatically download model files. Installed Chroma 1.5.9 source inspection confirms its default delegates to ONNXMiniLM_L6_V2 and advertises a 256-token input limit.
- https://cookbook.chromadb.dev/core/clients/ — PersistentClient writes to its selected local path.
- https://cookbook.chromadb.dev/core/configuration/ — Settings/anonymized telemetry opt-out; helper explicitly disables anonymized telemetry and does not configure Chroma tracing.
- https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter — recursive splitting defaults to character sizing and targets overlap rather than guaranteeing exact overlap.
- https://docs.langchain.com/oss/python/integrations/chat/anthropic — bind_tools, tool choices and normalized tool_calls. No temperature override is needed here.
- https://docs.langchain.com/oss/python/langgraph/graph-api — MessagesState, partial updates, explicit boundary edges, conditional routes, recursion config.

The helper talks to an embedded local Chroma client, not a paid embedding endpoint. First-use embedding model download requires internet. Generation still requires real Anthropic calls in authorized live validation. Offline tests explicitly use named model and collection doubles; they are not retrieval-quality or paid-model validation.
