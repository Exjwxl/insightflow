import pytest
from app.tools.sql_validator import sql_validator

def test_valid_select_queries():
    valid_queries = [
        "SELECT * FROM sales;",
        "SELECT region, SUM(revenue) FROM sales GROUP BY region;",
        "SELECT order_date, revenue FROM sales WHERE revenue > 1000 ORDER BY order_date DESC;",
        "WITH monthly AS (SELECT strftime(order_date, '%Y-%m') as m, SUM(revenue) as rev FROM sales GROUP BY m) SELECT * FROM monthly;"
    ]
    for q in valid_queries:
        is_valid, err, meta = sql_validator.validate(q, allowed_tables=["sales"])
        assert is_valid is True, f"Query failed validation unexpectedly: {q}, Error: {err}"

def test_reject_dangerous_sql_injection():
    malicious_queries = [
        "DROP TABLE sales;",
        "DELETE FROM sales WHERE region = 'North';",
        "UPDATE sales SET revenue = 0;",
        "INSERT INTO sales VALUES (1, 2, 3);",
        "ALTER TABLE sales DROP COLUMN revenue;",
        "TRUNCATE TABLE sales;",
        "SELECT * FROM sales; DROP TABLE users;"
    ]
    for q in malicious_queries:
        is_valid, err, meta = sql_validator.validate(q, allowed_tables=["sales"])
        assert is_valid is False, f"Malicious query was not rejected: {q}"

def test_unknown_table_rejected():
    q = "SELECT * FROM secret_passwords;"
    is_valid, err, meta = sql_validator.validate(q, allowed_tables=["sales"])
    assert is_valid is False
    assert "does not exist in active dataset schema" in err
