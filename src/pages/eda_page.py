"""
src/pages/eda_page.py — UI-04: Exploratory Data Analysis (EDA) Screen.
Customer RFM Analysis

Student  : Gaurav Raj  |  Roll: 2500320140054
Programme: MCA 2nd Year  |  ABES Engineering College, Ghaziabad
Mentor   : Kalpana Diwedi
Scenario : ABC Retail Solutions Pvt. Ltd., Noida
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.config import DEFAULT_DATASET_PATH
from src.components.ui_components import (
    render_page_header,
    render_kpi_card,
    render_empty_state,
)
from src.pages.data_upload import process_and_cache_dataset
from src.eda import (
    compute_summary_stats,
    compute_monthly_revenue,
    compute_category_breakdown,
    compute_top_customers,
    compute_transaction_distribution,
    compute_regional_breakdown,
    compute_payment_method_breakdown,
)

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def build_monthly_trend_chart(monthly_df: pd.DataFrame) -> go.Figure:
    """Build dual-axis monthly revenue and order volume trend chart."""
    if monthly_df.empty:
        return go.Figure()

    fig = go.Figure()

    # Bar chart for Order Count
    fig.add_trace(
        go.Bar(
            x=monthly_df["year_month"],
            y=monthly_df["order_count"],
            name="Completed Orders",
            marker_color="rgba(37, 99, 235, 0.35)",
            yaxis="y2",
            hovertemplate="Orders: %{y:,}<extra></extra>",
        )
    )

    # Line chart for Revenue
    fig.add_trace(
        go.Scatter(
            x=monthly_df["year_month"],
            y=monthly_df["revenue"],
            name="Gross Revenue (₹)",
            mode="lines+markers",
            line=dict(color="#172554", width=3),
            marker=dict(size=7, color="#172554"),
            yaxis="y1",
            hovertemplate="Revenue: ₹%{y:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT_FAMILY),
        title=dict(text="Monthly Revenue Velocity & Order Volume", font=dict(family=FONT_FAMILY, size=15, color="#0F172A")),
        xaxis=dict(title=dict(text="Month (YYYY-MM)"), tickangle=-30, gridcolor="#F1F5F9"),
        yaxis=dict(
            title=dict(text="Gross Revenue (₹)", font=dict(color="#172554")),
            tickfont=dict(color="#172554"),
            gridcolor="#F1F5F9",
        ),
        yaxis2=dict(
            title=dict(text="Order Count", font=dict(color="#2563EB")),
            tickfont=dict(color="#2563EB"),
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family=FONT_FAMILY, size=11, color="#475569"),
        ),
        margin=dict(l=40, r=40, t=50, b=40),
        height=380,
    )
    return fig


def build_category_bar_chart(cat_df: pd.DataFrame) -> go.Figure:
    """Build horizontal bar chart for product category revenue contribution."""
    if cat_df.empty:
        return go.Figure()

    sorted_df = cat_df.sort_values(by="total_revenue", ascending=True)
    fig = px.bar(
        sorted_df,
        x="total_revenue",
        y="product_category",
        orientation="h",
        text=sorted_df["revenue_percentage"].apply(lambda v: f"{v:.1f}%"),
        title="Revenue by Product Category",
        color="total_revenue",
        color_continuous_scale="Blues",
    )
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT_FAMILY),
        title=dict(font=dict(family=FONT_FAMILY, size=14, color="#0F172A")),
        xaxis=dict(title=dict(text="Total Revenue (₹)"), gridcolor="#F1F5F9"),
        yaxis=dict(title=dict(text=""), tickfont=dict(size=11, color="#0F172A")),
        margin=dict(l=20, r=20, t=45, b=25),
        height=340,
        coloraxis_showscale=False,
    )
    fig.update_traces(textposition="outside", hovertemplate="<b>%{y}</b><br>Revenue: ₹%{x:,.2f}<extra></extra>")
    return fig


def build_spending_histogram(txn_dist_df: pd.DataFrame) -> go.Figure:
    """Build spending distribution histogram."""
    if txn_dist_df.empty:
        return go.Figure()

    fig = px.bar(
        txn_dist_df,
        x="bin_range",
        y="count",
        text="count",
        title="Transaction Spending Distribution",
        color="count",
        color_continuous_scale="Blues",
    )
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT_FAMILY),
        title=dict(font=dict(family=FONT_FAMILY, size=14, color="#0F172A")),
        xaxis=dict(title=dict(text="Spending Range (₹)"), tickangle=-20, gridcolor="#F1F5F9"),
        yaxis=dict(title=dict(text="Transaction Count"), gridcolor="#F1F5F9"),
        margin=dict(l=20, r=20, t=45, b=25),
        height=340,
        coloraxis_showscale=False,
    )
    fig.update_traces(textposition="outside")
    return fig


def build_payment_donut(pay_df: pd.DataFrame) -> go.Figure:
    """Build donut chart of payment method preferences."""
    if pay_df.empty:
        return go.Figure()

    palette = ["#2563EB", "#16A34A", "#D97706", "#7C3AED", "#64748B"]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=pay_df["payment_method"],
                values=pay_df["total_amount"],
                hole=0.55,
                marker=dict(colors=palette, line=dict(color="#FFFFFF", width=2)),
                textinfo="label+percent",
                textfont=dict(family=FONT_FAMILY, size=11),
                hovertemplate="<b>%{label}</b><br>Revenue: ₹%{value:,.2f}<br>Share: %{percent}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT_FAMILY),
        title=dict(text="Payment Method Revenue Share", font=dict(family=FONT_FAMILY, size=14, color="#0F172A")),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(family=FONT_FAMILY, size=11, color="#475569"),
        ),
        margin=dict(l=20, r=20, t=45, b=25),
        height=340,
    )
    return fig


def build_region_bar(reg_df: pd.DataFrame) -> go.Figure:
    """Build bar chart for store regional performance."""
    if reg_df.empty:
        return go.Figure()

    fig = px.bar(
        reg_df,
        x="store_region",
        y="total_revenue",
        text=reg_df["revenue_share"].apply(lambda v: f"{v:.1f}%"),
        title="Store Regional Revenue Contribution",
        color="store_region",
        color_discrete_sequence=["#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE"],
    )
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT_FAMILY),
        title=dict(font=dict(family=FONT_FAMILY, size=14, color="#0F172A")),
        xaxis=dict(title=dict(text="Store Region"), gridcolor="#F1F5F9"),
        yaxis=dict(title=dict(text="Total Revenue (₹)"), gridcolor="#F1F5F9"),
        showlegend=False,
        margin=dict(l=20, r=20, t=45, b=25),
        height=340,
    )
    fig.update_traces(textposition="outside", hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.2f}<extra></extra>")
    return fig


def render() -> None:
    """Render the Exploratory Data Analysis (EDA) screen."""
    render_page_header(
        title="Exploratory Data Analysis (EDA)",
        subtitle="Step 3 of 8: Macro revenue trends, product velocity, regional dynamics, and payment choices",
        breadcrumb="Analytics",
    )

    # Ensure valid data exists in session state
    if "valid_df" not in st.session_state or st.session_state["valid_df"] is None:
        if Path(DEFAULT_DATASET_PATH).exists():
            process_and_cache_dataset(DEFAULT_DATASET_PATH, source_label="Default Synthetic Dataset")

    valid_df = st.session_state.get("valid_df")
    if valid_df is None or valid_df.empty:
        render_empty_state("No validated transaction data found. Please upload a dataset in Data Upload.")
        return

    # ── Descriptive Statistics KPI Cards ───────────────────────────────────────
    stats = compute_summary_stats(valid_df)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Total Valid Revenue", f"₹{stats['total_gross_revenue']:,.2f}", icon="💰")
    with k2:
        render_kpi_card("Mean Order Value", f"₹{stats['mean_transaction_value']:,.2f}", icon="🛒")
    with k3:
        render_kpi_card("Avg Spend / Customer", f"₹{stats['avg_spend_per_customer']:,.2f}", icon="👤")
    with k4:
        render_kpi_card("Avg Orders / Customer", f"{stats['avg_orders_per_customer']:.2f}", icon="📦")

    st.write("")
    st.divider()

    # ── Section 1: Monthly Trend ───────────────────────────────────────────────
    st.markdown("### 📈 Monthly Revenue Velocity & Order Volume")
    monthly_df = compute_monthly_revenue(valid_df)
    fig_monthly = build_monthly_trend_chart(monthly_df)
    st.plotly_chart(fig_monthly, use_container_width=True)

    st.write("")

    # ── Section 2: Product Category & Spending Distribution ────────────────────
    st.markdown("### 🛍️ Product Category Velocity & Spending Distribution")
    col_cat, col_dist = st.columns(2)

    with col_cat:
        cat_df = compute_category_breakdown(valid_df)
        fig_cat = build_category_bar_chart(cat_df)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_dist:
        txn_dist_df = compute_transaction_distribution(valid_df)
        fig_dist = build_spending_histogram(txn_dist_df)
        st.plotly_chart(fig_dist, use_container_width=True)

    st.write("")

    # ── Section 3: Regional & Payment Method Dynamics ──────────────────────────
    st.markdown("### 🌍 Regional Sales & Payment Channel Preferences")
    col_reg, col_pay = st.columns(2)

    with col_reg:
        reg_df = compute_regional_breakdown(valid_df)
        fig_reg = build_region_bar(reg_df)
        st.plotly_chart(fig_reg, use_container_width=True)

    with col_pay:
        pay_df = compute_payment_method_breakdown(valid_df)
        fig_pay = build_payment_donut(pay_df)
        st.plotly_chart(fig_pay, use_container_width=True)

    st.write("")

    # ── Section 4: Top 10 Spending Customers Leaderboard ───────────────────────
    st.markdown("### 🏆 Top 10 Customer Spending Leaderboard")
    top_df = compute_top_customers(valid_df, n=10)
    if not top_df.empty:
        display_top = top_df.copy()
        display_top.columns = [
            "Customer ID",
            "Customer Name",
            "Total Spend (₹)",
            "Total Orders",
            "Units Purchased",
            "Latest Purchase Date",
        ]
        display_top["Total Spend (₹)"] = display_top["Total Spend (₹)"].apply(lambda v: f"₹{v:,.2f}")
        st.dataframe(display_top, use_container_width=True, hide_index=True)

    st.write("")

    # ── Next Step Callout ──────────────────────────────────────────────────────
    st.info(
        "💡 **Macro Trends Discovered:** Proceed to **📈 RFM Analysis** from the sidebar to inspect granular "
        "Recency, Frequency, and Monetary distributions and 3D customer clustering.",
        icon="👉",
    )
