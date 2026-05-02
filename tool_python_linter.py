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

def main():
    parser = argparse.ArgumentParser(description="Run python linter on a file.")
    parser.add_argument("file", help="Path to the python file to analyze")
    args = parser.parse_args()

    lint_results = run_linter(args.file)
    
    result = {
        "file": args.file,
        "linter_issues": lint_results
    }
    print(tson.dumps(result))

if __name__ == "__main__":
    main()
