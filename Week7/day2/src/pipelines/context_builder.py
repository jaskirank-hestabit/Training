MIN_CHUNK_SCORE = 0.40   # individual chunk must score above this to enter context

def build_context(results, max_words=800):
    context_parts = []
    sources       = []
    total_words   = 0

    for i, r in enumerate(results):
        # drop individually weak chunks even if they passed the gate
        if r.get("rerank_score", 0) < MIN_CHUNK_SCORE:
            continue

        text  = r["text"].strip()
        words = text.split()

        if total_words + len(words) > max_words:
            break

        context_parts.append(f"[{i+1}] {text}")
        total_words += len(words)

        meta = r.get("metadata", {})
        sources.append({
            "source":       meta.get("source", "unknown"),
            "page":         meta.get("page_number", "?"),
            "type":         meta.get("doc_type", "?"),
            "search_type":  r.get("search_type", "?"),
            "rerank_score": round(r.get("rerank_score", 0.0), 4),
        })

    context = "\n\n".join(context_parts)
    return context.strip(), sources