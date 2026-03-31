# src/pipelines/ingest_single.py
"""Ingest a single file into an in-memory FAISSStore (not persisted to disk)."""

import os, yaml
from src.utils.loader import load_file
from src.utils.chunker import chunk_text, chunk_pdf_pages
from src.embeddings.embedder import get_embeddings
from src.vectorstore.faiss_store import FAISSStore

with open("src/config/model.yaml") as f:
    _cfg = yaml.safe_load(f)

_chunk  = _cfg.get("chunking", {})
CHUNK_SIZE = _chunk.get("chunk_size", 500)
OVERLAP    = _chunk.get("overlap", 100)

_EXT_MAP = {".txt":"txt", ".md":"md", ".pdf":"pdf", ".docx":"docx", ".csv":"csv"}


def ingest_single_file(path: str, source_name: str = None) -> FAISSStore:
    """
    Load → chunk → embed a single file.
    Returns an in-memory FAISSStore ready for HybridRetriever.
    """
    if source_name is None:
        source_name = os.path.basename(path)

    doc_type = _EXT_MAP.get(os.path.splitext(path)[1].lower(), "unknown")
    content  = load_file(path)

    if not content:
        raise ValueError(f"File appears empty or unreadable: {path}")

    if doc_type == "pdf":
        chunks = chunk_pdf_pages(content, source=source_name,
                                 chunk_size=CHUNK_SIZE, overlap=OVERLAP)
    else:
        if not content.strip():
            raise ValueError("File has no text content.")
        chunks = chunk_text(content, source=source_name, doc_type=doc_type,
                            chunk_size=CHUNK_SIZE, overlap=OVERLAP)

    if not chunks:
        raise ValueError("No chunks could be created from this file.")

    texts = [c["text"] for c in chunks]
    embeddings = []
    for i in range(0, len(texts), 20):
        batch = get_embeddings(texts[i:i + 20])
        if batch:
            embeddings.extend(batch)

    if not embeddings:
        raise ValueError("Embedding generation failed.")

    store = FAISSStore(len(embeddings[0]))
    store.add(embeddings, chunks)
    return store