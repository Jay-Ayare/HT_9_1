#!/usr/bin/env python3

import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from vector_store.faiss_handler import FAISSHandler
from embeddings.embedder import Embedder

# Test data
texts = [
    "books to read",
    "quiet reading space", 
    "access to free library",
    "daily free time"
]

print("Testing FAISS in isolation...")
print(f"Processing {len(texts)} texts...")

# Generate embeddings
embedder = Embedder()
embeddings = np.array(embedder.get_embeddings(texts)).astype("float32")
print(f"Generated embeddings shape: {embeddings.shape}")

# Test FAISS
indexer = FAISSHandler()
indexer.add(embeddings)
print(f"Added to index, total: {indexer.index.ntotal}")

# Test search
print("Testing search...")
try:
    results = indexer.search(embeddings, top_k=3, threshold=0.1)
    print(f"Search successful! Found {len(results)} results")
    for query_idx, result_idx, score in results:
        print(f"  {query_idx} -> {result_idx}: {score:.4f}")
        print(f"    '{texts[query_idx]}' <-> '{texts[result_idx]}'")
except Exception as e:
    print(f"Search failed: {e}")
    import traceback
    traceback.print_exc()
