from src.embeddings.embedder import get_query_embedding
from src.vectorstore.faiss_store import FAISSStore
import yaml

CONFIG_PATH = "src/config/model.yaml"
with open(CONFIG_PATH) as f:
    _cfg = yaml.safe_load(f)

TOP_K = _cfg.get("retrieval", {}).get("top_k", 3)
FAISS_PATH = "src/vectorstore/index.faiss"


def query(text, k=TOP_K):
    query_emb = get_query_embedding(text)

    store = FAISSStore(dim=len(query_emb))
    store.load(FAISS_PATH)

    results = store.search(query_emb, k=k)
    return results


if __name__ == "__main__":
    print("RAG Query Engine")
    print("Type your question (or press Enter for default)\n")

    user_input = input("Enter your query: ").strip()

    if not user_input:
        user_input = "What is company policy?"

    print(f"\nSearching for: {user_input}\n")

    results = query(user_input)

    print("Top Results:\n")
    for i, r in enumerate(results, 1):
        meta = r.get("metadata", {})
        print(f"--- Result {i} ---")
        print(f"Score  : {r['score']:.4f}")
        print(f"Source : {meta.get('source', 'unknown')}")
        print(f"Page   : {meta.get('page_number', '?')}")
        print(f"Type   : {meta.get('doc_type', '?')}")
        print(f"Tags   : {meta.get('tags', [])}")
        print(f"Text   : {r['text'][:300]}...")
        print()
