import json
from pathlib import Path

from capabilities.base import Capability
from mcp.validation import extract_and_normalize


class ExtractParameters(Capability):
    name = "extract_parameters"

    def __init__(self, llm, prompt_file="extract_parameters.txt"):
        self.llm = llm
        self.schema = json.loads(
            Path("schemas/param_schema.json").read_text()
        )
        self.prompt_template = Path(
            f"prompts/{prompt_file}"
        ).read_text()

    def execute(self, input_text: str) -> dict:
        return extract_and_normalize(
            llm=self.llm,
            text=input_text,
            schema=self.schema,
            prompt_template=self.prompt_template
        )
