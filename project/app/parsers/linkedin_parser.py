import json
from typing import Dict, Any

def parse_linkedin_json(file_path: str) -> Dict[str, Any]:
    """Parses a LinkedIn profile JSON."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error parsing LinkedIn JSON {file_path}: {e}")
        return {}
