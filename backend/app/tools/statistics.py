from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

class StatisticalEngine:
    """
    Deterministic mathematical and statistical engine using Pandas / NumPy.
    Used by the Analysis Agent to eliminate LLM arithmetic hallucinations.
    """
    
    @staticmethod
    def calculate_period_over_period(
        data: List[Dict[str, Any]], 
        date_col: str, 
        metric_col: str
    ) -> Dict[str, Any]:
        """Calculates exact period-over-period differences and growth rates."""
        if not data:
            return {"error": "Empty dataset provided"}
            
        df = pd.DataFrame(data)
        if date_col not in df.columns or metric_col not in df.columns:
            return {"error": f"Columns {date_col} or {metric_col} not found in query results"}
            
        df[metric_col] = pd.to_numeric(df[metric_col], errors='coerce')
        df = df.dropna(subset=[date_col, metric_col]).sort_values(by=date_col)
        
        df['previous_value'] = df[metric_col].shift(1)
        df['absolute_change'] = df[metric_col] - df['previous_value']
        df['pct_change'] = (df['absolute_change'] / df['previous_value']) * 100.0
        
        periods = []
        for _, row in df.iterrows():
            periods.append({
                "period": str(row[date_col]),
                "value": float(round(row[metric_col], 2)),
                "previous_value": float(round(row['previous_value'], 2)) if pd.notnull(row['previous_value']) else None,
                "absolute_change": float(round(row['absolute_change'], 2)) if pd.notnull(row['absolute_change']) else None,
                "pct_change": float(round(row['pct_change'], 2)) if pd.notnull(row['pct_change']) else None
            })
            
        latest = periods[-1] if periods else {}
        return {
            "metric": metric_col,
            "periods": periods,
            "latest_period": latest.get("period"),
            "latest_value": latest.get("value"),
            "latest_pct_change": latest.get("pct_change"),
            "latest_absolute_change": latest.get("absolute_change")
        }

    @staticmethod
    def calculate_dimension_breakdown(
        data: List[Dict[str, Any]], 
        dimension_col: str, 
        metric_col: str
    ) -> Dict[str, Any]:
        """Calculates share and contribution of segments/dimensions."""
        if not data:
            return {"error": "Empty dataset provided"}
            
        df = pd.DataFrame(data)
        if dimension_col not in df.columns or metric_col not in df.columns:
            return {"error": f"Columns {dimension_col} or {metric_col} not found in query results"}
            
        df[metric_col] = pd.to_numeric(df[metric_col], errors='coerce')
        df = df.dropna(subset=[dimension_col, metric_col])
        
        total = df[metric_col].sum()
        df['share_pct'] = (df[metric_col] / total * 100.0) if total != 0 else 0.0
        df = df.sort_values(by=metric_col, ascending=False)
        
        breakdown = []
        for _, row in df.iterrows():
            breakdown.append({
                "dimension": str(row[dimension_col]),
                "value": float(round(row[metric_col], 2)),
                "share_pct": float(round(row['share_pct'], 2))
            })
            
        return {
            "dimension": dimension_col,
            "metric": metric_col,
            "total": float(round(total, 2)),
            "breakdown": breakdown,
            "top_contributor": breakdown[0] if breakdown else None
        }

    @staticmethod
    def detect_anomalies(
        data: List[Dict[str, Any]], 
        key_col: str, 
        metric_col: str, 
        threshold_std: float = 2.0
    ) -> Dict[str, Any]:
        """Detects outliers using Z-score calculation."""
        if not data:
            return {"error": "Empty dataset provided"}
            
        df = pd.DataFrame(data)
        if key_col not in df.columns or metric_col not in df.columns:
            return {"error": f"Columns {key_col} or {metric_col} not found in query results"}
            
        df[metric_col] = pd.to_numeric(df[metric_col], errors='coerce')
        df = df.dropna(subset=[key_col, metric_col])
        
        mean_val = df[metric_col].mean()
        std_val = df[metric_col].std()
        
        if std_val == 0 or pd.isnull(std_val):
            return {
                "mean": float(round(mean_val, 2)),
                "std": 0.0,
                "anomalies": []
            }
            
        df['z_score'] = (df[metric_col] - mean_val) / std_val
        anomalies_df = df[df['z_score'].abs() >= threshold_std]
        
        anomalies = []
        for _, row in anomalies_df.iterrows():
            anomalies.append({
                "key": str(row[key_col]),
                "value": float(round(row[metric_col], 2)),
                "z_score": float(round(row['z_score'], 2)),
                "direction": "HIGH" if row['z_score'] > 0 else "LOW"
            })
            
        return {
            "mean": float(round(mean_val, 2)),
            "std": float(round(std_val, 2)),
            "anomalies_found": len(anomalies),
            "anomalies": anomalies
        }

statistical_engine = StatisticalEngine()
