import numpy as np
import json
import re
from embeddings.embedder import Embedder
from vector_store.faiss_handler import FAISSHandler
from llm.sgllm import SuggestionGenerator
from nat.nat_filler import NATFiller  



# Init
nat_filler = NATFiller(api_key="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")
embedder = Embedder()
indexer = FAISSHandler()
sgllm = SuggestionGenerator(api_key="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")

# Load raw notes
with open("notes/user_notes.json") as f:
    data = json.load(f)["notes"]

nats = []
for i, note in enumerate(data):
    print(f"\nProcessing Note {i + 1}")
    nat_raw = nat_filler.fill_nat(note)
    print("NAT:", nat_raw)
    
    # OPTIONAL: clean output from stringified JSON to dict


for i, note in enumerate(data):
    print(f"\nProcessing Note {i + 1}")
    nat_raw = nat_filler.fill_nat(note)
    print("RAW RESPONSE:", nat_raw[:200])  # Optional: log start of raw response

    # Clean triple backticks + markdown around JSON
    cleaned = re.sub(r"(^```json\s*|```$)", "", nat_raw.strip(), flags=re.MULTILINE)
    nat = json.loads(cleaned)

    nat["original_note"] = note
    nat["id"] = i
    nats.append(nat)


    import json as pyjson
    cleaned = re.sub(r"(^```json\s*|```$)", "", nat_raw.strip(), flags=re.MULTILINE)
    nat = pyjson.loads(cleaned)
    nat["original_note"] = note
    nat["id"] = i
    nats.append(nat)

# Convert NATs into units for VDB
entries = []
for nat in nats:
    for need in nat["resources_needed"]:
        entries.append((need, "need", nat["id"]))
    for availability in nat["resources_available"]:
        entries.append((availability, "availability", nat["id"]))

# Embed and add
texts = [e[0] for e in entries]
embeddings = embedder.get_embeddings(texts)
indexer.add(np.array(embeddings).astype("float32"), [(t, i) for _, t, i in entries])

# Search + Suggest
similar_pairs = indexer.search(np.array(embeddings).astype("float32"), top_k=5, threshold=0.3)
for (type1, i), (type2, j), _ in similar_pairs:
    if type1 == "need" and type2 == "availability":
        suggestion = sgllm.generate(entries[i][0], entries[j][0])
        print(f"\n--- Suggestion ---")
        print(f"Need: {entries[i][0]}")
        print(f"Availability: {entries[j][0]}")
        print(f"Suggestion: {suggestion}")
