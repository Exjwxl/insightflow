from typing import List, Dict, Any
from app.graph.state import AnalystState
from app.tools.charts import chart_generator

def visualization_agent_node(state: AnalystState) -> dict:
    """
    Selects optimal chart types and formats responsive Plotly specifications
    for all investigation steps.
    """
    investigations = state.get("investigations", [])
    target_metric = state.get("target_metric", "revenue")
    charts = []
    
    for inv in investigations:
        result = inv.get("query_result", {})
        data = result.get("data", [])
        cols = result.get("columns", [])
        dim = inv.get("dimension")
        
        if not data or len(cols) < 2:
            continue
            
        # Determine best chart type
        if "month" in cols or any("date" in c for c in cols):
            date_col = next(c for c in cols if "month" in c or "date" in c)
            metric_col = next((c for c in cols if c != date_col and "count" not in c), cols[-1])
            chart = chart_generator.create_plotly_spec(
                data=data,
                chart_type="line",
                x_col=date_col,
                y_col=metric_col,
                title=f"Monthly {target_metric.replace('_', ' ').title()} Trend"
            )
            charts.append(chart)
        elif dim and dim in cols:
            metric_col = next((c for c in cols if c != dim and "count" not in c), cols[-1])
            # For 4 or fewer categories, also include donut or bar
            chart = chart_generator.create_plotly_spec(
                data=data[:10],
                chart_type="bar",
                x_col=dim,
                y_col=metric_col,
                title=f"{target_metric.replace('_', ' ').title()} by {dim.replace('_', ' ').title()}"
            )
            charts.append(chart)
            
    log_entry = f"✓ Visualization Agent: Generated {len(charts)} Plotly visualizations"
    
    return {
        "visualizations": charts,
        "logs": [log_entry]
    }
