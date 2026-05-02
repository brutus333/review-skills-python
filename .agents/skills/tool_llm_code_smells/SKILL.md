---
name: llm-code-smells
description: Identifies conceptual code smells like God Methods or Long Arguments by parsing the code through an LLM.
---

# LLM Code Smells Checker

## Overview
Unlike static analysis tools, this skill leverages a Large Language Model (specifically Gemini 2.5 Flash) to identify subjective and structural "code smells" in a Python file. Identifying anti-patterns like "God Methods" (functions that try to do too many things) or "Long Argument Lists" requires analyzing the semantic intent of the code, which the LLM excels at.

## Requirements
You must have the `google-genai` pip package installed, and have an active API key exported in your environment.

```bash
pip install google-genai
set GEMINI_API_KEY="your_api_key_here"  # Windows Command Prompt
$env:GEMINI_API_KEY="your_api_key_here" # Windows PowerShell
export GEMINI_API_KEY="your_api_key_here" # Linux/MacOS
```

## How to use
```bash
python tool_llm_code_smells.py <path_to_your_file.py>
```

## Output Explanation
The tool translates the AI's conclusions into a highly-structured TSON payload:

`{@file: <filename>, @code_smells: [ {@type, @function, @line, @description}, ... ]}`

- `file`: The path to the inspected Python script.
- `code_smells`: A structured list of code smell instances identified by the LLM.
  - `type`: The anti-pattern name (e.g. `God Method`, `Long Argument List`).
  - `function`: The name of the function or class hosting the smell.
  - `line`: The approximate line number where the issue was found (or `N/A`).
  - `description`: The AI's justification for why this code segment exhibits the smell.
