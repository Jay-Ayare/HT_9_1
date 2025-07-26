#!/usr/bin/env python3
"""
Simple test script for GraphRAG integration
"""

import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

def test_graphrag():
    """Test GraphRAG integration."""
    print("Testing GraphRAG Integration...")
    
    try:
        # Import the integration module
        from graph_rag_integration import GraphRAGIntegration, GraphRAGConfig
        
        print("✓ GraphRAG integration module imported successfully")
        
        # Test configuration
        config = GraphRAGConfig(
            chunk_size=300,
            chunk_overlap=50,
            similarity_threshold=0.2,
            enable_visualization=True
        )
        print("✓ Configuration created successfully")
        
        # Test initialization
        graph_rag = GraphRAGIntegration(config)
        print("✓ GraphRAG integration initialized successfully")
        
        # Test with sample documents
        sample_documents = [
            "Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models.",
            "Deep learning uses neural networks with multiple layers to process complex patterns in data.",
            "Natural language processing enables computers to understand and generate human language.",
            "Computer vision allows machines to interpret and analyze visual information from images and videos."
        ]
        
        print("Processing sample documents...")
        graph_rag.process_documents(sample_documents)
        print("✓ Documents processed successfully")
        
        # Test querying
        print("Testing query functionality...")
        response, traversal_path, relevant_content = graph_rag.query("What is machine learning?")
        print(f"✓ Query successful")
        print(f"  Response: {response[:100]}...")
        print(f"  Traversal path: {traversal_path}")
        print(f"  Relevant content chunks: {len(relevant_content)}")
        
        # Test graph info
        graph_info = graph_rag.get_graph_info()
        print(f"✓ Graph info retrieved: {graph_info}")
        
        print("\n🎉 All tests passed! GraphRAG integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_graphrag()
    if success:
        print("\n✅ GraphRAG integration is ready to use!")
    else:
        print("\n❌ Please fix the integration issues before proceeding.") 