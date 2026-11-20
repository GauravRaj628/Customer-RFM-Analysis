"""
src/pages/rfm_analysis.py — UI-05: RFM Analysis & Scoring Screen.
Customer RFM Analysis

Student  : Gaurav Raj  |  Roll: 2500320140054
Programme: MCA 2nd Year  |  ABES Engineering College, Ghaziabad
Mentor   : Kalpana Diwedi
Scenario : ABC Retail Solutions Pvt. Ltd., Noida
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.config import (
    DEFAULT_DATASET_PATH,
    DATABASE_PATH,
    COL_DATE,
    SEGMENT_COLOURS,
)
from src.components.ui_components import (
    render_page_header,
    render_kpi_card,
    build_rfm_3d_scatter,
    build_recency_histogram,
    build_rfm_heatmap,
    render_empty_state,
)
from src.pages.data_upload import process_and_cache_dataset
from src.rfm_calculator import calculate_rfm, score_rfm, compute_rfm_summary
from src.segmentation import assign_segments, compute_segment_summary
from src.database import (
    get_connection,
    log_analysis_run,
    save_rfm_results,
    save_segment_summary,
)

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def build_score_bar(score_series: pd.Series, title: str, color_hex: str) -> go.Figure:
    """Build a bar chart showing distribution of scores (1 to 5)."""
    counts = score_series.value_counts().sort_index()
    df_plot = pd.DataFrame({"Score": [f"Score {s}" for s in counts.index], "Count": counts.values})

    fig = px.bar(
        df_plot,
        x="Score",
        y="Count",
        text="Count",
        title=title,
        color_discrete_sequence=[color_hex],
    )
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT_FAMILY),
        title_font=dict(family=FONT_FAMILY, size=13, color="#0F172A"),
        xaxis=dict(title=dict(text=""), gridcolor="#F1F5F9"),
        yaxis=dict(title=dict(text="Customers"), gridcolor="#F1F5F9"),
        margin=dict(l=15, r=15, t=40, b=25),
        height=260,
    )
    fig.update_traces(textposition="outside")
    return fig


def render() -> None:
    """Render the RFM Analysis & Quintile Scoring screen."""
    render_page_header(
        title="RFM Calculation & Scoring Model",
        subtitle="Step 4 of 8: Calculate Recency, Frequency, and Monetary scores and explore 3D customer clustering",
        breadcrumb="Scoring Engine",
    )

    # Auto-load demo if session state is missing
    if "valid_df" not in st.session_state or st.session_state["valid_df"] is None:
        if Path(DEFAULT_DATASET_PATH).exists():
            process_and_cache_dataset(DEFAULT_DATASET_PATH, source_label="Default Synthetic Dataset")

    valid_df = st.session_state.get("valid_df")
    rfm_df = st.session_state.get("rfm_df")

    if valid_df is None or valid_df.empty:
        render_empty_state("No validated transaction data found. Please upload a dataset in Data Upload.")
        return

    # ── Reference Date & Recalculate Controls ──────────────────────────────────
    # Determine default reference date (max transaction date + 1 day)
    default_ref = date(2026, 1, 1)
    if COL_DATE in valid_df.columns:
        valid_dates = pd.to_datetime(valid_df[COL_DATE], errors="coerce").dropna()
        if not valid_dates.empty:
            default_ref = (valid_dates.max() + pd.Timedelta(days=1)).date()

    with st.expander("⚙️ RFM Calculation Parameters & Re-scoring", expanded=True):
        col_date, col_db, col_btn = st.columns([1.2, 1.0, 1.0])
        with col_date:
            selected_date = st.date_input(
                "Reference Date (Cut-off for Recency)",
                value=default_ref,
                help="Transactions after this date are excluded; recency is measured relative to this date.",
            )
        with col_db:
            persist_run = st.checkbox(
                "Persist to SQLite Database",
                value=True,
                help="Log execution run and archive RFM results in data/rfm_analysis.db",
            )
        with col_btn:
            st.write("")
            st.write("")
            if st.button("🔄 Recalculate RFM Scores", type="primary", use_container_width=True):
                with st.spinner("Re-computing RFM scores and customer segmentation..."):
                    new_rfm_raw = calculate_rfm(valid_df, reference_date=selected_date)
                    new_rfm_scored = score_rfm(new_rfm_raw)
                    new_rfm_final = assign_segments(new_rfm_scored)
                    new_seg_summary = compute_segment_summary(new_rfm_final)

                    st.session_state["rfm_df"] = new_rfm_final
                    st.session_state["segment_summary"] = new_seg_summary
                    rfm_df = new_rfm_final

                    if persist_run:
                        try:
                            conn = get_connection(DATABASE_PATH)
                            run_id = log_analysis_run(
                                conn,
                                reference_date=selected_date,
                                customer_count=len(new_rfm_final),
                                total_revenue=float(new_rfm_final["monetary"].sum()),
                                notes=f"Interactive run via UI-05 (ref: {selected_date})",
                            )
                            save_rfm_results(conn, new_rfm_final, run_id=run_id)
                            save_segment_summary(conn, new_seg_summary, run_id=run_id)
                            conn.close()
                            st.success(f"Scores recalculated & logged to database as Run #{run_id}!")
                        except Exception as e:
                            st.warning(f"Recalculated successfully, but SQLite save had an issue: {e}")
                    else:
                        st.success("Scores recalculated successfully in memory!")

    st.write("")

    if rfm_df is None or rfm_df.empty:
        render_empty_state("RFM dataframe is empty.")
        return

    # ── RFM Summary Metrics ────────────────────────────────────────────────────
    summary = compute_rfm_summary(rfm_df)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_kpi_card(
            "Median Recency",
            f"{summary['median_recency_days']:.0f} days",
            icon="⏱️",
            help_text="Lower recency indicates more recent purchasing activity.",
        )
    with m2:
        render_kpi_card(
            "Median Frequency",
            f"{summary['median_frequency']:.0f} orders",
            icon="🛒",
            help_text="Count of distinct completed orders per customer.",
        )
    with m3:
        render_kpi_card(
            "Median Monetary",
            f"₹{summary['median_monetary']:,.2f}",
            icon="💰",
            help_text="Sum of total completed transaction spend.",
        )
    with m4:
        render_kpi_card(
            "Avg Combined Score",
            f"{summary['avg_rfm_score']:.1f} / 15",
            icon="⭐",
            help_text="Composite RFM score (R_Score + F_Score + M_Score, range 3 to 15).",
        )

    st.write("")
    st.divider()

    # ── 3D Interactive Cluster Visualization ───────────────────────────────────
    st.markdown("### 🌐 3D Interactive RFM Customer Space")
    st.caption("Rotate, zoom, and inspect individual customer positions across Recency (x), Frequency (y), and Monetary (z).")
    fig_3d = build_rfm_3d_scatter(rfm_df)
    st.plotly_chart(fig_3d, use_container_width=True)

    st.write("")

    # ── Recency Distribution & Heatmap ─────────────────────────────────────────
    st.markdown("### 📊 Distribution Dynamics & RFM Spending Matrix")
    col_hist, col_heat = st.columns(2)

    with col_hist:
        fig_hist = build_recency_histogram(rfm_df)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_heat:
        fig_heat = build_rfm_heatmap(rfm_df)
        st.plotly_chart(fig_heat, use_container_width=True)

    st.write("")

    # ── Individual Score Component Breakdown (1 to 5) ──────────────────────────
    st.markdown("### 🎯 Quintile Score Distributions (1 to 5)")
    st.caption("Verification of quintile binning across each dimension.")
    s1, s2, s3 = st.columns(3)

    with s1:
        fig_r = build_score_bar(rfm_df["r_score"], "Recency Score (R) — 5 is Best", "#16A34A")
        st.plotly_chart(fig_r, use_container_width=True)

    with s2:
        fig_f = build_score_bar(rfm_df["f_score"], "Frequency Score (F) — 5 is Best", "#2563EB")
        st.plotly_chart(fig_f, use_container_width=True)

    with s3:
        fig_m = build_score_bar(rfm_df["m_score"], "Monetary Score (M) — 5 is Best", "#7C3AED")
        st.plotly_chart(fig_m, use_container_width=True)

    st.write("")

    # ── Next Step Callout ──────────────────────────────────────────────────────
    st.info(
        "💡 **Scoring Complete:** Composite scores assigned from 3 to 15. "
        "Proceed to **🎯 Customer Segmentation** from the sidebar to inspect cohort sizes, revenue concentration, and retention priorities.",
        icon="👉",
    )
