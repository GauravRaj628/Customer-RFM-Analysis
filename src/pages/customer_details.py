"""
src/pages/customer_details.py — UI-07: Customer Details & 360° Profile Screen.
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

from src.config import (
    DEFAULT_DATASET_PATH,
    COL_CUSTOMER_ID,
    COL_CUSTOMER_NAME,
    COL_DATE,
    COL_AMOUNT,
    COL_CATEGORY,
    SEGMENT_COLOURS,
    ACTIVITY_COLOURS,
    ACTIVITY_LABELS,
)
from src.components.ui_components import (
    render_page_header,
    render_kpi_card,
    render_segment_badge,
    render_activity_badge,
    render_empty_state,
)
from src.pages.data_upload import process_and_cache_dataset

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def build_customer_category_donut(cust_txns: pd.DataFrame) -> go.Figure:
    """Build a donut chart of spending across product categories for an individual customer."""
    if cust_txns.empty or COL_CATEGORY not in cust_txns.columns:
        return go.Figure()

    cat_spend = (
        cust_txns.groupby(COL_CATEGORY)[COL_AMOUNT]
        .sum()
        .reset_index()
        .sort_values(by=COL_AMOUNT, ascending=False)
    )

    fig = go.Figure(
        data=[
            go.Pie(
                labels=cat_spend[COL_CATEGORY],
                values=cat_spend[COL_AMOUNT],
                hole=0.55,
                marker=dict(line=dict(color="#FFFFFF", width=2)),
                textinfo="label+percent",
                textfont=dict(family=FONT_FAMILY, size=11),
                hovertemplate="<b>%{label}</b><br>Spend: ₹%{value:,.2f}<br>Share: %{percent}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT_FAMILY),
        title=dict(text="Category Spend Distribution", font=dict(family=FONT_FAMILY, size=14, color="#0F172A")),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(family=FONT_FAMILY, size=11, color="#475569"),
        ),
        margin=dict(l=20, r=20, t=45, b=25),
        height=320,
    )
    return fig


def render() -> None:
    """Render the Customer Details & 360° Profile screen."""
    render_page_header(
        title="Customer 360° Profile & Order History",
        subtitle="Step 6 of 8: Deep-dive into individual customer behavioral footprints, scoring breakdown, and transaction timelines",
        breadcrumb="Customer 360",
    )

    # Ensure valid transaction data exists in session state
    if (
        "valid_df" not in st.session_state
        or st.session_state["valid_df"] is None
        or "rfm_df" not in st.session_state
        or st.session_state["rfm_df"] is None
    ):
        if Path(DEFAULT_DATASET_PATH).exists():
            process_and_cache_dataset(DEFAULT_DATASET_PATH, source_label="Default Synthetic Dataset")

    rfm_df = st.session_state.get("rfm_df")
    valid_df = st.session_state.get("valid_df")

    if rfm_df is None or rfm_df.empty or valid_df is None or valid_df.empty:
        render_empty_state("No customer or transaction data available. Please upload a dataset in Data Upload.")
        return

    # ── Customer Search & Selector ─────────────────────────────────────────────
    # Sort customers by spend descending so high-value patrons appear first
    sorted_customers = rfm_df.sort_values(by="monetary", ascending=False).reset_index(drop=True)
    customer_options = {
        f"{row['customer_id']} — {row['customer_name']} (₹{row['monetary']:,.0f} | {row['customer_segment']})": row['customer_id']
        for _, row in sorted_customers.iterrows()
    }

    st.markdown("### 🔍 Select Customer Profile")
    selected_label = st.selectbox(
        "Choose a customer from the catalog or search by ID/Name",
        options=list(customer_options.keys()),
        label_visibility="collapsed",
    )
    selected_cust_id = customer_options[selected_label]

    cust_rfm = rfm_df[rfm_df["customer_id"] == selected_cust_id].iloc[0]
    cust_txns = valid_df[valid_df["customer_id"] == selected_cust_id].sort_values(by=COL_DATE, ascending=False)

    st.write("")

    # ── Customer Profile Card Header ───────────────────────────────────────────
    cust_name = cust_rfm["customer_name"]
    segment_name = cust_rfm["customer_segment"]
    activity_name = cust_rfm["activity_band"]
    seg_color = SEGMENT_COLOURS.get(segment_name, "#172554")
    act_color = ACTIVITY_COLOURS.get(activity_name, "#475569")
    act_label = ACTIVITY_LABELS.get(activity_name, activity_name)

    # Determine first and latest purchase dates
    valid_dates = pd.to_datetime(cust_txns[COL_DATE], errors="coerce").dropna()
    first_date_str = valid_dates.min().strftime("%d %b %Y") if not valid_dates.empty else "N/A"
    latest_date_str = valid_dates.max().strftime("%d %b %Y") if not valid_dates.empty else "N/A"

    # Determine region and city if present
    region_str = cust_txns["store_region"].dropna().iloc[0] if "store_region" in cust_txns.columns and not cust_txns["store_region"].dropna().empty else "N/A"
    city_str = cust_txns["city"].dropna().iloc[0] if "city" in cust_txns.columns and not cust_txns["city"].dropna().empty else "N/A"

    st.markdown(
        f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid {seg_color};
                    border-radius: 10px; padding: 1.25rem 1.4rem; margin-bottom: 1.25rem;
                    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <h3 style="margin: 0; color: #0F172A; font-size: 1.35rem; font-weight: 700; letter-spacing: -0.01em;">{cust_name}</h3>
                    <p style="margin: 0.25rem 0 0 0; color: #64748B; font-size: 0.88rem;">
                        <strong>ID:</strong> <code>{selected_cust_id}</code> • 📍 {city_str}, {region_str}
                    </p>
                    <p style="margin: 0.25rem 0 0 0; color: #64748B; font-size: 0.82rem;">
                        Customer since <strong>{first_date_str}</strong> • Latest active purchase: <strong>{latest_date_str}</strong>
                    </p>
                </div>
                <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
                    <span style="background-color: {seg_color}18; color: {seg_color}; border: 1px solid {seg_color};
                                 padding: 0.35rem 0.75rem; border-radius: 9999px; font-weight: 600; font-size: 0.82rem;">
                        {segment_name}
                    </span>
                    <span style="background-color: {act_color}18; color: {act_color}; border: 1px solid {act_color};
                                 padding: 0.35rem 0.75rem; border-radius: 9999px; font-weight: 600; font-size: 0.82rem;">
                        {act_label}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Executive Customer KPI Cards ───────────────────────────────────────────
    spend = float(cust_rfm["monetary"])
    orders = int(cust_rfm["frequency"])
    recency_days = int(cust_rfm["recency_days"])
    rfm_score = int(cust_rfm["rfm_score"])
    rfm_cell = str(cust_rfm["rfm_cell"])
    avg_basket = (spend / orders) if orders > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Lifetime Spend", f"₹{spend:,.2f}", icon="💰")
    with k2:
        render_kpi_card("Completed Orders", f"{orders} orders", icon="🛒")
    with k3:
        render_kpi_card("Days Since Purchase", f"{recency_days} days", icon="⏱️")
    with k4:
        render_kpi_card("RFM Score & Cell", f"{rfm_score} / 15", delta=f"Cell: {rfm_cell}", icon="⭐")

    st.write("")
    st.divider()

    # ── RFM Quintile Score Breakdown (1 to 5) ──────────────────────────────────
    st.markdown("### 🎯 RFM Score Breakdown (1–5 Quintiles)")
    r_val = int(cust_rfm["r_score"])
    f_val = int(cust_rfm["f_score"])
    m_val = int(cust_rfm["m_score"])

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f"**Recency Score (R): `{r_val} / 5`**")
        st.progress(r_val / 5.0)
        st.caption(f"{recency_days} days since last order (Score 5 = most recent).")

    with sc2:
        st.markdown(f"**Frequency Score (F): `{f_val} / 5`**")
        st.progress(f_val / 5.0)
        st.caption(f"{orders} completed order(s) (Score 5 = highest frequency).")

    with sc3:
        st.markdown(f"**Monetary Score (M): `{m_val} / 5`**")
        st.progress(m_val / 5.0)
        st.caption(f"₹{spend:,.2f} lifetime spend (Score 5 = highest monetary).")

    st.write("")

    # ── Customer Purchase Insights & Category Distribution ────────────────────
    st.markdown("### 🛍️ Customer Basket & Product Preferences")
    col_cat_chart, col_pref_card = st.columns([1.1, 0.9])

    with col_cat_chart:
        fig_cust_cat = build_customer_category_donut(cust_txns)
        st.plotly_chart(fig_cust_cat, use_container_width=True)

    with col_pref_card:
        st.markdown("##### Behavioral Highlights")
        # Favorite payment method
        fav_pay = cust_txns["payment_method"].mode()[0] if "payment_method" in cust_txns.columns and not cust_txns["payment_method"].empty else "N/A"
        total_items = cust_txns["quantity"].sum() if "quantity" in cust_txns.columns else orders

        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.15rem; font-size: 0.88rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                <div style="margin-bottom: 0.5rem; color: #334155;"><strong>Average Order Basket:</strong> ₹{avg_basket:,.2f}</div>
                <div style="margin-bottom: 0.5rem; color: #334155;"><strong>Total Units Purchased:</strong> {int(total_items):,} units</div>
                <div style="margin-bottom: 0.5rem; color: #334155;"><strong>Primary Payment Mode:</strong> {fav_pay}</div>
                <div style="color: #334155;"><strong>Home City & Region:</strong> {city_str} ({region_str})</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # ── Full Purchase History Table ────────────────────────────────────────────
    st.markdown(f"### 📜 Purchase History Timeline ({len(cust_txns)} Transaction Records)")
    history_cols = [
        "transaction_id",
        "order_id",
        "transaction_date",
        "product_category",
        "product_name",
        "quantity",
        "unit_price",
        "transaction_amount",
        "payment_method",
        "store_region",
    ]
    present_hist_cols = [c for c in history_cols if c in cust_txns.columns]
    display_history = cust_txns[present_hist_cols].copy()
    if "transaction_amount" in display_history.columns:
        display_history["transaction_amount"] = display_history["transaction_amount"].apply(lambda v: f"₹{v:,.2f}")
    if "unit_price" in display_history.columns:
        display_history["unit_price"] = display_history["unit_price"].apply(lambda v: f"₹{v:,.2f}")

    st.dataframe(display_history, use_container_width=True, hide_index=True)

    # Download customer statement
    csv_bytes = cust_txns.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Download Statement for {selected_cust_id} (CSV)",
        data=csv_bytes,
        file_name=f"statement_{selected_cust_id}.csv",
        mime="text/csv",
    )

    st.write("")

    # ── Next Step Callout ──────────────────────────────────────────────────────
    st.info(
        "💡 **Profile Inspected:** Proceed to **💰 Revenue Analysis** from the sidebar to inspect cohort lifetime "
        "value, cumulative revenue curves, and Pareto 80/20 spend concentration.",
        icon="👉",
    )
