---
name: code-duplication
description: Detects near-duplicate functional blocks of code in a Python file.
---

# Code Duplication Checker

## Overview
This skill detects near-duplicate codebase segments inside a Python file. It utilizes `rapidfuzz` to evaluate fuzzy similarities between function bodies (ignoring comments, docstrings, and whitespace). High similarity scores (usually over 80-90) strongly suggest code smells and opportunities for refactoring into reusable functions.

## How to use
```bash
python tool_code_duplication.py <path_to_your_file.py> [--threshold 80.0]
```
The `--threshold` argument is optional and defaults to `80.0`. You can increase it to find stricter duplicates.

## Output Explanation
The tool outputs the findings in TSON format containing any matched pairs of duplicates that exceed the similarity threshold:

`{@file: <filename>, @duplicates: [ {@id1, @id2, @score}, ... ]}`

- `file`: The path to the inspected Python script.
- `duplicates`: A list of pairs indicating which functions resemble each other.
  - `id1`: The name of the first function/method block.
  - `id2`: The name of the second function/method block.
  - `score`: The fuzzy matching ratio (a float out of 100). Higher scores mean greater similarity.
