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

def main():
    parser = argparse.ArgumentParser(description="Find nested loops in a Python file.")
    parser.add_argument("file", help="Path to the python file to analyze")
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

    hotspots = detect_nested_loops(tree)
    
    result = {
        "file": args.file,
        "nested_loops": hotspots
    }
    print(tson.dumps(result))

if __name__ == "__main__":
    main()
