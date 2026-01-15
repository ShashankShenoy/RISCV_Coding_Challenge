import argparse
import sys
from pathlib import Path
import yaml

from llm.ollama_cloud import OllamaCloudLLM
from mcp.server import MCPServer
from capabilities.extract_parameters import ExtractParameters


# -----------------------------
# CLI argument parsing
# -----------------------------
parser = argparse.ArgumentParser(description="Extract parameters from RISC-V spec snippets using LLMs.")
parser.add_argument("model", nargs="?", default="gpt-oss", help="Model to use (default: gpt-oss)")
parser.add_argument("--snippets", nargs="*", help="Names of snippets to process (default: all in snippets/ directory)")
args = parser.parse_args()

LLM_NAME = args.model


# -----------------------------
# Model selection
# -----------------------------

MODEL_MAP = {
    "gpt-oss": "gpt-oss:20b-cloud",
    "gemini-flash": "gemini-3-flash-preview:cloud",
    "mistral" : "mistral:latest",
    "phi3" : "phi3:latest"
}

if LLM_NAME not in MODEL_MAP:
    raise ValueError(
        f"Unknown LLM '{LLM_NAME}'. "
        f"Choose one of: {', '.join(MODEL_MAP.keys())}"
    )

llm = OllamaCloudLLM(model=MODEL_MAP[LLM_NAME])


# -----------------------------
# MCP server
# -----------------------------

server = MCPServer()

# Select prompt based on model
prompt_file = "extract_parameters_mistral.txt" if LLM_NAME == "mistral" else "extract_parameters.txt"

# IMPORTANT: inject the capability directly
# (this matches your existing MCP design)
server.capabilities = {
    "extract_parameters": ExtractParameters(llm=llm, prompt_file=prompt_file)
}


# -----------------------------
# Input snippets (auto-discovered from snippets/ directory, with CLI filtering)
# -----------------------------

SNIPPETS = {}
snippet_dir = Path("snippets")
all_snippet_files = list(snippet_dir.glob("*.txt"))

# If --snippets is provided, filter to only those
if args.snippets:
    selected = set(args.snippets)
    snippet_files = [f for f in all_snippet_files if f.stem in selected]
else:
    snippet_files = all_snippet_files

for snippet_file in snippet_files:
    snippet_name = snippet_file.stem
    SNIPPETS[snippet_name] = snippet_file.read_text(encoding="utf-8").strip()

if args.snippets:
    SNIPPETS = {k: SNIPPETS[k] for k in args.snippets if k in SNIPPETS}
    if len(SNIPPETS) != len(args.snippets):
        missing = set(args.snippets) - set(SNIPPETS)
        print(f"Warning: Snippet(s) not found - {', '.join(missing)}", file=sys.stderr)


# -----------------------------
# Output directory (per LLM)
# -----------------------------

out_dir = Path("output") / LLM_NAME
out_dir.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Run extraction
# -----------------------------

for name, text in SNIPPETS.items():
    result = server.handle({
        "capability": "extract_parameters",
        "input": text
    })

    out_file = out_dir / f"{name}.yaml"
    with open(out_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(result, f, sort_keys=False)

    print(f"[OK] Wrote {out_file}")


print(f"\nAll snippets processed using model: {MODEL_MAP[LLM_NAME]}")
