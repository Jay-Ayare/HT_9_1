# FAISS storage/retrieval logic

import faiss
import numpy as np
from typing import List, Tuple

class FAISSHandler:
    def __init__(self, dim=384):
        self.index = faiss.IndexFlatIP(dim)

    def add(self, vectors: np.ndarray):
        if vectors.ndim == 1:  # single vector case
            vectors = vectors.reshape(1, -1)
        self.index.add(vectors)

    def search(self, query: np.ndarray, top_k: int = 5, threshold: float = 0.85):
        scores, indices = self.index.search(query, top_k)
        results = []
        for i, idx_list in enumerate(indices):
            for j, idx in enumerate(idx_list):
                if scores[i][j] > threshold and idx != i:
                    results.append((i, idx, scores[i][j]))
        return results
