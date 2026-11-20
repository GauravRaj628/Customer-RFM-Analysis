"""
tests/test_rfm_calculator.py — Unit tests for RFM calculation and scoring.
Customer RFM Analysis
"""

import pytest
import pandas as pd
from datetime import date
from src.rfm_calculator import calculate_rfm, score_rfm, compute_rfm_summary
from src.config import COL_AMOUNT


def test_calculate_rfm_dimensions(sample_valid_df, reference_date):
    """Verify that calculate_rfm produces exactly one row per customer."""
    rfm = calculate_rfm(sample_valid_df, reference_date=reference_date)
    assert len(rfm) == 3
    assert set(rfm["customer_id"]) == {"CUST0001", "CUST0002", "CUST0003"}


def test_calculate_rfm_frequency_distinct_orders(sample_valid_df, reference_date):
    """
    CRITICAL BUSINESS RULE:
    Frequency must count DISTINCT Order IDs, NOT transaction rows.
    CUST0001 placed 4 transactions across 3 distinct orders (ORD00001 twice, ORD00002, ORD00003).
    """
    rfm = calculate_rfm(sample_valid_df, reference_date=reference_date)
    cust1 = rfm[rfm["customer_id"] == "CUST0001"].iloc[0]
    assert cust1["frequency"] == 3  # Not 4!


def test_calculate_rfm_monetary_sum(sample_valid_df, reference_date):
    """Verify that Monetary sums valid transaction amounts accurately."""
    rfm = calculate_rfm(sample_valid_df, reference_date=reference_date)
    cust1 = rfm[rfm["customer_id"] == "CUST0001"].iloc[0]
    expected_spend = sample_valid_df[sample_valid_df["customer_id"] == "CUST0001"][COL_AMOUNT].sum()
    assert cust1["monetary"] == round(expected_spend, 2)


def test_calculate_rfm_recency_days(sample_valid_df):
    """Verify Recency is calculated correctly against a specified reference date."""
    ref = date(2024, 7, 6)
    rfm = calculate_rfm(sample_valid_df, reference_date=ref)
    # CUST0002 latest purchase was 2024-07-05 -> recency = 1 day
    cust2 = rfm[rfm["customer_id"] == "CUST0002"].iloc[0]
    assert cust2["recency_days"] == 1


def test_calculate_rfm_default_reference_date(sample_valid_df):
    """Verify default reference date is automatically max date + 1 day."""
    rfm = calculate_rfm(sample_valid_df)
    # Max valid date in sample is 2024-07-05 -> default ref is 2024-07-06
    # So customer with purchase on 2024-07-05 should have recency 1 day
    min_recency = rfm["recency_days"].min()
    assert min_recency == 1


def test_calculate_rfm_activity_bands(sample_valid_df):
    """Verify activity band assignments: Recent (<=30), At-risk (31-90), Inactive (>90)."""
    ref = date(2024, 7, 6)
    rfm = calculate_rfm(sample_valid_df, reference_date=ref)
    bands = dict(zip(rfm["customer_id"], rfm["activity_band"]))

    # CUST0002 latest: 2024-07-05 -> 1 day -> Recent
    assert bands["CUST0002"] == "Recent"
    # CUST0001 latest: 2024-06-10 -> 26 days -> Recent
    assert bands["CUST0001"] == "Recent"
    # CUST0003 latest: 2024-05-15 -> 52 days -> At-risk
    assert bands["CUST0003"] == "At-risk"


def test_score_rfm_score_ranges(sample_valid_df):
    """Verify all individual scores are integers between 1 and 5."""
    rfm = calculate_rfm(sample_valid_df)
    scored = score_rfm(rfm)
    for col in ["r_score", "f_score", "m_score"]:
        assert scored[col].between(1, 5).all()


def test_score_rfm_reverse_recency():
    """Verify that customers with LOWER recency days receive HIGHER R_Scores."""
    dummy_rfm = pd.DataFrame({
        "customer_id": [f"C{i}" for i in range(1, 6)],
        "recency_days": [5, 20, 60, 120, 300],  # strictly increasing days
        "frequency": [5, 4, 3, 2, 1],
        "monetary": [5000, 4000, 3000, 2000, 1000],
    })
    scored = score_rfm(dummy_rfm)
    # Lowest recency (5 days) should have highest R score (5)
    assert scored.loc[scored["recency_days"] == 5, "r_score"].iloc[0] == 5
    # Highest recency (300 days) should have lowest R score (1)
    assert scored.loc[scored["recency_days"] == 300, "r_score"].iloc[0] == 1


def test_score_rfm_composite_sum(sample_valid_df):
    """Verify composite RFM score sum and cell concatenation string."""
    rfm = calculate_rfm(sample_valid_df)
    scored = score_rfm(rfm)
    for _, row in scored.iterrows():
        expected_sum = row["r_score"] + row["f_score"] + row["m_score"]
        assert row["rfm_score"] == expected_sum
        assert row["rfm_cell"] == f"{row['r_score']}{row['f_score']}{row['m_score']}"


def test_calculate_rfm_empty_input():
    """Verify calculate_rfm handles empty DataFrames safely."""
    empty_rfm = calculate_rfm(pd.DataFrame())
    assert empty_rfm.empty
    assert "recency_days" in empty_rfm.columns
    assert "frequency" in empty_rfm.columns
    assert "monetary" in empty_rfm.columns


def test_compute_rfm_summary_metrics(sample_valid_df):
    """Verify summary calculations over scored RFM DataFrame."""
    rfm = calculate_rfm(sample_valid_df)
    scored = score_rfm(rfm)
    summary = compute_rfm_summary(scored)
    assert summary["total_customers"] == 3
    assert summary["avg_recency_days"] > 0
    assert summary["avg_frequency"] > 0
    assert summary["avg_monetary"] > 0
    assert "activity_distribution" in summary
