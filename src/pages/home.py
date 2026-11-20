"""
src/pages/home.py — UI-01: Home / Executive Overview Screen.
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
    APP_TITLE,
    APP_SUBTITLE,
    STUDENT_NAME,
    ROLL_NUMBER,
    PROGRAMME,
    INSTITUTION,
    MENTOR,
    DEFAULT_DATASET_PATH,
    DATABASE_PATH,
    SEGMENT_COLOURS,
    ACTIVITY_LABELS,
    ACTIVITY_COLOURS,
)
from src.components.ui_components import (
    render_page_header,
    render_kpi_card,
    build_segment_donut,
    render_activity_badge,
    render_segment_badge,
    render_empty_state,
)
from src.data_loader import load_data
from src.data_validator import validate_data
from src.rfm_calculator import calculate_rfm, score_rfm
from src.segmentation import assign_segments, compute_segment_summary
from src.database import get_connection, load_rfm_results, load_segment_summary, list_analysis_runs


def ensure_demo_data_loaded() -> None:
    """
    Ensure standard session state is initialized with RFM data.
    Attempts to read from SQLite database first, then raw dataset fallback.
    """
    if "rfm_df" in st.session_state and st.session_state["rfm_df"] is not None:
        return

    # Try loading from existing SQLite database
    db_file = Path(DATABASE_PATH)
    if db_file.exists():
        try:
            conn = get_connection(DATABASE_PATH)
            rfm = load_rfm_results(conn)
            seg = load_segment_summary(conn)
            conn.close()
            if not rfm.empty and not seg.empty:
                st.session_state["rfm_df"] = rfm
                st.session_state["segment_summary"] = seg
                return
        except Exception:
            pass

    # Fallback: compute from default dataset CSV
    csv_file = Path(DEFAULT_DATASET_PATH)
    if csv_file.exists():
        try:
            raw_df = load_data(csv_file)
            valid_df, invalid_df, quality_report = validate_data(raw_df)
            rfm_raw = calculate_rfm(valid_df)
            rfm_scored = score_rfm(rfm_raw)
            rfm_final = assign_segments(rfm_scored)
            seg_summary = compute_segment_summary(rfm_final)

            st.session_state["raw_df"] = raw_df
            st.session_state["valid_df"] = valid_df
            st.session_state["invalid_df"] = invalid_df
            st.session_state["quality_report"] = quality_report
            st.session_state["rfm_df"] = rfm_final
            st.session_state["segment_summary"] = seg_summary
        except Exception:
            pass


def render() -> None:
    """Render the Home / Overview dashboard screen."""
    render_page_header(
        title="Customer RFM Analysis & Segmentation",
        subtitle=f"Executive Overview & Strategic Portfolio Intelligence | {APP_SUBTITLE}",
        breadcrumb="Dashboard",
    )

    # ── Executive Hero Card (Clean SaaS Light Style) ───────────────────────────
    st.markdown(
        f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #2563EB;
                    border-radius: 12px; padding: 1.15rem 1.4rem; margin-bottom: 1.5rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div style="flex: 1; min-width: 280px;">
                    <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #2563EB; margin-bottom: 0.25rem;">
                        Enterprise Retail Intelligence Suite
                    </div>
                    <h2 style="margin: 0; color: #0F172A; font-size: 1.35rem; font-weight: 700; letter-spacing: -0.01em;">
                        ABC Retail Solutions — Customer Lifecycle & RFM Analytics
                    </h2>
                    <p style="margin: 0.35rem 0 0 0; color: #64748B; font-size: 0.88rem; line-height: 1.4;">
                        Algorithmic segmentation model classifying retail patrons by Recency, Frequency, and Monetary spend to drive targeted retention.
                    </p>
                </div>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.6rem 0.9rem; font-size: 0.78rem; color: #334155;">
                    <div style="font-weight: 600; color: #0F172A;">{STUDENT_NAME} ({ROLL_NUMBER})</div>
                    <div style="color: #64748B; margin-top: 0.15rem;">Mentor: {MENTOR} • {PROGRAMME}</div>
                    <div style="color: #94A3B8; font-size: 0.72rem; margin-top: 0.15rem;">{INSTITUTION}, Ghaziabad</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Ensure data is populated
    ensure_demo_data_loaded()

    rfm_df = st.session_state.get("rfm_df")
    segment_summary = st.session_state.get("segment_summary")
    valid_df = st.session_state.get("valid_df")

    # ── Executive KPI Metrics ──────────────────────────────────────────────────
    if rfm_df is not None and not rfm_df.empty:
        total_customers = len(rfm_df)
        total_revenue = float(rfm_df["monetary"].sum())
        total_orders = int(rfm_df["frequency"].sum())
        rec_col = "recency_days" if "recency_days" in rfm_df.columns else "recency"
        avg_recency = float(rfm_df[rec_col].mean())

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_kpi_card("Total Customers", f"{total_customers:,}", icon="👥")
        with m2:
            render_kpi_card("Total Revenue", f"₹{total_revenue:,.2f}", icon="💰")
        with m3:
            render_kpi_card("Total Completed Orders", f"{int(total_orders):,}", icon="🛒")
        with m4:
            render_kpi_card("Avg Recency", f"{avg_recency:.1f} days", icon="⏱️")
    else:
        render_empty_state("No active analysis data found. Please upload a dataset in Data Upload or reload demo data.")
        return

    st.write("")

    # ── Segment Distribution & Activity Breakdown ─────────────────────────────
    st.subheader("📊 Customer Portfolio Breakdown")
    col_chart, col_activity = st.columns([1.1, 0.9])

    with col_chart:
        st.markdown("##### Customer Segment Distribution")
        if segment_summary is not None and not segment_summary.empty:
            fig_donut = build_segment_donut(segment_summary)
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            render_empty_state("Segment summary data is unavailable.")

    with col_activity:
        st.markdown("##### Customer Activity Status")
        if "activity_band" in rfm_df.columns:
            activity_counts = rfm_df["activity_band"].value_counts()
            for band in ["Recent", "At-risk", "Inactive"]:
                count = int(activity_counts.get(band, 0))
                pct = (count / total_customers * 100) if total_customers > 0 else 0
                label = ACTIVITY_LABELS.get(band, band)
                color = ACTIVITY_COLOURS.get(band, "#4A5568")

                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span style="font-weight: 600; color: {color};">{label}</span>
                        <span><strong>{count:,}</strong> ({pct:.1f}%)</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(pct / 100)

            st.write("")
            st.caption(
                "• **Recent:** 0–30 days since last purchase  \n"
                "• **At-risk:** 31–90 days since last purchase  \n"
                "• **Inactive:** >90 days since last purchase"
            )

    st.write("")
    st.divider()

    # ── Project Scope & RFM Architecture ──────────────────────────────────────
    st.subheader("🎯 Project Methodology & Business Architecture")
    m_col1, m_col2, m_col3 = st.columns(3)

    with m_col1:
        st.markdown(
            """
            <div style="border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.15rem; height: 100%; background: #FFFFFF; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
                <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #2563EB; margin-bottom: 0.35rem;">Strategic Context</div>
                <h4 style="margin: 0 0 0.5rem 0; color: #0F172A; font-size: 1.05rem;">🏢 Business Objective</h4>
                <p style="font-size: 0.86rem; color: #475569; line-height: 1.5; margin: 0;">
                    Equip <strong>ABC Retail Solutions Pvt. Ltd.</strong> with granular customer value intelligence.
                    Mitigate churn, reward loyal buyers, and optimize promotional budgets through targeted cohort marketing.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m_col2:
        st.markdown(
            """
            <div style="border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.15rem; height: 100%; background: #FFFFFF; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
                <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #2563EB; margin-bottom: 0.35rem;">Mathematical Framework</div>
                <h4 style="margin: 0 0 0.5rem 0; color: #0F172A; font-size: 1.05rem;">📐 RFM Scoring Model</h4>
                <p style="font-size: 0.86rem; color: #475569; line-height: 1.5; margin: 0;">
                    <strong>Recency (R):</strong> Days since last purchase (reversed quintiles 1–5).<br/>
                    <strong>Frequency (F):</strong> Count of distinct completed orders (1–5).<br/>
                    <strong>Monetary (M):</strong> Sum of completed transaction amounts (1–5).<br/>
                    <em>Composite Score: 3 to 15 points.</em>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m_col3:
        st.markdown(
            """
            <div style="border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.15rem; height: 100%; background: #FFFFFF; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
                <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #2563EB; margin-bottom: 0.35rem;">Engineering Pipeline</div>
                <h4 style="margin: 0 0 0.5rem 0; color: #0F172A; font-size: 1.05rem;">⚙️ Analytics Pipeline</h4>
                <p style="font-size: 0.86rem; color: #475569; line-height: 1.5; margin: 0;">
                    Automated data validation & anomaly auditing, SQL persistence with parameterized queries,
                    interactive Plotly 3D visualizers, and comprehensive pytest verification suites.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # ── Dashboard Navigation Quick Guide ──────────────────────────────────────
    st.subheader("🗺️ Dashboard Navigation Guide")
    st.caption("Access all 8 analytical modules from the left navigation sidebar:")

    nav1, nav2, nav3, nav4 = st.columns(4)
    with nav1:
        st.markdown("**1. 📂 Data Upload**\nIngest transactional CSV or Excel files with preview and column verification.")
        st.markdown("**2. ✅ Data Validation**\nAudit negative amounts, missing IDs, invalid statuses, and hygiene scores.")
    with nav2:
        st.markdown("**3. 🔍 Exploratory Data Analysis**\nExplore monthly revenue velocity, top categories, and store regional trends.")
        st.markdown("**4. 📈 RFM Analysis**\nReview quantile distribution, 3D RFM scatter, and 5×5 scoring heatmaps.")
    with nav3:
        st.markdown("**5. 🎯 Customer Segmentation**\nAnalyze Champions, Loyal, Potential, At-Risk, and Lost customer cohorts.")
        st.markdown("**6. 👤 Customer Details**\nSearch individual customer 360° profiles, historical orders, and segment flags.")
    with nav4:
        st.markdown("**7. 💰 Revenue Analysis**\nTrack revenue concentration, Pareto 80/20 distribution, and customer lifetime value.")
        st.markdown("**8. 💡 Business Insights**\nAccess automated executive recommendations and targeted marketing strategies.")
