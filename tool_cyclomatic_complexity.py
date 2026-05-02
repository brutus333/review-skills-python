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

def main():
    parser = argparse.ArgumentParser(description="Calculate cyclomatic complexity of a Python file.")
    parser.add_argument("file", help="Path to the python file to analyze")
    args = parser.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(tson.dumps({"error": str(e)}))
        sys.exit(1)

    metrics = get_function_metrics(code)
    
    result = {
        "file": args.file,
        "metrics": metrics
    }
    
    print(tson.dumps(result))

if __name__ == "__main__":
    main()
