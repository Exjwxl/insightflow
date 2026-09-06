from typing import Dict, Any, List
import pandas as pd
import numpy as np
from app.tools.database import db_manager

class DatasetProfiler:
    """Profiles datasets to extract comprehensive column metadata, stats, types, and quality alerts."""
    
    @staticmethod
    def profile_table(table_name: str) -> Dict[str, Any]:
        info = db_manager.get_table_info(table_name)
        total_rows = info["row_count"]
        
        # Pull a rich sample or full dataframe if reasonable
        sample_query = f"SELECT * FROM {table_name} LIMIT 10000;"
        sample_res = db_manager.execute_query(sample_query)
        df = pd.DataFrame(sample_res["data"])
        
        if df.empty:
            return {
                "table_name": table_name,
                "total_rows": total_rows,
                "total_columns": len(info["columns"]),
                "columns": {},
                "numeric_columns": [],
                "categorical_columns": [],
                "date_columns": [],
                "quality_alerts": ["Table contains 0 rows."]
            }
            
        columns_meta = {}
        numeric_cols = []
        categorical_cols = []
        date_cols = []
        quality_alerts = []
        
        for col in df.columns:
            series = df[col]
            null_count = int(series.isnull().sum())
            null_pct = round((null_count / len(series)) * 100, 2)
            unique_count = int(series.nunique())
            inferred_type = "string"
            col_stats = {
                "null_count": null_count,
                "null_percentage": null_pct,
                "unique_values": unique_count,
                "sample_values": [str(x) for x in series.dropna().unique()[:5]]
            }
            
            # Check date
            is_date = False
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    pd.to_datetime(series.dropna().iloc[:50])
                    is_date = True
                except Exception:
                    pass
                    
            if is_date:
                inferred_type = "date"
                date_cols.append(col)
                valid_dates = pd.to_datetime(series.dropna(), errors='coerce').dropna()
                if not valid_dates.empty:
                    col_stats["min_date"] = str(valid_dates.min())
                    col_stats["max_date"] = str(valid_dates.max())
            elif pd.api.types.is_numeric_dtype(series):
                inferred_type = "numeric"
                numeric_cols.append(col)
                non_null = series.dropna()
                if not non_null.empty:
                    col_stats["min"] = float(round(non_null.min(), 4))
                    col_stats["max"] = float(round(non_null.max(), 4))
                    col_stats["mean"] = float(round(non_null.mean(), 4))
                    col_stats["median"] = float(round(non_null.median(), 4))
                    col_stats["std"] = float(round(non_null.std(), 4)) if len(non_null) > 1 else 0.0
            else:
                inferred_type = "categorical"
                categorical_cols.append(col)
                top_values = series.value_counts().head(5).to_dict()
                col_stats["top_categories"] = {str(k): int(v) for k, v in top_values.items()}
                
            col_stats["data_type"] = inferred_type
            columns_meta[col] = col_stats
            
            if null_pct > 0.0:
                quality_alerts.append(f"Column '{col}' has {null_count} missing values ({null_pct}%).")
                
        return {
            "table_name": table_name,
            "total_rows": total_rows,
            "total_columns": len(columns_meta),
            "columns": columns_meta,
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "date_columns": date_cols,
            "quality_alerts": quality_alerts
        }

dataset_profiler = DatasetProfiler()
