# Retrieval Strategies — Day 2

## Architecture Overview
```
Query
  │
  ├── Semantic Search (FAISS + all-MiniLM-L6-v2)
  │       └── Top-2K nearest neighbours by cosine similarity
  │
  ├── Keyword Search (BM25Okapi)
  │       └── TF-IDF style sparse retrieval
  │
  ├── Merge & Filter
  │       └── Optional metadata filters (doc_type, source, page, year)
  │
  ├── Reranker (cosine cross-score)
  │       └── Re-scores every candidate against query embedding
  │
  ├── Deduplication
  │       └── Exact text match — removes repeated chunks from both retrievers
  │
  └── MMR (Max Marginal Relevance)
          └── Balances relevance vs diversity in final top-K
```

## Why Hybrid?

| Method | Strength | Weakness |
|---|---|---|
| Semantic (FAISS) | Captures meaning, synonyms | Misses exact keywords |
| BM25 | Great for exact terms, numbers | No semantic understanding |
| Hybrid | Best of both | Needs reranking to merge scores |

## Reranking

We use **cosine similarity** between the query embedding and each candidate's embedding
as a rerank score. This re-orders the merged list by true semantic proximity rather than
the separate BM25/FAISS scores (which are not on the same scale).

A cross-encoder model (e.g. `cross-encoder/ms-marco-MiniLM-L-6-v2`) would give higher
precision but adds ~200ms latency per query.

## MMR (Max Marginal Relevance)

Prevents the top-K from being 5 nearly identical chunks.
```
MMR(d) = λ · sim(query, d) − (1−λ) · max sim(d, selected)
```

- `λ = 1` → pure relevance
- `λ = 0` → pure diversity  
- We use `λ = 0.5` as default

## Chunking Strategy

- **Chunk size**: 500 words ≈ 667 tokens (within 500–800 token target)
- **Overlap**: 100 words — preserves cross-boundary context
- **PDF**: real page numbers tracked per chunk
- **Non-PDF**: estimated page numbers (acceptable — no page boundaries)

## Hallucination Reduction

1. Prompt instructs LLM to answer ONLY from context
2. Numbered context blocks `[1] ... [2] ...` help the model localise answers
3. `repetition_penalty=1.1` reduces output loops
4. `do_sample=False` (greedy) gives deterministic, conservative answers
5. Context window capped at 500 words to avoid noise

## Traceable Sources

Every answer comes with a source list showing:
- Filename
- Page number
- Document type
- Whether found via semantic or BM25
- Rerank score