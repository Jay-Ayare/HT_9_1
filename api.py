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
from graph_db.subgraph_generator import SubgraphGenerator
from graph_db.neo4j_handler import get_neo4j_handler

# Import GraphRAG integration
try:
    from graph_rag_integration import GraphRAGIntegration, GraphRAGConfig, integrate_with_existing_notes
    GRAPHRAG_AVAILABLE = True
except ImportError as e:
    print(f"Warning: GraphRAG integration not available: {e}")
    GRAPHRAG_AVAILABLE = False

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# --- Constants ---
SIMILARITY_THRESHOLD = 0.001
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
subgraph_generator = SubgraphGenerator(api_key=API_KEY)
neo4j_handler = get_neo4j_handler()

# Initialize components
embedder = Embedder()
indexer = FAISSHandler()
sgllm = SuggestionGenerator(api_key=os.getenv("GEMINI_API_KEY"))
nat_filler = NATFiller(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize GraphRAG if available
graph_rag = None
if GRAPHRAG_AVAILABLE:
    try:
        config = GraphRAGConfig(
            chunk_size=300,
            chunk_overlap=50,
            similarity_threshold=0.2,
            enable_visualization=True
        )
        graph_rag = GraphRAGIntegration(config)
        print("GraphRAG integration initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize GraphRAG: {e}")

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
        
        # Generate subgraph for this note (skip if Neo4j not available)
        neo4j_enabled = os.getenv("ENABLE_NEO4J", "true").lower() == "true"
        
        if neo4j_enabled:
            print(f"Generating subgraph for note {note_id}...")
            try:
                # Test Neo4j connection first
                if not neo4j_handler.health_check():
                    print("Neo4j not available, skipping subgraph generation")
                    nat["subgraph_stored"] = False
                else:
                    subgraph_data = subgraph_generator.generate_subgraph(note_text)
                    
                    # Store in Neo4j
                    success = neo4j_handler.create_note_subgraph(str(note_id), subgraph_data)
                    if success:
                        print(f"Subgraph stored successfully for note {note_id}")
                        nat["subgraph_stored"] = True
                    else:
                        print(f"Failed to store subgraph for note {note_id}")
                        nat["subgraph_stored"] = False
            except Exception as e:
                print(f"Error generating/storing subgraph for note {note_id}: {e}")
                nat["subgraph_stored"] = False
        else:
            print("Neo4j disabled, skipping subgraph generation")
            nat["subgraph_stored"] = False
        
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

@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Get all notes."""
    try:
        with open('notes/user_notes.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"notes": []})

@app.route('/api/notes', methods=['POST'])
def add_note():
    """Add a new note."""
    try:
        data = request.get_json()
        note_text = data.get('text', '').strip()
        
        if not note_text:
            return jsonify({"error": "Note text is required"}), 400
        
        # Load existing notes
        try:
            with open('notes/user_notes.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"notes": []}
        
        # Add new note
        data["notes"].append(note_text)
        
        # Save updated notes
        with open('notes/user_notes.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update GraphRAG if available
        if graph_rag:
            try:
                graph_rag.process_documents(data["notes"])
                print("GraphRAG updated with new note")
            except Exception as e:
                print(f"Warning: Could not update GraphRAG: {e}")
        
        return jsonify({"message": "Note added successfully", "note": note_text})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/suggestions', methods=['POST'])
def generate_suggestions():
    """Generate suggestions based on needs and availability."""
    try:
        data = request.get_json()
        need = data.get('need', '').strip()
        availability = data.get('availability', '').strip()
        
        if not need or not availability:
            return jsonify({"error": "Both need and availability are required"}), 400
        
        # Generate basic suggestion
        suggestion = sgllm.generate(need, availability)
        
        # Enhance with GraphRAG if available
        enhanced_suggestion = suggestion
        if graph_rag:
            try:
                from graph_rag_integration import enhance_existing_suggestions
                enhanced_suggestion = enhance_existing_suggestions(graph_rag, need, availability)
            except Exception as e:
                print(f"Warning: Could not enhance suggestion with GraphRAG: {e}")
        
        return jsonify({
            "suggestion": enhanced_suggestion,
            "need": need,
            "availability": availability
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/graphrag/query', methods=['POST'])
def graphrag_query():
    """Query the GraphRAG system."""
    if not GRAPHRAG_AVAILABLE or not graph_rag:
        return jsonify({"error": "GraphRAG is not available"}), 503
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Check if documents have been processed
        if not graph_rag.query_engine:
            return jsonify({"error": "No documents processed. Please add some notes first."}), 400
        
        # Perform query
        response, traversal_path, relevant_content = graph_rag.query(query)
        
        return jsonify({
            "response": response,
            "traversal_path": traversal_path,
            "relevant_content": relevant_content,
            "query": query
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/graphrag/info', methods=['GET'])
def graphrag_info():
    """Get information about the GraphRAG system."""
    if not GRAPHRAG_AVAILABLE:
        return jsonify({"error": "GraphRAG is not available"}), 503
    
    try:
        info = graph_rag.get_graph_info() if graph_rag else {"nodes": 0, "edges": 0}
        return jsonify({
            "available": True,
            "initialized": graph_rag is not None,
            "graph_info": info
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/graphrag/process', methods=['POST'])
def graphrag_process():
    """Process documents for GraphRAG."""
    if not GRAPHRAG_AVAILABLE:
        return jsonify({"error": "GraphRAG is not available"}), 503
    
    try:
        data = request.get_json() or {}
        notes = data.get("notes")
        if notes is None:
            # Fallback to file
            try:
                with open('notes/user_notes.json', 'r') as f:
                    file_data = json.load(f)
                    notes = file_data.get("notes", [])
            except FileNotFoundError:
                notes = []
        
        if not notes:
            return jsonify({"error": "No notes found to process"}), 400
        
        graph_rag.process_documents(notes)
        info = graph_rag.get_graph_info()
        return jsonify({
            "message": "Documents processed successfully",
            "graph_info": info,
            "notes_processed": len(notes)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/nat/fill', methods=['POST'])
def nat_fill():
    """Fill NAT (Needs, Availability, Tasks) from text."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Extract NAT components
        nat_components = nat_filler.extract_nat(text)
        
        return jsonify({
            "nat_components": nat_components,
            "original_text": text
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting HiddenThread API server...")
    print(f"Environment variables loaded: API_KEY={'✓' if API_KEY else '✗'}")
    app.run(debug=True, port=3001, host='0.0.0.0')