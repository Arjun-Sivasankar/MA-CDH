from typing import Dict, Any


def format_specialist_response(domain: str, response: Dict[str, Any]) -> str:
    """Format specialist response for display"""
    if not response:
        return f"{domain.upper()}: Not consulted"
    
    output = [f"\n{domain.upper()} SPECIALIST:"]
    output.append(f"Assessment: {response.get('assessment', 'N/A')}")
    
    if response.get('recommendations'):
        output.append("Recommendations:")
        for rec in response['recommendations']:
            output.append(f"  - {rec}")
    
    if response.get('concerns'):
        output.append("Concerns:")
        for concern in response['concerns']:
            output.append(f"  - {concern}")
    
    output.append(f"Confidence: {response.get('confidence', 0):.2%}")
    
    return "\n".join(output)


def format_result(result: Dict[str, Any]) -> str:
    """Format complete result for display"""
    output = []
    
    # Routing
    output.append("="*70)
    output.append("ROUTING DECISION")
    output.append("="*70)
    routing = result.get("routing", {})
    output.append(f"Primary: {routing.get('primary')}")
    output.append(f"Consult: {routing.get('consult', [])}")
    output.append(f"Reasoning: {routing.get('reasoning', 'N/A')}")
    
    # Specialist Assessments
    output.append("\n" + "="*70)
    output.append("SPECIALIST ASSESSMENTS")
    output.append("="*70)
    
    for domain in ["cardiology", "diabetes", "hypertension"]:
        resp = result.get(f"{domain}_response", {})
        if resp:
            output.append(format_specialist_response(domain, resp))
    
    # Consensus
    output.append("\n" + "="*70)
    output.append("CONSENSUS")
    output.append("="*70)
    consensus = result.get("consensus", {})
    output.append(f"Final Assessment: {consensus.get('final_assessment', 'N/A')}")
    output.append(f"Agreement Level: {consensus.get('specialist_agreement', 'N/A')}")
    output.append(f"Confidence: {consensus.get('confidence', 0):.2%}")
    
    if consensus.get("unified_plan"):
        output.append("\nUnified Plan:")
        for i, step in enumerate(consensus.get("unified_plan", []), 1):
            output.append(f"  {i}. {step}")
    
    if consensus.get("critical_alerts"):
        output.append("\nCRITICAL ALERTS:")
        for alert in consensus.get("critical_alerts", []):
            output.append(f"  - {alert}")
    
    return "\n".join(output)