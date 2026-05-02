---
name: deep-references
description: Detects deep object attributes or nested method call chains in a Python file.
---

# Deep References Checker

## Overview
This skill calculates and surfaces deeply nested reference chains (e.g., `a.b.c.d.e()` or multiple layered object accesses) in a target Python file. Such structures often imply high coupling, poor abstraction, or violations of the Law of Demeter. Reducing deep references makes code much more modular, generic, and isolated.

## How to use
```bash
python tool_deep_references.py <path_to_your_file.py> [--threshold 3]
```
The `--threshold` argument specifies the minimum depth of a chain before it gets reported. It defaults to 3.

## Output Explanation
The tool scans for top-level chains matching or exceeding the threshold and presents the depths in TSON format:

`{@file: <filename>, @deep_references: [ {@line_number, @depth}, ... ]}`

- `file`: The path to the inspected Python script.
- `deep_references`: An array detailing the occurrences of deep references.
  - `line_number`: The line inside the source file where the access chain occurs.
  - `depth`: The counted length of the attribute/method reference chain.
