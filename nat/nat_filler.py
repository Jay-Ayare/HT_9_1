# nat/nat_filler.py

import requests

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

Return your answer in JSON with keys: "sentiments", "resources_needed", "resources_available"
"""
        payload = {
            "model": "tngtech/deepseek-r1t2-chimera:free",
            "messages": [{"role": "user", "content": prompt.strip()}]
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        print("RAW RESPONSE:", response.status_code, response.text)
        return response.json()["choices"][0]["message"]["content"]
