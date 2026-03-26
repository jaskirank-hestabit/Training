from src.embeddings.embedder import get_query_embedding, get_embeddings
import numpy as np


def cosine_sim(a, b):
    return float(np.dot(a, b))


def rerank_results(query, results):
    """
    Blended reranking: 60% cosine similarity + 40% normalized BM25 score.
    This prevents the cosine reranker from completely ignoring strong
    keyword matches when semantic similarity is moderate.
    """
    if not results:
        return results

    query_emb = get_query_embedding(query)
    texts     = [r["text"] for r in results]
    doc_embs  = get_embeddings(texts)

    # --- cosine scores ---
    cosine_scores = [cosine_sim(query_emb, emb) for emb in doc_embs]

    # --- normalize BM25 scores to [0, 1] ---
    raw_bm25 = [r.get("score", 0.0) if r.get("search_type") == "bm25" else 0.0
                for r in results]

    max_bm25 = max(raw_bm25) if max(raw_bm25) > 0 else 1.0
    norm_bm25 = [s / max_bm25 for s in raw_bm25]

    # --- blend ---
    scored = []
    for r, cos, bm25 in zip(results, cosine_scores, norm_bm25):
        blended = 0.6 * cos + 0.4 * bm25
        r["rerank_score"]  = round(blended, 4)
        r["cosine_score"]  = round(cos, 4)
        r["bm25_score"]    = round(bm25, 4)
        scored.append(r)

    scored.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored