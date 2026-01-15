import subprocess
import json
import shutil
from llm.base import BaseLLM


def find_gemini():
    """
    Locate the Gemini CLI executable in a robust, cross-platform way.
    """
    exe = shutil.which("gemini")
    if exe:
        return exe

    # Windows npm global fallback
    exe = shutil.which("gemini.cmd")
    if exe:
        return exe

    raise FileNotFoundError(
        "Gemini CLI not found. Ensure it is installed and accessible."
    )


class GeminiCLI(BaseLLM):
    def __init__(self):
        self.gemini_path = find_gemini()

    def generate(self, prompt: str) -> str:
        proc = subprocess.run(
            [self.gemini_path, "-o", "json"],
            input=prompt,
            text=True,
            capture_output=True
        )

        if proc.returncode != 0:
            raise RuntimeError(proc.stderr)

        outer = json.loads(proc.stdout)
        return outer["response"]
