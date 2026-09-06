from typing import Dict, Any, List, Optional, TypedDict, Annotated
import operator

class InvestigationStep(TypedDict, total=False):
    step_num: int
    goal: str
    dimension: Optional[str]
    sql_query: str
    is_valid: bool
    validation_error: Optional[str]
    query_result: Optional[Dict[str, Any]]
    findings: Optional[Dict[str, Any]]
    interpretation: Optional[str]

class AnalystState(TypedDict, total=False):
    # Context
    question: str
    table_name: str
    schema_metadata: Dict[str, Any]
    quality_alerts: List[str]
    
    # Planning
    plan: Dict[str, Any]
    target_metric: Optional[str]
    target_date_col: Optional[str]
    dimensions_to_explore: List[str]
    
    # Iterative Multi-step Investigation
    current_step: int
    max_steps: int
    investigations: Annotated[List[InvestigationStep], operator.add]
    
    # Active SQL & Result for current step
    current_sql: Optional[str]
    sql_is_valid: bool
    sql_validation_error: Optional[str]
    current_result: Optional[Dict[str, Any]]
    
    # Error recovery & retry
    retry_count: int
    max_retries: int
    
    # Statistical computation & Visualizations
    computed_metrics: Dict[str, Any]
    visualizations: List[Dict[str, Any]]
    
    # Validation & Final Synthesis
    validation_status: str  # "PASSED", "RETRY_REQUIRED", "FAILED"
    validation_feedback: Optional[str]
    report: Dict[str, Any]  # Executive summary, findings table, drivers, recommendations
    
    # Streaming progress trace
    logs: Annotated[List[str], operator.add]
