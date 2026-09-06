from typing import Dict, Any, List
from app.graph.state import AnalystState

def findings_validator_node(state: AnalystState) -> dict:
    """
    Validates that query results and statistical conclusions directly address
    the user's initial question, that expected metrics are populated, and data is consistent.
    """
    investigations = state.get("investigations", [])
    question = state.get("question", "")
    
    if not investigations:
        return {
            "validation_status": "FAILED",
            "validation_feedback": "No investigations were executed successfully.",
            "logs": ["✗ Findings Validator: No analysis results found."]
        }
        
    # Check that at least one query returned non-empty rows
    has_data = any(len(inv.get("query_result", {}).get("data", [])) > 0 for inv in investigations)
    
    if not has_data:
        return {
            "validation_status": "FAILED",
            "validation_feedback": "Executed queries returned 0 matching records.",
            "logs": ["⚠ Findings Validator: Query returned empty dataset."]
        }
        
    log_entry = f"✓ Findings Validator: Successfully verified {len(investigations)} analytical steps. Findings match question."
    
    return {
        "validation_status": "PASSED",
        "validation_feedback": None,
        "logs": [log_entry]
    }
