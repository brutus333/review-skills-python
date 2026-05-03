---
name: smell-score
description: Computes a 0–100 code smell suspicion score for Python files by aggregating signals from five static analyzers (cyclomatic complexity, code duplication, nested loops, deep references, and linter issues).
---

# Code Smell Suspicion Score

## Overview
This skill aggregates the output of all five static analysis tools into a single **0–100 suspicion score** per Python file. A higher score indicates a higher likelihood of problematic code (God methods, copy-paste patterns, performance bottlenecks, etc.). Results in folder mode are sorted by score descending so the highest-risk files appear first.

### Scoring model

| Metric | Default weight | How normalised to 0–100 |
|---|---|---|
| Cyclomatic complexity | 30% | % of functions with CC ≥ `--cc-threshold` (default 10) |
| Code duplication | 25% | Each near-duplicate pair = +20 pts |
| Nested loops | 20% | Each hotspot = +25 pts |
| Deep references | 15% | Each deep-chain line = +15 pts |
| Linter issues | 10% | Severity-weighted (error/fatal=10, warning=4, refactor=2, convention=1), raw cap at 50 |

Weights are automatically re-normalised to sum to 1.0, so custom combinations always stay in range.

## Requirements
All five analysis tools must be importable from the same directory:
- `tool_cyclomatic_complexity.py`
- `tool_code_duplication.py`
- `tool_nested_loops.py`
- `tool_deep_references.py`
- `tool_python_linter.py` (requires `pylint` to be installed)

```bash
pip install pylint rapidfuzz tson
```

## How to use

```bash
# Single file
python tool_smell_score.py <path_to_file.py>

# Entire folder (recursive)
python tool_smell_score.py <path_to_folder>

# Custom thresholds
python tool_smell_score.py <path> --cc-threshold 7 --dup-threshold 85 --ref-depth 4

# Custom weights (auto-normalized)
python tool_smell_score.py <path> --w-complexity 0.4 --w-duplication 0.3 --w-linter 0.0
```

## Output Explanation

**Single file:**
```
{@file, @smell_score, @breakdown{@cyclomatic_complexity, @code_duplication, @nested_loops, @deep_references, @linter_issues}}
```

**Folder:**
```
{@path, @results[ {@file, @smell_score, @breakdown{...}}, ... ]}
```

- `smell_score`: Overall suspicion score from 0 (clean) to 100 (very smelly).
- `breakdown`: Per-metric sub-scores (each 0–100) before weighting.
- Results are sorted by `smell_score` descending when analyzing a folder.

## When to use this skill
- As a first-pass triage tool to decide which files need manual review.
- To track code quality trends across a codebase over time.
- As input context for the `llm-code-smells` skill — run this first, then pass the highest-scoring files to the LLM for a deeper conceptual analysis.
