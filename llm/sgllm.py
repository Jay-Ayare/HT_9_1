import requests
import json

class SuggestionGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate(self, need: str, availability: str):
        prompt = (
            f"A person wrote this as a problem note: \"{need}\"\n"
            f"Another resource note says: \"{availability}\"\n\n"
            "Generate a thoughtful, creative, actionable suggestion connecting the two.\n\n"
            "Format your response with:\n"
            "- Clear paragraph breaks using double line breaks\n"
            "- **Bold** for headings and key concepts\n"
            "- *Italic* for emphasis\n"
            "- Well-structured sections (Why it works, Action steps, etc.)\n"
            "- Easy-to-read formatting with proper spacing\n\n"
            "Make it engaging, actionable, and well-formatted for reading.\n"

        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
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
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.RequestException as e:
            print(f"An API request error occurred: {e}")
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Error parsing LLM response: {e}")
        
        return "Could not generate a suggestion due to an error."
