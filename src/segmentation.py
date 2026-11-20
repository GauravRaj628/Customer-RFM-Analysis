"""
src/segmentation.py — Customer Segmentation and Revenue Aggregation Module.
Customer RFM Analysis

Assigns customer segments based on composite RFM scores and computes
business aggregation tables, segment comparisons, and cohort revenue streams.
"""

from __future__ import annotations

from typing import Any
import pandas as pd
import numpy as np

from src.config import (
    COL_CUSTOMER_ID,
    COL_DATE,
    COL_AMOUNT,
    SEGMENT_MAP,
    SEGMENT_ORDER,
    SEGMENT_COLOURS,
)


def _map_rfm_score_to_segment(score: int | float) -> str:
    """
    Map an integer RFM composite score (3 to 15) to its defined segment.

    Rules:
    - 13–15 : Champions
    - 10–12 : Loyal Customers
    - 7–9   : Potential Loyalists
    - 4–6   : At-Risk Customers
    - 3     : Lost Customers
    """
    int_score = int(round(score)) if not pd.isna(score) else 3
    for (min_s, max_s), segment_name in SEGMENT_MAP.items():
        if min_s <= int_score <= max_s:
            return segment_name
    if int_score > 15:
        return "Champions"
    return "Lost Customers"


def assign_segments(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign each customer deterministically to exactly one segment.

    Parameters
    ----------
    rfm_df : pd.DataFrame
        Scored RFM DataFrame containing 'rfm_score'.

    Returns
    -------
    pd.DataFrame
        DataFrame with added columns:
        ['customer_segment', 'segment_color']
    """
    if rfm_df.empty or "rfm_score" not in rfm_df.columns:
        return rfm_df.copy().assign(
            customer_segment=pd.Series(dtype=str),
            segment_color=pd.Series(dtype=str),
        )

    df_segmented = rfm_df.copy()
    df_segmented["customer_segment"] = df_segmented["rfm_score"].apply(
        _map_rfm_score_to_segment
    )
    df_segmented["segment_color"] = df_segmented["customer_segment"].map(
        SEGMENT_COLOURS
    ).fillna("#95A5A6")

    return df_segmented


def compute_segment_summary(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute aggregate customer and revenue metrics grouped by customer segment.

    Parameters
    ----------
    rfm_df : pd.DataFrame
        Segmented customer RFM DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns:
        ['customer_segment', 'customer_count', 'customer_percentage',
         'total_revenue', 'revenue_percentage', 'avg_recency',
         'avg_frequency', 'avg_monetary', 'avg_rfm_score']
    """
    if rfm_df.empty or "customer_segment" not in rfm_df.columns:
        return pd.DataFrame(
            columns=[
                "customer_segment",
                "customer_count",
                "customer_percentage",
                "total_revenue",
                "revenue_percentage",
                "avg_recency",
                "avg_frequency",
                "avg_monetary",
                "avg_rfm_score",
            ]
        )

    total_custs = len(rfm_df)
    total_rev = rfm_df["monetary"].sum() if "monetary" in rfm_df.columns else 0.0

    grouped = rfm_df.groupby("customer_segment").agg(
        customer_count=(COL_CUSTOMER_ID, "count"),
        total_revenue=("monetary", "sum"),
        avg_recency=("recency_days", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        avg_rfm_score=("rfm_score", "mean") if "rfm_score" in rfm_df.columns else ("monetary", lambda x: 0.0),
    ).reset_index()

    grouped["customer_percentage"] = (
        (grouped["customer_count"] / total_custs * 100).round(2)
        if total_custs > 0
        else 0.0
    )
    grouped["revenue_percentage"] = (
        (grouped["total_revenue"] / total_rev * 100).round(2)
        if total_rev > 0
        else 0.0
    )
    grouped["total_revenue"] = grouped["total_revenue"].round(2)
    grouped["avg_recency"] = grouped["avg_recency"].round(1)
    grouped["avg_frequency"] = grouped["avg_frequency"].round(2)
    grouped["avg_monetary"] = grouped["avg_monetary"].round(2)
    grouped["avg_rfm_score"] = grouped["avg_rfm_score"].round(2)

    # Reorder according to standard business priority
    summary_df = pd.DataFrame({"customer_segment": SEGMENT_ORDER}).merge(
        grouped, on="customer_segment", how="left"
    )
    summary_df = summary_df.fillna({
        "customer_count": 0,
        "customer_percentage": 0.0,
        "total_revenue": 0.0,
        "revenue_percentage": 0.0,
        "avg_recency": 0.0,
        "avg_frequency": 0.0,
        "avg_monetary": 0.0,
        "avg_rfm_score": 0.0,
    })
    summary_df["customer_count"] = summary_df["customer_count"].astype(int)

    return summary_df


def compute_revenue_by_segment(
    rfm_df: pd.DataFrame, valid_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Link customer segment mapping with transactions to aggregate revenue over time.

    Parameters
    ----------
    rfm_df : pd.DataFrame
        Segmented customer RFM DataFrame.
    valid_df : pd.DataFrame
        Validated transaction DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns: ['year_month', 'customer_segment', 'revenue', 'transaction_count']
    """
    if rfm_df.empty or valid_df.empty or "customer_segment" not in rfm_df.columns:
        return pd.DataFrame(
            columns=["year_month", "customer_segment", "revenue", "transaction_count"]
        )

    # Create mapping: customer_id -> customer_segment
    seg_map = rfm_df.set_index(COL_CUSTOMER_ID)["customer_segment"].to_dict()

    df_tx = valid_df.dropna(subset=[COL_DATE]).copy()
    df_tx["customer_segment"] = df_tx[COL_CUSTOMER_ID].map(seg_map).fillna("Lost Customers")
    df_tx["year_month"] = df_tx[COL_DATE].dt.to_period("M").astype(str)

    grouped = df_tx.groupby(["year_month", "customer_segment"]).agg(
        revenue=(COL_AMOUNT, "sum"),
        transaction_count=(COL_AMOUNT, "count"),
    ).reset_index()

    grouped["revenue"] = grouped["revenue"].round(2)
    return grouped.sort_values(["year_month", "customer_segment"]).reset_index(drop=True)


def compute_cohort_revenue(valid_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute customer acquisition cohort revenue matrix.

    Groups customers by their first purchase month and aggregates subsequent
    monthly revenues indexed by months since acquisition (cohort_index).

    Parameters
    ----------
    valid_df : pd.DataFrame
        Validated transaction DataFrame.

    Returns
    -------
    pd.DataFrame
        Cohort revenue matrix pivoted by cohort_month (rows) and cohort_index (columns).
    """
    if valid_df.empty or COL_CUSTOMER_ID not in valid_df.columns or COL_DATE not in valid_df.columns:
        return pd.DataFrame()

    df_clean = valid_df.dropna(subset=[COL_DATE]).copy()
    df_clean["order_month"] = df_clean[COL_DATE].dt.to_period("M")

    # Determine cohort month for each customer
    first_purchase = df_clean.groupby(COL_CUSTOMER_ID)["order_month"].min().reset_index()
    first_purchase.columns = [COL_CUSTOMER_ID, "cohort_month"]

    df_cohort = df_clean.merge(first_purchase, on=COL_CUSTOMER_ID, how="left")

    # Calculate cohort index (integer months elapsed since acquisition)
    df_cohort["cohort_index"] = (
        (df_cohort["order_month"].dt.year - df_cohort["cohort_month"].dt.year) * 12
        + (df_cohort["order_month"].dt.month - df_cohort["cohort_month"].dt.month)
    )

    cohort_agg = df_cohort.groupby(["cohort_month", "cohort_index"])[COL_AMOUNT].sum().reset_index()
    cohort_agg["cohort_month"] = cohort_agg["cohort_month"].astype(str)
    cohort_agg[COL_AMOUNT] = cohort_agg[COL_AMOUNT].round(2)

    pivot_matrix = cohort_agg.pivot(
        index="cohort_month", columns="cohort_index", values=COL_AMOUNT
    ).fillna(0.0)

    return pivot_matrix
