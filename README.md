# HiddenThread (HT_9_1)

**Personal AI Agent for Thought Analysis & Connection Discovery**

HiddenThread transforms scattered thoughts, notes, and observations into structured insights by discovering hidden connections between what you need and what you already have access to. It acts as a "second brain" that generates actionable suggestions when your needs match available resources.

## 🎯 Project Overview

**Core Functionality:**
1. **Input**: Personal notes/thoughts (unstructured text)
2. **Processing**: Extracts sentiments, needs, and available resources using AI
3. **Analysis**: Finds semantic connections using vector similarity search
4. **Output**: AI-generated actionable suggestions when needs match availabilities

**Example Flow:**
- Note 1: "I need quiet reading space and free books"
- Note 2: "I know about CubbonPark Reader's Club nearby"
- Output: Suggestion to visit the club for reading needs + community connection

## 🛠 Tech Stack & Architecture

### Frontend
- **React 18** + **TypeScript** + **Vite**
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Lucide React** for icons

### Backend
- **Python 3.9+** with **Flask**
- **CORS** enabled for frontend communication
- **dotenv** for environment management

### AI/ML Stack
- **SentenceTransformers** (`all-MiniLM-L6-v2`) for embeddings
- **FAISS** for fast similarity search
- **Google Gemini 2.0 Flash** for LLM processing
- **scikit-learn** for additional ML utilities

### Data Storage
- **JSON files** for notes and metadata
- **NumPy arrays** for embeddings
- **FAISS indices** for vector search

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- Gemini API key

### Backend Setup
```bash
# Clone repository
git clone <repo-url>
cd HT_9_1

# Create Python virtual environment
python3.9 -m venv .venv39
source .venv39/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your Gemini API key to .env:
# GEMINI_API_KEY=your_api_key_here

# Run CLI version (optional)
python main.py

# Run API server
python api.py
# Server runs on http://localhost:3001
```

### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
# Frontend runs on http://localhost:5173

# Build for production
npm run build
```

## 📁 Folder Structure

```
HT_9_1/
├── 📁 embeddings/          # Text-to-vector conversion
│   └── embedder.py         # SentenceTransformers wrapper
├── 📁 frontend/            # React TypeScript application
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── types/          # TypeScript definitions
│   │   └── utils/          # API calls, mock data
│   └── package.json
├── 📁 llm/                 # LLM interaction
│   └── sgllm.py           # Suggestion Generator LLM
├── 📁 nat/                 # Note Analysis Tool
│   └── nat_filler.py      # Extracts structured data from notes
├── 📁 notes/               # Sample/test notes
│   └── user_notes.json    # Test data
├── 📁 utils/               # Utility functions
├── 📁 vector_store/        # Vector storage & search
│   ├── faiss_handler.py   # FAISS operations
│   ├── ht.index          # FAISS index file
│   ├── entries.json      # Metadata for vectors
│   └── embeddings.npy    # Stored embeddings
├── api.py                 # Flask API server
├── main.py               # CLI interface
├── requirements.txt      # Python dependencies
└── .env                 # Environment variables
```

## 🔄 How Files Connect to Each Other

### Data Flow Architecture
```
[Frontend UI] 
    ↓ HTTP POST /api/notes
[api.py] 
    ↓ calls
[nat_filler.py] → [Gemini API] (extract sentiments/needs/resources)
    ↓ structured data
[embedder.py] → [SentenceTransformers] (convert to vectors)
    ↓ embeddings
[faiss_handler.py] → [FAISS] (find similar pairs)
    ↓ matched pairs
[sgllm.py] → [Gemini API] (generate suggestions)
    ↓ suggestions
[Frontend UI] (display formatted results)
```

### Module Interactions

**API Layer (`api.py`)**
- Receives notes from frontend
- Orchestrates the entire processing pipeline
- Returns processed notes + suggestions as JSON

**Processing Pipeline:**
1. **`nat_filler.py`** extracts structured data from raw notes
2. **`embedder.py`** converts text fragments to numerical vectors
3. **`faiss_handler.py`** finds connections using cosine similarity
4. **`sgllm.py`** generates human-readable suggestions for matches

**Frontend (`frontend/src/`)**
- **`App.tsx`**: Main application component
- **`NoteInput.tsx`**: Note submission interface
- **`SuggestionCard.tsx`**: Displays AI suggestions with markdown formatting
- **`api.ts`**: HTTP client for backend communication

## 📋 Module Descriptions

### 🧠 NAT (Note Analysis Tool) - `nat/nat_filler.py`
**Purpose**: Extracts structured information from unstructured personal notes

**Input**: Raw text note
**Output**: JSON with `sentiments`, `resources_needed`, `resources_available`
**LLM Used**: Gemini 2.0 Flash
**Example**:
```json
{
  "sentiments": ["learning curiosity", "happiness"],
  "resources_needed": ["quiet reading space"],
  "resources_available": ["daily free time", "nearby library"]
}
```

### 🔍 Semantic Embedder - `embeddings/embedder.py`
**Purpose**: Converts text to high-dimensional vectors for similarity comparison

**Model**: `sentence-transformers/all-MiniLM-L6-v2`
**Dimensions**: 384
**Normalization**: L2 normalized for cosine similarity

### 🎯 Vector Search - `vector_store/faiss_handler.py`
**Purpose**: Fast similarity search across embeddings

**Index Type**: FAISS IndexFlatIP (Inner Product)
**Similarity Metric**: Cosine similarity 
**Threshold**: 0.3 (configurable)
**Search Strategy**: Find needs matching availabilities across different notes

### 💡 Suggestion Generator - `llm/sgllm.py`
**Purpose**: Creates actionable suggestions connecting needs with availabilities

**LLM**: Gemini 2.0 Flash
**Input**: Need text + Availability text
**Output**: Formatted markdown suggestion with structure:
- Bold headings (`**text**`)
- Italic emphasis (`*text*`)
- Paragraph breaks for readability
- Action steps and implementation details

## 🌐 API Reference

### POST `/api/notes`
Submit notes for processing and get suggestions.

**Request:**
```json
{
  "notes": [
    "I need quiet reading space and love books",
    "I know about a free library nearby"
  ]
}
```

**Response:**
```json
{
  "processed_notes": [
    {
      "id": "0",
      "content": "original note text",
      "timestamp": "2025-01-23T10:30:00Z",
      "sentiments": ["learning curiosity"],
      "resources_needed": ["quiet reading space"],
      "resources_available": ["awareness of library"],
      "processed": true
    }
  ],
  "suggestions": [
    {
      "id": "sugg_1",
      "noteId": "0",
      "need": "quiet reading space",
      "availability": "awareness of library", 
      "suggestion": "**Visit the Library**: Transform your awareness..."
    }
  ]
}
```

### GET `/api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-23T10:30:00Z"
}
```

## 🛠 Dev Notes & Known Issues

### Current Limitations
- **Rate Limits**: Gemini API has daily quotas
- **Memory**: All data stored in local files (no database)
- **Concurrency**: No handling of concurrent requests
- **Error Recovery**: Limited retry logic for API failures

### Temporary Design Decisions
- **File Storage**: Using JSON/NumPy files instead of proper database
- **Similarity Threshold**: Hardcoded to 0.3, should be configurable
- **Debug Logging**: Extensive console output for development
- **CORS**: Wide open for development (`*`)

### Performance Considerations
- **Embeddings**: Cached in `embeddings.npy` to avoid recomputation
- **FAISS Index**: Saved to disk for persistence
- **Frontend**: Typewriter animation may be slow for long suggestions

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional (with defaults)
SIMILARITY_THRESHOLD=0.3
FAISS_INDEX_PATH=vector_store/ht.index
```

### Testing
```bash
# Test backend only
python main.py

# Test API endpoint
curl -X POST http://localhost:3001/api/notes \
  -H "Content-Type: application/json" \
  -d '{"notes": ["I need help", "I have resources"]}'

# Frontend build test
cd frontend && npm run build
```

### Future Improvements
- [ ] Database integration (PostgreSQL + pgvector)
- [ ] User authentication and data isolation
- [ ] Configurable similarity thresholds per user
- [ ] Batch processing for large note collections
- [ ] Real-time collaboration features
- [ ] Mobile-responsive design improvements
- [ ] Export suggestions to various formats

---

**Target Users**: Founders, creators, deep thinkers who want to organize scattered thoughts and discover unexpected connections between their goals and available resources.
