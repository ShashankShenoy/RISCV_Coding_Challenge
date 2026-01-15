from ollama import Client
from llm.base import BaseLLM

class OllamaCloudLLM(BaseLLM):
    def __init__(self, model: str):
        self.client = Client()
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.chat(
            self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        return response["message"]["content"]
