import os
import faiss
import numpy as np
import pickle


class FAISSStore:
    def __init__(self, dim):
        # IndexFlatIP = Inner Product = cosine similarity (for normalised vectors)
        # Original used IndexFlatL2 (Euclidean distance) — both work but
        # cosine is more standard for sentence embeddings
        self.index = faiss.IndexFlatIP(dim)
        self.texts = []       # chunk text strings
        self.metadata = []    # chunk metadata dicts (source, page, tags, etc.)

    def add(self, embeddings, chunks):
        """
        Add embeddings + chunks to the index.

        chunks can be:
          - list of dicts: {"text": "...", "metadata": {...}}  - new format
          - list of plain strings                              - old format (still works)
        """
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)

        for chunk in chunks:
            if isinstance(chunk, dict):
                self.texts.append(chunk["text"])
                self.metadata.append(chunk.get("metadata", {}))
            else:
                # backwards compatible with plain strings
                self.texts.append(chunk)
                self.metadata.append({})

    def save(self, path="src/vectorstore/index.faiss"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        faiss.write_index(self.index, path)

        pkl_path = path.replace(".faiss", "_texts.pkl")
        with open(pkl_path, "wb") as f:
            pickle.dump({"texts": self.texts, "metadata": self.metadata}, f)

        print(f"Saved FAISS index → {path}")
        print(f"Saved texts+metadata → {pkl_path}")

    def load(self, path="src/vectorstore/index.faiss"):
        self.index = faiss.read_index(path)

        # load from same folder as faiss file
        pkl_path = path.replace(".faiss", "_texts.pkl")
        with open(pkl_path, "rb") as f:
            data = pickle.load(f)

        # Handle both old format (list of strings) and new format (dict)
        if isinstance(data, dict):
            self.texts = data["texts"]
            self.metadata = data.get("metadata", [{} for _ in self.texts])
        else:
            # old format was just a list of strings
            self.texts = data
            self.metadata = [{} for _ in self.texts]

    def search(self, query_embedding, k=3):
        # Search for top-k similar chunks, Returns list of dicts with text, score, and metadata.
        D, I = self.index.search(
            np.array([query_embedding]).astype("float32"), k
        )

        results = []
        for score, idx in zip(D[0], I[0]):
            if idx == -1:
                continue
            results.append({
                "text": self.texts[idx],
                "score": float(score),
                "metadata": self.metadata[idx],
            })

        return results
