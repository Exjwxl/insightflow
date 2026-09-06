from typing import Dict, Any, List, Optional
import pandas as pd

class ChartGenerator:
    """Generates structured Plotly chart specifications (data and layout) from query results."""
    
    @staticmethod
    def create_plotly_spec(
        data: List[Dict[str, Any]], 
        chart_type: str, 
        x_col: str, 
        y_col: str, 
        title: str,
        color_col: Optional[str] = None,
        orientation: str = "v"
    ) -> Dict[str, Any]:
        """
        Creates a Plotly JSON-compatible spec with dark/modern theme colors.
        chart_type: 'line', 'bar', 'scatter', 'pie', 'donut', 'area'
        """
        if not data:
            return {"error": "No data available to create chart"}
            
        df = pd.DataFrame(data)
        if x_col not in df.columns or y_col not in df.columns:
            return {"error": f"Columns {x_col} or {y_col} not in data"}
            
        # Color palette for modern dark UI
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4', '#f97316']
        
        traces = []
        
        if color_col and color_col in df.columns:
            # Grouped traces by color column
            for i, (group_name, group_df) in enumerate(df.groupby(color_col)):
                color = colors[i % len(colors)]
                trace = ChartGenerator._build_trace(
                    group_df, chart_type, x_col, y_col, str(group_name), color, orientation
                )
                traces.append(trace)
        else:
            trace = ChartGenerator._build_trace(
                df, chart_type, x_col, y_col, y_col, colors[0], orientation
            )
            traces.append(trace)
            
        layout = {
            "title": {
                "text": title,
                "font": {"size": 16, "color": "#f3f4f6", "family": "Inter, sans-serif"}
            },
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"color": "#9ca3af", "family": "Inter, sans-serif"},
            "xaxis": {
                "title": x_col.replace('_', ' ').title(),
                "gridcolor": "#1f2937",
                "linecolor": "#374151",
                "zerolinecolor": "#1f2937"
            },
            "yaxis": {
                "title": y_col.replace('_', ' ').title(),
                "gridcolor": "#1f2937",
                "linecolor": "#374151",
                "zerolinecolor": "#1f2937"
            },
            "legend": {
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1
            },
            "margin": {"l": 50, "r": 30, "t": 60, "b": 50},
            "hovermode": "closest"
        }
        
        if chart_type in ['pie', 'donut']:
            layout.pop("xaxis", None)
            layout.pop("yaxis", None)
            
        return {
            "chart_type": chart_type,
            "title": title,
            "spec": {
                "data": traces,
                "layout": layout
            }
        }
        
    @staticmethod
    def _build_trace(
        df: pd.DataFrame, 
        chart_type: str, 
        x_col: str, 
        y_col: str, 
        name: str, 
        color: str,
        orientation: str
    ) -> Dict[str, Any]:
        x_data = df[x_col].tolist()
        y_data = df[y_col].tolist()
        
        if chart_type == "line":
            return {
                "type": "scatter",
                "mode": "lines+markers",
                "x": x_data,
                "y": y_data,
                "name": name,
                "line": {"color": color, "width": 3, "shape": "spline"},
                "marker": {"size": 6, "color": color}
            }
        elif chart_type == "area":
            return {
                "type": "scatter",
                "mode": "lines",
                "fill": "tozeroy",
                "x": x_data,
                "y": y_data,
                "name": name,
                "line": {"color": color, "width": 2.5},
                "fillcolor": f"{color}33"  # semi-transparent
            }
        elif chart_type == "bar":
            if orientation == "h":
                return {
                    "type": "bar",
                    "orientation": "h",
                    "x": y_data,
                    "y": x_data,
                    "name": name,
                    "marker": {"color": color, "opacity": 0.85}
                }
            return {
                "type": "bar",
                "x": x_data,
                "y": y_data,
                "name": name,
                "marker": {"color": color, "opacity": 0.85, "cornerradius": 4}
            }
        elif chart_type in ["pie", "donut"]:
            hole = 0.5 if chart_type == "donut" else 0
            return {
                "type": "pie",
                "labels": x_data,
                "values": y_data,
                "hole": hole,
                "name": name,
                "textinfo": "label+percent"
            }
        elif chart_type == "scatter":
            return {
                "type": "scatter",
                "mode": "markers",
                "x": x_data,
                "y": y_data,
                "name": name,
                "marker": {"size": 8, "color": color, "opacity": 0.8}
            }
        return {
            "type": "bar",
            "x": x_data,
            "y": y_data,
            "name": name,
            "marker": {"color": color}
        }

chart_generator = ChartGenerator()
