from typing import List, Dict, Any, Callable
from .guidelines import search_guidelines
from .rag import retrieve_rag
from .dosing import calc_dose
from .interactions import check_interactions


def tool_specs() -> List[Dict[str, Any]]:
    """Return OpenAI-compatible tool specifications"""
    return [
        {
            "type": "function",
            "function": {
                "name": "search_guidelines",
                "description": "Search vetted clinical practice guidelines from major medical organizations (AHA/ACC, ESC, ADA, KDIGO). Returns evidence-based recommendations with citations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query - use medical terms and condition names (e.g., 'ACE inhibitor diabetes CKD', 'hypertension treatment elderly')"
                        },
                        "section": {
                            "type": "string",
                            "enum": ["diagnosis", "treatment", "monitoring", "drug-dosing"],
                            "description": "Specific guideline section to search. Use 'treatment' for therapy recommendations, 'drug-dosing' for dose information."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "retrieve_rag",
                "description": "Retrieve relevant passages from medical literature corpus (peer-reviewed studies, meta-analyses, clinical trials). Use to find specific research evidence.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query focused on specific medical topics (e.g., 'GLP-1 cardiovascular outcomes', 'SGLT2 inhibitor heart failure', 'ACE inhibitor renal dosing')"
                        },
                        "k": {
                            "type": "integer",
                            "default": 5,
                            "description": "Number of passages to retrieve (default 5, max 10)"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calc_dose",
                "description": "Calculate medication doses with adjustments for renal function, weight, or age. Provides starting and maximum doses.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rule": {
                            "type": "string",
                            "description": "Medication name (e.g., 'lisinopril', 'metformin', 'semaglutide')"
                        },
                        "weight_kg": {
                            "type": "number",
                            "description": "Patient weight in kg (if weight-based dosing)"
                        },
                        "egfr": {
                            "type": "number",
                            "description": "Estimated GFR in mL/min/1.73m² (for renal dose adjustment)"
                        }
                    },
                    "required": ["rule", "weight_kg"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_interactions",
                "description": "Check for drug-drug interactions and contraindications based on current medications and patient conditions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "medications": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of current medications (generic names preferred)"
                        },
                        "conditions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of patient conditions (e.g., 'CKD stage 3', 'heart failure', 'diabetes')"
                        }
                    },
                    "required": ["medications"]
                }
            }
        }
    ]


# Tool implementation registry
TOOL_IMPL: Dict[str, Callable] = {
    "search_guidelines": search_guidelines,
    "retrieve_rag": retrieve_rag,
    "calc_dose": calc_dose,
    "check_interactions": check_interactions
}


def execute_tools(tool_requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Execute requested tools and return results"""
    results = []
    
    for req in tool_requests:
        tool_name = req.get("tool")
        args = req.get("args", {})
        
        if tool_name not in TOOL_IMPL:
            results.append({
                "tool": tool_name,
                "args": args,
                "output": {"error": f"Unknown tool: {tool_name}"}
            })
            continue
        
        try:
            print(f"  Executing: {tool_name}({', '.join(f'{k}={v}' for k, v in args.items())})")
            output = TOOL_IMPL[tool_name](**args)
            results.append({
                "tool": tool_name,
                "args": args,
                "output": output
            })
        except Exception as e:
            print(f"  ERROR in {tool_name}: {e}")
            results.append({
                "tool": tool_name,
                "args": args,
                "output": {"error": str(e)}
            })
    
    return results