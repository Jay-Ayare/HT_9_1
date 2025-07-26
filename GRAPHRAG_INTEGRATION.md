# GraphRAG Integration

This document describes the integration of a third-party GraphRAG implementation with the existing HiddenThread project.

## Overview

GraphRAG (Graph-Enhanced Retrieval-Augmented Generation) is an advanced question-answering system that combines graph-based knowledge representation with retrieval-augmented generation. This integration enhances the existing note-taking and suggestion system with sophisticated document processing and querying capabilities.

## Features

### Core GraphRAG Features
- **Document Processing**: Intelligent chunking and embedding of documents
- **Knowledge Graph Construction**: Creates a graph representation of document relationships
- **Graph Traversal**: Uses graph algorithms to find relevant information
- **Enhanced Querying**: Combines vector search with graph traversal for better results
- **Visualization**: Shows the traversal path and graph structure

### Integration Benefits
- **Enhanced Suggestions**: Uses graph analysis to improve suggestion generation
- **Better Context Awareness**: Maintains relationships between different pieces of information
- **Explainable Results**: Shows how the system arrived at its answers
- **Scalable Architecture**: Integrates with existing FAISS and Neo4j infrastructure

## Architecture

### Components

1. **DocumentProcessor** (`graph_rag_integration.py`)
   - Handles document chunking using RecursiveCharacterTextSplitter
   - Creates embeddings using existing Embedder or Azure OpenAI
   - Integrates with existing FAISS vector store

2. **KnowledgeGraph** (`graph_rag_integration.py`)
   - Builds NetworkX graph from document chunks
   - Creates edges based on semantic similarity
   - Stores graph structure in Neo4j database
   - Extracts concepts using NLP techniques

3. **QueryEngine** (`graph_rag_integration.py`)
   - Combines vector search with graph traversal
   - Uses BFS algorithm for graph exploration
   - Generates responses based on relevant content

4. **GraphRAGIntegration** (`graph_rag_integration.py`)
   - Main orchestrator class
   - Manages all components and provides unified interface

### API Endpoints

- `GET /api/graphrag/info` - Get GraphRAG system status
- `POST /api/graphrag/query` - Query the GraphRAG system
- `POST /api/graphrag/process` - Process documents for GraphRAG

### Frontend Components

- **GraphRAGQuery** (`frontend/src/components/GraphRAGQuery.tsx`)
  - React component for GraphRAG querying
  - Shows system status and graph information
  - Displays query results with traversal paths

## Installation

### Prerequisites

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

### Configuration

1. Set up environment variables in `.env`:
```env
# Existing variables
GEMINI_API_KEY=your_gemini_api_key

# Optional: Azure OpenAI for enhanced embeddings
AZURE_OPENAI_EMBEDDING_KEY=your_azure_key
AZURE_OPENAI_EMBEDDING_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_EMBEDDING_MODEL=your_model_name
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your_deployment_name
AZURE_API_VERSION=2024-02-15-preview
```

2. Configure GraphRAG settings in `graph_rag_integration.py`:
```python
config = GraphRAGConfig(
    chunk_size=300,              # Size of document chunks
    chunk_overlap=50,            # Overlap between chunks
    similarity_threshold=0.2,    # Minimum similarity for graph edges
    max_traversal_depth=5,       # Maximum graph traversal depth
    enable_visualization=True,   # Enable graph visualization
    use_azure_openai=False       # Use Azure OpenAI or existing embedder
)
```

## Usage

### Starting the System

1. Start the API server:
```bash
python api.py
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

3. Navigate to the application and use the "GraphRAG Query" tab

### Basic Usage

1. **Process Documents**:
   - Add notes through the existing interface
   - Click "Process Documents" in the GraphRAG tab
   - The system will build the knowledge graph

2. **Query the System**:
   - Enter your question in the query interface
   - Click "Query GraphRAG"
   - View the response, traversal path, and relevant content

3. **Enhanced Suggestions**:
   - The system automatically enhances suggestions using graph analysis
   - Suggestions now include context from related documents

### Advanced Usage

#### Custom Configuration
```python
from graph_rag_integration import GraphRAGIntegration, GraphRAGConfig

# Custom configuration
config = GraphRAGConfig(
    chunk_size=500,
    chunk_overlap=100,
    similarity_threshold=0.3,
    max_traversal_depth=10
)

# Initialize with custom config
graph_rag = GraphRAGIntegration(config)
```

#### Programmatic Usage
```python
# Process documents
documents = ["Document 1", "Document 2", "Document 3"]
graph_rag.process_documents(documents)

# Query the system
response, traversal_path, relevant_content = graph_rag.query("Your question here")

# Get graph information
graph_info = graph_rag.get_graph_info()
```

## Testing

Run the integration test suite:
```bash
python test_graphrag_integration.py
```

This will test:
- Module imports and initialization
- Document processing
- Query functionality
- API endpoints (if server is running)

## Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

2. **GraphRAG Not Available**:
   - Verify all required packages are installed
   - Check environment variables are set correctly
   - Review error messages in the console

3. **API Connection Issues**:
   - Ensure the API server is running on port 5000
   - Check CORS configuration
   - Verify network connectivity

4. **Performance Issues**:
   - Reduce chunk size for faster processing
   - Lower similarity threshold for fewer graph edges
   - Use smaller documents for testing

### Debug Mode

Enable debug logging by setting environment variables:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## Performance Considerations

### Optimization Tips

1. **Chunk Size**: Smaller chunks (200-300) for better precision, larger chunks (500-1000) for better context
2. **Similarity Threshold**: Higher threshold (0.3-0.5) for fewer, stronger connections
3. **Traversal Depth**: Lower depth (3-5) for faster queries, higher depth (7-10) for more comprehensive results
4. **Batch Processing**: Process documents in batches for large datasets

### Memory Usage

- Graph storage: ~1MB per 1000 document chunks
- Embedding storage: ~4MB per 1000 chunks (768-dimensional embeddings)
- Runtime memory: Varies based on graph size and traversal depth

## Future Enhancements

### Planned Features

1. **Advanced Visualization**: Interactive graph visualization with D3.js
2. **Incremental Updates**: Add new documents without reprocessing everything
3. **Multi-modal Support**: Support for images, audio, and other media types
4. **Advanced NLP**: Better concept extraction and relationship detection
5. **Caching**: Intelligent caching of frequently accessed graph paths

### Integration Opportunities

1. **Real-time Collaboration**: Share graphs between users
2. **Version Control**: Track changes in knowledge graphs over time
3. **Export/Import**: Save and load graph structures
4. **API Extensions**: Additional endpoints for graph manipulation

## Contributing

To contribute to the GraphRAG integration:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style

- Follow existing Python and TypeScript conventions
- Add type hints for all functions
- Include docstrings for all classes and methods
- Write unit tests for new components

## License

This integration is part of the HiddenThread project and follows the same licensing terms.

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the test suite for examples
3. Open an issue on the project repository
4. Contact the development team

---

**Note**: This integration is designed to work alongside the existing HiddenThread system. It enhances rather than replaces the current functionality, providing additional capabilities for document analysis and querying. 