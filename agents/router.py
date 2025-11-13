from typing import Dict, Any
from .base import BaseAgent
from utils.parser import safe_json_parse  # kept for compatibility; not used here

# Fixed execution order for strict sequential mode
ORDER = ["cardiology", "hypertension", "diabetes"]
VALID_SPECIALISTS = set(ORDER)


class RouterAgent(BaseAgent):
    """Routes queries to ALL specialists in a strict fixed order."""

    @property
    def system_prompt(self) -> str:
        # Kept for API compatibility; not used in strict mode.
        return """Sequential Routing Mode:
Always involve ALL specialists in this exact order:
1) cardiology
2) hypertension
3) diabetes
Return JSON with these fields:
{
  "primary": "cardiology",
  "consult": ["hypertension", "diabetes"],
  "requires_consensus": true,
  "urgency": "routine",
  "reasoning": "Sequential mode: forced to run all specialists"
}"""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Strict, hard-coded routing:
        - Always run ALL three specialists
        - Preserve fixed order: cardiology -> hypertension -> diabetes
        - Mark requires_consensus = True
        - Default urgency = "routine"
        - Ignore LLM completely in this mode
        """
        print("\n[ROUTER] Sequential mode enabled — forcing all specialists in fixed order.")
        user_msg = state.get("user_msg", "")

        # Deterministic routing
        primary = ORDER[0]
        consult = ORDER[1:]

        routing = {
            "primary": primary,
            "consult": consult,
            "requires_consensus": True,
            "urgency": "routine",
            "reasoning": "Sequential mode: forced to run all specialists (cardiology → hypertension → diabetes).",
        }

        # Defensive final cleanup (keeps compatibility with any downstream checks)
        if routing.get("primary") not in VALID_SPECIALISTS:
            routing["primary"] = primary

        # Ensure consult is a list containing only valid specialists except primary, in fixed order
        consult_list = routing.get("consult", [])
        if not isinstance(consult_list, list):
            consult_list = [consult_list] if consult_list else []
        consult_list = [s for s in ORDER if s in VALID_SPECIALISTS and s != routing["primary"]]
        routing["consult"] = consult_list

        print(f"[ROUTER] Primary: {routing['primary']}")
        print(f"[ROUTER] Consult (fixed order): {routing['consult']}")
        print(f"[ROUTER] Urgency: {routing['urgency']}")
        print(f"[ROUTER] Reasoning: {routing.get('reasoning', 'N/A')}")
        print(f"[ROUTER] User message (for trace): {user_msg[:120]}{'...' if len(user_msg) > 120 else ''}")

        return {"routing": routing}
