# nat/nat_filler.py

import requests
import json

class NATFiller:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def fill_nat(self, note: str):
        prompt = f"""
You are an intelligent note analyzer.

Given this personal note:
\"\"\"{note}\"\"\"

Extract the following:
1. Sentiments to be satisfied (e.g., happiness, public service, learning curiosity).
2. Resources needed (concrete or abstract things the user desires).
3. Resources available (concrete or abstract things the user already has access to).

Return ONLY a valid JSON object with keys: "sentiments", "resources_needed", "resources_available"
Do not include any explanation, markdown formatting, or additional text. Only return the JSON.
"""
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt.strip()
                        }
                    ]
                }
            ]
        }
        headers = {
            "X-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            response = requests.post(url, json=payload, headers=headers)
            print("RAW RESPONSE:", response.status_code, response.text)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.RequestException as e:
            print(f"An API request error occurred: {e}")
            return "{}"
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Error parsing LLM response: {e}")
            return "{}"
