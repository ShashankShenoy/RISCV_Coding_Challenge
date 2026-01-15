from ollama import Client
from llm.base import BaseLLM

class OllamaCloudLLM(BaseLLM):
    def __init__(self, model: str):
        self.client = Client()
        self.model = model

    def generate(self, prompt: str) -> str:
        messages = [
            {"role": "user", "content": prompt}
        ]

        try:
            response = self.client.chat(
                self.model,
                messages=messages,
                stream=False
            )
        except Exception as e:
            print("[WARN] Ollama Cloud error:", e)
            return ""

        return response["message"]["content"]
