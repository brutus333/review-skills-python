import argparse
import sys
import json
import os
import tson

def detect_code_smells_gemini(code: str) -> list:
    """
    Uses the modern Google GenAI library to find code smells in the provided code snippet.
    Focuses on 'God Method' and 'Long Argument List'.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return [{"error": "GEMINI_API_KEY environment variable not set. LLM analysis requires an API key."}]
    
    try:
        from google import genai
    except ImportError:
        return [{"error": "google-genai package not found. Please 'pip install google-genai'"}]
        
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
Analyze the following Python code for code smells. Focus specifically on identifying 'God Method' (methods that do too much) and 'Long Argument List' (methods with too many parameters), but also include other significant structural smells if you find them.
Return ONLY a valid JSON array of objects, with no markdown formatting or backticks.
Each object should have:
- "type": The kind of smell (e.g. "God Method")
- "function": The name of the function or class
- "line": Approximate line number or "N/A"
- "description": Why it is a code smell.

Code to analyze:
{code}
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        return json.loads(text)
    except Exception as e:
        return [{"error": f"LLM analysis failed: {str(e)}"}]

def main():
    parser = argparse.ArgumentParser(description="Find code smells using an LLM (Gemini).")
    parser.add_argument("file", help="Path to the python file to analyze")
    args = parser.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(tson.dumps({"error": str(e)}))
        sys.exit(1)

    smells = detect_code_smells_gemini(code)
    
    result = {
        "file": args.file,
        "code_smells": smells
    }
    
    # Must use string serialization through tson
    print(tson.dumps(result))

if __name__ == "__main__":
    main()
