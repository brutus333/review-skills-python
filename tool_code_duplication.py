import ast
import argparse
import sys
import tson
from rapidfuzz import fuzz

class CodeSimilarityAnalyzer:
    def __init__(self, threshold: float = 80.0, min_length: int = 50):
        self.threshold = threshold
        self.min_length = min_length

    def normalize_code(self, code: str) -> str:
        import re
        code = re.sub(r'(""".*?"""|\'\'\'.*?\'\'\')', '', code, flags=re.DOTALL)
        code = re.sub(r'#.*', '', code)
        return "".join(code.split())

    def calculate_similarity(self, code1: str, code2: str) -> float:
        if not code1 or not code2:
            return 0.0
        if len(code1) < self.min_length or len(code2) < self.min_length:
            return 0.0
        norm1 = self.normalize_code(code1)
        norm2 = self.normalize_code(code2)
        if not norm1 or not norm2:
            return 0.0
        return fuzz.ratio(norm1, norm2)

    def find_near_duplicates(self, blocks: list, threshold=None) -> list:
        t = threshold if threshold is not None else self.threshold
        results = []
        for i in range(len(blocks)):
            for j in range(i + 1, len(blocks)):
                id1, code1 = blocks[i]
                id2, code2 = blocks[j]
                if id1 == id2:
                    continue
                score = self.calculate_similarity(code1, code2)
                if score >= t:
                    results.append({"id1": id1, "id2": id2, "score": score})
        return results

def get_blocks(code: str) -> list:
    try:
        tree = ast.parse(code)
    except Exception:
        return []
        
    blocks = []
    lines = code.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            try:
                start = node.lineno - 1
                end = node.end_lineno
                body = "\n".join(lines[start:end])
                blocks.append((node.name, body))
            except Exception:
                pass
    return blocks

def analyze_file(file_path: str, threshold: float) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        return {"file": file_path, "error": str(e)}

    blocks = get_blocks(code)
    analyzer = CodeSimilarityAnalyzer(threshold=threshold)
    duplicates = analyzer.find_near_duplicates(blocks)
    return {"file": file_path, "duplicates": duplicates}


def main():
    import pathlib
    parser = argparse.ArgumentParser(description="Find code duplication in a Python file or folder.")
    parser.add_argument("path", help="Path to a Python file or folder to analyze")
    parser.add_argument("--threshold", type=float, default=80.0, help="Similarity threshold")
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
