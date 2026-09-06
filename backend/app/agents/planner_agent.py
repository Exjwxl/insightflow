import json
from typing import Dict, Any, List
from app.graph.state import AnalystState
from app.services.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

def planner_agent_node(state: AnalystState) -> dict:
    """
    Decomposes the user business question into analytical intent,
    identifies key metrics, date columns, and relevant breakdown dimensions.
    """
    question = state.get("question", "")
    schema = state.get("schema_metadata", {})
    table_name = state.get("table_name", "sales")
    
    numeric_cols = schema.get("numeric_columns", [])
    cat_cols = schema.get("categorical_columns", [])
    date_cols = schema.get("date_columns", [])
    
    llm = get_llm(temperature=0.1)
    
    # Heuristic fallback if no LLM key provided or for rapid deterministic planning
    default_metric = "revenue" if "revenue" in numeric_cols else (numeric_cols[0] if numeric_cols else "count")
    default_date = date_cols[0] if date_cols else None
    default_dims = cat_cols[:3] if cat_cols else []
    
    plan = {
        "intent": "exploratory_analysis",
        "primary_metric": default_metric,
        "date_column": default_date,
        "dimensions": default_dims,
        "steps": [
            f"Calculate aggregate trends for '{default_metric}'" + (f" over time using '{default_date}'" if default_date else ""),
            f"Segment breakdown by key dimensions ({', '.join(default_dims)})" if default_dims else "Aggregate summary"
        ]
    }
    
    if llm:
        system_prompt = (
            "You are the Lead Planning Agent for InsightFlow. Your job is to dissect a business question "
            "and create a step-by-step hypothesis investigation plan based strictly on the available columns.\n"
            "Return ONLY valid JSON matching this schema:\n"
            "{\n"
            "  \"intent\": \"root_cause_analysis\" | \"aggregation\" | \"time_series\" | \"comparison\" | \"anomaly\",\n"
            "  \"primary_metric\": \"column_name\",\n"
            "  \"date_column\": \"column_name\" or null,\n"
            "  \"dimensions\": [\"col1\", \"col2\"],\n"
            "  \"steps\": [\"step 1 description\", \"step 2 description\"]\n"
            "}"
        )
        
        user_prompt = (
            f"Dataset: '{table_name}'\n"
            f"Numeric columns: {numeric_cols}\n"
            f"Categorical columns: {cat_cols}\n"
            f"Date columns: {date_cols}\n\n"
            f"User Question: \"{question}\"\n\n"
            "Generate the investigation plan in pure JSON."
        )
        
        try:
            response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
            text = response.content.strip()
            if text.startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
            if "primary_metric" in parsed:
                plan = parsed
        except Exception as e:
            print(f"LLM planner fallback used: {e}")
            
    log_entry = f"✓ Planner Agent: Goal identified as '{plan.get('intent')}' targeting metric '{plan.get('primary_metric')}' across dimensions {plan.get('dimensions')}"
    
    return {
        "plan": plan,
        "target_metric": plan.get("primary_metric"),
        "target_date_col": plan.get("date_column"),
        "dimensions_to_explore": plan.get("dimensions", []),
        "current_step": 1,
        "max_steps": len(plan.get("dimensions", [])) + 1,
        "retry_count": 0,
        "max_retries": 3,
        "logs": [log_entry]
    }
