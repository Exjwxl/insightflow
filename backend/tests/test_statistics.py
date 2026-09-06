import pytest
from app.tools.statistics import statistical_engine

def test_period_over_period():
    data = [
        {"month": "2025-05", "revenue": 125000.0},
        {"month": "2025-06", "revenue": 109000.0}
    ]
    res = statistical_engine.calculate_period_over_period(data, "month", "revenue")
    assert res["latest_period"] == "2025-06"
    assert res["latest_value"] == 109000.0
    assert round(res["latest_pct_change"], 1) == -12.8

def test_dimension_breakdown():
    data = [
        {"region": "North", "revenue": 50000.0},
        {"region": "South", "revenue": 30000.0},
        {"region": "East", "revenue": 20000.0}
    ]
    res = statistical_engine.calculate_dimension_breakdown(data, "region", "revenue")
    assert res["total"] == 100000.0
    assert res["top_contributor"]["dimension"] == "North"
    assert res["top_contributor"]["share_pct"] == 50.0

def test_anomaly_detection():
    data = [
        {"salesperson": "Sarah", "sales": 1000.0},
        {"salesperson": "Michael", "sales": 1050.0},
        {"salesperson": "David", "sales": 980.0},
        {"salesperson": "Elena", "sales": 1020.0},
        {"salesperson": "Outlier", "sales": 9500.0}
    ]
    res = statistical_engine.detect_anomalies(data, "salesperson", "sales", threshold_std=1.5)
    assert res["anomalies_found"] >= 1
    assert any(a["key"] == "Outlier" for a in res["anomalies"])
