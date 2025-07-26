"""
GraphRAG Integration Module

This module integrates the third-party GraphRAG implementation with the existing
project structure, providing enhanced document processing and querying capabilities.
"""

import os
import sys
import json
import networkx as nx
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import existing project components
from embeddings.embedder import Embedder
from vector_store.faiss_handler import FAISSHandler
from graph_db.neo4j_handler import Neo4jHandler

# Import third-party GraphRAG components
try:
    from langchain.vectorstores import FAISS as LangchainFAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
    from langchain_community.document_loaders import TextLoader
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from sklearn.metrics.pairwise import cosine_similarity
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize
    import nltk
    import spacy
    import heapq
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from tqdm import tqdm
    import numpy as np
    from pydantic import BaseModel
    GRAPHRAG_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some GraphRAG dependencies not available: {e}")
    GRAPHRAG_AVAILABLE = False


@dataclass
class GraphRAGConfig:
    """Configuration for GraphRAG integration."""
    chunk_size: int = 500
    chunk_overlap: int = 100
    similarity_threshold: float = 0.3
    max_traversal_depth: int = 5
    enable_visualization: bool = True
    use_azure_openai: bool = False


class DocumentProcessor:
    """Enhanced document processor that integrates with existing FAISS and Neo4j."""
    
    def __init__(self, config: GraphRAGConfig):
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size, 
            chunk_overlap=config.chunk_overlap
        )
        
        # Use existing embedder if available
        try:
            self.embedder = Embedder()
            self.use_existing_embedder = True
        except:
            self.use_existing_embedder = False
            if GRAPHRAG_AVAILABLE and config.use_azure_openai:
                self.embeddings = AzureOpenAIEmbeddings(
                    model=os.environ.get("AZURE_OPENAI_EMBEDDING_MODEL"),
                    azure_endpoint=os.environ.get("AZURE_OPENAI_EMBEDDING_ENDPOINT"),
                    azure_deployment=os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
                    openai_api_version=os.environ.get("AZURE_API_VERSION"),
                    api_key=os.environ.get("AZURE_OPENAI_EMBEDDING_KEY")
                )

    def process_documents(self, documents: List[str]) -> Tuple[List[str], FAISSHandler]:
        """Process documents and create both FAISS index and graph structure."""
        # Split documents into chunks
        splits = []
        for doc in documents:
            splits.extend(self.text_splitter.split_text(doc))
        
        # Create embeddings using existing embedder
        if self.use_existing_embedder:
            embeddings = []
            for split in splits:
                embedding = self.embedder.get_embedding(split)
                embeddings.append(embedding)
            embeddings = np.array(embeddings)
        else:
            # Use LangChain embeddings if available
            embeddings = self.embeddings.embed_documents(splits)
            embeddings = np.array(embeddings)
        
        # Create FAISS index
        faiss_handler = FAISSHandler()
        faiss_handler.add(embeddings)
        
        # Store entries for later retrieval (simplified)
        faiss_handler.save_index("vector_store/graphrag.index")
        
        return splits, faiss_handler


class KnowledgeGraph:
    """Enhanced knowledge graph that integrates with Neo4j."""
    
    def __init__(self, config: GraphRAGConfig):
        self.config = config
        self.graph = nx.Graph()
        self.neo4j_handler = Neo4jHandler()
        self.lemmatizer = WordNetLemmatizer()
        
        # Download required NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('wordnet', quiet=True)
        except:
            pass

    def extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text using NLP techniques."""
        # Simple concept extraction - can be enhanced with more sophisticated NLP
        tokens = word_tokenize(text.lower())
        concepts = []
        
        for token in tokens:
            if len(token) > 3:  # Filter out short words
                lemma = self.lemmatizer.lemmatize(token)
                concepts.append(lemma)
        
        return list(set(concepts))  # Remove duplicates

    def build_graph(self, splits: List[str], embeddings: np.ndarray):
        """Build knowledge graph from document splits."""
        print("Building knowledge graph...")
        
        # Create nodes for each split
        for i, split in enumerate(splits):
            self.graph.add_node(i, content=split, concepts=self.extract_concepts(split))
        
        # Create edges based on semantic similarity
        for i in tqdm(range(len(splits)), desc="Creating graph edges"):
            for j in range(i + 1, len(splits)):
                similarity = cosine_similarity(
                    embeddings[i].reshape(1, -1), 
                    embeddings[j].reshape(1, -1)
                )[0][0]
                
                if similarity > self.config.similarity_threshold:
                    self.graph.add_edge(i, j, weight=similarity)
        
        # Store graph in Neo4j
        self._store_in_neo4j(splits)
        
        print(f"Graph built with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")

    def _store_in_neo4j(self, splits: List[str]):
        """Store graph structure in Neo4j database."""
        try:
            # Create nodes in Neo4j
            for i, split in enumerate(splits):
                self.neo4j_handler.create_document_node(i, split[:200])  # Truncate for Neo4j
            
            # Create relationships
            for edge in self.graph.edges(data=True):
                node1, node2, data = edge
                self.neo4j_handler.create_similarity_relationship(
                    node1, node2, data['weight']
                )
        except Exception as e:
            print(f"Warning: Could not store graph in Neo4j: {e}")


class QueryEngine:
    """Enhanced query engine that uses both FAISS and graph traversal."""
    
    def __init__(self, faiss_handler: FAISSHandler, knowledge_graph: KnowledgeGraph, config: GraphRAGConfig):
        self.faiss_handler = faiss_handler
        self.knowledge_graph = knowledge_graph
        self.config = config

    def query(self, query: str, embedder: Embedder) -> Tuple[str, List[int], List[str]]:
        """Query the system using both vector search and graph traversal."""
        # Get query embedding
        query_embedding = embedder.get_embedding(query)
        
        # Vector search
        similar_docs = self.faiss_handler.search(
            query_embedding.reshape(1, -1), 
            top_k=5, 
            threshold=self.config.similarity_threshold
        )
        
        # Graph traversal
        traversal_path = self._graph_traversal(query_embedding, similar_docs)
        
        # Combine results
        all_relevant_nodes = list(set([doc[1] for doc in similar_docs] + traversal_path))
        
        # Get content from nodes
        relevant_content = []
        for node_id in all_relevant_nodes:
            if node_id in self.knowledge_graph.graph.nodes:
                content = self.knowledge_graph.graph.nodes[node_id]['content']
                relevant_content.append(content)
        
        # Generate response (simplified - can be enhanced with LLM)
        response = self._generate_response(query, relevant_content)
        
        # Convert numpy types to Python types for JSON serialization
        traversal_path = [int(x) for x in traversal_path]
        return response, traversal_path, relevant_content

    def _graph_traversal(self, query_embedding: np.ndarray, similar_docs: List[Tuple]) -> List[int]:
        """Perform graph traversal starting from similar documents."""
        if not similar_docs:
            return []
        
        # Start from the most similar document
        start_node = similar_docs[0][1]
        
        # Simple BFS traversal
        visited = set()
        queue = [(start_node, 0)]  # (node, depth)
        traversal_path = []
        
        while queue and len(traversal_path) < self.config.max_traversal_depth:
            current_node, depth = queue.pop(0)
            
            if current_node in visited or depth > self.config.max_traversal_depth:
                continue
            
            visited.add(current_node)
            traversal_path.append(current_node)
            
            # Add neighbors to queue
            if current_node in self.knowledge_graph.graph.nodes:
                neighbors = list(self.knowledge_graph.graph.neighbors(current_node))
                for neighbor in neighbors:
                    if neighbor not in visited:
                        queue.append((neighbor, depth + 1))
        
        return traversal_path

    def _generate_response(self, query: str, relevant_content: List[str]) -> str:
        """Generate a response based on relevant content."""
        # Simple response generation - can be enhanced with LLM
        if not relevant_content:
            return "I couldn't find relevant information to answer your query."
        
        # Combine relevant content
        combined_content = "\n\n".join(relevant_content[:3])  # Limit to first 3 chunks
        
        return f"Based on the relevant information:\n\n{combined_content}"


class GraphRAGIntegration:
    """Main integration class that combines all components."""
    
    def __init__(self, config: GraphRAGConfig = None):
        self.config = config or GraphRAGConfig()
        load_dotenv()
        
        # Initialize components
        self.document_processor = DocumentProcessor(self.config)
        self.knowledge_graph = KnowledgeGraph(self.config)
        self.embedder = Embedder()
        
        # Query engine will be initialized after documents are processed
        self.query_engine = None

    def process_documents(self, documents: List[str]):
        """Process documents and build the integrated system."""
        print("Processing documents...")
        
        # Process documents
        splits, faiss_handler = self.document_processor.process_documents(documents)
        
        # Get embeddings for graph building
        embeddings = []
        for split in splits:
            embedding = self.embedder.get_embedding(split)
            embeddings.append(embedding)
        embeddings = np.array(embeddings)
        
        # Build knowledge graph
        self.knowledge_graph.build_graph(splits, embeddings)
        
        # Initialize query engine
        self.query_engine = QueryEngine(faiss_handler, self.knowledge_graph, self.config)
        
        print("Document processing complete!")

    def query(self, query: str) -> Tuple[str, List[int], List[str]]:
        """Query the integrated system."""
        if not self.query_engine:
            raise ValueError("Documents must be processed before querying")
        
        return self.query_engine.query(query, self.embedder)

    def get_graph_info(self) -> Dict:
        """Get information about the current graph."""
        if not self.knowledge_graph.graph:
            return {"nodes": 0, "edges": 0}
        
        return {
            "nodes": self.knowledge_graph.graph.number_of_nodes(),
            "edges": self.knowledge_graph.graph.number_of_edges(),
            "density": nx.density(self.knowledge_graph.graph)
        }


# Utility functions for integration with existing system
def integrate_with_existing_notes(notes_file: str = "notes/user_notes.json") -> GraphRAGIntegration:
    """Integrate GraphRAG with existing notes system."""
    # Load existing notes
    with open(notes_file, 'r') as f:
        data = json.load(f)
        notes = data.get("notes", [])
    
    # Initialize GraphRAG
    graph_rag = GraphRAGIntegration()
    
    # Process notes
    graph_rag.process_documents(notes)
    
    return graph_rag


def enhance_existing_suggestions(graph_rag: GraphRAGIntegration, need: str, availability: str) -> str:
    """Enhance existing suggestion generation with GraphRAG."""
    # Query the graph for related information
    response, traversal_path, relevant_content = graph_rag.query(f"{need} {availability}")
    
    # Use the relevant content to enhance suggestions
    enhanced_context = "\n".join(relevant_content[:2])  # Use top 2 relevant chunks
    
    return f"Enhanced suggestion based on graph analysis:\n\n{enhanced_context}\n\nOriginal suggestion context: {need} + {availability}"


if __name__ == "__main__":
    # Example usage
    config = GraphRAGConfig(
        chunk_size=300,
        chunk_overlap=50,
        similarity_threshold=0.2,
        enable_visualization=True
    )
    
    graph_rag = GraphRAGIntegration(config)
    
    # Example documents
    documents = [
        "This is a sample document about machine learning and artificial intelligence.",
        "Machine learning algorithms can be used for pattern recognition and prediction.",
        "Artificial intelligence encompasses various techniques including neural networks.",
        "Neural networks are inspired by biological brain structures and processes."
    ]
    
    graph_rag.process_documents(documents)
    
    # Example query
    response, path, content = graph_rag.query("What is machine learning?")
    print(f"Response: {response}")
    print(f"Traversal path: {path}")
    print(f"Graph info: {graph_rag.get_graph_info()}") 