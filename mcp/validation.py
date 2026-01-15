#codebase now
#
# MCP (Model Context Protocol) provides a structured way to register, invoke, and validate AI-powered capabilities (like parameter extraction)
# in a modular, model-agnostic fashion. It allows you to:
#   - Register different extraction or analysis capabilities, each using any LLM backend (local or cloud)
#   - Cleanly swap models (e.g., GPT-OSS 20B, Gemini, Mistral) and prompts for each capability
#   - Validate and normalize LLM outputs against strict schemas, ensuring reliable downstream use
#   - Run batch or interactive extraction with consistent, reproducible results
#
# In this project, MCP enables you to test and compare LLMs for extracting architectural parameters from ISA specs, ensuring only correct,
# implementation-specific parameters are surfaced, and making it easy to adapt as models or requirements evolve.
import json
from jsonschema import validate
from pathlib import Path


def strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 1)[1]
        if "```" in text:
            text = text.rsplit("```", 1)[0]
    return text.strip()


def contains_parameter_triggers(text: str) -> bool:
    triggers = [
        "implementation-specific",
        "implementation defined",
        "implementation-defined",
        "optional",
        "optionally",
        "may",
        "might",
        "should",
        "shall"
    ]
    lower = text.lower()
    return any(t in lower for t in triggers)


def is_string_parameter_list(parsed: dict) -> bool:
    return (
        isinstance(parsed.get("parameters"), list)
        and parsed["parameters"]
        and isinstance(parsed["parameters"][0], str)
    )


def refine_parameters(llm, param_names, schema):
    prompt = Path("prompts/refine_parameters.txt").read_text()
    filled = prompt.replace(
        "{{PARAMETERS}}",
        json.dumps(param_names, indent=2)
    )

    raw = llm.generate(filled)
    cleaned = strip_code_fences(raw)
    parsed = json.loads(cleaned)

    validate(instance=parsed, schema=schema)
    return parsed

def must_have_parameters(text: str) -> bool:
    mandatory_triggers = [
        "implementation-specific",
        "implementation defined",
        "implementation-defined"
    ]
    lower = text.lower()
    return any(t in lower for t in mandatory_triggers)


def validate_with_retry(llm, build_prompt, schema, retries=3):
    source_prompt = build_prompt()

    for _ in range(retries):
        raw = llm.generate(source_prompt)

        # 🔑 FINAL RULE: empty output = no parameters
        if not raw or not raw.strip():
            return {"parameters": []}

        cleaned = strip_code_fences(raw)

        try:
            parsed = json.loads(cleaned)

            # Case 1: already schema-valid
            validate(instance=parsed, schema=schema)
            return parsed

        except Exception:
            # Case 2: names-only → refine once
            try:
                parsed = json.loads(cleaned)
                if is_string_parameter_list(parsed):
                    return refine_parameters(
                        llm, parsed["parameters"], schema
                    )
            except Exception:
                pass

    # If nothing worked, fall back safely
    return {"parameters": []}

def normalize_parameter(p: dict) -> dict:
    label = p["label"].strip().lower()
    name = label.replace(" ", "_")

    return {
        "name": name,
        "description": p["label"].capitalize(),
        "type": infer_type(label),
        "constraints": infer_constraints(p.get("evidence", ""))
    }

def infer_type(label: str) -> str:
    if "size" in label or "capacity" in label:
        return "integer"
    if "enable" in label or "support" in label:
        return "boolean"
    if "mode" in label or "type" in label:
        return "enum"
    return "structure"


def infer_constraints(evidence: str) -> list:
    constraints = []
    if "uniform" in evidence.lower():
        constraints.append("must be uniform across the system")
    return constraints

def extract_and_normalize(llm, text: str, schema: dict, prompt_template: str = None) -> dict:
    from pathlib import Path
    import json
    from jsonschema import validate

    if prompt_template is None:
        prompt_template = Path("prompts/extract_parameters.txt").read_text()
    
    prompt = prompt_template.replace("{{INPUT}}", text)

    raw = llm.generate(prompt)

    if not raw or not raw.strip():
        return {"parameters": []}

    try:
        parsed = json.loads(strip_code_fences(raw))
    except Exception:
        return {"parameters": []}

    extracted = parsed.get("parameters", [])
    if not extracted:
        return {"parameters": []}

    normalized = [normalize_parameter(p) for p in extracted]

    result = {"parameters": normalized}
    validate(instance=result, schema=schema)
    return result

