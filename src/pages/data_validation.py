"""
src/pages/data_validation.py — UI-03: Data Validation & Quality Assurance Screen.
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
)
from src.components.ui_components import (
    render_page_header,
    render_kpi_card,
    render_quality_banner,
    render_empty_state,
)
from src.pages.data_upload import process_and_cache_dataset

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def build_validation_donut(valid_count: int, invalid_count: int) -> go.Figure:
    """Build a donut chart showing the split between valid and flagged transactions."""
    labels = ["Valid Records", "Flagged Records"]
    values = [valid_count, invalid_count]
    colors = ["#16A34A", "#DC2626"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
                textinfo="label+percent",
                textfont=dict(family=FONT_FAMILY, size=11),
                hoverinfo="label+value+percent",
            )
        ]
    )
    fig.update_layout(
        template="plotly_white",
        title=dict(text="Transaction Eligibility Split", font=dict(family=FONT_FAMILY, size=14, color="#0F172A")),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(family=FONT_FAMILY, size=11, color="#475569"),
        ),
        margin=dict(l=20, r=20, t=45, b=25),
        height=320,
    )
    return fig


def build_completeness_bar(completeness_dict: dict[str, float]) -> go.Figure:
    """Build a horizontal bar chart displaying column data completeness percentages."""
    df_comp = (
        pd.DataFrame(list(completeness_dict.items()), columns=["Column", "Completeness"])
        .sort_values(by="Completeness", ascending=True)
    )

    fig = px.bar(
        df_comp,
        x="Completeness",
        y="Column",
        orientation="h",
        text=df_comp["Completeness"].apply(lambda v: f"{v:.1f}%"),
        title="Column-Level Completeness Ratio",
        color="Completeness",
        color_continuous_scale=["#DC2626", "#D97706", "#16A34A"],
        range_color=[80, 100],
    )
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT_FAMILY),
        title=dict(font=dict(family=FONT_FAMILY, size=14, color="#0F172A")),
        xaxis=dict(range=[0, 105], title="Non-Null Percentage (%)", gridcolor="#F1F5F9", title_font=dict(size=11, color="#475569")),
        yaxis=dict(title="", tickfont=dict(size=11, color="#0F172A")),
        margin=dict(l=20, r=20, t=45, b=25),
        height=320,
        coloraxis_showscale=False,
    )
    fig.update_traces(textposition="outside", textfont=dict(family=FONT_FAMILY, size=10))
    return fig


def render() -> None:
    """Render the Data Validation & Quality Assurance screen."""
    render_page_header(
        title="Data Quality Assurance & Anomaly Audit",
        subtitle="Step 2 of 8: Inspect transaction integrity, anomaly breakdowns, and column hygiene",
        breadcrumb="Data Management",
    )

    # Auto-load demo if session state is missing
    if "quality_report" not in st.session_state or st.session_state["quality_report"] is None:
        if Path(DEFAULT_DATASET_PATH).exists():
            process_and_cache_dataset(DEFAULT_DATASET_PATH, source_label="Default Synthetic Dataset")

    quality_report = st.session_state.get("quality_report")
    valid_df = st.session_state.get("valid_df")
    invalid_df = st.session_state.get("invalid_df")

    if not quality_report or valid_df is None:
        render_empty_state("No data validation report available. Please upload a dataset in Data Upload.")
        return

    # ── Quality Status Banner ──────────────────────────────────────────────────
    render_quality_banner(quality_report)
    st.write("")

    # ── Quality KPI Cards ──────────────────────────────────────────────────────
    total_recs = quality_report.get("total_records", 0)
    valid_recs = quality_report.get("valid_records", 0)
    invalid_recs = quality_report.get("invalid_records", 0)
    quality_score = quality_report.get("data_quality_score", 100.0)

    q1, q2, q3, q4 = st.columns(4)
    with q1:
        render_kpi_card("Data Quality Score", f"{quality_score:.1f}%", icon="🛡️")
    with q2:
        render_kpi_card("Total Ingested Rows", f"{total_recs:,}", icon="📄")
    with q3:
        render_kpi_card("Eligible Transactions", f"{valid_recs:,}", icon="✅")
    with q4:
        render_kpi_card("Flagged Anomalies", f"{invalid_recs:,}", icon="⚠️")

    st.write("")
    st.divider()

    # ── Validation Visuals ─────────────────────────────────────────────────────
    st.markdown("### 📊 Data Integrity Visualizations")
    col_donut, col_comp = st.columns(2)

    with col_donut:
        fig_donut = build_validation_donut(valid_recs, invalid_recs)
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_comp:
        completeness = quality_report.get("column_completeness", {})
        if completeness:
            fig_comp = build_completeness_bar(completeness)
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            render_empty_state("No column completeness data available.")

    st.write("")

    # ── Issue Summary Breakdown ────────────────────────────────────────────────
    st.markdown("### 📋 Anomaly Classification Summary")
    issue_summary = quality_report.get("issue_summary", [])
    if issue_summary:
        summary_df = pd.DataFrame(issue_summary)
        summary_df.columns = ["Anomaly Classification", "Affected Records", "Impact Ratio (%)"]
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    else:
        st.success("🎉 Perfect dataset! Zero business rule anomalies detected.")

    st.write("")

    # ── Flagged Records Explorer & CSV Export ──────────────────────────────────
    st.markdown("### 🔍 Flagged Records Explorer & Audit Export")
    if invalid_df is not None and not invalid_df.empty:
        st.caption(
            "Below are the records excluded from RFM scoring due to non-positive amounts, "
            "cancellations, returns, or missing identifiers."
        )

        # Filter by issue type
        issue_options = ["All Issues"] + list(quality_report.get("issue_breakdown", {}).keys())
        selected_issue = st.selectbox("Filter records by anomaly category", issue_options)

        if selected_issue == "All Issues":
            filtered_invalid = invalid_df
        else:
            filtered_invalid = invalid_df[
                invalid_df["validation_issue"].str.contains(selected_issue, case=False, na=False)
            ]

        st.dataframe(filtered_invalid, use_container_width=True)

        # Download CSV export
        csv_bytes = filtered_invalid.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Flagged Records (CSV)",
            data=csv_bytes,
            file_name="flagged_transactions_audit.csv",
            mime="text/csv",
        )
    else:
        st.info("No invalid records present in the dataset.")

    st.write("")

    # ── Next Step Callout ──────────────────────────────────────────────────────
    st.info(
        f"💡 **Data Validated:** Clean dataset of **{valid_recs:,} transactions** is approved for RFM segmentation. "
        "Proceed to **🔍 Exploratory Data Analysis** from the sidebar to inspect revenue patterns and category velocity.",
        icon="👉",
    )
