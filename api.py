import numpy as np
import os
import re
import json
import sys
from dotenv import load_dotenv
from fastapi import FastAPI

# Add the project root to the Python path to resolve module imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from embeddings.embedder import Embedder
from vector_store.faiss_handler import FAISSHandler
from llm.sgllm import SuggestionGenerator
from nat.nat_filler import NATFiller

# --- Models ---
class NotesRequest(BaseModel):
    notes: List[str]

class Suggestion(BaseModel):
    need: str
    availability: str
    suggestion: str
    score: float

class ProcessedNote(BaseModel):
    id: str
    content: str
    sentiments: List[str]
    resources_needed: List[str]
    resources_available: List[str]

class ProcessResponse(BaseModel):
    processed_notes: List[ProcessedNote]
    suggestions: List[Suggestion]

# --- Initialization ---
load_dotenv()

app = FastAPI(
    title="HT - The Cognition Engine API",
    description="Processes user notes to find and suggest non-obvious connections.",
    version="0.1.0",
)

# Allow requests from your React frontend (assuming it runs on localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables.")

embedder = Embedder()
sgllm = SuggestionGenerator(api_key=API_KEY)
nat_filler = NATFiller(api_key=API_KEY)

# --- Helper Functions (adapted from main.py) ---

def process_notes_api(notes: list[str], nat_filler: NATFiller) -> list[dict]:
    """Processes raw notes into structured NATs without console output."""
    nats = []
    for i, note in enumerate(notes):
        nat_raw = nat_filler.fill_nat(note)
        try:
            cleaned = re.sub(r"(^```json\s*|```$)", "", nat_raw.strip(), flags=re.MULTILINE)
            nat = json.loads(cleaned)
            nat.setdefault("resources_needed", [])
            nat.setdefault("resources_available", [])
            nat["original_note"] = note
            nat["id"] = i
            nats.append(nat)
        except (json.JSONDecodeError, TypeError):
            # In a real app, you'd log this error
            print(f"Could not decode JSON for Note {i+1}. Skipping.")
    return nats

def prepare_vdb_entries(nats: list[dict]) -> list[tuple]:
    """Converts structured NATs into a flat list of entries for the vector database."""
    entries = []
    for nat in nats:
        for need in nat.get("resources_needed", []):
            entries.append((need, "need", nat["id"]))
        for availability in nat.get("resources_available", []):
            entries.append((availability, "availability", nat["id"]))
    return entries

# --- API Endpoint ---

@app.post("/process-notes", response_model=ProcessResponse)
async def process_notes_endpoint(request: NotesRequest):
    """
    Receives a list of notes, processes them, and returns suggestions.
    """
    # 1. Process notes to get structured NATs
    nats = process_notes_api(request.notes, nat_filler)
    
    # 2. Prepare entries for the vector database
    entries = prepare_vdb_entries(nats)
    if not entries:
        return []

    # 3. Embed entries and build the index
    # For an API, we rebuild the index on each call.
    # For a production system, you'd use a persistent vector DB.
    indexer = FAISSHandler()
    texts = [e[0] for e in entries]
    embeddings = np.array(embedder.get_embeddings(texts)).astype("float32")
    indexer.add(embeddings)

    # 4. Search for connections and generate suggestions
    similar_pairs = indexer.search(embeddings, top_k=5, threshold=0.3)
    suggestions = []
    for query_idx, result_idx, score in similar_pairs:
        type1 = entries[query_idx][1]
        type2 = entries[result_idx][1]

        if type1 == "need" and type2 == "availability":
            need_text = entries[query_idx][0]
            availability_text = entries[result_idx][0]
            suggestion_text = sgllm.generate(need_text, availability_text)
            suggestions.append({
                "need": need_text,
                "availability": availability_text,
                "suggestion": suggestion_text,
                "score": score,
            })

    # 5. Prepare the processed notes for the response
    processed_notes = [
        {
            "id": str(nat["id"]),
            "content": nat["original_note"],
            "sentiments": nat["sentiments"],
            "resources_needed": nat["resources_needed"],
            "resources_available": nat["resources_available"],
        } for nat in nats
    ]

    return {"processed_notes": processed_notes, "suggestions": suggestions}