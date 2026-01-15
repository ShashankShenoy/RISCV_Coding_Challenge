# RISC-V Parameter Extraction with MCP

## Coding Challenge Summary
This project demonstrates AI-assisted extraction of architectural parameters from RISC-V ISA specifications using the Model Context Protocol (MCP) framework. The solution is designed to:
- Extract only true implementation-specific parameters, as signaled by trigger words ("may", "might", "should", "optional", "optionally", "implementation defined", "implementation specific").
- Minimize hallucination and ensure output validity using prompt engineering and schema validation.
- Compare and validate multiple LLMs for reliability and generalization.

## Why MCP is Central
- **Modular & Model-Agnostic**: MCP lets you register, invoke, and validate extraction capabilities for any LLM and prompt, making it easy to test, compare, and swap models.
- **Schema Validation**: All LLM outputs are validated against a strict JSON schema (`schemas/param_schema.json`), ensuring only well-formed, expected data is accepted.
- **Prompt Flexibility**: Prompts can be specialized per model (e.g., stricter for Mistral) and are easy to update or extend.
- **Generalization & Reproducibility**: MCP enables batch and interactive extraction, with consistent, schema-validated results.

## Prompt Engineering & Hallucination Mitigation
- **Trigger Phrase Focus**: Prompts require explicit trigger phrases for parameter extraction, reducing false positives.
- **Negative Examples**: Prompts include examples of what NOT to extract (e.g., fixed bit fields, standard encodings).
- **Specialization**: Weaker models like Mistral use stricter, custom prompts to further reduce hallucination.
- **Generalization Testing**: The script `test_generalization.py` verifies that the system does not hallucinate parameters from fixed or descriptive text.

## Model Output Comparison
- **Mistral**: Sometimes hallucinated parameters from fixed/descriptive text or missed valid parameters, even with prompt specialization.
- **GPT-OSS 20B & Gemini-3-Flash**: Consistently followed prompt instructions, extracting only true implementation-specific parameters and returning empty lists for fixed architecture. Their outputs matched the schema and intended logic.

## LLMs Used
- **GPT-OSS 20B (Ollama Cloud)**
  - Name: gpt-oss:20b-cloud
  - Context length: 128K tokens
- **Mistral (Ollama Cloud)**
  - Name: mistral:latest
  - Context length: 32K tokens
- **Gemini-3-Flash-Preview (Ollama Cloud)**
  - Name: gemini-3-flash-preview:cloud
  - Context length: 1M tokens

## YAML Output Format (Schema)
All results are formatted as YAML files with fields for `name`, `description`, `type`, and `constraints`, matching the schema in `schemas/param_schema.json`.

**Example 1: Implementation-specific parameters**
```yaml
parameters:
- name: cache_capacity
  description: Cache capacity
  type: integer
  constraints: []
- name: cache_organization
  description: Cache organization
  type: structure
  constraints: []
- name: cache_block_size
  description: Cache block size
  type: integer
  constraints:
    - must be uniform across the system
```

**Example 2: No parameters (fixed specification)**
```yaml
parameters: []
```

**Example 3: TLB and superpages**
```yaml
parameters:
- name: translation_lookaside_buffer_tlb_size
  description: Translation lookaside buffer (tlb) size
  type: integer
  constraints: []
- name: tlb_associativity
  description: Tlb associativity
  type: integer
  constraints: []
- name: superpages_support
  description: Superpages support
  type: boolean
  constraints: []
```

> **Note:** The TLB/superpages example in the YAML output section is illustrative and not from an actual run. Only the cache and CSR examples have been tested and validated in this project. If you wish to validate additional cases, you can add them to the input snippets and rerun the extraction.

## Project Structure
```
RISC-V/
├── capabilities/                  # Extraction logic (e.g., ExtractParameters)
├── llm/                           # LLM wrappers (Ollama, Gemini, etc.)
├── mcp/                           # MCP registry, server, validation
├── output/                        # YAML results for each model
│   ├── gpt-oss/
│   ├── mistral/
│   └── gemini-flash/
├── prompts/                       # Prompt templates for each model
│   ├── extract_parameters.txt
│   └── extract_parameters_mistral.txt
├── schemas/                       # JSON schema for output validation
│   └── param_schema.json
├── snippets/                      # Input text snippets
├── requirements.txt               # Python dependencies
├── run.py                         # Main entry point
├── test_generalization.py         # Generalization/hallucination test script
└── README.md                      # This file
```

## Usage
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run extraction for a specific model:
   ```sh
   python run.py gpt-oss
   python run.py mistral
   python run.py gemini-flash
   ```
   Output files will be written to `output/<model>/`.
3. Test generalization (optional):
   ```sh
   python test_generalization.py
   ```

## License
MIT

