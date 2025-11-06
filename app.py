import streamlit as st
from typing import Dict, Any
from config.llm_config import LLMConfig
from core.llm import LLM
from graph.builder import run_collaborative_graph
from utils.formatters import format_specialist_response


# Page config
st.set_page_config(
    page_title="Multi-Agent Medical AI",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

if 'llm_config' not in st.session_state:
    st.session_state.llm_config = None


def render_sidebar():
    """Render configuration sidebar"""
    st.sidebar.title("Configuration")
    
    provider = st.sidebar.selectbox(
        "LLM Provider",
        ["ollama", "vllm"],
        help="Choose your LLM backend"
    )
    
    if provider == "ollama":
        model = st.sidebar.text_input(
            "Model Name",
            value="qwen2.5:1.5b-instruct",
            help="Ollama model name"
        )
        endpoint = st.sidebar.text_input(
            "Endpoint",
            value="http://localhost:11434",
            help="Ollama API endpoint"
        )
    else:  # vllm
        model = st.sidebar.text_input(
            "Model Name",
            value="your-7b-checkpoint",
            help="vLLM model name"
        )
        endpoint = st.sidebar.text_input(
            "Endpoint",
            value="http://localhost:8000/v1",
            help="vLLM API endpoint"
        )
    
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
        help="Model temperature"
    )
    
    max_tokens = st.sidebar.number_input(
        "Max Tokens",
        min_value=256,
        max_value=4096,
        value=1024,
        step=256,
        help="Maximum tokens in response"
    )
    
    if st.sidebar.button("Apply Configuration"):
        st.session_state.llm_config = LLMConfig(
            provider=provider,
            model=model,
            endpoint=endpoint,
            temperature=temperature,
            max_tokens=max_tokens
        )
        st.sidebar.success("Configuration updated!")
    
    # Sample queries
    st.sidebar.markdown("---")
    st.sidebar.subheader("Sample Queries")
    
    samples = [
        "58yo male, HTN with T2D (A1c 8.5%) and eGFR 55. First-line therapy?",
        "65yo female with stable angina, HTN 150/90, on metoprolol. Reports fatigue.",
        "52yo male, T2D, A1c 9.2%, BMI 32, history of MI. Currently on metformin only.",
        "Patient on lisinopril 20mg, started spironolactone. K+ now 5.8.",
        "45yo African American male, newly diagnosed HTN 165/95, no other conditions.",
        "72yo with HTN and T2D, BP 185/110, chest discomfort, troponin elevation."
    ]
    
    for idx, sample in enumerate(samples):
        if st.sidebar.button(f"Sample {idx + 1}", key=f"sample_{idx}"):
            st.session_state.current_query = sample


def render_routing_info(result: Dict[str, Any]):
    """Render routing information"""
    routing = result.get("routing", {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Handle both string and list for primary
        primary = routing.get("primary", "N/A")
        if isinstance(primary, list):
            primary_display = ", ".join([p.title() for p in primary])
        elif isinstance(primary, str):
            primary_display = primary.title()
        else:
            primary_display = "N/A"
        
        st.metric("Primary Specialist", primary_display)
    
    with col2:
        consult = routing.get("consult", [])
        if not isinstance(consult, list):
            consult = [consult] if consult else []
        st.metric("Additional Consults", len(consult))
    
    with col3:
        urgency = routing.get("urgency", "routine")
        if isinstance(urgency, str):
            urgency_display = urgency.title()
        else:
            urgency_display = str(urgency).title()
        st.metric("Urgency Level", urgency_display)
    
    # Display consult specialists if any
    if consult:
        consult_list = ", ".join([c.title() for c in consult])
        st.info(f"Additional Specialists Consulted: {consult_list}")
    
    if routing.get("reasoning"):
        st.info(f"Reasoning: {routing['reasoning']}")


def render_specialist_tabs(result: Dict[str, Any]):
    """Render specialist responses in tabs"""
    tabs = st.tabs(["Cardiology", "Diabetes", "Hypertension"])
    
    domains = ["cardiology", "diabetes", "hypertension"]
    
    for tab, domain in zip(tabs, domains):
        with tab:
            response = result.get(f"{domain}_response", {})
            
            if not response:
                st.warning(f"{domain.title()} specialist was not consulted for this query.")
                continue
            
            # Assessment
            st.subheader("Assessment")
            st.write(response.get("assessment", "No assessment provided"))
            
            # Recommendations
            if response.get("recommendations"):
                st.subheader("Recommendations")
                for rec in response["recommendations"]:
                    st.markdown(f"- {rec}")
            
            # Concerns
            if response.get("concerns"):
                st.subheader("Concerns")
                for concern in response["concerns"]:
                    st.warning(concern)
            
            # Contraindications
            if response.get("contraindications"):
                st.subheader("Contraindications")
                for contra in response["contraindications"]:
                    st.error(contra)
            
            # Metadata
            col1, col2 = st.columns(2)
            with col1:
                confidence = response.get('confidence', 0)
                # Handle confidence as either float or string
                if isinstance(confidence, (int, float)):
                    confidence_display = f"{confidence:.0%}"
                else:
                    try:
                        confidence_display = f"{float(confidence):.0%}"
                    except (ValueError, TypeError):
                        confidence_display = str(confidence)
                st.metric("Confidence", confidence_display)
            with col2:
                citations = response.get("citations", [])
                if not isinstance(citations, list):
                    citations = []
                st.metric("Citations", len(citations))


def render_consensus(result: Dict[str, Any]):
    """Render consensus recommendations"""
    consensus = result.get("consensus", {})
    
    if not consensus:
        st.warning("No consensus reached")
        return
    
    # Final Assessment
    st.subheader("Final Assessment")
    st.write(consensus.get("final_assessment", "No assessment provided"))
    
    # Agreement Level
    agreement = consensus.get("specialist_agreement", "unknown")
    if isinstance(agreement, str):
        agreement_display = agreement.lower()
    else:
        agreement_display = "unknown"
    
    color = {"high": "green", "medium": "orange", "low": "red"}.get(agreement_display, "gray")
    st.markdown(f"**Specialist Agreement:** :{color}[{agreement_display.title()}]")
    
    # Unified Plan
    if consensus.get("unified_plan"):
        st.subheader("Unified Care Plan")
        unified_plan = consensus["unified_plan"]
        if isinstance(unified_plan, list):
            for idx, step in enumerate(unified_plan, 1):
                st.markdown(f"{idx}. {step}")
        else:
            st.write(unified_plan)
    
    # Critical Alerts
    if consensus.get("critical_alerts"):
        st.subheader("Critical Alerts")
        critical_alerts = consensus["critical_alerts"]
        if isinstance(critical_alerts, list):
            for alert in critical_alerts:
                st.error(alert)
        else:
            st.error(critical_alerts)
    
    # Conflicts Resolved
    if consensus.get("conflicts_resolved"):
        st.subheader("Conflicts Resolved")
        conflicts = consensus["conflicts_resolved"]
        if isinstance(conflicts, list):
            for conflict in conflicts:
                st.info(conflict)
        else:
            st.info(conflicts)
    
    # Next Steps
    if consensus.get("next_steps"):
        st.subheader("Next Steps")
        next_steps = consensus["next_steps"]
        if isinstance(next_steps, list):
            for step in next_steps:
                st.markdown(f"- {step}")
        else:
            st.markdown(f"- {next_steps}")
    
    # Confidence
    confidence = consensus.get('confidence', 0)
    if isinstance(confidence, (int, float)):
        confidence_display = f"{confidence:.0%}"
    else:
        try:
            confidence_display = f"{float(confidence):.0%}"
        except (ValueError, TypeError):
            confidence_display = str(confidence)
    st.metric("Overall Confidence", confidence_display)


def render_tool_results(result: Dict[str, Any]):
    """Render tool execution results"""
    tool_results = result.get("tool_results", [])
    
    if not tool_results:
        st.info("No tools were executed")
        return
    
    for idx, tool_result in enumerate(tool_results, 1):
        with st.expander(f"Tool {idx}: {tool_result.get('tool', 'Unknown')}"):
            st.json(tool_result.get("output", {}))


def main():
    """Main application"""
    st.title("Multi-Agent Medical AI System")
    st.markdown("Collaborative clinical decision support with specialist agents")
    
    # Sidebar
    render_sidebar()
    
    # Check if config is set
    if st.session_state.llm_config is None:
        st.warning("Please configure the LLM settings in the sidebar")
        st.session_state.llm_config = LLMConfig.ollama_default()
    
    # Query input
    query = st.text_area(
        "Enter Clinical Query",
        value=st.session_state.get('current_query', ''),
        height=100,
        placeholder="Example: 58yo male, new HTN diagnosis with T2D (A1c 8.5%) and eGFR 55. What's first-line therapy?"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        analyze_button = st.button("Analyze", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("Clear History", use_container_width=True)
    
    if clear_button:
        st.session_state.history = []
        st.rerun()
    
    if analyze_button and query:
        with st.spinner("Analyzing query with multi-agent system..."):
            try:
                # Initialize LLM
                llm = LLM(st.session_state.llm_config)
                
                # Run graph
                result = run_collaborative_graph(llm, query)
                
                # Add to history
                st.session_state.history.append({
                    "query": query,
                    "result": result
                })
                
                # Display results
                st.success("Analysis complete!")
                
                # Routing Info
                st.markdown("---")
                st.header("Routing Decision")
                render_routing_info(result)
                
                # Specialist Responses
                st.markdown("---")
                st.header("Specialist Assessments")
                render_specialist_tabs(result)
                
                # Consensus
                st.markdown("---")
                st.header("Consensus Recommendations")
                render_consensus(result)
                
                # Tool Results (collapsed by default)
                st.markdown("---")
                with st.expander("View Tool Execution Details"):
                    render_tool_results(result)
                
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.exception(e)
    
    # History
    if st.session_state.history:
        st.markdown("---")
        st.header("Query History")
        
        for idx, item in enumerate(reversed(st.session_state.history), 1):
            with st.expander(f"Query {len(st.session_state.history) - idx + 1}: {item['query'][:100]}..."):
                st.markdown(f"**Query:** {item['query']}")
                
                consensus = item['result'].get('consensus', {})
                if consensus.get('final_assessment'):
                    st.markdown("**Assessment:**")
                    st.write(consensus['final_assessment'])
                
                if consensus.get('unified_plan'):
                    st.markdown("**Plan:**")
                    unified_plan = consensus['unified_plan']
                    if isinstance(unified_plan, list):
                        for step in unified_plan:
                            st.markdown(f"- {step}")
                    else:
                        st.markdown(f"- {unified_plan}")


if __name__ == "__main__":
    main()