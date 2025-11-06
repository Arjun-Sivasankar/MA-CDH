import json
from typing import Dict, Any
from .base import BaseAgent
from tools.registry import tool_specs, execute_tools
from utils.parser import safe_json_parse


class SpecialistAgent(BaseAgent):
    """Domain-specific specialist agent"""
    
    def __init__(self, llm, domain: str):
        super().__init__(llm)
        self.domain = domain
    
    @property
    def system_prompt(self) -> str:
        return f"""You are a {self.domain} specialist in a multi-disciplinary medical team.

Your role:
1. Analyze the clinical query from your specialty's perspective
2. Use available tools to gather evidence (guidelines, literature, dosing calculators)
3. Flag any concerns or contraindications relevant to your domain
4. Consider input from other specialists if provided
5. Never invent facts - only use tool results and established guidelines

Available tools and when to use them:
- search_guidelines: For official clinical practice guidelines (use query + optional section)
- retrieve_rag: For research evidence and studies (use query + k)
- calc_dose: For medication dosing (requires: rule=medication_name, weight_kg=number, egfr=number)
- check_interactions: For drug interactions (requires: medications=[list], conditions=[list])

Respond with valid JSON only (no markdown, no code blocks):
{{
  "assessment": "your clinical assessment based on the query and available evidence",
  "recommendations": ["specific recommendation 1", "specific recommendation 2"],
  "concerns": ["specific concern 1", "specific concern 2"],
  "tool_calls": [
    {{"tool": "search_guidelines", "args": {{"query": "ACE inhibitor diabetes CKD", "section": "treatment"}}}},
    {{"tool": "calc_dose", "args": {{"rule": "lisinopril", "weight_kg": 80, "egfr": 55}}}}
  ],
  "contraindications": ["contraindication 1 if any"],
  "confidence": 0.8,
  "citations": ["guideline-id-1", "pmid12345"]
}}

Important for tool_calls:
- Use "tool_calls" NOT "tool_needs"
- Each tool call must have proper "args" matching the tool's requirements
- For calc_dose: must include rule (medication name), weight_kg (number), and optionally egfr
- For check_interactions: must include medications (array) and optionally conditions (array)
- For search_guidelines: use query (string) and optionally section
- For retrieve_rag: use query (string) and optionally k (number)

Guidelines:
- Be specific with doses, monitoring parameters, and timelines
- Always consider drug interactions and contraindications
- Reference specific guidelines when making recommendations
- State confidence honestly based on evidence quality
"""
    
    def _extract_patient_info(self, query: str) -> Dict[str, Any]:
        """Extract basic patient information from query"""
        query_lower = query.lower()
        
        # Extract age
        age = None
        age_patterns = [r'(\d+)\s*y', r'(\d+)\s*yo', r'(\d+)\s*year']
        import re
        for pattern in age_patterns:
            match = re.search(pattern, query_lower)
            if match:
                age = int(match.group(1))
                break
        
        # Estimate weight if not given (average adult)
        weight_kg = 75.0  # default
        
        # Extract eGFR if mentioned
        egfr = None
        egfr_match = re.search(r'egfr\s*(\d+)', query_lower)
        if egfr_match:
            egfr = float(egfr_match.group(1))
        
        # Extract mentioned conditions
        conditions = []
        condition_keywords = {
            'htn': 'hypertension',
            'hypertension': 'hypertension',
            't2d': 'diabetes',
            'diabetes': 'diabetes',
            'ckd': 'chronic kidney disease',
            'heart failure': 'heart failure',
            'hf': 'heart failure',
            'cad': 'coronary artery disease',
            'mi': 'myocardial infarction'
        }
        
        for keyword, condition in condition_keywords.items():
            if keyword in query_lower:
                conditions.append(condition)
        
        return {
            'age': age,
            'weight_kg': weight_kg,
            'egfr': egfr,
            'conditions': list(set(conditions))
        }
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process query from specialist perspective"""
        
        # Check if this specialist should run
        routing = state.get("routing", {})
        primary = routing.get("primary", "")
        consult = routing.get("consult", [])
        
        # Ensure consult is a list
        if not isinstance(consult, list):
            consult = [consult] if consult else []
        
        # Build list of active domains
        active_domains = [primary] + consult
        
        # Clean up any malformed primary values
        if "|" in str(primary):
            # If primary contains multiple specialists separated by |
            active_domains = str(primary).split("|") + consult
        
        # Normalize domain names
        active_domains = [str(d).strip().lower() for d in active_domains]
        
        # Check if this specialist should be active
        if self.domain.lower() not in active_domains:
            print(f"[{self.domain.upper()}] Skipped (not in routing)")
            print(f"  Active domains: {active_domains}")
            return {}
        
        print(f"\n[{self.domain.upper()}] Analyzing...")
        
        # Extract patient info for potential tool calls
        patient_info = self._extract_patient_info(state['user_msg'])
        
        # Gather context from other specialists
        context_parts = []
        for other_domain in ["cardiology", "diabetes", "hypertension"]:
            if other_domain == self.domain:
                continue
            resp = state.get(f"{other_domain}_response", {})
            if resp and resp.get("assessment"):
                context_parts.append(
                    f"{other_domain.title()}: {resp.get('assessment', '')}"
                )
        
        context_str = "\n".join(context_parts) if context_parts else \
                      "No input from other specialists yet."
        
        # Build prompt with patient info hint
        prompt = f"""Clinical Query: {state['user_msg']}

Patient Information Extracted:
- Age: {patient_info.get('age', 'not specified')}
- Weight: ~{patient_info.get('weight_kg')} kg (estimated if not given)
- eGFR: {patient_info.get('egfr', 'not specified')} mL/min/1.73m²
- Conditions: {', '.join(patient_info.get('conditions', [])) or 'see query'}

Other Specialists' Input:
{context_str}

Tool Results Available:
{json.dumps(state.get('tool_results', []), indent=2)}

Provide your {self.domain} specialist assessment. If you need to call tools like calc_dose or check_interactions, use the patient information above to construct proper arguments."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        res = self.llm.chat(messages, tools=tool_specs())
        content = res.get("content", "{}")
        
        response = safe_json_parse(content, default={
            "assessment": f"Assessment from {self.domain} specialist",
            "recommendations": [],
            "concerns": [],
            "confidence": 0.5
        })
        
        # Execute any new tools requested
        tool_calls = response.get("tool_calls", [])
        
        # Also check for legacy "tool_needs" format
        if not tool_calls and response.get("tool_needs"):
            print(f"[{self.domain.upper()}] Converting legacy tool_needs to tool_calls...")
            # Convert simple tool names to proper tool calls
            tool_needs = response.get("tool_needs", [])
            tool_calls = []
            
            for tool_name in tool_needs:
                if tool_name == "search_guidelines":
                    tool_calls.append({
                        "tool": "search_guidelines",
                        "args": {
                            "query": state["user_msg"],
                            "section": "treatment"
                        }
                    })
                elif tool_name == "retrieve_rag":
                    tool_calls.append({
                        "tool": "retrieve_rag",
                        "args": {
                            "query": state["user_msg"],
                            "k": 3
                        }
                    })
                elif tool_name == "calc_dose":
                    # Use extracted patient info
                    tool_calls.append({
                        "tool": "calc_dose",
                        "args": {
                            "rule": "lisinopril",  # Default medication
                            "weight_kg": patient_info.get('weight_kg', 75),
                            "egfr": patient_info.get('egfr')
                        }
                    })
                elif tool_name == "check_interactions":
                    # Extract medications from query or use common ones
                    tool_calls.append({
                        "tool": "check_interactions",
                        "args": {
                            "medications": ["lisinopril", "metformin"],  # Common for this case
                            "conditions": patient_info.get('conditions', [])
                        }
                    })
        
        if tool_calls:
            print(f"[{self.domain.upper()}] Executing {len(tool_calls)} tool(s)")
            
            # Validate and execute tool calls
            valid_tool_calls = []
            for tc in tool_calls:
                if not isinstance(tc, dict) or "tool" not in tc or "args" not in tc:
                    print(f"  WARNING: Invalid tool call format: {tc}")
                    continue
                valid_tool_calls.append(tc)
            
            if valid_tool_calls:
                tool_results = execute_tools(valid_tool_calls)
                
                # Update state with new tool results
                existing_results = state.get("tool_results", [])
                state["tool_results"] = existing_results + tool_results
        
        print(f"[{self.domain.upper()}] Assessment: {response.get('assessment', '')[:100]}...")
        print(f"[{self.domain.upper()}] Recommendations: {len(response.get('recommendations', []))}")
        print(f"[{self.domain.upper()}] Confidence: {response.get('confidence', 0):.2f}")
        
        return response