"""
src/pages/segmentation_page.py — UI-06: Customer Segmentation Screen.
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

from src.config import (
    DEFAULT_DATASET_PATH,
    SEGMENT_COLOURS,
    SEGMENT_ORDER,
)
from src.components.ui_components import (
    render_page_header,
    render_kpi_card,
    build_segment_donut,
    build_revenue_bar,
    render_segment_badge,
    render_activity_badge,
    render_empty_state,
)
from src.pages.data_upload import process_and_cache_dataset


SEGMENT_STRATEGIES = {
    "Champions": {
        "tagline": "🏆 Top 1% VIP Customers — Your Brand Ambassadors",
        "description": "High spenders who purchase frequently and bought recently. Reward them to maintain advocacy.",
        "actions": [
            "Provide exclusive early access to upcoming product launches.",
            "Offer dedicated concierge customer support and VIP rewards.",
            "Incentivize user-generated content and referral advocacy programs.",
        ],
        "alert_type": "success",
    },
    "Loyal Customers": {
        "tagline": "⭐ Reliable Core Revenue Generators",
        "description": "Consistent buyers with above-average order frequency and healthy basket sizes.",
        "actions": [
            "Cross-sell and upsell premium category items based on purchase history.",
            "Offer tiered milestone loyalty discounts (e.g. 5th purchase bonus).",
            "Engage through personalized multi-channel product recommendations.",
        ],
        "alert_type": "info",
    },
    "Potential Loyalists": {
        "tagline": "💡 High-Potential Growth Prospects",
        "description": "Recent shoppers with moderate spend who can become core loyalists with targeted nurturing.",
        "actions": [
            "Encourage 2nd and 3rd repeat purchases with time-sensitive coupons.",
            "Recommend complementary accessories and popular category bestsellers.",
            "Enroll in loyalty points program with immediate sign-up rewards.",
        ],
        "alert_type": "warning",
    },
    "At-Risk Customers": {
        "tagline": "⚠️ High-Value Buyers Drifting Away",
        "description": "Used to buy frequently and spend well, but haven't made a purchase in over 30–90 days.",
        "actions": [
            "Deploy urgent 'We Miss You' win-back email and WhatsApp campaigns.",
            "Offer limited-time reactivation voucher (15–20% off basket).",
            "Send short feedback survey to uncover service or product friction.",
        ],
        "alert_type": "error",
    },
    "Lost Customers": {
        "tagline": "🔄 Inactive Dormant Customers",
        "description": "Lowest frequency, lowest spend, and over 90 days since last purchase.",
        "actions": [
            "Launch aggressive clearance or deep-discount reactivation promos.",
            "Audit contact deliverability and sanitize inactive marketing lists.",
            "Focus budget primarily on higher-ROI segments if CAC is prohibitive.",
        ],
        "alert_type": "error",
    },
}


def render() -> None:
    """Render the Customer Segmentation screen."""
    render_page_header(
        title="Customer Segmentation Matrix",
        subtitle="Step 5 of 8: Group customers into 5 value tiers, analyze revenue share, and plan targeted campaigns",
        breadcrumb="Customer Intelligence",
    )

    # Ensure valid data exists in session state
    if "rfm_df" not in st.session_state or st.session_state["rfm_df"] is None:
        if Path(DEFAULT_DATASET_PATH).exists():
            process_and_cache_dataset(DEFAULT_DATASET_PATH, source_label="Default Synthetic Dataset")

    rfm_df = st.session_state.get("rfm_df")
    segment_summary = st.session_state.get("segment_summary")

    if rfm_df is None or rfm_df.empty or segment_summary is None or segment_summary.empty:
        render_empty_state("No segmented RFM data available. Please upload a dataset in Data Upload.")
        return

    # ── Segment Count & Revenue KPI Cards ──────────────────────────────────────
    seg_counts = rfm_df["customer_segment"].value_counts().to_dict()
    champ_count = seg_counts.get("Champions", 0)
    loyal_count = seg_counts.get("Loyal Customers", 0)
    at_risk_count = seg_counts.get("At-Risk Customers", 0)
    lost_count = seg_counts.get("Lost Customers", 0)

    total_custs = len(rfm_df)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        champ_pct = (champ_count / total_custs * 100) if total_custs > 0 else 0
        render_kpi_card("Champions (VIP)", f"{champ_count:,}", delta=f"{champ_pct:.1f}% share", icon="🏆")
    with c2:
        loyal_pct = (loyal_count / total_custs * 100) if total_custs > 0 else 0
        render_kpi_card("Loyal Customers", f"{loyal_count:,}", delta=f"{loyal_pct:.1f}% share", icon="⭐")
    with c3:
        at_risk_pct = (at_risk_count / total_custs * 100) if total_custs > 0 else 0
        render_kpi_card("At-Risk Customers", f"{at_risk_count:,}", delta=f"{at_risk_pct:.1f}% share", icon="⚠️")
    with c4:
        lost_pct = (lost_count / total_custs * 100) if total_custs > 0 else 0
        render_kpi_card("Lost Customers", f"{lost_count:,}", delta=f"{lost_pct:.1f}% share", icon="🔄")

    st.write("")
    st.divider()

    # ── Segment Visuals: Donut vs Revenue Contribution ────────────────────────
    st.markdown("### 📊 Portfolio Segmentation Visuals")
    col_donut, col_rev = st.columns(2)

    with col_donut:
        fig_donut = build_segment_donut(
            segment_summary,
            values_col="customer_count",
            title="Customer Headcount by Segment",
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_rev:
        fig_rev = build_revenue_bar(
            df=segment_summary,
            x_col="customer_segment",
            y_col="total_revenue",
            title="Revenue Contribution by Segment (₹)",
            color_col="customer_segment",
        )
        st.plotly_chart(fig_rev, use_container_width=True)

    st.write("")

    # ── Benchmark Performance Summary Table ────────────────────────────────────
    st.markdown("### 📋 Segment Benchmark Performance Table")
    display_summary = segment_summary.copy()
    display_summary.columns = [
        "Segment",
        "Customers",
        "Customer Share (%)",
        "Total Revenue (₹)",
        "Revenue Share (%)",
        "Avg Recency (Days)",
        "Avg Frequency (Orders)",
        "Avg Spend (₹)",
        "Avg RFM Score",
    ]
    display_summary["Total Revenue (₹)"] = display_summary["Total Revenue (₹)"].apply(lambda v: f"₹{v:,.2f}")
    display_summary["Avg Spend (₹)"] = display_summary["Avg Spend (₹)"].apply(lambda v: f"₹{v:,.2f}")
    display_summary["Customer Share (%)"] = display_summary["Customer Share (%)"].apply(lambda v: f"{v:.1f}%")
    display_summary["Revenue Share (%)"] = display_summary["Revenue Share (%)"].apply(lambda v: f"{v:.1f}%")

    st.dataframe(display_summary, use_container_width=True, hide_index=True)

    st.write("")
    st.divider()

    # ── Interactive Segment Drill-Down & Strategy Explorer ─────────────────────
    st.markdown("### 🎯 Segment Deep-Dive & Marketing Strategy")
    segment_options = ["All Segments"] + SEGMENT_ORDER
    selected_segment = st.selectbox("Select a customer cohort to inspect", segment_options)

    # Strategy Card
    if selected_segment != "All Segments" and selected_segment in SEGMENT_STRATEGIES:
        strat = SEGMENT_STRATEGIES[selected_segment]
        color = SEGMENT_COLOURS.get(selected_segment, "#172554")
        st.markdown(
            f"""
            <div style="border-left: 4px solid {color}; background-color: #FFFFFF; border: 1px solid #E2E8F0;
                        padding: 1.15rem 1.35rem; border-radius: 10px; margin: 0.85rem 0 1.35rem 0;
                        box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
                <h4 style="margin: 0; color: #0F172A; font-size: 1.05rem;">{strat['tagline']}</h4>
                <p style="margin: 0.35rem 0 0.75rem 0; color: #475569; font-size: 0.88rem; line-height: 1.45;">{strat['description']}</p>
                <div style="font-size: 0.82rem; font-weight: 700; color: #0F172A; margin-bottom: 0.35rem;">Recommended Marketing Interventions:</div>
                <ul style="margin: 0 0 0 1.25rem; color: #334155; font-size: 0.85rem; line-height: 1.5;">
                    {''.join(f'<li>{action}</li>' for action in strat['actions'])}
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Filtered customer table
    if selected_segment == "All Segments":
        filtered_df = rfm_df
    else:
        filtered_df = rfm_df[rfm_df["customer_segment"] == selected_segment]

    # Search bar
    search_query = st.text_input("Search customer by ID or Name", "")
    if search_query:
        query = search_query.strip().lower()
        filtered_df = filtered_df[
            filtered_df["customer_id"].str.lower().str.contains(query)
            | filtered_df["customer_name"].str.lower().str.contains(query)
        ]

    st.caption(f"Displaying **{len(filtered_df):,}** customer record(s).")

    cols_to_show = [
        "customer_id",
        "customer_name",
        "customer_segment",
        "activity_band",
        "recency_days",
        "frequency",
        "monetary",
        "rfm_score",
        "rfm_cell",
    ]
    present_cols = [c for c in cols_to_show if c in filtered_df.columns]
    table_display = filtered_df[present_cols].copy()
    if "monetary" in table_display.columns:
        table_display["monetary"] = table_display["monetary"].apply(lambda v: f"₹{v:,.2f}")

    st.dataframe(table_display, use_container_width=True, hide_index=True)

    # Export Segment List CSV
    csv_bytes = filtered_df[present_cols].to_csv(index=False).encode("utf-8")
    filename = f"customers_{selected_segment.lower().replace(' ', '_')}.csv"
    st.download_button(
        label=f"📥 Download '{selected_segment}' Cohort (CSV)",
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
    )

    st.write("")

    # ── Next Step Callout ──────────────────────────────────────────────────────
    st.info(
        "💡 **Cohorts Analyzed:** Proceed to **👤 Customer Details** from the sidebar to drill down into 360° "
        "historical order logs, spend timelines, and customer profile details.",
        icon="👉",
    )
