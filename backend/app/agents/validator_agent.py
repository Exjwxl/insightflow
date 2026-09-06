from app.graph.state import AnalystState
from app.tools.sql_validator import sql_validator
from app.tools.database import db_manager

def validator_agent_node(state: AnalystState) -> dict:
    """
    Validates SQL using SQLGlot AST parser for security, syntax, and schema correctness.
    If valid, executes the query in DuckDB.
    If invalid or fails execution, sets state to trigger self-correction retry loop.
    """
    sql = state.get("current_sql", "")
    available_tables = db_manager.list_tables()
    current_retries = state.get("retry_count", 0)
    
    is_valid, error_msg, metadata = sql_validator.validate(sql, allowed_tables=available_tables)
    
    if not is_valid:
        log_entry = f"⚠ SQL Validator: Query rejected ({error_msg}). Triggering self-correction loop (Attempt {current_retries + 1})."
        return {
            "sql_is_valid": False,
            "sql_validation_error": error_msg,
            "retry_count": current_retries + 1,
            "logs": [log_entry]
        }
        
    # Execute query in DuckDB
    exec_result = db_manager.execute_query(sql)
    
    if not exec_result["success"]:
        err = exec_result.get("error", "Execution failed")
        log_entry = f"⚠ Execution Engine: Query failed during execution ({err}). Triggering self-correction."
        return {
            "sql_is_valid": False,
            "sql_validation_error": err,
            "retry_count": current_retries + 1,
            "logs": [log_entry]
        }
        
    log_entry = f"✓ SQL Validator & Execution: Query validated and executed successfully ({exec_result['row_count']} rows returned)"
    
    return {
        "sql_is_valid": True,
        "sql_validation_error": None,
        "current_result": exec_result,
        "logs": [log_entry]
    }
