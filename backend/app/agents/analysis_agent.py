from typing import Dict, Any, List
from app.graph.state import AnalystState, InvestigationStep
from app.tools.statistics import statistical_engine
from app.services.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

def analysis_agent_node(state: AnalystState) -> dict:
    """
    Computes exact deterministic statistics (MoM growth, contributions, anomalies) using Pandas,
    then uses LLM for natural-language interpretation of the computed findings.
    """
    exec_result = state.get("current_result", {})
    data = exec_result.get("data", [])
    cols = exec_result.get("columns", [])
    current_step = state.get("current_step", 1)
    target_metric = state.get("target_metric", "revenue")
    dims = state.get("dimensions_to_explore", [])
    
    active_dim = None
    if current_step > 1 and len(dims) >= (current_step - 1):
        active_dim = dims[current_step - 2]
        
    stat_findings = {}
    
    # 1. Exact deterministic computation
    if "month" in cols or "order_date" in cols or any("date" in c for c in cols):
        date_col = next(c for c in cols if "month" in c or "date" in c)
        metric_col = next((c for c in cols if c != date_col and "count" not in c), cols[-1])
        stat_findings["time_series"] = statistical_engine.calculate_period_over_period(data, date_col, metric_col)
    elif active_dim and active_dim in cols:
        metric_col = next((c for c in cols if c != active_dim and "count" not in c), cols[-1])
        stat_findings["breakdown"] = statistical_engine.calculate_dimension_breakdown(data, active_dim, metric_col)
        
    # Anomaly detection if numeric series available
    if len(cols) >= 2 and len(data) >= 4:
        key_c = cols[0]
        val_c = cols[1]
        anomalies = statistical_engine.detect_anomalies(data, key_c, val_c)
        if anomalies.get("anomalies_found", 0) > 0:
            stat_findings["anomalies"] = anomalies
            
    # 2. LLM Interpretation of computed exact statistics
    interpretation = ""
    llm = get_llm(temperature=0.2)
    
    if llm and stat_findings:
        system_prompt = (
            "You are a Senior Quantitative Data Analyst. You are given exact computed statistical results. "
            "Write a concise, high-impact 2-3 sentence business takeaway explaining what the numbers mean. "
            "Do NOT recalculate or invent numbers. Use the exact numbers provided."
        )
        user_prompt = f"Computed statistics for Step {current_step}:\n{stat_findings}\nData sample:\n{data[:5]}"
        try:
            resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
            interpretation = resp.content.strip()
        except Exception as e:
            print(f"Analysis Agent LLM fallback: {e}")
            
    if not interpretation:
        if "time_series" in stat_findings:
            ts = stat_findings["time_series"]
            pct = ts.get("latest_pct_change")
            period = ts.get("latest_period")
            val = ts.get("latest_value")
            interpretation = f"In {period}, {target_metric} was ${val:,.2f}, representing a {pct:+.1f}% change compared to the preceding period."
        elif "breakdown" in stat_findings:
            bd = stat_findings["breakdown"]
            top = bd.get("top_contributor")
            if top:
                interpretation = f"{top['dimension']} is the leading driver, contributing ${top['value']:,.2f} ({top['share_pct']}% of total)."
        else:
            interpretation = f"Analyzed {len(data)} records across {cols}."

    # Record investigation step
    step_record: InvestigationStep = {
        "step_num": current_step,
        "goal": f"Investigate {active_dim}" if active_dim else f"Analyze overall {target_metric} trend",
        "dimension": active_dim,
        "sql_query": state.get("current_sql", ""),
        "is_valid": True,
        "validation_error": None,
        "query_result": exec_result,
        "findings": stat_findings,
        "interpretation": interpretation
    }
    
    log_entry = f"✓ Analysis Agent (Step {current_step}): Computed exact statistics & business takeaway for " + (f"'{active_dim}'" if active_dim else "baseline metric")
    
    return {
        "investigations": [step_record],
        "current_step": current_step + 1,
        "logs": [log_entry]
    }
