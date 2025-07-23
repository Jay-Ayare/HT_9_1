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
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

nat_filler = NATFiller(api_key=API_KEY)
embedder = Embedder()
indexer = FAISSHandler()
sgllm = SuggestionGenerator(api_key=API_KEY)

def process_note_with_nat(note_text: str, note_id: int) -> Dict:
    """Process a single note through NAT extraction."""
    try:
        nat_raw = nat_filler.fill_nat(note_text)
        # Extract JSON from markdown code blocks and explanatory text
        json_match = re.search(r'```json\s*\n(.*?)\n```', nat_raw, re.DOTALL)
        if json_match:
            cleaned = json_match.group(1).strip()
        else:
            # Fallback: try to clean the old way
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
    
    print(f"DEBUG: Processing {len(entries)} entries with {len(embeddings)} embeddings")
    for i, entry in enumerate(entries):
        print(f"  Entry {i}: {entry}")
    
    if not entries:
        print("DEBUG: No entries to process")
        return suggestions
    
    try:
        # Build or load index
        if len(embeddings) > 0:
            # Use numpy-based similarity instead of FAISS to avoid threading issues
            print("DEBUG: Computing similarity using numpy...")
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Compute cosine similarity matrix
            similarity_matrix = cosine_similarity(embeddings)
            print(f"DEBUG: Similarity matrix shape: {similarity_matrix.shape}")
            
            # Find pairs above threshold
            similar_pairs = []
            for i in range(len(embeddings)):
                for j in range(len(embeddings)):
                    if i != j and similarity_matrix[i][j] > SIMILARITY_THRESHOLD:
                        similar_pairs.append((i, j, float(similarity_matrix[i][j])))
            
            print("DEBUG: Similarity computation completed successfully")
            print(f"DEBUG: Found {len(similar_pairs)} similar pairs above threshold {SIMILARITY_THRESHOLD}")
            
            suggestion_id = 1
            for query_idx, result_idx, score in similar_pairs:
                type1 = entries[query_idx][1]
                type2 = entries[result_idx][1]
                print(f"DEBUG: Pair {query_idx}->{result_idx}, types: {type1}->{type2}, score: {score}")
                
                # Only connect needs with availabilities
                if type1 == "need" and type2 == "availability":
                    need_text = entries[query_idx][0]
                    availability_text = entries[result_idx][0]
                    need_note_id = entries[query_idx][2]
                    availability_note_id = entries[result_idx][2]
                    
                    print(f"DEBUG: Generating suggestion for need '{need_text}' + availability '{availability_text}'")
                    
                    # Generate suggestion using LLM
                    try:
                        suggestion_text = sgllm.generate(need_text, availability_text)
                        print(f"DEBUG: Generated suggestion: {suggestion_text[:100]}...")
                    except Exception as e:
                        print(f"DEBUG: LLM generation failed: {e}")
                        suggestion_text = f"Could not generate suggestion: {e}"
                    
                    suggestions.append({
                        "id": f"sugg_{suggestion_id}",
                        "noteId": str(need_note_id),  # Frontend expects noteId (singular)
                        "need": need_text,
                        "availability": availability_text,
                        "suggestion": suggestion_text  # Frontend expects 'suggestion' not 'description'
                    })
                    suggestion_id += 1
                    
    except Exception as e:
        print(f"Error generating suggestions: {e}")
    
    print(f"DEBUG: Generated {len(suggestions)} suggestions")
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
        
        response_data = {
            "processed_notes": processed_notes,
            "suggestions": suggestions
        }
        print(f"DEBUG: Returning response with {len(processed_notes)} notes and {len(suggestions)} suggestions")
        print(f"DEBUG: First suggestion sample: {suggestions[0] if suggestions else 'None'}")
        return jsonify(response_data)
        
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