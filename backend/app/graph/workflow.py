from langgraph.graph import StateGraph, END
from app.graph.state import AnalystState
from app.agents.schema_agent import schema_profiler_node
from app.agents.planner_agent import planner_agent_node
from app.agents.sql_agent import sql_agent_node
from app.agents.validator_agent import validator_agent_node
from app.agents.analysis_agent import analysis_agent_node
from app.agents.visualization_agent import visualization_agent_node
from app.agents.findings_validator import findings_validator_node
from app.agents.report_agent import report_agent_node

def check_sql_validity(state: AnalystState) -> str:
    """Branching condition after SQL Validator."""
    if not state.get("sql_is_valid", False):
        if state.get("retry_count", 0) < state.get("max_retries", 3):
            return "retry_sql"
        # If max retries reached, proceed to next step to avoid infinite loop
        return "analysis"
    return "analysis"

def check_investigation_progress(state: AnalystState) -> str:
    """Determines whether more drill-down investigation steps are needed."""
    current_step = state.get("current_step", 1)
    max_steps = state.get("max_steps", 1)
    
    if current_step <= max_steps:
        return "continue_investigation"
    return "visualize"

def create_analyst_graph():
    """Builds and compiles the full stateful LangGraph multi-agent workflow."""
    workflow = StateGraph(AnalystState)
    
    # Register agent nodes
    workflow.add_node("schema_profiler", schema_profiler_node)
    workflow.add_node("planner", planner_agent_node)
    workflow.add_node("sql_generator", sql_agent_node)
    workflow.add_node("validator", validator_agent_node)
    workflow.add_node("analysis", analysis_agent_node)
    workflow.add_node("visualization", visualization_agent_node)
    workflow.add_node("findings_validator", findings_validator_node)
    workflow.add_node("reporter", report_agent_node)
    
    # Set Entrypoint
    workflow.set_entry_point("schema_profiler")
    
    # Linear transitions
    workflow.add_edge("schema_profiler", "planner")
    workflow.add_edge("planner", "sql_generator")
    workflow.add_edge("sql_generator", "validator")
    
    # Conditional edge for SQL self-correction loop
    workflow.add_conditional_edges(
        "validator",
        check_sql_validity,
        {
            "retry_sql": "sql_generator",
            "analysis": "analysis"
        }
    )
    
    # Conditional edge for multi-step autonomous investigation
    workflow.add_conditional_edges(
        "analysis",
        check_investigation_progress,
        {
            "continue_investigation": "sql_generator",
            "visualize": "visualization"
        }
    )
    
    workflow.add_edge("visualization", "findings_validator")
    workflow.add_edge("findings_validator", "reporter")
    workflow.add_edge("reporter", END)
    
    return workflow.compile()

analyst_app = create_analyst_graph()
