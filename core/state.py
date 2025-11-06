from typing import TypedDict, Dict, Any, List


class CollabState(TypedDict, total=False):
    """State passed between graph nodes"""
    user_msg: str
    routing: Dict[str, Any]
    tool_results: List[Dict[str, Any]]
    cardiology_response: Dict[str, Any]
    diabetes_response: Dict[str, Any]
    hypertension_response: Dict[str, Any]
    consensus: Dict[str, Any]
    final: Dict[str, Any]