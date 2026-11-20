"""
src/data_loader.py — Data loading and preprocessing module.
Customer RFM Analysis

Responsible for ingesting transaction data from CSV or Excel files,
performing initial data type parsing, and providing high-level dataset summaries.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import pandas as pd

from src.config import (
    COL_TRANSACTION_ID,
    COL_CUSTOMER_ID,
    COL_ORDER_ID,
    COL_DATE,
    COL_AMOUNT,
    COL_STATUS,
    COL_QUANTITY,
    COL_UNIT_PRICE,
    REQUIRED_COLUMNS,
)


def load_data(source: str | Path | Any) -> pd.DataFrame:
    """
    Load retail transaction dataset from CSV or Excel file or file buffer.

    Parameters
    ----------
    source : str | Path | Any
        Path to the transaction data file or a file-like buffer (e.g. UploadedFile).

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized column names and initial parsed dtypes.

    Raises
    ------
    FileNotFoundError
        If the given filepath does not exist.
    ValueError
        If the file format is unsupported or required columns are missing.
    """
    if hasattr(source, "name") and not isinstance(source, (str, Path)):
        # Streamlit UploadedFile or file-like buffer
        filename = getattr(source, "name", "").lower()
        if filename.endswith(".csv"):
            df = pd.read_csv(source)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(source)
        else:
            raise ValueError(
                f"Unsupported file format '{filename}'. Supported formats: .csv, .xlsx, .xls"
            )
    else:
        path = Path(source)
        if not path.is_file():
            raise FileNotFoundError(f"Dataset file not found: {path.resolve()}")

        suffix = path.suffix.lower()
        if suffix == ".csv":
            df = pd.read_csv(path)
        elif suffix in (".xlsx", ".xls"):
            df = pd.read_excel(path)
        else:
            raise ValueError(
                f"Unsupported file format '{suffix}'. Supported formats: .csv, .xlsx, .xls"
            )

    # 1. Normalize column names (strip whitespace and convert to lowercase)
    df.columns = [str(col).strip().lower() for col in df.columns]

    # 2. Check for required core columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Dataset is missing required columns: {missing_cols}. "
            f"Present columns: {list(df.columns)}"
        )

    # 3. Clean and parse date column
    if COL_DATE in df.columns:
        df[COL_DATE] = pd.to_datetime(df[COL_DATE], errors="coerce")

    # 4. Standardize numeric columns
    numeric_cols = [COL_AMOUNT, COL_UNIT_PRICE, COL_QUANTITY]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 5. Clean string/categorical columns (strip whitespace, normalize casing)
    string_cols = [COL_TRANSACTION_ID, COL_CUSTOMER_ID, COL_ORDER_ID, COL_STATUS]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def get_dataset_summary(df: pd.DataFrame) -> dict[str, Any]:
    """
    Compute descriptive metadata summary of the raw loaded dataset.

    Parameters
    ----------
    df : pd.DataFrame
        The loaded transactions DataFrame.

    Returns
    -------
    dict[str, Any]
        Dictionary of dataset metrics including row counts, unique entities,
        date span, and missing value totals.
    """
    if df.empty:
        return {
            "total_rows": 0,
            "total_columns": 0,
            "unique_customers": 0,
            "unique_orders": 0,
            "min_date": None,
            "max_date": None,
            "total_gross_amount": 0.0,
            "missing_values_count": 0,
            "columns": list(df.columns),
        }

    # Extract date ranges safely
    min_date = None
    max_date = None
    if COL_DATE in df.columns:
        valid_dates = df[COL_DATE].dropna()
        if not valid_dates.empty:
            min_date = valid_dates.min().strftime("%Y-%m-%d")
            max_date = valid_dates.max().strftime("%Y-%m-%d")

    unique_custs = int(df[COL_CUSTOMER_ID].nunique()) if COL_CUSTOMER_ID in df.columns else 0
    unique_orders = int(df[COL_ORDER_ID].nunique()) if COL_ORDER_ID in df.columns else 0
    gross_amount = (
        float(df[COL_AMOUNT].dropna().sum()) if COL_AMOUNT in df.columns else 0.0
    )

    return {
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "unique_customers": unique_custs,
        "unique_orders": unique_orders,
        "min_date": min_date,
        "max_date": max_date,
        "total_gross_amount": round(gross_amount, 2),
        "missing_values_count": int(df.isnull().sum().sum()),
        "columns": list(df.columns),
    }
