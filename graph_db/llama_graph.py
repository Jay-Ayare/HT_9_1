# graph_db/llama_graph.py

from llama_index.core import KnowledgeGraphIndex
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.llms.openai import OpenAI

# Set up Neo4j connection
graph_store = Neo4jGraphStore(
    username="neo4j",
    password="your_password",
    url="bolt://localhost:7687"
)

# Set up OpenAI LLM with gpt-4-1106-nano
llm = OpenAI(model="gpt-4-1106-nano")

# Create the KnowledgeGraphIndex with the custom LLM
kg_index = KnowledgeGraphIndex(graph_store=graph_store, llm=llm)

def add_note_to_graph(note_text: str):
    # This will use the default LLM (OpenAI) unless you configure Gemini
    kg_index.insert(note_text)
    # The graph is now updated in Neo4j!
