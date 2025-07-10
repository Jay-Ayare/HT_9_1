import requests

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
            "model": "tngtech/deepseek-r1t2-chimera:free",
            "messages": [{"role": "user", "content": prompt}]
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        return response.json()["choices"][0]["message"]["content"]
