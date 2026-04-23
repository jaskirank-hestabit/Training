
import os
import json
import hashlib
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# FAISS import guard
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[VectorStore] WARNING: faiss-cpu not installed. Run: pip install faiss-cpu")

"""
VECTOR MEMORY — FAISS-based semantic similarity store.
Stores embeddings of facts/answers for similarity-based recall.
Persists to disk at data/memory/faiss_index.bin + vector_meta.json
"""

# Local embedder (no API needed)
def _embed(text: str, dim: int = 128) -> np.ndarray:
    """
    Deterministic character-bigram hash embedding.
    Produces a normalised float32 vector — good enough for local semantic search.
    """
    vec = np.zeros(dim, dtype=np.float32)
    text = text.lower().strip()
    for i in range(len(text) - 1):
        bigram = text[i:i + 2]
        h = int(hashlib.md5(bigram.encode()).hexdigest(), 16)
        vec[h % dim] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


MEMORY_DIR  = os.getenv("MEMORY_DIR", "data/memory")
INDEX_FILE  = os.path.join(MEMORY_DIR, "faiss_index.bin")
META_FILE   = os.path.join(MEMORY_DIR, "vector_meta.json")
DIM = 128


class VectorStore:
    """
    Persistent FAISS vector store for long-term semantic memory.

    Each entry:
        id      : integer index
        text    : raw content stored
        type    : 'fact' | 'summary' | 'query' | 'answer'
        session : session identifier
        ts      : ISO timestamp
        score   : L2 distance (lower = more similar), added on search results
    """

    def __init__(self):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        self._meta: list[dict] = []
        self._index = None
        self._load()

    # persistence

    def _load(self):
        if not FAISS_AVAILABLE:
            return
        if os.path.exists(INDEX_FILE) and os.path.exists(META_FILE):
            try:
                self._index = faiss.read_index(INDEX_FILE)
                with open(META_FILE, "r", encoding="utf-8") as f:
                    self._meta = json.load(f)
                print(f"[VectorStore] Loaded {len(self._meta)} vectors from disk.")
                return
            except Exception as e:
                print(f"[VectorStore] Load error ({e}). Starting fresh.")
        self._index = faiss.IndexFlatL2(DIM)
        self._meta  = []

    def _save(self):
        if not FAISS_AVAILABLE or self._index is None:
            return
        faiss.write_index(self._index, INDEX_FILE)
        with open(META_FILE, "w", encoding="utf-8") as f:
            json.dump(self._meta, f, indent=2)

    # public API

    def add(self, text: str, mem_type: str = "fact", session: str = "default") -> int:
        """
        Embed and store a piece of text.
        Returns its integer ID.
        """
        if not FAISS_AVAILABLE or self._index is None:
            return -1
        vec = _embed(text, DIM).reshape(1, -1)
        self._index.add(vec)
        entry = {
            "id":      len(self._meta),
            "text":    text,
            "type":    mem_type,
            "session": session,
            "ts":      datetime.utcnow().isoformat(),
        }
        self._meta.append(entry)
        self._save()
        return entry["id"]

    def search(self, query: str, top_k: int = 5, session: str = None) -> list[dict]:
        """
        Find the top_k most semantically similar stored texts.
        Optionally filter by session.
        Returns list of entry dicts with an added 'score' key (L2 distance).
        """
        if not FAISS_AVAILABLE or self._index is None or len(self._meta) == 0:
            return []
        vec = _embed(query, DIM).reshape(1, -1)
        k   = min(top_k * 3, len(self._meta))
        distances, indices = self._index.search(vec, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self._meta):
                continue
            entry = self._meta[idx].copy()
            entry["score"] = float(dist)
            if session and entry["session"] != session:
                continue
            results.append(entry)
            if len(results) >= top_k:
                break
        return results

    def get_all(self, session: str = None) -> list[dict]:
        """Return all stored entries, optionally filtered by session."""
        if session:
            return [m for m in self._meta if m["session"] == session]
        return list(self._meta)

    def count(self) -> int:
        return len(self._meta)

    def clear(self):
        """Delete all vectors and metadata."""
        if FAISS_AVAILABLE:
            self._index = faiss.IndexFlatL2(DIM)
        self._meta = []
        self._save()
        print("[VectorStore] Cleared.")


# module-level singleton
_vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store