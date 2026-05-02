# Review Tools

A suite of standalone Python CLI scripts tailored to enforce and analyze code quality, complexity, structural anti-patterns, and conceptual code smells programmatically.

Each tool in this repository runs independently on target Python files and standardizes its findings into a Typed JSON ([TSON](https://github.com/zenoaihq/tson)) payload, making it exceptionally modular and easy to integrate directly into agent workflows, CI/CD pipelines, or any other LLM orchestration framework.

---

## 🛠 Prerequisites

Ensure all dependencies are met:
```bash
# Core serialization library required for all tools
pip install tson

# Required for code duplication fuzzy matching
pip install rapidfuzz

# Required for 'Python Linter'
pip install pylint

# Required for LLM Code Smells (Gemini)
pip install google-genai
```

---

## 🧰 Available Tools

### 1. Cyclomatic Complexity
**Script**: `tool_cyclomatic_complexity.py`  
Calculates the cyclomatic complexity for all functions and class methods. Useful for identifying code that has too many branching/decision paths and is hard to test.

**Usage:**
```bash
python tool_cyclomatic_complexity.py target_file.py
```

### 2. Code Duplication
**Script**: `tool_code_duplication.py`  
Scans functions inside a module against each other using Levenshtein distance (`rapidfuzz`) to catch near-duplicate copy-pasted structures.

**Usage:**
```bash
python tool_code_duplication.py target_file.py --threshold 80.0
```

### 3. Nested Loops
**Script**: `tool_nested_loops.py`  
Parses the Python AST to find deep iterations (`For`, `While`, `AsyncFor`) inside of each other, spotting potential $O(N^2)$ algorithm bottlenecks.

**Usage:**
```bash
python tool_nested_loops.py target_file.py
```

### 4. Deep References
**Script**: `tool_deep_references.py`  
Walks the AST looking for long attribute chaining or chained method calls (e.g., `a.b.c.d.e`), helping enforce the Law of Demeter and reducing high coupling.

**Usage:**
```bash
python tool_deep_references.py target_file.py --threshold 3
```

### 5. Python Linter
**Script**: `tool_python_linter.py`  
Programmatic wrapper executing `pylint` on the target script and normalizing its JSON output seamlessly back to TSON standard format.

**Usage:**
```bash
python tool_python_linter.py target_file.py
```

### 6. LLM Code Smells
**Script**: `tool_llm_code_smells.py`  
Utilizes `google-genai` (Gemini Flash 2.5) to review code structurally for subjective "Code Smells" like God Methods, Long Argument Lists, and semantic anti-patterns that static analysis misses.

**Usage:**
```bash
export GEMINI_API_KEY="your_api_key_here"  # Setup LLM Key
python tool_llm_code_smells.py target_file.py
```

---

## 🧠 Output Format (TSON)
All CLI tools strictly constrain their standard output (stdout) to `tson` serialization strings for deterministic parsing. This ensures the cheapest token cost possible while remaining entirely deterministic.

Example payload format printed by `tool_cyclomatic_complexity`:
```
{@file: target_file.py, @metrics: [ {@name: main, @type: function, @complexity: 4, @line_number: 21} ]}
```
