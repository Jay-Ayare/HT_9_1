# FAISS storage/retrieval logic

import faiss
import numpy as np

class FAISSHandler:
    def __init__(self, dim=384):
        self.index = faiss.IndexFlatIP(dim)
        self.data = []

    def add(self, vectors: np.ndarray, metadata: list[tuple[str, int]]):
        if vectors.ndim == 1:  # single vector case
            vectors = vectors.reshape(1, -1)
        self.index.add(vectors)
        self.data.extend(metadata)

    def search(self, query: np.ndarray, top_k: int = 5, threshold: float = 0.85):
        scores, indices = self.index.search(query, top_k)
        results = []
        for i, idx_list in enumerate(indices):
            for j, idx in enumerate(idx_list):
                if scores[i][j] > threshold and idx != i:
                    results.append((self.data[i], self.data[idx], scores[i][j]))
        return results
