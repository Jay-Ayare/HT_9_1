import requests
import json

class SuggestionGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate(self, need: str, availability: str):
        prompt = (
            f"A person wrote this as a problem note: \"{need}\"\n"
            f"Another resource note says: \"{availability}\"\n"
            "Generate a thoughtful, creative, actionable suggestion connecting the two."
        )
        payload = {
            "model": "google/gemma-3-4b-it:free",
            "messages": [{"role": "user", "content": prompt}]
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            print(f"An API request error occurred: {e}")
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Error parsing LLM response: {e}")
        
        return "Could not generate a suggestion due to an error."
