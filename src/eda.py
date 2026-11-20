"""
src/eda.py — Exploratory Data Analysis and Descriptive Statistics module.
Customer RFM Analysis

Provides computational routines to calculate sales performance trends,
product distribution, regional insights, and summary customer statistics.
Operates on validated transaction data.
"""

from __future__ import annotations

from typing import Any
import pandas as pd
import numpy as np

from src.config import (
    COL_TRANSACTION_ID,
    COL_CUSTOMER_ID,
    COL_CUSTOMER_NAME,
    COL_ORDER_ID,
    COL_DATE,
    COL_AMOUNT,
    COL_QUANTITY,
    COL_CATEGORY,
    COL_REGION,
    COL_PAYMENT,
)


def compute_summary_stats(df: pd.DataFrame) -> dict[str, Any]:
    """
    Compute comprehensive descriptive statistics for transaction spending and orders.

    Parameters
    ----------
    df : pd.DataFrame
        Validated transaction DataFrame.

    Returns
    -------
    dict[str, Any]
        Dictionary containing central tendency, dispersion, and order metrics.
    """
    if df.empty:
        return {
            "total_gross_revenue": 0.0,
            "total_transactions": 0,
            "total_orders": 0,
            "total_customers": 0,
            "mean_transaction_value": 0.0,
            "median_transaction_value": 0.0,
            "std_transaction_value": 0.0,
            "min_transaction_value": 0.0,
            "max_transaction_value": 0.0,
            "avg_orders_per_customer": 0.0,
            "avg_spend_per_customer": 0.0,
            "avg_items_per_transaction": 0.0,
        }

    amounts = df[COL_AMOUNT].dropna()
    total_revenue = float(amounts.sum())
    total_txns = len(df)
    total_orders = int(df[COL_ORDER_ID].nunique()) if COL_ORDER_ID in df.columns else 0
    total_custs = int(df[COL_CUSTOMER_ID].nunique()) if COL_CUSTOMER_ID in df.columns else 0

    avg_orders_per_cust = round(total_orders / total_custs, 2) if total_custs > 0 else 0.0
    avg_spend_per_cust = round(total_revenue / total_custs, 2) if total_custs > 0 else 0.0

    quantities = df[COL_QUANTITY].dropna() if COL_QUANTITY in df.columns else pd.Series(dtype=float)
    avg_items = round(float(quantities.mean()), 2) if not quantities.empty else 0.0

    return {
        "total_gross_revenue": round(total_revenue, 2),
        "total_transactions": total_txns,
        "total_orders": total_orders,
        "total_customers": total_custs,
        "mean_transaction_value": round(float(amounts.mean()), 2),
        "median_transaction_value": round(float(amounts.median()), 2),
        "std_transaction_value": round(float(amounts.std(ddof=1)), 2) if len(amounts) > 1 else 0.0,
        "min_transaction_value": round(float(amounts.min()), 2),
        "max_transaction_value": round(float(amounts.max()), 2),
        "avg_orders_per_customer": avg_orders_per_cust,
        "avg_spend_per_customer": avg_spend_per_cust,
        "avg_items_per_transaction": avg_items,
    }


def compute_monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate monthly revenue, order volume, and customer participation.

    Parameters
    ----------
    df : pd.DataFrame
        Validated transaction DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns: ['year_month', 'revenue', 'order_count', 'customer_count', 'avg_order_value']
    """
    if df.empty or COL_DATE not in df.columns:
        return pd.DataFrame(
            columns=["year_month", "revenue", "order_count", "customer_count", "avg_order_value"]
        )

    df_clean = df.dropna(subset=[COL_DATE]).copy()
    df_clean["year_month"] = df_clean[COL_DATE].dt.to_period("M").astype(str)

    grouped = df_clean.groupby("year_month").agg(
        revenue=(COL_AMOUNT, "sum"),
        order_count=(COL_ORDER_ID, "nunique"),
        customer_count=(COL_CUSTOMER_ID, "nunique"),
    ).reset_index()

    grouped["revenue"] = grouped["revenue"].round(2)
    grouped["avg_order_value"] = (
        grouped["revenue"] / grouped["order_count"].replace(0, np.nan)
    ).round(2).fillna(0.0)

    return grouped.sort_values("year_month").reset_index(drop=True)


def compute_category_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate financial and unit metrics across product categories.

    Parameters
    ----------
    df : pd.DataFrame
        Validated transaction DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns: ['product_category', 'total_revenue', 'total_units_sold',
                  'transaction_count', 'revenue_percentage']
    """
    if df.empty or COL_CATEGORY not in df.columns:
        return pd.DataFrame(
            columns=[
                "product_category",
                "total_revenue",
                "total_units_sold",
                "transaction_count",
                "revenue_percentage",
            ]
        )

    grouped = df.groupby(COL_CATEGORY).agg(
        total_revenue=(COL_AMOUNT, "sum"),
        total_units_sold=(COL_QUANTITY, "sum") if COL_QUANTITY in df.columns else (COL_AMOUNT, "count"),
        transaction_count=(COL_TRANSACTION_ID, "count"),
    ).reset_index()

    total_revenue_all = grouped["total_revenue"].sum()
    grouped["revenue_percentage"] = (
        (grouped["total_revenue"] / total_revenue_all * 100).round(2)
        if total_revenue_all > 0
        else 0.0
    )
    grouped["total_revenue"] = grouped["total_revenue"].round(2)

    return grouped.sort_values("total_revenue", ascending=False).reset_index(drop=True)


def compute_top_customers(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Rank top N customers by total monetary spend.

    Parameters
    ----------
    df : pd.DataFrame
        Validated transaction DataFrame.
    n : int
        Number of top customers to return (default 10).

    Returns
    -------
    pd.DataFrame
        Columns: ['customer_id', 'customer_name', 'total_spend', 'total_orders',
                  'total_items', 'latest_purchase_date']
    """
    if df.empty or COL_CUSTOMER_ID not in df.columns:
        return pd.DataFrame(
            columns=[
                "customer_id",
                "customer_name",
                "total_spend",
                "total_orders",
                "total_items",
                "latest_purchase_date",
            ]
        )

    name_col = COL_CUSTOMER_NAME if COL_CUSTOMER_NAME in df.columns else COL_CUSTOMER_ID

    grouped = df.groupby(COL_CUSTOMER_ID).agg(
        customer_name=(name_col, "first"),
        total_spend=(COL_AMOUNT, "sum"),
        total_orders=(COL_ORDER_ID, "nunique"),
        total_items=(COL_QUANTITY, "sum") if COL_QUANTITY in df.columns else (COL_AMOUNT, "count"),
        latest_purchase_date=(COL_DATE, "max"),
    ).reset_index()

    grouped["total_spend"] = grouped["total_spend"].round(2)
    grouped["latest_purchase_date"] = pd.to_datetime(
        grouped["latest_purchase_date"]
    ).dt.strftime("%Y-%m-%d")

    return grouped.sort_values("total_spend", ascending=False).head(n).reset_index(drop=True)


def compute_transaction_distribution(
    df: pd.DataFrame, bins: int = 15
) -> pd.DataFrame:
    """
    Generate binned distribution table for transaction amounts.

    Parameters
    ----------
    df : pd.DataFrame
        Validated transaction DataFrame.
    bins : int
        Number of histogram bins (default 15).

    Returns
    -------
    pd.DataFrame
        Columns: ['bin_range', 'count', 'percentage']
    """
    if df.empty or COL_AMOUNT not in df.columns:
        return pd.DataFrame(columns=["bin_range", "count", "percentage"])

    amounts = df[COL_AMOUNT].dropna()
    if amounts.empty or amounts.nunique() <= 1:
        return pd.DataFrame(columns=["bin_range", "count", "percentage"])

    counts, bin_edges = np.histogram(amounts, bins=bins)
    total = len(amounts)

    rows = []
    for i in range(len(counts)):
        low = round(bin_edges[i], 1)
        high = round(bin_edges[i + 1], 1)
        count = int(counts[i])
        pct = round((count / total) * 100, 2)
        rows.append({
            "bin_range": f"₹{low:,.0f} – ₹{high:,.0f}",
            "count": count,
            "percentage": pct,
        })

    return pd.DataFrame(rows)


def compute_regional_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate transaction metrics by store geographic region.

    Parameters
    ----------
    df : pd.DataFrame
        Validated transaction DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns: ['store_region', 'total_revenue', 'order_count', 'customer_count', 'revenue_share']
    """
    if df.empty or COL_REGION not in df.columns:
        return pd.DataFrame(
            columns=["store_region", "total_revenue", "order_count", "customer_count", "revenue_share"]
        )

    grouped = df.groupby(COL_REGION).agg(
        total_revenue=(COL_AMOUNT, "sum"),
        order_count=(COL_ORDER_ID, "nunique"),
        customer_count=(COL_CUSTOMER_ID, "nunique"),
    ).reset_index()

    total_revenue_all = grouped["total_revenue"].sum()
    grouped["revenue_share"] = (
        (grouped["total_revenue"] / total_revenue_all * 100).round(2)
        if total_revenue_all > 0
        else 0.0
    )
    grouped["total_revenue"] = grouped["total_revenue"].round(2)

    return grouped.sort_values("total_revenue", ascending=False).reset_index(drop=True)


def compute_payment_method_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate volume and amount shares across payment channels.

    Parameters
    ----------
    df : pd.DataFrame
        Validated transaction DataFrame.

    Returns
    -------
    pd.DataFrame
        Columns: ['payment_method', 'transaction_count', 'total_amount', 'percentage_amount']
    """
    if df.empty or COL_PAYMENT not in df.columns:
        return pd.DataFrame(
            columns=["payment_method", "transaction_count", "total_amount", "percentage_amount"]
        )

    grouped = df.groupby(COL_PAYMENT).agg(
        transaction_count=(COL_TRANSACTION_ID, "count"),
        total_amount=(COL_AMOUNT, "sum"),
    ).reset_index()

    total_amount_all = grouped["total_amount"].sum()
    grouped["percentage_amount"] = (
        (grouped["total_amount"] / total_amount_all * 100).round(2)
        if total_amount_all > 0
        else 0.0
    )
    grouped["total_amount"] = grouped["total_amount"].round(2)

    return grouped.sort_values("total_amount", ascending=False).reset_index(drop=True)
