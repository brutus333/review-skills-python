"""
tool_smell_score.py
-------------------
Computes a code smell suspicion score (0–100) for each Python file by
aggregating signals from five static analyzers:

  1. Cyclomatic complexity  (weight 0.30) – % of functions with complexity > HIGH_CC
  2. Code duplication       (weight 0.25) – number of near-duplicate block pairs
  3. Nested loops           (weight 0.20) – number of nested-loop hotspots
  4. Deep references        (weight 0.15) – number of deep attribute/method chains
  5. Linter issues          (weight 0.10) – severity-weighted pylint issue count

Each sub-score is capped at 100 before weighting.  A final weighted sum
(also 0–100) is reported alongside the breakdown.

Usage:
    python tool_smell_score.py <file_or_folder> [options]

Options:
    --cc-threshold INT      Cyclomatic complexity "high" threshold (default: 10)
    --dup-threshold FLOAT   Duplication similarity threshold 0-100 (default: 80)
    --ref-depth INT         Minimum deep-reference chain depth (default: 3)
    --w-complexity FLOAT    Weight for complexity score (default: 0.30)
    --w-duplication FLOAT   Weight for duplication score (default: 0.25)
    --w-nested FLOAT        Weight for nested-loops score (default: 0.20)
    --w-refs FLOAT          Weight for deep-refs score   (default: 0.15)
    --w-linter FLOAT        Weight for linter score      (default: 0.10)
"""

import argparse
import pathlib
import sys
import tson

# ---------------------------------------------------------------------------
# Import analysis helpers from the other tools
# ---------------------------------------------------------------------------
from tool_cyclomatic_complexity import get_function_metrics as cc_get_metrics
from tool_code_duplication import get_blocks, CodeSimilarityAnalyzer
from tool_nested_loops import detect_nested_loops
from tool_deep_references import detect_deep_references
from tool_python_linter import run_linter

import ast

# Severity weights for pylint message types
LINTER_SEVERITY = {
    "error":      10,
    "fatal":      10,
    "warning":    4,
    "refactor":   2,
    "convention": 1,
}

# ---------------------------------------------------------------------------
# Per-metric scorers  (all return a float in [0, 100])
# ---------------------------------------------------------------------------

def score_complexity(code: str, high_threshold: int) -> float:
    """% of functions/methods with cyclomatic complexity above threshold → 0-100."""
    metrics = cc_get_metrics(code)
    if not metrics:
        return 0.0
    high = sum(1 for m in metrics if m["complexity"] >= high_threshold)
    return min((high / len(metrics)) * 100, 100.0)


def score_duplication(code: str, dup_threshold: float) -> float:
    """Each near-duplicate pair adds 20 points (capped at 100)."""
    blocks = get_blocks(code)
    analyzer = CodeSimilarityAnalyzer(threshold=dup_threshold)
    pairs = analyzer.find_near_duplicates(blocks)
    return min(len(pairs) * 20, 100.0)


def score_nested_loops(tree: ast.AST) -> float:
    """Each nested-loop hotspot adds 25 points (capped at 100)."""
    hotspots = detect_nested_loops(tree)
    return min(len(hotspots) * 25, 100.0)


def score_deep_refs(tree: ast.AST, min_depth: int) -> float:
    """Each deep-reference line adds 15 points (capped at 100)."""
    refs = detect_deep_references(tree, min_depth=min_depth)
    return min(len(refs) * 15, 100.0)


def score_linter(file_path: str) -> float:
    """Severity-weighted pylint issue count, normalised to 0-100 (cap at 50pts raw)."""
    issues = run_linter(file_path)
    raw = 0
    for issue in issues:
        msg_type = issue.get("type", "convention").lower()
        raw += LINTER_SEVERITY.get(msg_type, 1)
    # 50 raw points → 100 score; scale linearly
    return min((raw / 50) * 100, 100.0)


# ---------------------------------------------------------------------------
# File-level aggregator
# ---------------------------------------------------------------------------

def analyze_file(
    file_path: str,
    cc_threshold: int,
    dup_threshold: float,
    ref_depth: int,
    weights: dict,
) -> dict:
    """Return a dict with per-metric scores plus a weighted overall score."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        return {"file": file_path, "error": str(e)}

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"file": file_path, "error": "SyntaxError", "msg": str(e)}

    s_cc   = score_complexity(code, cc_threshold)
    s_dup  = score_duplication(code, dup_threshold)
    s_nl   = score_nested_loops(tree)
    s_dr   = score_deep_refs(tree, ref_depth)
    s_lint = score_linter(file_path)

    total = (
        weights["complexity"]  * s_cc  +
        weights["duplication"] * s_dup +
        weights["nested"]      * s_nl  +
        weights["refs"]        * s_dr  +
        weights["linter"]      * s_lint
    )
    total = round(min(total, 100.0), 2)

    return {
        "file": file_path,
        "smell_score": total,
        "breakdown": {
            "cyclomatic_complexity": round(s_cc, 2),
            "code_duplication":      round(s_dup, 2),
            "nested_loops":          round(s_nl, 2),
            "deep_references":       round(s_dr, 2),
            "linter_issues":         round(s_lint, 2),
        },
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compute a code smell suspicion score (0–100) for Python files."
    )
    parser.add_argument("path", help="Path to a Python file or folder to analyze")

    # Thresholds
    parser.add_argument("--cc-threshold",   type=int,   default=10,   help="Cyclomatic complexity 'high' threshold (default: 10)")
    parser.add_argument("--dup-threshold",  type=float, default=80.0, help="Duplication similarity threshold (default: 80)")
    parser.add_argument("--ref-depth",      type=int,   default=3,    help="Minimum deep-reference depth (default: 3)")

    # Weights
    parser.add_argument("--w-complexity",   type=float, default=0.30, help="Weight for complexity score")
    parser.add_argument("--w-duplication",  type=float, default=0.25, help="Weight for duplication score")
    parser.add_argument("--w-nested",       type=float, default=0.20, help="Weight for nested-loops score")
    parser.add_argument("--w-refs",         type=float, default=0.15, help="Weight for deep-refs score")
    parser.add_argument("--w-linter",       type=float, default=0.10, help="Weight for linter score")

    args = parser.parse_args()

    # Normalise weights so they always sum to 1.0
    raw_weights = {
        "complexity":  args.w_complexity,
        "duplication": args.w_duplication,
        "nested":      args.w_nested,
        "refs":        args.w_refs,
        "linter":      args.w_linter,
    }
    total_w = sum(raw_weights.values())
    if total_w == 0:
        print(tson.dumps({"error": "All weights are zero"}))
        sys.exit(1)
    weights = {k: v / total_w for k, v in raw_weights.items()}

    target = pathlib.Path(args.path)

    if target.is_dir():
        py_files = sorted(target.rglob("*.py"))
        if not py_files:
            print(tson.dumps({"error": f"No Python files found in {args.path}"}))
            sys.exit(1)
        results = [
            analyze_file(str(f), args.cc_threshold, args.dup_threshold, args.ref_depth, weights)
            for f in py_files
        ]
        # Sort by score descending so highest-risk files come first
        results.sort(key=lambda r: r.get("smell_score", 0), reverse=True)
        print(tson.dumps({"path": args.path, "results": results}))

    elif target.is_file():
        result = analyze_file(
            str(target), args.cc_threshold, args.dup_threshold, args.ref_depth, weights
        )
        print(tson.dumps(result))

    else:
        print(tson.dumps({"error": f"Path not found: {args.path}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
