from src.retriever.hybrid_retriever import HybridRetriever
from src.pipelines.context_builder import build_context
import yaml

CONFIG_PATH = "src/config/model.yaml"

with open(CONFIG_PATH) as f:
    _cfg = yaml.safe_load(f)

TOP_K = _cfg.get("retrieval", {}).get("top_k", 5)


def query(text, k=TOP_K, filters=None):
    retriever = HybridRetriever()

    results = retriever.retrieve(
        query=text,
        k=k,
        filters=filters
    )

    context, sources = build_context(results)

    return {
        "results": results,
        "context": context,
        "sources": sources
    }


if __name__ == "__main__":
    print("Advanced RAG Query Engine (Day 2)")
    print("Type your question (or press Enter for default)\n")

    user_input = input("Enter your query: ").strip()

    if not user_input:
        user_input = "Explain how credit underwriting works"

    print(f"\n Searching for: {user_input}\n")

    output = query(
        user_input,
        filters=None  # Example: {"doc_type": "pdf"}
    )

    print("\n================ CONTEXT ================\n")
    print(output["context"][:1000])

    print("\n================ SOURCES ================\n")
    for s in output["sources"]:
        print(s)

    print("\n================ RAW RESULTS ================\n")
    for i, r in enumerate(output["results"], 1):
        meta = r.get("metadata", {})
        print(f"--- Result {i} ---")
        print(f"Rerank Score : {r.get('rerank_score', 0):.4f}")
        print(f"Search Type  : {r.get('source')}")
        print(f"Source       : {meta.get('source', 'unknown')}")
        print(f"Page         : {meta.get('page_number', '?')}")
        print(f"Type         : {meta.get('doc_type', '?')}")
        print(f"Text         : {r['text'][:200]}...\n")