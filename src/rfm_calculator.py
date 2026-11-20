"""
src/rfm_calculator.py — RFM Calculation and Quintile Scoring Module.
Customer RFM Analysis

Implements core RFM analytics according to ABC Retail Solutions requirements:
- Recency (R): Elapsed days between reference date and customer's latest purchase.
- Frequency (F): Count of DISTINCT Order IDs placed by the customer.
- Monetary (M): Sum of valid transaction spending per customer.
- Scoring (1-5): Quintile-based scoring. Recency is reversed (low days = 5).
- Activity Bands: Recent (0-30d), At-risk (31-90d), Inactive (>90d).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
import pandas as pd
import numpy as np

from src.config import (
    COL_CUSTOMER_ID,
    COL_CUSTOMER_NAME,
    COL_ORDER_ID,
    COL_DATE,
    COL_AMOUNT,
    RFM_SCORE_MIN,
    RFM_SCORE_MAX,
)


def calculate_rfm(
    df: pd.DataFrame,
    reference_date: date | str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """
    Calculate customer-level Recency, Frequency, and Monetary metrics.

    Parameters
    ----------
    df : pd.DataFrame
        Validated transaction DataFrame.
    reference_date : date | str | pd.Timestamp | None
        Analysis anchor date. If None, defaults to 1 day after the latest
        valid transaction date in the dataset.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        ['customer_id', 'customer_name', 'recency_days', 'frequency',
         'monetary', 'latest_purchase_date', 'first_purchase_date', 'activity_band']
    """
    if df.empty or COL_CUSTOMER_ID not in df.columns:
        return pd.DataFrame(
            columns=[
                "customer_id",
                "customer_name",
                "recency_days",
                "frequency",
                "monetary",
                "latest_purchase_date",
                "first_purchase_date",
                "activity_band",
            ]
        )

    # 1. Ensure date column is datetime
    df_clean = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_clean[COL_DATE]):
        df_clean[COL_DATE] = pd.to_datetime(df_clean[COL_DATE], errors="coerce")
    df_clean = df_clean.dropna(subset=[COL_DATE])

    # 2. Determine reference date
    if reference_date is None:
        latest_date = df_clean[COL_DATE].max()
        ref_dt = pd.to_datetime(latest_date) + pd.Timedelta(days=1)
    else:
        ref_dt = pd.to_datetime(reference_date)

    name_col = COL_CUSTOMER_NAME if COL_CUSTOMER_NAME in df_clean.columns else COL_CUSTOMER_ID

    # 3. Aggregate metrics per customer
    # IMPORTANT: Frequency counts distinct order_id, NOT transaction rows.
    rfm = df_clean.groupby(COL_CUSTOMER_ID).agg(
        customer_name=(name_col, "first"),
        latest_purchase_date=(COL_DATE, "max"),
        first_purchase_date=(COL_DATE, "min"),
        frequency=(COL_ORDER_ID, "nunique"),
        monetary=(COL_AMOUNT, "sum"),
    ).reset_index()

    # 4. Compute Recency in days
    rfm["recency_days"] = (ref_dt - rfm["latest_purchase_date"]).dt.days
    # Prevent negative recency if reference date is earlier than latest purchase
    rfm["recency_days"] = rfm["recency_days"].clip(lower=0)

    rfm["monetary"] = rfm["monetary"].round(2)

    # 5. Assign Activity Band based on recency days
    # - 0–30 days: Recent
    # - 31–90 days: At-risk
    # - More than 90 days: Inactive
    def _assign_activity_band(days: int) -> str:
        if days <= 30:
            return "Recent"
        elif days <= 90:
            return "At-risk"
        return "Inactive"

    rfm["activity_band"] = rfm["recency_days"].apply(_assign_activity_band)

    return rfm.sort_values(COL_CUSTOMER_ID).reset_index(drop=True)


def score_rfm(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign quintile scores (1 to 5) to Recency, Frequency, and Monetary metrics.

    Business Rules:
    - Recency score is reversed: Lower recency_days = Higher score (5).
    - Frequency: Higher distinct orders = Higher score (5).
    - Monetary: Higher total spending = Higher score (5).
    - RFM_Score: Integer sum of R + F + M (range 3 to 15).
    - RFM_Cell: Concatenation string f"{R}{F}{M}" (e.g., '555', '111').

    Parameters
    ----------
    rfm_df : pd.DataFrame
        Customer-level RFM metrics DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with added columns:
        ['r_score', 'f_score', 'm_score', 'rfm_score', 'rfm_cell']
    """
    if rfm_df.empty:
        return rfm_df.copy().assign(
            r_score=pd.Series(dtype=int),
            f_score=pd.Series(dtype=int),
            m_score=pd.Series(dtype=int),
            rfm_score=pd.Series(dtype=int),
            rfm_cell=pd.Series(dtype=str),
        )

    df_scored = rfm_df.copy()
    n_custs = len(df_scored)

    def _assign_score(series: pd.Series, reverse: bool = False) -> pd.Series:
        """Assign 1–5 score using rank-based quintiles to handle duplicate values cleanly."""
        if n_custs < 5:
            # Fallback for very small sample sizes
            ranks = series.rank(method="min", ascending=not reverse)
            max_rank = ranks.max()
            if max_rank > 1:
                scaled = 1 + ((ranks - 1) / (max_rank - 1)) * 4
                return scaled.round().astype(int)
            return pd.Series(3, index=series.index, dtype=int)

        # Rank-based quantile binning: prevents errors on duplicate bin edges (e.g. many freq=1)
        ranks = series.rank(method="first")
        quintiles = pd.qcut(ranks, q=5, labels=[1, 2, 3, 4, 5]).astype(int)

        if reverse:
            # Reverse score: rank 1 becomes 5, rank 5 becomes 1
            return 6 - quintiles
        return quintiles

    # Recency: Lower days is better -> reverse=True
    df_scored["r_score"] = _assign_score(df_scored["recency_days"], reverse=True)

    # Frequency: Higher count is better -> reverse=False
    df_scored["f_score"] = _assign_score(df_scored["frequency"], reverse=False)

    # Monetary: Higher spend is better -> reverse=False
    df_scored["m_score"] = _assign_score(df_scored["monetary"], reverse=False)

    # Combined composite score (3 to 15)
    df_scored["rfm_score"] = (
        df_scored["r_score"] + df_scored["f_score"] + df_scored["m_score"]
    )

    # Textual 3-digit cell identifier
    df_scored["rfm_cell"] = (
        df_scored["r_score"].astype(str)
        + df_scored["f_score"].astype(str)
        + df_scored["m_score"].astype(str)
    )

    return df_scored


def compute_rfm_summary(rfm_df: pd.DataFrame) -> dict[str, Any]:
    """
    Generate summary statistics of RFM distributions across customers.

    Parameters
    ----------
    rfm_df : pd.DataFrame
        Scored customer RFM DataFrame.

    Returns
    -------
    dict[str, Any]
        Summary metrics dictionary.
    """
    if rfm_df.empty:
        return {
            "total_customers": 0,
            "avg_recency_days": 0.0,
            "median_recency_days": 0.0,
            "avg_frequency": 0.0,
            "median_frequency": 0.0,
            "avg_monetary": 0.0,
            "median_monetary": 0.0,
            "avg_rfm_score": 0.0,
            "activity_distribution": {},
            "score_distribution": {},
        }

    total_custs = len(rfm_df)
    activity_counts = rfm_df["activity_band"].value_counts().to_dict() if "activity_band" in rfm_df.columns else {}
    score_counts = rfm_df["rfm_score"].value_counts().sort_index().to_dict() if "rfm_score" in rfm_df.columns else {}

    return {
        "total_customers": total_custs,
        "avg_recency_days": round(float(rfm_df["recency_days"].mean()), 1),
        "median_recency_days": round(float(rfm_df["recency_days"].median()), 1),
        "avg_frequency": round(float(rfm_df["frequency"].mean()), 2),
        "median_frequency": round(float(rfm_df["frequency"].median()), 1),
        "avg_monetary": round(float(rfm_df["monetary"].mean()), 2),
        "median_monetary": round(float(rfm_df["monetary"].median()), 2),
        "avg_rfm_score": round(float(rfm_df["rfm_score"].mean()), 2) if "rfm_score" in rfm_df.columns else 0.0,
        "activity_distribution": activity_counts,
        "score_distribution": score_counts,
    }
