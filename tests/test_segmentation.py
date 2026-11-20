"""
tests/test_segmentation.py — Unit tests for customer segmentation and cohort analysis.
Customer RFM Analysis
"""

import pytest
import pandas as pd
from src.segmentation import (
    assign_segments,
    compute_segment_summary,
    compute_revenue_by_segment,
    compute_cohort_revenue,
    _map_rfm_score_to_segment,
)
from src.rfm_calculator import calculate_rfm, score_rfm
from src.config import SEGMENT_ORDER, SEGMENT_COLOURS, COL_AMOUNT


def test_map_rfm_score_boundaries():
    """Verify exact mapping boundaries for all 5 customer segments."""
    # 13–15 : Champions
    assert _map_rfm_score_to_segment(15) == "Champions"
    assert _map_rfm_score_to_segment(14) == "Champions"
    assert _map_rfm_score_to_segment(13) == "Champions"

    # 10–12 : Loyal Customers
    assert _map_rfm_score_to_segment(12) == "Loyal Customers"
    assert _map_rfm_score_to_segment(11) == "Loyal Customers"
    assert _map_rfm_score_to_segment(10) == "Loyal Customers"

    # 7–9 : Potential Loyalists
    assert _map_rfm_score_to_segment(9) == "Potential Loyalists"
    assert _map_rfm_score_to_segment(8) == "Potential Loyalists"
    assert _map_rfm_score_to_segment(7) == "Potential Loyalists"

    # 4–6 : At-Risk Customers
    assert _map_rfm_score_to_segment(6) == "At-Risk Customers"
    assert _map_rfm_score_to_segment(5) == "At-Risk Customers"
    assert _map_rfm_score_to_segment(4) == "At-Risk Customers"

    # 3 : Lost Customers
    assert _map_rfm_score_to_segment(3) == "Lost Customers"


def test_assign_segments_coverage(sample_valid_df):
    """
    CRITICAL BUSINESS RULE:
    Every eligible customer must receive exactly ONE segment (no nulls).
    """
    rfm = calculate_rfm(sample_valid_df)
    scored = score_rfm(rfm)
    segmented = assign_segments(scored)

    assert len(segmented) == len(rfm)
    assert "customer_segment" in segmented.columns
    assert segmented["customer_segment"].isna().sum() == 0
    assert set(segmented["customer_segment"]).issubset(set(SEGMENT_ORDER))


def test_assign_segments_colors(sample_valid_df):
    """Verify segment colors match configured brand definitions."""
    rfm = calculate_rfm(sample_valid_df)
    scored = score_rfm(rfm)
    segmented = assign_segments(scored)

    for _, row in segmented.iterrows():
        expected_color = SEGMENT_COLOURS[row["customer_segment"]]
        assert row["segment_color"] == expected_color


def test_compute_segment_summary_dimensions(sample_valid_df):
    """Verify summary table contains all 5 approved segments in standard order."""
    rfm = calculate_rfm(sample_valid_df)
    scored = score_rfm(rfm)
    segmented = assign_segments(scored)
    summary = compute_segment_summary(segmented)

    assert len(summary) == 5
    assert list(summary["customer_segment"]) == SEGMENT_ORDER
    assert summary["customer_count"].sum() == len(segmented)


def test_compute_segment_summary_percentages(sample_valid_df):
    """Verify customer and revenue share percentages sum to 100%."""
    rfm = calculate_rfm(sample_valid_df)
    scored = score_rfm(rfm)
    segmented = assign_segments(scored)
    summary = compute_segment_summary(segmented)

    assert pytest.approx(summary["customer_percentage"].sum(), 0.1) == 100.0
    assert pytest.approx(summary["revenue_percentage"].sum(), 0.1) == 100.0


def test_compute_segment_summary_empty():
    """Verify that an empty DataFrame produces empty summary safely."""
    summary = compute_segment_summary(pd.DataFrame())
    assert summary.empty
    assert "customer_segment" in summary.columns


def test_compute_revenue_by_segment(sample_valid_df):
    """Verify revenue aggregation across monthly periods and segments."""
    rfm = calculate_rfm(sample_valid_df)
    scored = score_rfm(rfm)
    segmented = assign_segments(scored)
    seg_rev = compute_revenue_by_segment(segmented, sample_valid_df)

    assert isinstance(seg_rev, pd.DataFrame)
    assert "year_month" in seg_rev.columns
    assert "customer_segment" in seg_rev.columns
    assert "revenue" in seg_rev.columns
    assert round(seg_rev["revenue"].sum(), 2) == round(sample_valid_df[COL_AMOUNT].sum(), 2)


def test_compute_cohort_revenue(sample_valid_df):
    """Verify customer cohort matrix construction and total revenue."""
    cohort_matrix = compute_cohort_revenue(sample_valid_df)
    assert isinstance(cohort_matrix, pd.DataFrame)
    assert 0 in cohort_matrix.columns  # Acquisition month index 0
    # Total revenue in cohort matrix matches valid transactions
    matrix_sum = cohort_matrix.values.sum()
    expected_sum = sample_valid_df[COL_AMOUNT].sum()
    assert pytest.approx(matrix_sum, 0.01) == expected_sum
