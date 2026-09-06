import pytest
from app.graph.workflow import analyst_app

def test_full_analyst_workflow_execution():
    initial_state = {
        "question": "Why did revenue decrease in August?",
        "table_name": "sales",
        "logs": [],
        "investigations": []
    }
    
    final_state = analyst_app.invoke(initial_state)
    
    assert final_state["table_name"] == "sales"
    assert "plan" in final_state
    assert len(final_state.get("investigations", [])) > 0
    assert len(final_state.get("visualizations", [])) > 0
    assert "report" in final_state
    assert "executive_summary" in final_state["report"]
    assert len(final_state["report"]["recommendations"]) > 0
