import base64
import requests
import json
from src.config import Config

class DarknessAnalyzer:
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.model = Config.MODEL_NAME

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_step(self, image_path, step_context):
        base64_image = self._encode_image(image_path)
        
        prompt = f"""
        You are 'Dead Hand', an expert UI auditor. 
        Current Context: {step_context}
        
        Analyze the attached mobile app screenshot for "Dark Patterns" designed to manipulate users.
        Look for:
        1. Forced account creation (No skip option).
        2. Hidden costs or subscriptions (Prime traps).
        3. Pre-selected negative options (Privacy intrusion).
        4. Nagging popups or confusing "X" buttons.
        5. Visual interference (Fake hair, fake smudges, hidden text).

        Return a JSON object strictly:
        {{
            "darkness_score": <int 0-10>,
            "detected_patterns": [<list of strings>],
            "reasoning": "<concise explanation>",
            "is_blocker": <boolean> 
        }}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            "response_format": {"type": "json_object"} 
        }

        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Analyzer Error: {e}")
            return '{"darkness_score": 0, "reasoning": "Error analyzing", "detected_patterns": []}'