from src.vectorstore.faiss_store import FAISSStore
from src.embeddings.clip_embedder import get_text_embedding, get_image_embedding

IMAGE_INDEX = "src/vectorstore/image_index.faiss"


class ImageSearcher:
    def __init__(self):
        self.store = FAISSStore(dim=512)  # CLIP dimension
        self.store.load(IMAGE_INDEX)

    # TEXT -> IMAGE
    def search_by_text(self, query, k=5):
        emb = get_text_embedding(query)
        return self.store.search(emb, k)

    # IMAGE -> IMAGE
    def search_by_image(self, image_path, k=5):
        emb = get_image_embedding(image_path)
        return self.store.search(emb, k)


# IMAGE -> TEXT ANSWER  (standalone function, not a method)
def image_to_text_answer(image_path, query):
    from src.generator.llm_client import generate_answer

    searcher = ImageSearcher()
    results = searcher.search_by_image(image_path)

    context = "\n".join([
        r["metadata"]["caption"] + " " + r["metadata"]["ocr_text"]
        for r in results
    ])

    prompt = f"""
Context:
{context}

Question: {query}

Answer using only the context.
"""
    return generate_answer(prompt)