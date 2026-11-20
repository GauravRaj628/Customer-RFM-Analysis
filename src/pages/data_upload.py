"""
src/pages/data_upload.py — UI-02: Data Upload & Ingestion Screen.
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
    REQUIRED_COLUMNS,
    COL_TRANSACTION_ID,
    COL_CUSTOMER_ID,
    COL_ORDER_ID,
    COL_DATE,
    COL_AMOUNT,
    COL_STATUS,
)
from src.components.ui_components import (
    render_page_header,
    render_kpi_card,
    render_empty_state,
)
from src.data_loader import load_data, get_dataset_summary
from src.data_validator import validate_data
from src.rfm_calculator import calculate_rfm, score_rfm
from src.segmentation import assign_segments, compute_segment_summary


def process_and_cache_dataset(source: str | Path | any, source_label: str = "custom") -> bool:
    """
    Ingest raw dataset, run validation, calculate RFM, and cache everything in session state.

    Returns
    -------
    bool
        True if ingestion and pipeline execution succeeded, False otherwise.
    """
    try:
        raw_df = load_data(source)
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
        st.session_state["active_dataset_source"] = source_label
        return True
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return False


def render() -> None:
    """Render the Data Upload & Ingestion screen."""
    render_page_header(
        title="Data Ingestion & Schema Inspector",
        subtitle="Step 1 of 8: Ingest transaction records, verify column schema, and preview raw data",
        breadcrumb="Data Management",
    )

    # ── Ingestion Controls Cards ───────────────────────────────────────────────
    col_upload, col_demo = st.columns([1.1, 0.9])

    with col_upload:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.15rem; box-shadow: 0 1px 2px rgba(0,0,0,0.03); margin-bottom: 0.75rem;">
                <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #2563EB; margin-bottom: 0.25rem;">Custom Source</div>
                <h4 style="margin: 0 0 0.35rem 0; color: #0F172A; font-size: 1.05rem;">📤 Upload Retail Transactions</h4>
                <p style="font-size: 0.82rem; color: #64748B; margin: 0 0 0.75rem 0;">Supports standard retail CSV or Excel workbook files.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel transaction file",
            type=["csv", "xlsx", "xls"],
            help="Supported formats: .csv, .xlsx, .xls (Maximum recommended size: 100MB)",
            label_visibility="collapsed",
        )
        if uploaded_file is not None:
            if st.button("Process Uploaded File", type="primary", use_container_width=True):
                with st.spinner("Ingesting and processing uploaded file..."):
                    if process_and_cache_dataset(uploaded_file, source_label=uploaded_file.name):
                        st.success(f"Successfully loaded '{uploaded_file.name}'!")

    with col_demo:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.15rem; box-shadow: 0 1px 2px rgba(0,0,0,0.03); margin-bottom: 0.75rem;">
                <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #16A34A; margin-bottom: 0.25rem;">Pre-configured Demo</div>
                <h4 style="margin: 0 0 0.35rem 0; color: #0F172A; font-size: 1.05rem;">⚡ Instant Sandbox Dataset</h4>
                <p style="font-size: 0.82rem; color: #64748B; margin: 0 0 0.75rem 0;">5,000 synthetic transactions matching ABC Retail Solutions schema.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📥 Load Default Synthetic Dataset", use_container_width=True):
            with st.spinner("Loading demo transaction dataset..."):
                if process_and_cache_dataset(DEFAULT_DATASET_PATH, source_label="Default Synthetic Dataset"):
                    st.success("Default retail dataset loaded successfully!")

    # Auto-load default if session state is empty
    if "raw_df" not in st.session_state or st.session_state["raw_df"] is None:
        if Path(DEFAULT_DATASET_PATH).exists():
            process_and_cache_dataset(DEFAULT_DATASET_PATH, source_label="Default Synthetic Dataset")

    raw_df = st.session_state.get("raw_df")
    if raw_df is None or raw_df.empty:
        st.write("")
        render_empty_state("No transaction dataset currently loaded. Please upload a file above.")
        return

    st.write("")
    st.divider()

    # ── Dataset Summary Statistics ─────────────────────────────────────────────
    st.markdown("### 📊 Ingested Dataset Summary")
    summary = get_dataset_summary(raw_df)
    source_name = st.session_state.get("active_dataset_source", "Active Dataset")

    st.caption(f"**Active Source:** `{source_name}`")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Total Rows", f"{summary['total_rows']:,}", icon="📄")
    with k2:
        render_kpi_card("Unique Customers", f"{summary['unique_customers']:,}", icon="👥")
    with k3:
        render_kpi_card("Unique Orders", f"{summary['unique_orders']:,}", icon="🛒")
    with k4:
        date_span = f"{summary['min_date']} to {summary['max_date']}" if summary['min_date'] else "N/A"
        render_kpi_card("Date Range", date_span, icon="📅")

    st.write("")

    # ── Schema Verification Checklist ──────────────────────────────────────────
    st.markdown("### 📋 Column Schema Verification")
    st.caption("Verification against required analytics fields defined in `src/config.py`.")

    col_status_list = []
    for col in REQUIRED_COLUMNS:
        present = col in raw_df.columns
        dtype_str = str(raw_df[col].dtype) if present else "Missing"
        sample_val = str(raw_df[col].dropna().iloc[0]) if present and not raw_df[col].dropna().empty else "None"
        col_status_list.append({
            "Column Name": f"`{col}`",
            "Requirement": "Required Core Field",
            "Status": "🟢 Present" if present else "🔴 Missing",
            "Detected Type": f"`{dtype_str}`",
            "Sample Value": sample_val,
        })

    # Optional / Contextual columns
    optional_cols = ["customer_name", "product_category", "product_name", "quantity", "unit_price", "payment_method", "store_region", "city"]
    for col in optional_cols:
        if col in raw_df.columns:
            dtype_str = str(raw_df[col].dtype)
            sample_val = str(raw_df[col].dropna().iloc[0]) if not raw_df[col].dropna().empty else "None"
            col_status_list.append({
                "Column Name": f"`{col}`",
                "Requirement": "Contextual Field",
                "Status": "🟢 Present",
                "Detected Type": f"`{dtype_str}`",
                "Sample Value": sample_val,
            })

    schema_df = pd.DataFrame(col_status_list)
    st.dataframe(schema_df, use_container_width=True, hide_index=True)

    st.write("")

    # ── Raw Data Preview ───────────────────────────────────────────────────────
    st.markdown("### 🔍 Raw Transaction Data Preview")
    preview_limit = st.slider("Number of preview rows", min_value=5, max_value=100, value=20, step=5)
    st.dataframe(raw_df.head(preview_limit), use_container_width=True)

    st.write("")

    # ── Next Step Callout ──────────────────────────────────────────────────────
    st.info(
        "💡 **Data Ready for Validation:** Proceed to **✅ Data Validation** from the sidebar to inspect anomalies, "
        "examine negative amounts, check cancellation rates, and review the data hygiene report.",
        icon="👉",
    )
