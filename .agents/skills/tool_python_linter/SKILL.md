---
name: python-linter
description: Runs a static python linter (pylint) to detect code quality issues, bugs, and style violations.
---

# Python Linter Tool

## Overview
This skill executes `pylint` against a targeted Python script to discover structural issues, undefined variables, styling divergence, and broader static analysis errors. 

## Requirements
You must have `pylint` installed in your environment.
```bash
pip install pylint
```

## How to use
```bash
python tool_python_linter.py <path_to_your_file.py>
```

## Output Explanation
The tool translates the JSON findings of `pylint` into TSON format.

`{@file: <filename>, @linter_issues: [ {@type, @module, @obj, @line, @column, @path, @symbol, @message, @message-id}, ... ]}`

- `file`: The path to the inspected Python script.
- `linter_issues`: A list detailing everything the linter flagged.
  - `type`: Severity classification (e.g. `warning`, `error`, `convention`, `refactor`).
  - `line`: The line where the issue occurred.
  - `symbol`: A readable name for the error (e.g. `missing-module-docstring`).
  - `message`: Detailed description of the problem.
