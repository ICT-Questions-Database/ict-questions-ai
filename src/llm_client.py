import httpx
import json
from typing import Optional
from src.config import settings

class OllamaClient:
    def __init__(self):
        self.api_key = settings.OLLAMA_API_KEY
        self.host = settings.OLLAMA_HOST.rstrip("/")
        self.timeout = settings.OLLAMA_REQUEST_TIMEOUT
        self.default_model = settings.models_list[0] if settings.models_list else "gemma3:4b"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate(self, prompt: str, model: Optional[str] = None, max_tokens: Optional[int] = None) -> str:
        model = model or self.default_model
        max_tokens = max_tokens or settings.OLLAMA_MAX_TOKENS
        url = f"{self.host}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

ollama_client = OllamaClient()