"""
SubgraphGenerator LLM Module
Creates rich, disconnected subgraphs for individual notes
"""

import requests
import json
import re
from typing import Dict, List, Any


class SubgraphGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def generate_subgraph(self, note_text: str) -> Dict[str, Any]:
        """
        Generate a rich contextual subgraph for a single note
        
        Args:
            note_text: Original note text
            
        Returns:
            Dict containing nodes, edges, and context metadata
        """
        
        prompt = f"""
You are an expert knowledge graph creator. Given a personal note, create a rich contextual subgraph that captures ALL the semantic relationships, implicit context, and connections within this single note.

ORIGINAL NOTE:
"{note_text}"



CREATE A DISCONNECTED SUBGRAPH with these components:

1. NODES - Include all relevant entities with attributes:
   - PERSON nodes (user, people mentioned)
   - PLACE nodes (locations, venues, areas)
   - ORGANIZATION nodes (clubs, institutions, companies)


2. RELATIONSHIPS - Connect nodes meaningfully:
   - NEEDS (entity needs something)
   - PROVIDES (entity offers something) 
   - DESIRES (wants, wishes for)
   - RELATES_TO (general connection)
   - LOCATED_AT (spatial relationship)
   - PARTICIPATES_IN (involvement)
   - ENABLES (makes possible)

3. CONTEXT - Capture implicit information:
   - Location context (where is this happening?)
   - Time context (when, frequency, duration?)
   - Social context (alone, with others, community?)
   - Emotional context (mood, feelings, motivations?)
   - Practical context (constraints, requirements, priorities?)

Return ONLY a valid JSON object with this exact structure:
{{
  "nodes": [
    {{"id": "unique_id", "type": "NODE_TYPE", "attributes": {{"key": "value"}}}},
    ...
  ],
  "edges": [
    {{"from": "node_id", "to": "node_id", "type": "RELATIONSHIP_TYPE", "attributes": {{"strength": 0.8}}}},
    ...
  ],
  "context": {{
    "location": "inferred_location_context",
    "time": "inferred_time_context", 
    "social": "inferred_social_context",
    "emotional": "inferred_emotional_context",
    "practical": "inferred_practical_context"
  }}
}}

Make the subgraph RICH and DETAILED - capture nuances, implications, and context that might be useful for connecting with other notes later.
"""

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt.strip()}]
                }
            ]
        }
        headers = {
            "Content-Type": "application/json"
        }

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            response = requests.post(url, json=payload, headers=headers)
            print(f"SUBGRAPH RAW RESPONSE: {response.status_code} {response.text}")
            response.raise_for_status()
            
            response_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            
            # Extract JSON from the response
            json_match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1).strip()
            else:
                # Try to find JSON directly
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                else:
                    json_text = response_text.strip()
            
            # Parse and validate the JSON
            subgraph_data = json.loads(json_text)
            
            # Validate structure
            if not all(key in subgraph_data for key in ['nodes', 'edges', 'context']):
                raise ValueError("Missing required keys in subgraph data")
            
            print(f"SUBGRAPH GENERATED: {len(subgraph_data['nodes'])} nodes, {len(subgraph_data['edges'])} edges")
            print(f"SUBGRAPH CONTEXT: {subgraph_data['context']}")
            return subgraph_data
            
        except requests.exceptions.RequestException as e:
            print(f"API request error in subgraph generation: {e}. Returning empty subgraph.")
            return {
                "nodes": [],
                "edges": [],
                "context": {"error": f"API request failed: {e}", "status": "generation_failed"}
            }
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error parsing subgraph response: {e}. Returning empty subgraph.")
            return {
                "nodes": [],
                "edges": [],
                "context": {"error": f"Failed to parse LLM response: {e}", "status": "generation_failed"}
            }