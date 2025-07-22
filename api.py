from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import json
import os
import sys
import re
from datetime import datetime
from typing import List, Dict, Tuple

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from dotenv import load_dotenv
from embeddings.embedder import Embedder
from vector_store.faiss_handler import FAISSHandler
from llm.sgllm import SuggestionGenerator
from nat.nat_filler import NATFiller

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# --- Constants ---
SIMILARITY_THRESHOLD = 0.3
FAISS_INDEX_PATH = "vector_store/ht.index"
ENTRIES_FILE_PATH = "vector_store/entries.json"
EMBEDDINGS_FILE_PATH = "vector_store/embeddings.npy"

# --- Global instances (initialize once) ---
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")

nat_filler = NATFiller(api_key=API_KEY)
embedder = Embedder()
indexer = FAISSHandler()
sgllm = SuggestionGenerator(api_key=API_KEY)

def process_note_with_nat(note_text: str, note_id: int) -> Dict:
    """Process a single note through NAT extraction."""
    try:
        nat_raw = nat_filler.fill_nat(note_text)
        # Clean JSON response
        cleaned = re.sub(r"(^```json\s*|```$)", "", nat_raw.strip(), flags=re.MULTILINE)
        nat = json.loads(cleaned)
        
        # Ensure required fields exist
        nat.setdefault("sentiments", [])
        nat.setdefault("resources_needed", [])
        nat.setdefault("resources_available", [])
        nat["original_note"] = note_text
        nat["id"] = note_id
        
        return nat
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing JSON for note {note_id}: {e}")
        return {
            "sentiments": [],
            "resources_needed": [],
            "resources_available": [],
            "original_note": note_text,
            "id": note_id
        }

def find_connections_and_generate_suggestions(entries: List[Tuple], embeddings: np.ndarray) -> List[Dict]:
    """Find connections between needs and availabilities, generate suggestions."""
    suggestions = []
    
    if not entries:
        return suggestions
    
    try:
        # Build or load index
        if len(embeddings) > 0:
            indexer.add(embeddings)
            similar_pairs = indexer.search(embeddings, top_k=5, threshold=SIMILARITY_THRESHOLD)
            
            suggestion_id = 1
            for query_idx, result_idx, score in similar_pairs:
                type1 = entries[query_idx][1]
                type2 = entries[result_idx][1]
                
                # Only connect needs with availabilities
                if type1 == "need" and type2 == "availability":
                    need_text = entries[query_idx][0]
                    availability_text = entries[result_idx][0]
                    need_note_id = entries[query_idx][2]
                    availability_note_id = entries[result_idx][2]
                    
                    # Generate suggestion using LLM
                    suggestion_text = sgllm.generate(need_text, availability_text)
                    
                    suggestions.append({
                        "id": f"sugg_{suggestion_id}",
                        "type": "connection",
                        "title": f"Resource Connection: {availability_text[:50]}...",
                        "description": suggestion_text,
                        "confidence": float(score),
                        "relatedNoteIds": [str(need_note_id), str(availability_note_id)],
                        "category": "resource_matching",
                        "need": need_text,
                        "availability": availability_text
                    })
                    suggestion_id += 1
                    
    except Exception as e:
        print(f"Error generating suggestions: {e}")
    
    return suggestions

@app.route('/api/notes', methods=['POST'])
def submit_notes():
    """Process submitted notes and return analyzed data with suggestions."""
    try:
        data = request.get_json()
        notes = data.get('notes', [])
        
        if not notes:
            return jsonify({"error": "No notes provided"}), 400
        
        # Process each note through NAT
        processed_nats = []
        for i, note_text in enumerate(notes):
            nat = process_note_with_nat(note_text, i)
            processed_nats.append(nat)
        
        # Create entries for embedding and indexing
        entries = []
        for nat in processed_nats:
            # Add needs
            for need in nat.get("resources_needed", []):
                entries.append((need, "need", nat["id"]))
            # Add availabilities  
            for availability in nat.get("resources_available", []):
                entries.append((availability, "availability", nat["id"]))
        
        # Generate embeddings
        embeddings = np.array([])
        suggestions = []
        
        if entries:
            texts = [e[0] for e in entries]
            embeddings = np.array(embedder.get_embeddings(texts)).astype("float32")
            suggestions = find_connections_and_generate_suggestions(entries, embeddings)
        
        # Format processed notes for frontend
        processed_notes = []
        for nat in processed_nats:
            processed_notes.append({
                "id": str(nat["id"]),
                "content": nat["original_note"],
                "timestamp": datetime.now().isoformat(),
                "sentiments": nat.get("sentiments", []),
                "resources_needed": nat.get("resources_needed", []),
                "resources_available": nat.get("resources_available", []),
                "processed": True
            })
        
        return jsonify({
            "processed_notes": processed_notes,
            "suggestions": suggestions
        })
        
    except Exception as e:
        print(f"Error in submit_notes: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Get all existing suggestions."""
    try:
        # This would typically load from a database
        # For now, return empty array as suggestions are generated per request
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notes/<note_id>/reprocess', methods=['POST'])
def reprocess_note(note_id):
    """Reprocess a specific note."""
    try:
        # This would typically reload the note from database and reprocess
        # For now, return a placeholder response
        return jsonify({
            "id": note_id,
            "content": "Reprocessed note content",
            "timestamp": datetime.now().isoformat(),
            "sentiments": ["hopeful", "determined"],
            "resources_needed": ["guidance"],
            "resources_available": ["experience"],
            "processed": True
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting HiddenThread API server...")
    print(f"Environment variables loaded: API_KEY={'✓' if API_KEY else '✗'}")
    app.run(debug=True, port=3001)