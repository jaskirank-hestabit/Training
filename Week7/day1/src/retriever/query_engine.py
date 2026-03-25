from embeddings.embedder import get_embeddings
from vectorstore.faiss_store import FAISSStore

def query(text):
    store = FAISSStore(dim=1536)
    store.load("src/vectorstore/index.faiss")

    query_embedding = get_embeddings([text])[0]
    results = store.search(query_embedding)

    return results


if __name__ == "__main__":
    res = query("What is company policy?")
    for r in res:
        print("\n---\n", r)