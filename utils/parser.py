import json
from typing import Dict, Any, Optional


def safe_json_parse(content: str, default: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Safely parse JSON with fallback
    
    Args:
        content: JSON string to parse
        default: Default dict to return on error
    
    Returns:
        Parsed dictionary or default
    """
    if default is None:
        default = {}
    
    if not content:
        return default
    
    # Clean up common JSON issues
    content = content.strip()
    
    # Remove markdown code blocks
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1] if len(lines) > 2 else lines)
        content = content.strip()
    
    # Remove language identifier
    if content.startswith("json"):
        content = content[4:].strip()
    
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"WARNING - JSON parse error: {e}")
        print(f"Content: {repr(content[:200])}")
        return {**default, "_raw_content": content}