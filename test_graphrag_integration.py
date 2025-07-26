#!/usr/bin/env python3
"""
Test script for GraphRAG integration
"""

import sys
import os
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

def test_graphrag_integration():
    """Test the GraphRAG integration."""
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
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_api_endpoints():
    """Test the API endpoints."""
    print("\nTesting API endpoints...")
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:5000/api/health")
        if response.status_code == 200:
            print("✓ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test GraphRAG info endpoint
        response = requests.get("http://localhost:5000/api/graphrag/info")
        if response.status_code == 200:
            print("✓ GraphRAG info endpoint working")
        else:
            print(f"❌ GraphRAG info endpoint failed: {response.status_code}")
            return False
        
        print("🎉 API endpoints are working correctly.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure the server is running on port 5000.")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 50)
    print("GraphRAG Integration Test Suite")
    print("=" * 50)
    
    # Test GraphRAG integration
    integration_success = test_graphrag_integration()
    
    # Test API endpoints (only if server is running)
    api_success = test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"GraphRAG Integration: {'✓ PASSED' if integration_success else '❌ FAILED'}")
    print(f"API Endpoints: {'✓ PASSED' if api_success else '❌ FAILED'}")
    print("=" * 50)
    
    if integration_success:
        print("\n✅ GraphRAG integration is ready to use!")
        print("\nTo use the integration:")
        print("1. Start the API server: python api.py")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Navigate to the GraphRAG Query tab in the application")
    else:
        print("\n❌ Please fix the integration issues before proceeding.")

if __name__ == "__main__":
    main() 