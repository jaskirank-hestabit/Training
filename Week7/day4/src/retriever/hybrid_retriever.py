from rank_bm25 import BM25Okapi
from src.embeddings.embedder import get_query_embedding
from src.vectorstore.faiss_store import FAISSStore
from src.retriever.reranker import rerank_results
import numpy as np
import yaml

CONFIG_PATH = "src/config/model.yaml"

with open(CONFIG_PATH) as f:
    _cfg = yaml.safe_load(f)

TOP_K   = _cfg.get("retrieval", {}).get("top_k", 5)
FAISS_PATH = "src/vectorstore/index.faiss"

# ---------- helpers ----------

def _cosine(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))


def _mmr(query_emb, candidates, k, lambda_=0.5):
    """
    Max Marginal Relevance — balances relevance vs diversity.
    lambda_ = 1 → pure relevance  |  lambda_ = 0 → pure diversity
    """
    selected, remaining = [], list(candidates)

    while len(selected) < k and remaining:
        # relevance score to query
        relevance = [_cosine(query_emb, r["_emb"]) for r in remaining]

        # redundancy score = max similarity to already-selected docs
        if not selected:
            redundancy = [0.0] * len(remaining)
        else:
            redundancy = [
                max(_cosine(r["_emb"], s["_emb"]) for s in selected)
                for r in remaining
            ]

        mmr_scores = [
            lambda_ * rel - (1 - lambda_) * red
            for rel, red in zip(relevance, redundancy)
        ]

        best_idx = int(np.argmax(mmr_scores))
        selected.append(remaining.pop(best_idx))

    return selected


# ---------- retriever ----------

class HybridRetriever:
    def __init__(self):
        self.store = FAISSStore(dim=384)   # all-MiniLM-L6-v2 dimension
        self.store.load(FAISS_PATH)

        self.corpus = [t.split() for t in self.store.texts]
        self.bm25   = BM25Okapi(self.corpus)

    # ---- private helpers ----

    def _apply_filters(self, results, filters):
        """
        Flexible filter matching.
        Supports both canonical keys (doc_type) and task shorthand (type).
        Example filters: {"type": "pdf"} or {"doc_type": "pdf"}
        """
        KEY_ALIASES = {
            "type": "doc_type",
            "doc_type": "doc_type",
            "source": "source",
            "page": "page_number",
            "page_number": "page_number",
            "year": "year",   # only present if you add it to metadata
        }

        def match(meta, key, val):
            canonical = KEY_ALIASES.get(key, key)
            return str(meta.get(canonical, "")).lower() == str(val).lower()

        return [
            r for r in results
            if all(match(r["metadata"], k, v) for k, v in filters.items())
        ]

    # ---- public search methods ----

    def keyword_search(self, query, k=TOP_K):
        scores  = self.bm25.get_scores(query.split())
        ranked  = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:k * 2]

        results = []
        for idx, score in ranked:
            results.append({
                "text":     self.store.texts[idx],
                "score":    float(score),
                "metadata": self.store.metadata[idx],
                "search_type": "bm25",
            })
        return results

    def semantic_search(self, query, k=TOP_K):
        query_emb = get_query_embedding(query)
        results   = self.store.search(query_emb, k=k * 2)

        for r in results:
            r["search_type"] = "semantic"

        return results, query_emb

    # ---- main entry point ----

    def retrieve(self, query, k=TOP_K, filters=None, use_mmr=True, lambda_mmr=0.5):
        """
        Full hybrid pipeline:
          1. Semantic search (FAISS)
          2. Keyword fallback (BM25)
          3. Merge + optional filter
          4. Rerank (cosine)
          5. Deduplicate
          6. MMR diversity selection
        """
        semantic_results, query_emb = self.semantic_search(query, k)
        keyword_results              = self.keyword_search(query, k)

        # --- merge ---
        combined = semantic_results + keyword_results

        # --- filter ---
        if filters:
            filtered = self._apply_filters(combined, filters)
            # keyword fallback: if filter removes everything, use unfiltered
            if not filtered:
                print("  [Retriever] Filter returned 0 results — using unfiltered fallback")
            else:
                combined = filtered

        # --- rerank ---
        reranked = rerank_results(query, combined)

        # --- deduplicate ---
        seen, unique = set(), []
        for r in reranked:
            if r["text"] not in seen:
                seen.add(r["text"])
                unique.append(r)

        # --- attach embeddings for MMR ---
        if use_mmr and len(unique) > k:
            from src.embeddings.embedder import get_embeddings
            embs = get_embeddings([r["text"] for r in unique])
            for r, emb in zip(unique, embs):
                r["_emb"] = emb

            unique = _mmr(query_emb, unique, k=k, lambda_=lambda_mmr)

        # --- clean up internal keys ---
        for r in unique:
            r.pop("_emb", None)

        return unique[:k]