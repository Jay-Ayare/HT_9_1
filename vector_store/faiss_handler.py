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
        print(f"FAISS DEBUG: Searching with threshold {threshold}")
        print(f"FAISS DEBUG: Query shape: {query.shape}, Index total: {self.index.ntotal}")
        
        try:
            scores, indices = self.index.search(query, top_k)
            print(f"FAISS DEBUG: Search completed successfully")
            print(f"FAISS DEBUG: Raw scores shape: {scores.shape}")
            print(f"FAISS DEBUG: Score ranges: min={scores.min():.4f}, max={scores.max():.4f}")
            
            results = []
            for i, idx_list in enumerate(indices):
                for j, idx in enumerate(idx_list):
                    print(f"FAISS DEBUG: Query {i} -> Index {idx} = {scores[i][j]:.4f} (threshold: {threshold})")
                    if scores[i][j] > threshold and idx != i:
                        results.append((i, idx, scores[i][j]))
            print(f"FAISS DEBUG: Found {len(results)} results above threshold")
            return results
        except Exception as e:
            print(f"FAISS DEBUG: Search failed with error: {e}")
            import traceback
            traceback.print_exc()
            return []
