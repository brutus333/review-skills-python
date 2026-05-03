import ast
import argparse
import sys
import tson

def calculate_cyclomatic_complexity(node: ast.AST) -> int:
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.AsyncWith,
                             ast.And, ast.Or, ast.ExceptHandler, ast.Try, ast.Assert)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity

def get_function_metrics(code: str) -> list:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
        
    metrics = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            metrics.append({
                "name": getattr(node, 'name', 'anonymous'),
                "type": "function",
                "complexity": calculate_cyclomatic_complexity(node),
                "line_number": node.lineno
            })
        elif isinstance(node, ast.ClassDef):
            for subnode in node.body:
                if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    metrics.append({
                        "name": getattr(subnode, 'name', 'anonymous'),
                        "type": "method",
                        "complexity": calculate_cyclomatic_complexity(subnode),
                        "line_number": subnode.lineno,
                        "class_name": node.name
                    })
    return metrics

def analyze_file(file_path: str) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        return {"file": file_path, "error": str(e)}

    metrics = get_function_metrics(code)
    return {"file": file_path, "metrics": metrics}


def main():
    import pathlib
    parser = argparse.ArgumentParser(description="Calculate cyclomatic complexity of a Python file or folder.")
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
