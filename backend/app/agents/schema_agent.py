from app.graph.state import AnalystState
from app.tools.profiler import dataset_profiler
from app.tools.database import db_manager

def schema_profiler_node(state: AnalystState) -> dict:
    """
    Analyzes and registers the active dataset schema, column data types,
    sample values, and data health alerts into the agent state.
    """
    table_name = state.get("table_name") or "sales"
    available_tables = db_manager.list_tables()
    
    if table_name not in available_tables and available_tables:
        table_name = available_tables[0]
        
    profile = dataset_profiler.profile_table(table_name)
    
    log_entry = f"✓ Schema Profiler: Ingested table '{table_name}' ({profile['total_rows']:,} rows, {profile['total_columns']} columns)"
    
    return {
        "table_name": table_name,
        "schema_metadata": profile,
        "quality_alerts": profile.get("quality_alerts", []),
        "logs": [log_entry]
    }
