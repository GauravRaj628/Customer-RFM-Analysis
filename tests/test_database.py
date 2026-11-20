"""
tests/test_database.py — Unit tests for SQLite database persistence module.
Customer RFM Analysis
"""

import pytest
import sqlite3
import pandas as pd
from src.database import (
    get_connection,
    init_db,
    log_analysis_run,
    save_rfm_results,
    load_rfm_results,
    save_segment_summary,
    load_segment_summary,
    list_analysis_runs,
)
from src.rfm_calculator import calculate_rfm, score_rfm
from src.segmentation import assign_segments, compute_segment_summary


@pytest.fixture
def in_memory_db():
    """In-memory SQLite database connection fixture initialized with tables."""
    conn = get_connection(":memory:")
    init_db(conn)
    yield conn
    conn.close()


def test_init_db(in_memory_db):
    """Verify that all required tables are successfully created."""
    cursor = in_memory_db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    assert "analysis_runs" in tables
    assert "rfm_results" in tables
    assert "segment_summary" in tables


def test_log_analysis_run(in_memory_db):
    """Verify that an analysis execution run is logged and returns an integer ID."""
    run_id = log_analysis_run(
        in_memory_db,
        reference_date="2024-07-06",
        total_transactions=5000,
        valid_transactions=4600,
        total_customers=531,
        total_revenue=80047642.10,
        notes="Automated test run",
    )
    assert isinstance(run_id, int)
    assert run_id >= 1

    cursor = in_memory_db.cursor()
    cursor.execute("SELECT * FROM analysis_runs WHERE run_id = ?", (run_id,))
    row = cursor.fetchone()
    assert row["total_transactions"] == 5000
    assert row["reference_date"] == "2024-07-06"


def test_save_and_load_rfm_results(in_memory_db, sample_valid_df):
    """Verify persisting and querying customer RFM scores."""
    rfm = calculate_rfm(sample_valid_df)
    scored = score_rfm(rfm)
    segmented = assign_segments(scored)

    run_id = log_analysis_run(
        in_memory_db, "2024-07-06", 10, 10, len(segmented), 100000.0
    )
    save_rfm_results(in_memory_db, segmented, run_id=run_id)

    loaded = load_rfm_results(in_memory_db, run_id=run_id)
    assert len(loaded) == len(segmented)
    assert set(loaded["customer_id"]) == set(segmented["customer_id"])
    assert "customer_segment" in loaded.columns
    assert "rfm_score" in loaded.columns


def test_save_and_load_segment_summary(in_memory_db, sample_valid_df):
    """Verify persisting and querying segment summary performance overview."""
    rfm = calculate_rfm(sample_valid_df)
    scored = score_rfm(rfm)
    segmented = assign_segments(scored)
    summary = compute_segment_summary(segmented)

    run_id = log_analysis_run(
        in_memory_db, "2024-07-06", 10, 10, len(segmented), 100000.0
    )
    save_segment_summary(in_memory_db, summary, run_id=run_id)

    loaded = load_segment_summary(in_memory_db, run_id=run_id)
    assert len(loaded) == 5
    assert set(loaded["customer_segment"]) == set(summary["customer_segment"])
    assert loaded["customer_count"].sum() == len(segmented)


def test_parameterized_query_safety(in_memory_db):
    """Verify SQL injection payloads in customer IDs or names are escaped safely."""
    malicious_id = "CUST'; DROP TABLE rfm_results; --"
    dummy_rfm = pd.DataFrame([{
        "customer_id": malicious_id,
        "customer_name": "Test Injection",
        "recency_days": 10,
        "frequency": 2,
        "monetary": 500.0,
        "r_score": 5,
        "f_score": 4,
        "m_score": 3,
        "rfm_score": 12,
        "rfm_cell": "543",
        "activity_band": "Recent",
        "customer_segment": "Loyal Customers",
    }])

    run_id = log_analysis_run(
        in_memory_db, "2024-07-06", 1, 1, 1, 500.0
    )
    save_rfm_results(in_memory_db, dummy_rfm, run_id=run_id)
    loaded = load_rfm_results(in_memory_db, run_id=run_id)

    # Table must still exist and record retrieved intact
    assert len(loaded) == 1
    assert loaded["customer_id"].iloc[0] == malicious_id


def test_list_analysis_runs(in_memory_db):
    """Verify historical execution runs list ordered newest first."""
    run_1 = log_analysis_run(in_memory_db, "2024-07-01", 100, 90, 50, 1000.0, "Run 1")
    run_2 = log_analysis_run(in_memory_db, "2024-07-02", 150, 140, 75, 2000.0, "Run 2")

    runs = list_analysis_runs(in_memory_db)
    assert len(runs) == 2
    assert runs["run_id"].iloc[0] == run_2
    assert runs["run_id"].iloc[1] == run_1


def test_empty_dataframe_save(in_memory_db):
    """Verify that saving empty DataFrames does not raise exceptions."""
    save_rfm_results(in_memory_db, pd.DataFrame())
    save_segment_summary(in_memory_db, pd.DataFrame())
