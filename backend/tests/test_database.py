import pytest
from app.tools.database import db_manager
from app.tools.profiler import dataset_profiler

def test_database_table_listing():
    tables = db_manager.list_tables()
    assert "sales" in tables

def test_database_query_execution():
    result = db_manager.execute_query("SELECT COUNT(*) AS total_rows FROM sales")
    assert result["row_count"] == 1
    assert result["data"][0]["total_rows"] >= 100000

def test_dataset_profiler():
    profile = dataset_profiler.profile_table("sales")
    assert profile["table_name"] == "sales"
    assert profile["total_rows"] >= 100000
    assert "revenue" in profile["columns"]
    assert "revenue" in profile["numeric_columns"]
    assert "order_date" in profile["date_columns"]
