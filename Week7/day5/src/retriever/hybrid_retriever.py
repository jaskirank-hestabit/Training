# src/retriever/hybrid_retriever.py  (full file — only __init__ changed)
from rank_bm25 import BM25Okapi
from src.embeddings.embedder import get_query_embedding
from src.vectorstore.faiss_store import FAISSStore
from src.retriever.reranker import rerank_results
import numpy as np
import yaml

CONFIG_PATH = "src/config/model.yaml"

with open(CONFIG_PATH) as f:
    _cfg = yaml.safe_load(f)

TOP_K      = _cfg.get("retrieval", {}).get("top_k", 5)
FAISS_PATH = "src/vectorstore/index.faiss"

def _cosine(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))

def _mmr(query_emb, candidates, k, lambda_=0.5):
    selected, remaining = [], list(candidates)
    while len(selected) < k and remaining:
        relevance   = [_cosine(query_emb, r["_emb"]) for r in remaining]
        redundancy  = ([0.0] * len(remaining) if not selected else
                       [max(_cosine(r["_emb"], s["_emb"]) for s in selected)
                        for r in remaining])
        mmr_scores  = [lambda_ * rel - (1 - lambda_) * red
                       for rel, red in zip(relevance, redundancy)]
        best_idx = int(np.argmax(mmr_scores))
        selected.append(remaining.pop(best_idx))
    return selected


class HybridRetriever:
    def __init__(self, store: FAISSStore = None):
        if store is not None:
            self.store = store
        else:
            self.store = FAISSStore(dim=384)
            self.store.load(FAISS_PATH)

        self.corpus = [t.split() for t in self.store.texts]
        self.bm25   = BM25Okapi(self.corpus)

    def _apply_filters(self, results, filters):
        KEY_ALIASES = {
            "type": "doc_type", "doc_type": "doc_type",
            "source": "source", "page": "page_number",
            "page_number": "page_number", "year": "year",
        }
        def match(meta, key, val):
            canonical = KEY_ALIASES.get(key, key)
            return str(meta.get(canonical, "")).lower() == str(val).lower()
        return [r for r in results
                if all(match(r["metadata"], k, v) for k, v in filters.items())]

    def keyword_search(self, query, k=TOP_K):
        scores = self.bm25.get_scores(query.split())
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:k * 2]
        return [{"text": self.store.texts[idx], "score": float(sc),
                 "metadata": self.store.metadata[idx], "search_type": "bm25"}
                for idx, sc in ranked]

    def semantic_search(self, query, k=TOP_K):
        query_emb = get_query_embedding(query)
        results   = self.store.search(query_emb, k=k * 2)
        for r in results:
            r["search_type"] = "semantic"
        return results, query_emb

    def retrieve(self, query, k=TOP_K, filters=None, use_mmr=True, lambda_mmr=0.5):
        semantic_results, query_emb = self.semantic_search(query, k)
        keyword_results             = self.keyword_search(query, k)

        combined = semantic_results + keyword_results

        if filters:
            filtered = self._apply_filters(combined, filters)
            if filtered:
                combined = filtered
            else:
                print("  [Retriever] Filter returned 0 results — using unfiltered fallback")

        reranked = rerank_results(query, combined)

        seen, unique = set(), []
        for r in reranked:
            if r["text"] not in seen:
                seen.add(r["text"])
                unique.append(r)

        if use_mmr and len(unique) > k:
            from src.embeddings.embedder import get_embeddings
            embs = get_embeddings([r["text"] for r in unique])
            for r, emb in zip(unique, embs):
                r["_emb"] = emb
            unique = _mmr(query_emb, unique, k=k, lambda_=lambda_mmr)

        for r in unique:
            r.pop("_emb", None)

        return unique[:k]