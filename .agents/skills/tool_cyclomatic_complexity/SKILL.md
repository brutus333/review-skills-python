---
name: cyclomatic-complexity
description: Detects the cyclomatic complexity of functions in a Python file.
---

# Cyclomatic Complexity Checker

## Overview
This skill calculates the cyclomatic complexity for all functions, methods, and asynchronous functions within a specified Python file. Cyclomatic complexity measures the number of linearly independent paths through a program's source code, acting as an indicator for how complex and hard to test a piece of code might be (typically, > 10 requires attention, and > 15 is too complex).

## How to use
You can run this tool from the command line using Python. Make sure to have the required dependencies (like `tson`) installed.

```bash
python tool_cyclomatic_complexity.py <path_to_your_file.py>
```

## Output Explanation
The tool outputs the result in TSON format to standard output. When parsed or read, the output structure looks like this:

`{@file: <filename>, @metrics: [ {@name, @type, @complexity, @line_number}, ... ]}`

- `file`: The path to the analyzed Python script.
- `metrics`: A list of objects containing details for each detected function/method.
  - `name`: The name of the function or method.
  - `type`: Either `function` (top-level) or `method` (inside a class).
  - `complexity`: An integer representing the cyclomatic complexity score.
  - `line_number`: The line number where this function begins.
  - `class_name` (optional): If it is a method, specifies the parent class name.
