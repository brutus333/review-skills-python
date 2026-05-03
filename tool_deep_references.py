import ast
import argparse
import sys
import tson

def get_chain_depth(node):
    depth = 0
    current = node
    while isinstance(current, (ast.Attribute, ast.Call)):
        if isinstance(current, ast.Attribute):
            current = current.value
            depth += 1
        elif isinstance(current, ast.Call):
            current = current.func
            depth += 1
    return depth

def detect_deep_references(tree: ast.AST, min_depth=3) -> list:
    refs = []
    
    # We want to find the top of the chain to avoid reporting sub-chains.
    # We can collect all valid chains and then only keep those not contained in others.
    # Alternatively, start from Expr / Assign and find max depth.
    chains = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Attribute, ast.Call)):
            depth = get_chain_depth(node)
            if depth >= min_depth:
                chains.append({
                    "line_number": getattr(node, 'lineno', -1),
                    "depth": depth
                })
    
    # Filter out subchains by grouping by line number and taking max depth
    grouped = {}
    for c in chains:
        ln = c["line_number"]
        if ln not in grouped or c["depth"] > grouped[ln]["depth"]:
            grouped[ln] = c
            
    return list(grouped.values())

def analyze_file(file_path: str, threshold: int) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        return {"file": file_path, "error": str(e)}

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"file": file_path, "error": "SyntaxError", "msg": str(e)}

    refs = detect_deep_references(tree, min_depth=threshold)
    return {"file": file_path, "deep_references": refs}


def main():
    import pathlib
    parser = argparse.ArgumentParser(description="Find deep object or method references in a Python file or folder.")
    parser.add_argument("path", help="Path to a Python file or folder to analyze")
    parser.add_argument("--threshold", type=int, default=3, help="Minimum depth of reference chain")
    args = parser.parse_args()

    target = pathlib.Path(args.path)

    if target.is_dir():
        py_files = sorted(target.rglob("*.py"))
        if not py_files:
            print(tson.dumps({"error": f"No Python files found in {args.path}"}))
            sys.exit(1)
        results = [analyze_file(str(f), args.threshold) for f in py_files]
        print(tson.dumps({"path": args.path, "results": results}))
    elif target.is_file():
        result = analyze_file(str(target), args.threshold)
        print(tson.dumps(result))
    else:
        print(tson.dumps({"error": f"Path not found: {args.path}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
