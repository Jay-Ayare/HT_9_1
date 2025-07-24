"""
Neo4j Graph Database Handler for HiddenThread
Manages connections and operations for note subgraphs
"""

from neo4j import GraphDatabase
import json
from typing import Dict, List, Any, Optional
import logging
import os


class Neo4jHandler:
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "hiddenthread"):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logging.info(f"Neo4jHandler initialized with URI: {uri}, User: {user}")
        
    def close(self):
        """Close the Neo4j connection"""
        if self.driver:
            logging.info("Closing Neo4j connection")
            self.driver.close()
        else:
            logging.warning("Neo4j driver is already closed or not initialized")
    

    def create_note_subgraph(self, note_id: str, subgraph_data: Dict[str, Any]) -> bool:
        """
        Create a disconnected subgraph for a single note
        
        Args:
            note_id: Unique identifier for the note
            subgraph_data: Dictionary containing nodes, edges, and metadata
            
        Returns:
            bool: Success status
        """
        with self.driver.session() as session:
            logging.info(f"Creating subgraph for note {note_id}")
            try:
                # Clear existing subgraph for this note if it exists
                session.run(
                    "MATCH (n)-[r]-(m) WHERE n.note_id = $note_id OR m.note_id = $note_id "
                    "DELETE r, n, m",
                    note_id=note_id
                )
                logging.info(f"Cleared existing subgraph for note {note_id}")
                
                # Create nodes
                for node in subgraph_data.get('nodes', []):
                    session.run(
                        "CREATE (n {id: $id, type: $type, note_id: $note_id, attributes: $attributes})",
                        id=node['id'],
                        type=node['type'],
                        note_id=note_id,
                        attributes=json.dumps(node.get('attributes', {}))
                    )
                logging.info(f"Created nodes for note {note_id}")
                
                # Create relationships
                for edge in subgraph_data.get('edges', []):
                    session.run(
                        "MATCH (a {id: $from_id, note_id: $note_id}), "
                        "      (b {id: $to_id, note_id: $note_id}) "
                        "CREATE (a)-[r:RELATES {type: $rel_type, attributes: $attributes}]->(b)",
                        from_id=edge['from'],
                        to_id=edge['to'],
                        note_id=note_id,
                        rel_type=edge['type'],
                        attributes=json.dumps(edge.get('attributes', {}))
                    )
                logging.info(f"Created relationships for note {note_id}")
                
                # Store metadata
                context = subgraph_data.get('context', {})
                session.run(
                    "CREATE (meta:NoteMetadata {note_id: $note_id, context: $context})",
                    note_id=note_id,
                    context=json.dumps(context)
                )
                logging.info(f"Stored metadata for note {note_id}")
                
                logging.info(f"Subgraph created successfully for note {note_id}")
                return True
            except Exception as e:
                logging.error(f"Error creating subgraph for note {note_id}: {e}")
                return False

    
    def get_note_subgraph(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the complete subgraph for a note
        
        Args:
            note_id: Unique identifier for the note
            
        Returns:
            Dict containing nodes, edges, and metadata, or None if not found
        """
        with self.driver.session() as session:
            try:
                logging.info(f"Retrieving subgraph for note {note_id}")
                # Get nodes
                nodes_result = session.run(
                    "MATCH (n) WHERE n.note_id = $note_id RETURN n",
                    note_id=note_id
                )
                nodes = []
                for record in nodes_result:
                    node = record['n']
                    nodes.append({
                        'id': node['id'],
                        'type': node['type'],
                        'attributes': json.loads(node.get('attributes', '{}'))
                    })
                logging.info(f"Retrieved nodes for note {note_id}")
                
                # Get edges
                edges_result = session.run(
                    "MATCH (a)-[r]-(b) WHERE a.note_id = $note_id AND b.note_id = $note_id "
                    "RETURN a.id as from_id, b.id as to_id, r.type as rel_type, r.attributes as attributes",
                    note_id=note_id
                )
                edges = []
                for record in edges_result:
                    edges.append({
                        'from': record['from_id'],
                        'to': record['to_id'],
                        'type': record['rel_type'],
                        'attributes': json.loads(record.get('attributes', '{}'))
                    })
                logging.info(f"Retrieved edges for note {note_id}")
                
                # Get metadata
                meta_result = session.run(
                    "MATCH (meta:NoteMetadata) WHERE meta.note_id = $note_id RETURN meta.context as context",
                    note_id=note_id
                )
                context = {}
                for record in meta_result:
                    context = json.loads(record.get('context', '{}'))
                    break
                
                logging.info(f"Retrieved metadata for note {note_id}")
                if nodes:  # Only return if we found data
                    logging.info(f"Subgraph retrieved successfully for note {note_id}")
                    return {
                        'nodes': nodes,
                        'edges': edges,
                        'context': context
                    }
                logging.info(f"No data found for note {note_id}")
                return None
                
            except Exception as e:
                logging.error(f"Error retrieving subgraph for note {note_id}: {e}")
                return None
    
    def health_check(self) -> bool:
        """Check if Neo4j is accessible"""
        try:
            logging.info("Performing Neo4j health check")
            with self.driver.session() as session:
                result = session.run("RETURN 1")
                return result.single() is not None
        except Exception as e:
            logging.error(f"Neo4j health check failed: {e}")
            return False


# Global instance
neo4j_handler = None

def get_neo4j_handler() -> Neo4jHandler:
    """Get or create Neo4j handler instance"""
    global neo4j_handler
    if neo4j_handler is None:
        # Read from environment or use defaults
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j") 
        password = os.getenv("NEO4J_PASSWORD", "hiddenthread")
        neo4j_handler = Neo4jHandler(uri, user, password)
    return neo4j_handler
