import argparse
import sys
import json
import subprocess
import tson

def run_linter(file_path: str) -> list:
    """
    Runs pylint on the provided file and returns a list of warnings/errors.
    Assumes `pylint` is installed in the environment.
    """
    try:
        # Run pylint with json output format
        result = subprocess.run(
            [sys.executable, "-m", "pylint", file_path, "--output-format=json"],
            capture_output=True,
            text=True
        )
        # Pylint returns 0 on perfect score, but often returns non-zero on linting errors.
        # But we only care about stdout containing the JSON.
        if not result.stdout.strip():
            return []
            
        try:
            lint_data = json.loads(result.stdout)
            return lint_data
        except json.JSONDecodeError:
            return [{"error": "Failed to parse pylint output", "output": result.stdout}]
            
    except Exception as e:
        return [{"error": str(e)}]

def analyze_file(file_path: str) -> dict:
    lint_results = run_linter(file_path)
    return {"file": file_path, "linter_issues": lint_results}


def main():
    import pathlib
    parser = argparse.ArgumentParser(description="Run python linter on a file or folder.")
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
