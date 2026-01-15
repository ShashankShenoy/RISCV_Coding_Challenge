import subprocess
from llm.base import BaseLLM

class OllamaLLM(BaseLLM):
    def __init__(self, model="mistral"):
        self.model = model

    def generate(self, prompt: str) -> str:
        proc = subprocess.run(
            ["ollama", "run", self.model],
            input=prompt,
            text=True,
            encoding="utf-8",
            capture_output=True
        )

        if proc.returncode != 0:
            print("[WARN] Ollama error:")
            print(proc.stderr)
            return ""   # safe fallback

        return proc.stdout.strip()
