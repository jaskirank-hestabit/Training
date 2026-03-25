import faiss
import numpy as np
import pickle

class FAISSStore:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, embeddings, texts):
        self.index.add(np.array(embeddings).astype("float32"))
        self.texts.extend(texts)

    def save(self, path="index.faiss"):
        faiss.write_index(self.index, path)
        with open("texts.pkl", "wb") as f:
            pickle.dump(self.texts, f)

    def load(self, path="index.faiss"):
        self.index = faiss.read_index(path)
        with open("texts.pkl", "rb") as f:
            self.texts = pickle.load(f)

    def search(self, query_embedding, k=3):
        D, I = self.index.search(
            np.array([query_embedding]).astype("float32"), k
        )
        return [self.texts[i] for i in I[0]]