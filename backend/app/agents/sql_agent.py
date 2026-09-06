import json
from typing import Dict, Any
from app.graph.state import AnalystState
from app.services.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

def sql_agent_node(state: AnalystState) -> dict:
    """
    Generates tailored, read-only DuckDB SQL queries based on current state,
    target metrics, date periods, or active dimension drilldown.
    """
    question = state.get("question", "")
    table_name = state.get("table_name", "sales")
    schema = state.get("schema_metadata", {})
    current_step = state.get("current_step", 1)
    target_metric = state.get("target_metric", "revenue")
    target_date_col = state.get("target_date_col")
    dims = state.get("dimensions_to_explore", [])
    validation_err = state.get("sql_validation_error")
    
    columns_info = "\n".join([f"- {col}: {meta.get('data_type')}" for col, meta in schema.get("columns", {}).items()])
    
    # Active dimension for this step
    active_dim = None
    if current_step > 1 and len(dims) >= (current_step - 1):
        active_dim = dims[current_step - 2]
        
    llm = get_llm(temperature=0.0)
    
    generated_sql = None
    
    if llm:
        system_prompt = (
            "You are an expert SQL Engineer for DuckDB. Your task is to write a single, read-only SELECT SQL query "
            "to answer the question or investigate a specific sub-dimension.\n\n"
            "STRICT RULES:\n"
            "1. ONLY use valid DuckDB SQL syntax.\n"
            "2. Read-only queries only (SELECT, WITH, GROUP BY, ORDER BY).\n"
            "3. Use DATE_TRUNC('month', <date_col>) or strftime(<date_col>, '%Y-%m') when grouping by month.\n"
            "4. NEVER use DROP, DELETE, UPDATE, INSERT, ALTER.\n"
            "5. Return ONLY the raw SQL string inside a ```sql code block. No additional commentary."
        )
        
        user_prompt = (
            f"Table: {table_name}\n"
            f"Columns:\n{columns_info}\n\n"
            f"User Question: \"{question}\"\n"
            f"Current Investigation Step {current_step}: " + 
            (f"Analyze {target_metric} grouped by {active_dim}" if active_dim else f"Analyze overall aggregate and time trend for {target_metric}") + "\n"
        )
        
        if validation_err:
            user_prompt += f"\nPREVIOUS QUERY FAILED VALIDATION WITH ERROR:\n{validation_err}\nPlease FIX the query.\n"
            
        try:
            resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
            text = resp.content.strip()
            if "```sql" in text:
                text = text.split("```sql")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            generated_sql = text
        except Exception as e:
            print(f"SQL Agent LLM fallback: {e}")

    # Deterministic fallback generator if LLM is unavailable or for standard analytical questions
    if not generated_sql:
        if active_dim:
            generated_sql = f"""SELECT 
    {active_dim},
    ROUND(SUM({target_metric}), 2) AS total_{target_metric},
    ROUND(AVG({target_metric}), 2) AS avg_{target_metric},
    COUNT(*) AS transaction_count
FROM {table_name}
GROUP BY {active_dim}
ORDER BY total_{target_metric} DESC;"""
        elif target_date_col:
            generated_sql = f"""SELECT 
    strftime(CAST({target_date_col} AS DATE), '%Y-%m') AS month,
    ROUND(SUM({target_metric}), 2) AS total_{target_metric},
    COUNT(*) AS total_orders
FROM {table_name}
GROUP BY month
ORDER BY month ASC;"""
        else:
            generated_sql = f"""SELECT 
    ROUND(SUM({target_metric}), 2) AS total_{target_metric},
    ROUND(AVG({target_metric}), 2) AS avg_{target_metric},
    COUNT(*) AS total_records
FROM {table_name};"""
            
    log_entry = f"✓ SQL Agent (Step {current_step}): Generated DuckDB query for " + (f"dimension '{active_dim}'" if active_dim else "time series trend")
    
    return {
        "current_sql": generated_sql,
        "logs": [log_entry]
    }
