# Entry point for FastAPI app
import vector_store.faiss_handler
print("✅ faiss_handler.py loaded:", vector_store.faiss_handler.__file__)

import json
from embeddings.embedder import Embedder
from vector_store.faiss_handler import FAISSHandler
from llm.sgllm import SuggestionGenerator
import numpy as np

# Load data
with open("notes/dummy_data.json") as f:
    data = json.load(f)

print("Needs:", data.get("needs"))
print("Availabilities:", data.get("availabilities"))

notes = [(note, "need", i) for i, note in enumerate(data.get("needs", []))]
notes += [(note, "availability", i) for i, note in enumerate(data.get("availabilities", []))]

texts = [n[0] for n in notes]
print("Texts to embed:", texts)

embedder = Embedder()
embeddings = embedder.get_embeddings(texts)
print(f"Embeddings count: {len(embeddings)}")

embeddings_np = np.array(embeddings).astype("float32")
print("Embedding shape:", embeddings_np.shape)

indexer = FAISSHandler()
indexer.add(embeddings_np, [(typ, i) for _, typ, i in notes])

similar_pairs = indexer.search(embeddings_np, top_k=5, threshold=0.3)

sgllm = SuggestionGenerator(api_key="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")

print("\n--- Suggestions ---\n")
for (type1, i), (type2, j), score in similar_pairs:
    if type1 == "need" and type2 == "availability":
        suggestion = sgllm.generate(data["needs"][i], data["availabilities"][j])
        print(f"Need: {data['needs'][i]}")
        print(f"Availability: {data['availabilities'][j]}")
        print(f"Suggestion: {suggestion}\n{'-'*50}\n")
