"""
tests/test_eda.py — Unit tests for exploratory data analysis module.
Customer RFM Analysis
"""

import pytest
import pandas as pd
from src.eda import (
    compute_summary_stats,
    compute_monthly_revenue,
    compute_category_breakdown,
    compute_top_customers,
    compute_transaction_distribution,
    compute_regional_breakdown,
    compute_payment_method_breakdown,
)
from src.config import COL_AMOUNT


def test_compute_summary_stats(sample_valid_df):
    """Verify that summary statistics calculate accurately."""
    stats = compute_summary_stats(sample_valid_df)
    assert stats["total_transactions"] == 10
    assert stats["total_customers"] == 3
    assert stats["total_orders"] == 7
    assert stats["total_gross_revenue"] == round(sample_valid_df[COL_AMOUNT].sum(), 2)
    assert stats["mean_transaction_value"] == round(sample_valid_df[COL_AMOUNT].mean(), 2)
    assert stats["min_transaction_value"] == round(sample_valid_df[COL_AMOUNT].min(), 2)
    assert stats["max_transaction_value"] == round(sample_valid_df[COL_AMOUNT].max(), 2)


def test_compute_summary_stats_empty():
    """Verify that an empty DataFrame returns zeroed summary metrics."""
    stats = compute_summary_stats(pd.DataFrame())
    assert stats["total_transactions"] == 0
    assert stats["total_gross_revenue"] == 0.0
    assert stats["mean_transaction_value"] == 0.0


def test_compute_monthly_revenue(sample_valid_df):
    """Verify monthly aggregation of revenue and distinct counts."""
    monthly = compute_monthly_revenue(sample_valid_df)
    assert isinstance(monthly, pd.DataFrame)
    assert "year_month" in monthly.columns
    assert "revenue" in monthly.columns
    assert "order_count" in monthly.columns
    assert "avg_order_value" in monthly.columns
    assert round(monthly["revenue"].sum(), 2) == round(sample_valid_df[COL_AMOUNT].sum(), 2)


def test_compute_category_breakdown(sample_valid_df):
    """Verify category grouping, descending revenue sort, and percentages."""
    cat_df = compute_category_breakdown(sample_valid_df)
    assert isinstance(cat_df, pd.DataFrame)
    assert len(cat_df) > 0
    # Check descending sort
    assert cat_df["total_revenue"].is_monotonic_decreasing
    # Check percentage sum equals 100% (within float tolerance)
    assert pytest.approx(cat_df["revenue_percentage"].sum(), 0.1) == 100.0


def test_compute_top_customers(sample_valid_df):
    """Verify top customer ranking and spend ordering."""
    top_custs = compute_top_customers(sample_valid_df, n=2)
    assert len(top_custs) == 2
    assert top_custs["total_spend"].iloc[0] >= top_custs["total_spend"].iloc[1]
    assert "customer_name" in top_custs.columns
    assert "latest_purchase_date" in top_custs.columns


def test_compute_transaction_distribution(sample_valid_df):
    """Verify amount binning and percentage sums."""
    dist_df = compute_transaction_distribution(sample_valid_df, bins=5)
    assert isinstance(dist_df, pd.DataFrame)
    assert "bin_range" in dist_df.columns
    assert "count" in dist_df.columns
    assert dist_df["count"].sum() == len(sample_valid_df)
    assert pytest.approx(dist_df["percentage"].sum(), 0.1) == 100.0


def test_compute_regional_breakdown(sample_valid_df):
    """Verify geographic breakdown calculation."""
    reg_df = compute_regional_breakdown(sample_valid_df)
    assert isinstance(reg_df, pd.DataFrame)
    assert "store_region" in reg_df.columns
    assert "revenue_share" in reg_df.columns
    assert pytest.approx(reg_df["revenue_share"].sum(), 0.1) == 100.0


def test_compute_payment_method_breakdown(sample_valid_df):
    """Verify payment channel shares."""
    pay_df = compute_payment_method_breakdown(sample_valid_df)
    assert isinstance(pay_df, pd.DataFrame)
    assert "payment_method" in pay_df.columns
    assert "percentage_amount" in pay_df.columns
    assert pytest.approx(pay_df["percentage_amount"].sum(), 0.1) == 100.0
