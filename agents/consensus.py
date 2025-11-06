import json
from typing import Dict, Any
from .base import BaseAgent
from utils.parser import safe_json_parse


class ConsensusAgent(BaseAgent):
    """Synthesizes all specialist inputs"""
    
    @property
    def system_prompt(self) -> str:
        return """You are a clinical coordinator synthesizing multi-specialist input.

Your role:
1. Reconcile recommendations from different specialists
2. Identify conflicts or contraindications
3. Prioritize actions based on urgency and safety
4. Create a unified, actionable care plan
5. Highlight areas of agreement vs disagreement

Respond with valid JSON only (no markdown):
{
  "final_assessment": "integrated clinical picture",
  "unified_plan": ["step1", "step2", "step3"],
  "critical_alerts": ["alert1"],
  "specialist_agreement": "high|medium|low",
  "conflicts_resolved": ["conflict and resolution"],
  "confidence": 0.85,
  "next_steps": ["action1", "action2"]
}"""
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize all specialist inputs"""
        print("\n[CONSENSUS] Synthesizing recommendations...")
        
        # Gather all specialist responses
        specialists = {
            "cardiology": state.get("cardiology_response", {}),
            "diabetes": state.get("diabetes_response", {}),
            "hypertension": state.get("hypertension_response", {})
        }
        
        # Filter to only specialists who responded
        active_specialists = {k: v for k, v in specialists.items() if v}
        
        prompt = f"""Clinical Query: {state['user_msg']}

Specialist Assessments:
{json.dumps(active_specialists, indent=2)}

Tool Evidence:
{json.dumps(state.get('tool_results', []), indent=2)}

Synthesize into unified clinical recommendation."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        res = self.llm.chat(messages)
        content = res.get("content", "{}")
        
        consensus = safe_json_parse(content, default={
            "final_assessment": "Consensus assessment",
            "unified_plan": [],
            "confidence": 0.5
        })
        
        print(f"[CONSENSUS] Agreement level: "
              f"{consensus.get('specialist_agreement', 'unknown')}")
        print(f"[CONSENSUS] Critical alerts: "
              f"{len(consensus.get('critical_alerts', []))}")
        
        return {
            "consensus": consensus,
            "final": consensus
        }