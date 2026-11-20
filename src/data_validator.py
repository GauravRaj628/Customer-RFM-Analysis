"""
src/data_validator.py — Data validation and quality assurance module.
Customer RFM Analysis

Implements business validation rules to segment incoming raw transactions into:
1. Valid transactions: Eligible for RFM and revenue calculations.
2. Invalid transactions: Flagged with explicit reasons for audit and reporting.
3. Data quality summary report.
"""

from __future__ import annotations

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
    VALID_STATUSES,
)


def validate_data(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """
    Validate transaction records against approved retail business rules.

    Rules applied:
    - transaction_amount > 0 and not null.
    - transaction_date not null/NaT.
    - quantity >= 1 and not null.
    - customer_id not null and not empty.
    - order_id not null and not empty.
    - transaction_status in VALID_STATUSES ('completed', 'valid').

    Parameters
    ----------
    df : pd.DataFrame
        Loaded transaction DataFrame.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]
        - valid_df: Clean DataFrame containing only eligible transactions.
        - invalid_df: DataFrame containing flagged rows with 'validation_issue' column.
        - quality_report: Dictionary with comprehensive quality statistics.
    """
    if df.empty:
        empty_report: dict[str, Any] = {
            "total_records": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "data_quality_score": 100.0,
            "issue_breakdown": {},
            "issue_summary": [],
            "column_completeness": {},
        }
        return df.copy(), df.copy(), empty_report

    df_working = df.copy()

    # Track list of issue descriptions per row
    issues: list[list[str]] = [[] for _ in range(len(df_working))]

    # 1. Rule: Amount must be > 0 and not null
    amount_series = pd.to_numeric(df_working[COL_AMOUNT], errors="coerce")
    bad_amount_mask = amount_series.isna() | (amount_series <= 0)
    for idx in df_working[bad_amount_mask].index:
        pos = df_working.index.get_loc(idx)
        issues[pos].append("Invalid or non-positive amount")

    # 2. Rule: Date must not be null/NaT
    if COL_DATE in df_working.columns:
        date_series = pd.to_datetime(df_working[COL_DATE], errors="coerce")
        bad_date_mask = date_series.isna()
        for idx in df_working[bad_date_mask].index:
            pos = df_working.index.get_loc(idx)
            issues[pos].append("Missing or unparseable date")

    # 3. Rule: Quantity must be >= 1
    if COL_QUANTITY in df_working.columns:
        qty_series = pd.to_numeric(df_working[COL_QUANTITY], errors="coerce")
        bad_qty_mask = qty_series.isna() | (qty_series < 1)
        for idx in df_working[bad_qty_mask].index:
            pos = df_working.index.get_loc(idx)
            issues[pos].append("Quantity less than 1 or missing")

    # 4. Rule: Customer ID must not be null or blank
    cust_series = df_working[COL_CUSTOMER_ID].astype(str).str.strip().str.lower()
    bad_cust_mask = (
        df_working[COL_CUSTOMER_ID].isna()
        | (cust_series == "")
        | (cust_series == "none")
        | (cust_series == "nan")
    )
    for idx in df_working[bad_cust_mask].index:
        pos = df_working.index.get_loc(idx)
        issues[pos].append("Missing customer identifier")

    # 5. Rule: Order ID must not be null or blank
    order_series = df_working[COL_ORDER_ID].astype(str).str.strip().str.lower()
    bad_order_mask = (
        df_working[COL_ORDER_ID].isna()
        | (order_series == "")
        | (order_series == "none")
        | (order_series == "nan")
    )
    for idx in df_working[bad_order_mask].index:
        pos = df_working.index.get_loc(idx)
        issues[pos].append("Missing order identifier")

    # 6. Rule: Transaction status must be valid
    status_series = df_working[COL_STATUS].astype(str).str.strip().str.lower()
    bad_status_mask = ~status_series.isin(VALID_STATUSES)
    for idx in df_working[bad_status_mask].index:
        pos = df_working.index.get_loc(idx)
        issues[pos].append(f"Invalid transaction status: '{df_working.loc[idx, COL_STATUS]}'")

    # Partition rows based on whether they encountered any issues
    issue_strings = ["; ".join(row_issues) if row_issues else None for row_issues in issues]
    df_working["validation_issue"] = issue_strings

    valid_mask = [len(row_issues) == 0 for row_issues in issues]
    valid_df = df_working[valid_mask].drop(columns=["validation_issue"]).reset_index(drop=True)
    invalid_df = df_working[[not m for m in valid_mask]].reset_index(drop=True)

    # ── Compute Data Quality Report ───────────────────────────────────────────
    total_records = len(df_working)
    valid_records = len(valid_df)
    invalid_records = len(invalid_df)
    quality_score = round((valid_records / total_records) * 100, 2) if total_records > 0 else 0.0

    # Aggregate breakdown of unique issues
    breakdown: dict[str, int] = {}
    for row_issues in issues:
        for issue_text in row_issues:
            # Group specific invalid status messages under one summary label
            cat = "Invalid transaction status" if issue_text.startswith("Invalid transaction status") else issue_text
            breakdown[cat] = breakdown.get(cat, 0) + 1

    issue_summary = [
        {
            "issue_type": k,
            "affected_rows": v,
            "percentage": round((v / total_records) * 100, 2),
        }
        for k, v in sorted(breakdown.items(), key=lambda item: item[1], reverse=True)
    ]

    # Calculate column-level completeness (% non-null)
    completeness = {
        col: round(((total_records - int(df[col].isna().sum())) / total_records) * 100, 2)
        for col in df.columns
    }

    quality_report: dict[str, Any] = {
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "data_quality_score": quality_score,
        "issue_breakdown": breakdown,
        "issue_summary": issue_summary,
        "column_completeness": completeness,
    }

    return valid_df, invalid_df, quality_report
