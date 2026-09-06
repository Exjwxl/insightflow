import os
from typing import Dict, Any, List, Optional
import duckdb
import pandas as pd
from app.config.settings import settings

class DatabaseManager:
    """Manages DuckDB in-memory / persistent analytics engine."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DUCKDB_PATH
        # Connect to DuckDB
        self.con = duckdb.connect(database=self.db_path, read_only=False)
        self._load_existing_tables()
        
    def _load_existing_tables(self):
        """Auto-register default sales dataset if present in data directory."""
        sales_csv = os.path.join(settings.DATA_DIR, "sales.csv")
        if os.path.exists(sales_csv):
            try:
                self.register_csv("sales", sales_csv)
            except Exception as e:
                print(f"Warning loading sales.csv into DuckDB: {e}")
                
    def register_csv(self, table_name: str, file_path: str):
        """Creates or replaces a DuckDB table from a CSV file."""
        clean_path = file_path.replace("\\", "/")
        query = f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto('{clean_path}', header=True);"
        self.con.execute(query)
        return self.get_table_info(table_name)
        
    def register_excel(self, table_name: str, file_path: str):
        """Reads Excel file via pandas and loads into DuckDB."""
        df = pd.read_excel(file_path)
        self.con.register('temp_df', df)
        self.con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM temp_df;")
        self.con.unregister('temp_df')
        return self.get_table_info(table_name)

    def register_parquet(self, table_name: str, file_path: str):
        clean_path = file_path.replace("\\", "/")
        query = f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_parquet('{clean_path}');"
        self.con.execute(query)
        return self.get_table_info(table_name)

    def list_tables(self) -> List[str]:
        """Returns list of user tables in the DuckDB instance."""
        res = self.con.execute("SHOW TABLES;").fetchall()
        return [r[0] for r in res]

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Returns column names and types for a given table."""
        desc = self.con.execute(f"DESCRIBE {table_name};").fetchall()
        columns = {col[0]: col[1] for col in desc}
        count = self.con.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
        return {
            "table_name": table_name,
            "row_count": count,
            "columns": columns
        }

    def execute_query(self, sql: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Executes a validated read-only SQL query and returns records and metadata as a dict.
        """
        enforced_limit = limit or settings.MAX_ROW_LIMIT
        
        # Enforce execution timeout via DuckDB pragma if applicable or Python
        try:
            # Wrap query to enforce hard row safety limit if not already present
            clean_sql = sql.strip().rstrip(';')
            limited_sql = f"SELECT * FROM ({clean_sql}) LIMIT {enforced_limit};"
            
            df = self.con.execute(limited_sql).df()
            
            # Convert timestamp/date columns to ISO strings for JSON serialization
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].astype(str)
                    
            records = df.to_dict(orient='records')
            
            return {
                "success": True,
                "sql": sql,
                "columns": list(df.columns),
                "row_count": len(df),
                "data": records,
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
            }
        except Exception as e:
            return {
                "success": False,
                "sql": sql,
                "error": str(e),
                "columns": [],
                "row_count": 0,
                "data": []
            }

db_manager = DatabaseManager()
