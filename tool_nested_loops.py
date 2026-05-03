import ast
import argparse
import sys
import tson

def detect_nested_loops(tree: ast.AST) -> list:
    hotspots = []
    
    def check_nesting(node, depth):
        if isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
            depth += 1
            if depth >= 2:
                hotspots.append({
                    "line_number": getattr(node, 'lineno', -1),
                    "depth": depth,
                    "type": type(node).__name__
                })
            
            for child in ast.iter_child_nodes(node):
                check_nesting(child, depth)
        else:
            for child in ast.iter_child_nodes(node):
                check_nesting(child, depth)

    check_nesting(tree, 0)
    return hotspots

def analyze_file(file_path: str) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        return {"file": file_path, "error": str(e)}

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"file": file_path, "error": "SyntaxError", "msg": str(e)}

    hotspots = detect_nested_loops(tree)
    return {"file": file_path, "nested_loops": hotspots}


def main():
    import pathlib
    parser = argparse.ArgumentParser(description="Find nested loops in a Python file or folder.")
    parser.add_argument("path", help="Path to a Python file or folder to analyze")
    args = parser.parse_args()

    target = pathlib.Path(args.path)

    if target.is_dir():
        py_files = sorted(target.rglob("*.py"))
        if not py_files:
            print(tson.dumps({"error": f"No Python files found in {args.path}"}))
            sys.exit(1)
        results = [analyze_file(str(f)) for f in py_files]
        print(tson.dumps({"path": args.path, "results": results}))
    elif target.is_file():
        result = analyze_file(str(target))
        print(tson.dumps(result))
    else:
        print(tson.dumps({"error": f"Path not found: {args.path}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
