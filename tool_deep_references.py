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

def main():
    parser = argparse.ArgumentParser(description="Find deep object or method references in a Python file.")
    parser.add_argument("file", help="Path to the python file to analyze")
    parser.add_argument("--threshold", type=int, default=3, help="Minimum depth of reference chain")
    args = parser.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(tson.dumps({"error": str(e)}))
        sys.exit(1)

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print(tson.dumps({"error": "SyntaxError", "msg": str(e)}))
        sys.exit(1)

    refs = detect_deep_references(tree, min_depth=args.threshold)
    
    result = {
        "file": args.file,
        "deep_references": refs
    }
    print(tson.dumps(result))

if __name__ == "__main__":
    main()
