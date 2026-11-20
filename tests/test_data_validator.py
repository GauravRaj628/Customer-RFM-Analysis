"""
tests/test_data_validator.py — Unit tests for data validation and quality reporting.
Customer RFM Analysis
"""

import pytest
import pandas as pd
from src.data_validator import validate_data
from src.config import (
    COL_TRANSACTION_ID,
    COL_CUSTOMER_ID,
    COL_ORDER_ID,
    COL_DATE,
    COL_AMOUNT,
    COL_STATUS,
    COL_QUANTITY,
)


def test_validate_all_valid(sample_valid_df):
    """Verify that a clean dataset produces 100% valid records."""
    valid_df, invalid_df, report = validate_data(sample_valid_df)
    assert len(valid_df) == len(sample_valid_df)
    assert len(invalid_df) == 0
    assert report["data_quality_score"] == 100.0
    assert report["invalid_records"] == 0
    assert "validation_issue" not in valid_df.columns


def test_validate_negative_amount(sample_valid_df):
    """Verify that non-positive amounts are moved to invalid_df."""
    df = sample_valid_df.copy()
    df.loc[0, COL_AMOUNT] = -50.0
    df.loc[1, COL_AMOUNT] = 0.0

    valid_df, invalid_df, report = validate_data(df)
    assert len(valid_df) == len(df) - 2
    assert len(invalid_df) == 2
    assert any("Invalid or non-positive amount" in issue for issue in invalid_df["validation_issue"])


def test_validate_null_date(sample_valid_df):
    """Verify that null/NaT dates are flagged."""
    df = sample_valid_df.copy()
    df.loc[0, COL_DATE] = pd.NaT

    valid_df, invalid_df, report = validate_data(df)
    assert len(valid_df) == len(df) - 1
    assert len(invalid_df) == 1
    assert "Missing or unparseable date" in invalid_df["validation_issue"].iloc[0]


def test_validate_zero_or_negative_quantity(sample_valid_df):
    """Verify that quantity < 1 is flagged."""
    df = sample_valid_df.copy()
    df.loc[0, COL_QUANTITY] = 0
    df.loc[1, COL_QUANTITY] = -2

    valid_df, invalid_df, report = validate_data(df)
    assert len(valid_df) == len(df) - 2
    assert len(invalid_df) == 2
    assert all("Quantity less than 1 or missing" in issue for issue in invalid_df["validation_issue"])


def test_validate_missing_customer_id(sample_valid_df):
    """Verify that blank or null customer IDs are flagged."""
    df = sample_valid_df.copy()
    df.loc[0, COL_CUSTOMER_ID] = None
    df.loc[1, COL_CUSTOMER_ID] = "   "

    valid_df, invalid_df, report = validate_data(df)
    assert len(valid_df) == len(df) - 2
    assert len(invalid_df) == 2
    assert all("Missing customer identifier" in issue for issue in invalid_df["validation_issue"])


def test_validate_missing_order_id(sample_valid_df):
    """Verify that missing order IDs are flagged."""
    df = sample_valid_df.copy()
    df.loc[0, COL_ORDER_ID] = None

    valid_df, invalid_df, report = validate_data(df)
    assert len(valid_df) == len(df) - 1
    assert len(invalid_df) == 1
    assert "Missing order identifier" in invalid_df["validation_issue"].iloc[0]


def test_validate_invalid_status(sample_valid_df):
    """Verify that cancelled, returned, or pending statuses are flagged."""
    df = sample_valid_df.copy()
    df.loc[0, COL_STATUS] = "returned"
    df.loc[1, COL_STATUS] = "cancelled"

    valid_df, invalid_df, report = validate_data(df)
    assert len(valid_df) == len(df) - 2
    assert len(invalid_df) == 2
    assert all("Invalid transaction status" in issue for issue in invalid_df["validation_issue"])


def test_validate_mixed_dataset(sample_mixed_df):
    """Verify accurate split and quality reporting on mixed dataset."""
    valid_df, invalid_df, report = validate_data(sample_mixed_df)
    assert len(valid_df) == 10
    assert len(invalid_df) == 2
    assert report["total_records"] == 12
    assert report["valid_records"] == 10
    assert report["invalid_records"] == 2
    assert report["data_quality_score"] == round((10 / 12) * 100, 2)


def test_validate_empty_dataframe():
    """Verify that an empty DataFrame is handled without error."""
    empty_df = pd.DataFrame()
    valid_df, invalid_df, report = validate_data(empty_df)
    assert valid_df.empty
    assert invalid_df.empty
    assert report["total_records"] == 0
    assert report["data_quality_score"] == 100.0


def test_quality_report_structure(sample_mixed_df):
    """Verify keys and structure in the quality report."""
    _, _, report = validate_data(sample_mixed_df)
    assert "total_records" in report
    assert "valid_records" in report
    assert "invalid_records" in report
    assert "data_quality_score" in report
    assert "issue_breakdown" in report
    assert "issue_summary" in report
    assert "column_completeness" in report
    assert isinstance(report["issue_summary"], list)
