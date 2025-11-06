# from typing import Dict, Any
# from langgraph.graph import StateGraph, END
# from core.llm import LLM
# from core.state import CollabState
# from agents import RouterAgent, SpecialistAgent, ConsensusAgent
# from tools.registry import execute_tools


# def tools_node(state: CollabState, llm: LLM) -> Dict[str, Any]:
#     """Execute initial tool calls"""
#     print("\n[TOOLS] Gathering initial evidence...")
    
#     query = state["user_msg"]
    
#     # Default tool plan
#     tool_plan = [
#         {"tool": "search_guidelines", "args": {"query": query, "section": "treatment"}},
#         {"tool": "retrieve_rag", "args": {"query": query, "k": 3}}
#     ]
    
#     # Execute tools
#     results = execute_tools(tool_plan)
    
#     print(f"[TOOLS] Executed {len(results)} tools")
    
#     return {"tool_results": results}


# def build_collaborative_graph(llm: LLM) -> Any:
#     """Build the collaborative multi-agent graph"""
    
#     # Initialize agents
#     router = RouterAgent(llm)
#     cardio_agent = SpecialistAgent(llm, "cardiology")
#     diabetes_agent = SpecialistAgent(llm, "diabetes")
#     htn_agent = SpecialistAgent(llm, "hypertension")
#     consensus = ConsensusAgent(llm)
    
#     # Build graph
#     g = StateGraph(CollabState)
    
#     # Add nodes
#     g.add_node("router", lambda s: router.process(s))
#     g.add_node("tools", lambda s: tools_node(s, llm))
#     g.add_node("cardiology", lambda s: {
#         "cardiology_response": cardio_agent.process(s)
#     })
#     g.add_node("diabetes", lambda s: {
#         "diabetes_response": diabetes_agent.process(s)
#     })
#     g.add_node("hypertension", lambda s: {
#         "hypertension_response": htn_agent.process(s)
#     })
#     g.add_node("consensus", lambda s: consensus.process(s))
    
#     # Define flow
#     g.set_entry_point("router")
#     g.add_edge("router", "tools")
    
#     # All specialists run after tools (they decide internally if they should process)
#     g.add_edge("tools", "cardiology")
#     g.add_edge("tools", "diabetes")
#     g.add_edge("tools", "hypertension")
    
#     # All feed into consensus
#     g.add_edge("cardiology", "consensus")
#     g.add_edge("diabetes", "consensus")
#     g.add_edge("hypertension", "consensus")
    
#     g.add_edge("consensus", END)
    
#     return g.compile()


# def run_collaborative_graph(llm: LLM, user_msg: str) -> Dict[str, Any]:
#     """Run the collaborative multi-agent system"""
#     print(f"\n{'='*70}")
#     print(f"COLLABORATIVE MULTI-AGENT SYSTEM")
#     print(f"{'='*70}")
#     print(f"Query: {user_msg}")
    
#     app = build_collaborative_graph(llm)
#     result = app.invoke({"user_msg": user_msg})
    
#     print(f"\n{'='*70}")
#     print(f"PROCESSING SUMMARY")
#     print(f"{'='*70}")
    
#     # Summary of what happened
#     routing = result.get("routing", {})
#     print(f"Routing - Primary: {routing.get('primary')}, Consult: {routing.get('consult', [])}")
    
#     for domain in ["cardiology", "diabetes", "hypertension"]:
#         resp = result.get(f"{domain}_response", {})
#         if resp:
#             print(f"  {domain.upper()}: Processed (confidence: {resp.get('confidence', 0):.2f})")
#         else:
#             print(f"  {domain.upper()}: Skipped")
    
#     consensus = result.get("consensus", {})
#     print(f"Consensus - Agreement: {consensus.get('specialist_agreement', 'N/A')}")
    
#     print(f"{'='*70}\n")
    
#     return result

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from core.llm import LLM
from core.state import CollabState
from agents import RouterAgent, SpecialistAgent, ConsensusAgent
from tools.registry import execute_tools


def tools_node(state: CollabState, llm: LLM) -> Dict[str, Any]:
    """Execute initial tool calls"""
    print("\n[TOOLS] Gathering initial evidence...")
    
    query = state["user_msg"]
    
    # Default tool plan
    tool_plan = [
        {"tool": "search_guidelines", "args": {"query": query, "section": "treatment"}},
        {"tool": "retrieve_rag", "args": {"query": query, "k": 3}}
    ]
    
    # Execute tools
    results = execute_tools(tool_plan)
    
    print(f"[TOOLS] Executed {len(results)} tools")
    
    return {"tool_results": results}


def specialist_coordinator(state: CollabState, llm: LLM) -> Dict[str, Any]:
    """
    Coordinates SEQUENTIAL specialist execution based on routing
    Each specialist can see previous specialists' responses
    """
    routing = state.get("routing", {})
    primary = routing.get("primary", "")
    consult = routing.get("consult", [])
    
    # Ensure consult is a list
    if not isinstance(consult, list):
        consult = [consult] if consult else []
    
    # Build ordered list: primary first, then consults
    active_specialists = []
    if primary:
        active_specialists.append(primary)
    active_specialists.extend([s for s in consult if s not in active_specialists])
    
    # If no specialists selected (shouldn't happen), default to hypertension
    if not active_specialists:
        print("[COORDINATOR] WARNING: No specialists selected, defaulting to hypertension")
        active_specialists = ["hypertension"]
    
    print(f"\n[COORDINATOR] Executing {len(active_specialists)} specialist(s) sequentially: {active_specialists}")
    
    # Initialize all specialist agents
    specialists = {
        "cardiology": SpecialistAgent(llm, "cardiology"),
        "diabetes": SpecialistAgent(llm, "diabetes"),
        "hypertension": SpecialistAgent(llm, "hypertension")
    }
    
    # Execute specialists SEQUENTIALLY so they can see each other's work
    updates = {}
    for i, specialist_name in enumerate(active_specialists):
        if specialist_name not in specialists:
            print(f"[COORDINATOR] WARNING: Unknown specialist '{specialist_name}'")
            continue
        
        print(f"\n[COORDINATOR] Executing specialist {i+1}/{len(active_specialists)}: {specialist_name.upper()}")
        
        agent = specialists[specialist_name]
        
        # Update state with previous specialists' responses so this specialist can see them
        current_state = {**state, **updates}
        
        response = agent.process(current_state)
        
        if response:  # Only update if specialist returned something
            updates[f"{specialist_name}_response"] = response
            print(f"[COORDINATOR] {specialist_name.upper()} completed with confidence: {response.get('confidence', 0):.2f}")
        else:
            print(f"[COORDINATOR] {specialist_name.upper()} returned empty response")
    
    print(f"\n[COORDINATOR] All {len(active_specialists)} specialists completed")
    
    return updates


def build_collaborative_graph(llm: LLM) -> Any:
    """Build the collaborative multi-agent graph with dynamic routing"""
    
    # Initialize agents
    router = RouterAgent(llm)
    consensus = ConsensusAgent(llm)
    
    # Build graph
    g = StateGraph(CollabState)
    
    # Add nodes
    g.add_node("router", lambda s: router.process(s))
    g.add_node("tools", lambda s: tools_node(s, llm))
    g.add_node("specialists", lambda s: specialist_coordinator(s, llm))
    g.add_node("consensus", lambda s: consensus.process(s))
    
    # Define linear flow - simple and efficient
    g.set_entry_point("router")
    g.add_edge("router", "tools")
    g.add_edge("tools", "specialists")
    g.add_edge("specialists", "consensus")
    g.add_edge("consensus", END)
    
    return g.compile()


def run_collaborative_graph(llm: LLM, user_msg: str) -> Dict[str, Any]:
    """Run the collaborative multi-agent system"""
    print(f"\n{'='*70}")
    print(f"COLLABORATIVE MULTI-AGENT SYSTEM")
    print(f"{'='*70}")
    print(f"Query: {user_msg}")
    
    app = build_collaborative_graph(llm)
    result = app.invoke({"user_msg": user_msg})
    
    print(f"\n{'='*70}")
    print(f"PROCESSING SUMMARY")
    print(f"{'='*70}")
    
    # Summary of what happened
    routing = result.get("routing", {})
    primary = routing.get("primary", "N/A")
    consult = routing.get("consult", [])
    print(f"\nRouting Decision:")
    print(f"  Primary: {primary}")
    print(f"  Consult: {consult if consult else 'None'}")
    print(f"  Reasoning: {routing.get('reasoning', 'N/A')}")
    
    print(f"\nSpecialist Responses:")
    for domain in ["cardiology", "diabetes", "hypertension"]:
        resp = result.get(f"{domain}_response", {})
        if resp:
            print(f"  ✓ {domain.upper()}: Processed (confidence: {resp.get('confidence', 0):.2%})")
            if resp.get('recommendations'):
                print(f"    Recommendations: {len(resp.get('recommendations', []))}")
        else:
            print(f"  ✗ {domain.upper()}: Not consulted")
    
    consensus = result.get("consensus", {})
    print(f"\nConsensus:")
    print(f"  Agreement Level: {consensus.get('specialist_agreement', 'N/A')}")
    print(f"  Critical Alerts: {len(consensus.get('critical_alerts', []))}")
    print(f"  Confidence: {consensus.get('confidence', 0):.2%}")
    
    print(f"\n{'='*70}\n")
    
    return result