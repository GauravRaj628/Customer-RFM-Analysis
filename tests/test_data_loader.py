"""
tests/test_data_loader.py — Unit tests for data loading module.
Customer RFM Analysis
"""

import pytest
import pandas as pd
from pathlib import Path
from src.data_loader import load_data, get_dataset_summary
from src.config import (
    DEFAULT_DATASET_PATH,
    COL_TRANSACTION_ID,
    COL_CUSTOMER_ID,
    COL_ORDER_ID,
    COL_DATE,
    COL_AMOUNT,
    COL_STATUS,
)


def test_load_data_success():
    """Verify that the synthetic dataset loads successfully with correct dimensions."""
    df = load_data(DEFAULT_DATASET_PATH)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5000
    assert COL_TRANSACTION_ID in df.columns
    assert COL_CUSTOMER_ID in df.columns
    assert COL_ORDER_ID in df.columns
    assert COL_DATE in df.columns
    assert COL_AMOUNT in df.columns
    assert COL_STATUS in df.columns


def test_load_data_file_not_found():
    """Verify that a non-existent filepath raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_data("data/non_existent_file.csv")


def test_load_data_unsupported_format(tmp_path):
    """Verify that unsupported extensions raise ValueError."""
    fake_file = tmp_path / "test.txt"
    fake_file.write_text("hello,world")
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_data(fake_file)


def test_load_data_missing_required_columns(tmp_path):
    """Verify that missing required columns raise ValueError."""
    incomplete_csv = tmp_path / "bad.csv"
    incomplete_csv.write_text("transaction_id,customer_id\nTXN1,CUST1\n")
    with pytest.raises(ValueError, match="Dataset is missing required columns"):
        load_data(incomplete_csv)


def test_load_data_date_parsing(tmp_path):
    """Verify that transaction_date is correctly converted to datetime objects."""
    custom_csv = tmp_path / "custom.csv"
    custom_csv.write_text(
        "transaction_id,customer_id,order_id,transaction_date,transaction_amount,transaction_status\n"
        "TXN001,CUST001,ORD001,2024-05-10,1200.50,completed\n"
        "TXN002,CUST002,ORD002,invalid_date,500.00,completed\n"
    )
    df = load_data(custom_csv)
    assert pd.api.types.is_datetime64_any_dtype(df[COL_DATE])
    assert df[COL_DATE].iloc[0] == pd.Timestamp("2024-05-10")
    assert pd.isna(df[COL_DATE].iloc[1])  # 'invalid_date' coerced to NaT


def test_load_data_whitespace_stripping(tmp_path):
    """Verify that extra spaces around column names and string values are stripped."""
    spaced_csv = tmp_path / "spaced.csv"
    spaced_csv.write_text(
        " transaction_id , customer_id , order_id , transaction_date , transaction_amount , transaction_status \n"
        " TXN001 , CUST001 , ORD001 , 2024-01-01 , 100.0 , completed \n"
    )
    df = load_data(spaced_csv)
    assert "transaction_id" in df.columns
    assert df[COL_CUSTOMER_ID].iloc[0] == "CUST001"
    assert df[COL_STATUS].iloc[0] == "completed"


def test_get_dataset_summary_valid(sample_valid_df):
    """Verify that get_dataset_summary produces accurate metrics."""
    summary = get_dataset_summary(sample_valid_df)
    assert summary["total_rows"] == 10
    assert summary["unique_customers"] == 3
    assert summary["unique_orders"] == 7
    assert summary["min_date"] == "2023-11-01"
    assert summary["max_date"] == "2024-07-05"
    assert summary["total_gross_amount"] == round(sample_valid_df[COL_AMOUNT].sum(), 2)


def test_get_dataset_summary_empty():
    """Verify that get_dataset_summary handles empty DataFrames safely."""
    empty_df = pd.DataFrame()
    summary = get_dataset_summary(empty_df)
    assert summary["total_rows"] == 0
    assert summary["unique_customers"] == 0
    assert summary["min_date"] is None
    assert summary["total_gross_amount"] == 0.0
