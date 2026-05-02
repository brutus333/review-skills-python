---
name: nested-loops
description: Detects deeply nested looping constructs in a Python file.
---

# Nested Loops Checker

## Overview
This skill actively scours a Python file to identify control-flow loops nested within one another (`for` and `while` structures). Having a high nesting depth usually correlates with polynomial time complexity (O(N^2), O(N^3), etc.) which can drastically affect system performance depending on loop sizes. The tool specifically flags loops that reach a depth of 2 or more.

## How to use
```bash
python tool_nested_loops.py <path_to_your_file.py>
```

## Output Explanation
The parsed TSON output highlights potential hotspots:

`{@file: <filename>, @nested_loops: [ {@line_number, @depth, @type}, ... ]}`

- `file`: The referenced Python script path.
- `nested_loops`: A list of objects representing hotspots detected in the AST.
  - `line_number`: The line inside the source file where the inner nested loop begins.
  - `depth`: The level of depth encountered. A depth of 2 means a loop within a loop.
  - `type`: The type of AST loop node (e.g., `For`, `While`, `AsyncFor`).
