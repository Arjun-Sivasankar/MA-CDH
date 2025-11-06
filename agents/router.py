from typing import Dict, Any
from .base import BaseAgent
from utils.parser import safe_json_parse


class RouterAgent(BaseAgent):
    """Routes queries to appropriate specialists"""
    
    @property
    def system_prompt(self) -> str:
        return """You are a medical triage coordinator. Analyze the clinical query and determine which specialists should be consulted.

Available specialists:
- cardiology (heart disease, BP management, cardiovascular risk)
- diabetes (blood sugar control, diabetes complications)
- hypertension (blood pressure management)

For multi-morbidity cases (e.g., patient has HTN + diabetes + CKD), you MUST select ALL relevant specialists.

Respond with valid JSON only (no markdown, no code blocks):
{
  "primary": "hypertension",
  "consult": ["cardiology", "diabetes"],
  "requires_consensus": true,
  "urgency": "routine",
  "reasoning": "Patient has HTN, T2D, and CKD - requires multi-specialist approach"
}

Rules:
- "primary" must be ONE of: "cardiology", "diabetes", "hypertension"
- "consult" must be an array of additional specialists (can be empty)
- For multi-condition patients, put the main concern in "primary" and others in "consult"
- "urgency" must be one of: "routine", "urgent", "emergent"
"""
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Route query to specialists"""
        print("\n[ROUTER] Analyzing query...")
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": state["user_msg"]}
        ]
        
        res = self.llm.chat(messages)
        content = res.get("content", "{}")
        
        routing = safe_json_parse(content, default={
            "primary": "hypertension",
            "consult": ["cardiology", "diabetes"],
            "requires_consensus": True,
            "urgency": "routine",
            "reasoning": "Default routing - all specialists consulted"
        })
        
        # Validation and cleanup
        valid_specialists = ["cardiology", "diabetes", "hypertension"]
        
        # Fix primary if it's malformed
        primary = routing.get("primary", "hypertension")
        if primary not in valid_specialists:
            # Check if it's a combined string like "cardiology|diabetes|hypertension"
            if "|" in str(primary):
                parts = str(primary).split("|")
                primary = parts[0].strip()
                # Add other parts to consult
                consult = routing.get("consult", [])
                if not isinstance(consult, list):
                    consult = []
                for part in parts[1:]:
                    part = part.strip()
                    if part in valid_specialists and part not in consult:
                        consult.append(part)
                routing["consult"] = consult
            else:
                # Default to hypertension if completely invalid
                primary = "hypertension"
        
        routing["primary"] = primary
        
        # Ensure consult is a list
        consult = routing.get("consult", [])
        if not isinstance(consult, list):
            consult = [consult] if consult else []
        
        # Filter consult to only valid specialists
        consult = [s for s in consult if s in valid_specialists and s != primary]
        routing["consult"] = consult
        
        print(f"[ROUTER] Primary: {routing['primary']}")
        print(f"[ROUTER] Consult: {routing['consult']}")
        print(f"[ROUTER] Reasoning: {routing.get('reasoning', 'N/A')}")
        
        return {"routing": routing}