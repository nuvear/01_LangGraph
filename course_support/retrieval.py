"""Portable synthetic-PDF retrieval using real local Chroma ONNX embeddings.

Public contract: prepare_store(directory: Path) -> collection;
search(collection, query: str, k: int = 3) -> list[dict].
No client or embedding download is started at import time.
"""
from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
from typing import Any

PDF_PATH = Path(__file__).resolve().parents[1] / "data" / "rag_teaching_handbook.pdf"
CHUNK_SIZE = 650
CHUNK_OVERLAP = 90
INDEX_SPEC = (
    f"rag-v1|minilm-l6-v2-onnx|chars{CHUNK_SIZE}-overlap{CHUNK_OVERLAP}|cosine"
)


def load_chunks(pdf_path: Path = PDF_PATH) -> list[dict]:
    """Read actual PDF pages; preserve their 1-based numbers when splitting."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from pypdf import PdfReader

    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise FileNotFoundError(f"Teaching PDF not found: {pdf_path}")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    fingerprint = sha256(pdf_path.read_bytes()).hexdigest()[:16]
    chunks = []
    for page_number, page in enumerate(PdfReader(pdf_path).pages, start=1):
        text = (page.extract_text() or "").strip()
        for part_number, part in enumerate(splitter.split_text(text), start=1):
            chunks.append({
                "id": f"{fingerprint}-p{page_number}-c{part_number}",
                "text": part,
                "source": pdf_path.name,
                "page": page_number,
            })
    if not chunks:
        raise ValueError("PDF contains no extractable text; scanned PDFs need OCR.")
    return chunks


def prepare_store(directory: Path) -> Any:
    """Build/reopen a versioned local collection with DefaultEmbeddingFunction.

    First use may download Chroma's real all-MiniLM-L6-v2 ONNX model. Persistent
    data stays in directory/chroma. PDF bytes, splitter settings and model tag
    select the collection; changing them never silently mixes incompatible data.
    Call serially for a given directory; this teaching helper is not a migration
    system or a multi-writer ingestion service.
    """
    # Set before lazy imports; Settings also explicitly opts out of telemetry.
    os.environ["ANONYMIZED_TELEMETRY"] = "False"
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

    chunks = load_chunks()
    fingerprint = sha256(PDF_PATH.read_bytes() + INDEX_SPEC.encode()).hexdigest()
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(directory / "chroma"),
        settings=Settings(
            anonymized_telemetry=False,
            chroma_otel_collection_endpoint="",
            chroma_otel_granularity="none",
        ),
    )
    collection = client.get_or_create_collection(
        name=f"course_rag_{fingerprint[:20]}",
        embedding_function=DefaultEmbeddingFunction(),
        metadata={"index_spec": INDEX_SPEC, "pdf_sha256": sha256(
            PDF_PATH.read_bytes()
        ).hexdigest(), "synthetic_replacement": True},
        configuration={"hnsw": {"space": "cosine"}},
    )
    if collection.metadata.get("index_spec") != INDEX_SPEC:
        raise ValueError("Incompatible index; choose a new run directory.")
    ids = [chunk["id"] for chunk in chunks]
    existing = set(collection.get(include=[])["ids"])
    if existing != set(ids):
        if existing - set(ids):
            raise ValueError("Unexpected records; choose a new run directory.")
        collection.upsert(
            ids=ids, documents=[chunk["text"] for chunk in chunks],
            metadatas=[{"source": chunk["source"], "page": chunk["page"]}
                       for chunk in chunks],
        )
    assert collection.count() == len(chunks)
    return collection


def search(store: Any, query: str, k: int = 3) -> list[dict]:
    """Return top-k nearest chunks, not a guarantee that the answer exists.

    Blank query and empty collection return []; invalid types/counts raise.
    Each hit has exactly id, text, source and 1-based page. No keyword fallback,
    invented similarity threshold or fake embedding path is implemented.
    """
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    if not query.strip():
        return []
    count = store.count()
    if not count:
        return []
    result = store.query(
        query_texts=[query.strip()], n_results=min(k, count),
        include=["documents", "metadatas"],
    )
    hits = []
    for identifier, text, metadata in zip(
        result["ids"][0], result["documents"][0], result["metadatas"][0],
        strict=True,
    ):
        if not text or not metadata:
            raise ValueError("Index hit is missing text or provenance.")
        page = metadata.get("page")
        if isinstance(page, bool) or not isinstance(page, int) or page < 1:
            raise ValueError("Index hit must have a 1-based integer page.")
        if not isinstance(metadata.get("source"), str) or not metadata["source"]:
            raise ValueError("Index hit must have a source filename.")
        hits.append({"id": identifier, "text": text,
                     "source": metadata["source"], "page": page})
    return hits
