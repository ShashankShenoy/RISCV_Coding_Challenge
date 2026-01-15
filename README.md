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


## Current Project Directory Structure

```
RISC-V/
├── capabilities/                 # Extraction logic (e.g., ExtractParameters)
│   ├── base.py
│   ├── extract_parameters.py
├── env/                          # Python virtual environment
├── llm/                          # LLM wrappers (Ollama, Gemini, etc.)
│   ├── base.py
│   ├── gemini_cli.py
│   ├── gemini_flash.py
│   ├── ollama.py
│   ├── ollama_cloud.py
├── mcp/                          # MCP registry, server, validation
│   ├── registry.py
│   ├── server.py
│   ├── validation.py
├── output/                       # YAML results for each model
│   ├── gemini-flash/
│   ├── gpt-oss/
│   ├── mistral/
│   └── phi3/
├── prompts/                      # Prompt templates for each model
│   ├── extract_parameters.txt
│   └── extract_parameters_mistral.txt
├── requirements.txt              # Python dependencies
├── run.py                        # Main entry point
├── schemas/                      # JSON schema for output validation
│   └── param_schema.json
├── snippets/                     # Input text snippets
│   ├── cache.txt
│   └── csr.txt
└── README.md                     # Project documentation
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

## Selective Snippet Execution with CLI Flags

You can use command-line flags to run extraction only on specific snippets. For example:

- To run all snippets (default):
  ```sh
  python run.py gpt-oss
  ```
- To run only the 'cache' and 'csr' snippets:
  ```sh
  python run.py gpt-oss --snippets cache csr
  ```

This makes it easy to test or process only the snippets you want, without editing the code or input files.

## Features & Improvements

This project includes the following key features and enhancements:

- **Modular Capability Registry:** Easily add new extraction or analysis capabilities by creating new classes in the `capabilities/` directory.
- **Dynamic Snippet Discovery:** All `.txt` files in the `snippets/` directory are automatically loaded and processed.
- **CLI Arguments for Model and Snippet Selection:** Select which model and which snippets to process via command-line flags.
- **Prompt Specialization:** Use different prompts for different models (e.g., stricter prompt for Mistral).
- **Schema Validation:** All outputs are validated against `schemas/param_schema.json` to ensure correctness.
- **Generalization and Hallucination Testing:** Includes a script to test prompt generalization and minimize hallucination.
- **Error Handling:** Improved error messages for missing files, extraction failures, and output write errors.
- **Extensible Project Structure:** Easy to add new capabilities, models, prompts, snippets, and validation logic.
- **Comprehensive Documentation:** README explains project structure, extension paths, CLI usage, and all major features.

These features make the project robust, flexible, and easy to extend or maintain for future work and experimentation.

## Future Improvements

Potential enhancements for this project include:

- **Automated Output Auditing:** Add a script to re-validate all YAML outputs against the schema for batch auditing and regression testing.
- **Advanced Benchmarking:** Integrate detailed benchmarking for extraction accuracy, speed, and hallucination rates across models and prompts.
- **Web or CLI User Interface:** Develop a simple interface for users to submit new snippets and view results interactively.
- **Plugin System for Capabilities:** Allow capabilities to be registered via plugins or config files for even easier extensibility.
- **Expanded Test Suite:** Add more unit and integration tests for edge cases, error handling, and new capabilities.
- **Enhanced Logging:** Use Python’s logging module for structured event and error tracking.
- **Support for More LLMs:** Integrate additional models and prompt templates as new LLMs become available.
- **Documentation Expansion:** Add troubleshooting, FAQ, and more usage examples to the README as the project grows.

These improvements will make the project even more robust, user-friendly, and adaptable to future requirements.

## License
MIT

