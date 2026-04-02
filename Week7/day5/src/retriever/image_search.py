# src/retriever/image_search.py
from src.vectorstore.faiss_store import FAISSStore
from src.embeddings.clip_embedder import get_text_embedding, get_image_embedding

IMAGE_INDEX = "src/vectorstore/image_index.faiss"


class ImageSearcher:
    def __init__(self):
        self.store = FAISSStore(dim=512)   # CLIP dimension
        self.store.load(IMAGE_INDEX)

    # ── TEXT → IMAGE (FAISS local index) ──
    def search_by_text(self, query: str, k: int = 5):
        emb = get_text_embedding(query)
        return self.store.search(emb, k)

    # ── IMAGE → IMAGE (FAISS local index) ──
    def search_by_image(self, image_path: str, k: int = 5):
        emb = get_image_embedding(image_path)
        return self.store.search(emb, k)

    # ── IMAGE → SIMILAR IMAGES (web — any image) ──
    def search_similar_web(
        self,
        image_path: str,
        user_hint: str = "",
        k: int = 6,
    ) -> tuple[list[dict], str]:
        """
        Find visually similar images anywhere on the web.
        Works for images NOT in our local index (uploaded images, etc.).

        Returns (results_list, query_used).
        """
        from src.retriever.web_image_search import search_similar_images_web
        return search_similar_images_web(image_path, user_hint=user_hint, k=k)


# ── IMAGE → TEXT ANSWER (standalone helper) ──
def image_to_text_answer(image_path: str, query: str) -> str:
    from src.generator.llm_client import generate_answer

    searcher = ImageSearcher()
    results  = searcher.search_by_image(image_path)

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