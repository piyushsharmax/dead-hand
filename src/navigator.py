import base64
import requests
import json
from src.config import Config

class NavigationAgent:
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.model = Config.MODEL_NAME

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def get_next_action(self, image_path, objective, step_history):
        base64_image = self._encode_image(image_path)
        
        # Simple, robust prompt for direct ADB control
        prompt = f"""
        You are an Android automation agent. 
        User Objective: "{objective}"
        
        Based on the screenshot, output the NEXT SINGLE ACTION to move towards the objective.
        
        Output JSON ONLY with this format:
        {{
            "action_type": "tap" or "type" or "key",
            "command": "raw adb shell command arguments" 
        }}
        
        Examples:
        - To tap a button at x=500, y=1000: {{"action_type": "tap", "command": "input tap 500 1000"}}
        - To type "headphones": {{"action_type": "type", "command": "input text 'headphones'"}}
        - To press enter/search: {{"action_type": "key", "command": "input keyevent 66"}}
        - To go home: {{"action_type": "key", "command": "input keyevent 3"}}
        
        IMPORTANT:
        - If the keyboard is open and you need to search, press Enter (keyevent 66).
        - If you need to open an app, look for its icon.
        - Guess coordinates (0-1080 width, 0-2400 height) as accurately as possible.
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
            content = response.json()['choices'][0]['message']['content']
            return json.loads(content)
        except Exception as e:
            print(f"Navigation Error: {e}")
            return {"action_type": "wait", "command": ""}