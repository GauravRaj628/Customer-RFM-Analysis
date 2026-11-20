"""
app.py — Customer RFM Analysis Dashboard
Main Streamlit application entry point and multi-page router.

Student  : Gaurav Raj  |  Roll: 2500320140054
Programme: MCA 2nd Year  |  ABES Engineering College, Ghaziabad
Mentor   : Kalpana Diwedi
Scenario : ABC Retail Solutions Pvt. Ltd., Noida
"""

from __future__ import annotations

from pathlib import Path
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
)
from src.pages.data_upload import process_and_cache_dataset

# ── Streamlit Page Configuration ───────────────────────────────────────────────
st.set_page_config(
    page_title=f"{APP_TITLE} — ABC Retail Solutions",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            f"**{APP_TITLE} Dashboard**\n\n"
            f"MCA Capstone Project • {INSTITUTION}, Ghaziabad\n\n"
            f"**Student:** {STUDENT_NAME} ({ROLL_NUMBER})\n\n"
            f"**Mentor:** {MENTOR}\n\n"
            f"**Client Scenario:** {APP_SUBTITLE}"
        )
    },
)

# ── Global Custom Styling (SaaS Light Theme) ──────────────────────────────────
st.markdown(
    """
    <style>
        /* Modern Inter font and global light canvas */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #0F172A;
            background-color: #F8FAFC;
        }

        /* Main container layout */
        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        /* Metric cards styling (Stripe / Linear KPI cards) */
        [data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 1rem 1.15rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }
        [data-testid="stMetric"]:hover {
            border-color: #CBD5E1;
            box-shadow: 0 4px 8px -2px rgba(0, 0, 0, 0.06);
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.76rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            color: #64748B !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.65rem !important;
            font-weight: 700 !important;
            color: #0F172A !important;
            letter-spacing: -0.02em !important;
        }

        /* Button styling */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.85rem;
            padding: 0.45rem 1rem;
            border: 1px solid #E2E8F0;
            background-color: #FFFFFF;
            color: #0F172A;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
            transition: all 0.15s ease-in-out;
        }
        .stButton>button:hover {
            border-color: #CBD5E1;
            background-color: #F8FAFC;
            color: #2563EB;
        }
        .stButton>button[kind="primary"] {
            background-color: #2563EB;
            color: #FFFFFF;
            border: 1px solid #1D4ED8;
            box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2);
        }
        .stButton>button[kind="primary"]:hover {
            background-color: #1D4ED8;
            color: #FFFFFF;
        }

        /* Sidebar container styling */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.25rem;
            padding-bottom: 2rem;
        }

        /* Sidebar Brand Card */
        .sidebar-brand-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1.15rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }
        .sidebar-brand-icon {
            width: 38px;
            height: 38px;
            background: linear-gradient(135deg, #172554 0%, #2563EB 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #FFFFFF;
            font-weight: 800;
            font-size: 1.1rem;
            flex-shrink: 0;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
        }
        .sidebar-brand-info {
            overflow: hidden;
        }
        .sidebar-brand-title {
            font-size: 0.92rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.2;
            letter-spacing: -0.01em;
            white-space: nowrap;
        }
        .sidebar-brand-sub {
            font-size: 0.72rem;
            color: #64748B;
            margin-top: 0.15rem;
            white-space: nowrap;
        }

        /* Modern card-style sidebar navigation */
        section[data-testid="stSidebar"] [class*="st-key-nav_"] {
            margin: 0 0 0.48rem 0;
        }
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button {
            width: 100%;
            min-height: 2.72rem;
            justify-content: flex-start;
            text-align: left;
            padding: 0.58rem 0.82rem;
            border: 1px solid #E2EAF5;
            border-radius: 12px;
            background: #FFFFFF;
            color: #172554;
            font-size: 0.91rem;
            font-weight: 550;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.035);
            transition: background .18s ease, border-color .18s ease,
                        box-shadow .18s ease, transform .18s ease;
        }
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button:hover {
            background: #EFF6FF;
            border-color: #93C5FD;
            color: #1D4ED8;
            box-shadow: 0 5px 12px rgba(37, 99, 235, 0.09);
            transform: translateY(-1px);
        }
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"] {
            background: linear-gradient(110deg, #2563EB 0%, #1D4ED8 100%);
            color: #FFFFFF !important;
            border-color: #2563EB;
            box-shadow: 0 5px 13px rgba(37, 99, 235, 0.20);
        }
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"] p,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"] span {
            color: #FFFFFF !important;
        }
        .sidebar-nav-heading {
            margin: 1.05rem 0 0.55rem 0.2rem;
            color: #64748B;
            font-size: 0.70rem;
            font-weight: 800;
            letter-spacing: .09em;
            text-transform: uppercase;
        }
        .sidebar-brand-card {
            background: linear-gradient(135deg, #172554 0%, #1E40AF 100%);
            border: 1px solid #1D4ED8;
            border-radius: 15px;
            padding: 1rem 0.85rem;
            box-shadow: 0 7px 18px rgba(30, 64, 175, .16);
        }
        .sidebar-brand-title { color: #FFFFFF; }
        .sidebar-brand-sub { color: #DBEAFE; }
        .sidebar-brand-icon {
            width: 44px; height: 44px; border-radius: 12px;
            background: rgba(255,255,255,.16);
            border: 1px solid rgba(255,255,255,.25);
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] .sidebar-nav-heading {
            color: #64748B !important;
        }

        /* Sidebar Telemetry Card */
        .sidebar-telemetry-box {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 0.75rem 0.85rem;
            font-size: 0.78rem;
            margin-bottom: 0.85rem;
        }
        .sidebar-telemetry-status {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            color: #16A34A;
            font-weight: 600;
            margin-bottom: 0.35rem;
        }

        /* Dataframe styling */
        [data-testid="stDataFrame"] {
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            overflow: hidden;
            background: #FFFFFF;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Global visual polish and light-theme safeguards ──────────────────────────
# Streamlit's config.toml also sets the base theme to light. These overrides
# keep embedded HTML, native widgets, dialogs and data elements visually aligned.
st.markdown(
    """
    <style>
      :root {
        color-scheme: light;
        --rfm-ink: #0f172a;
        --rfm-muted: #64748b;
        --rfm-border: #e2e8f0;
        --rfm-canvas: #f8fafc;
        --rfm-blue: #2563eb;
      }
      html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
      [data-testid="stHeader"] {
        background: var(--rfm-canvas) !important;
        color: var(--rfm-ink) !important;
      }
      [data-testid="stHeader"] { background: rgba(248,250,252,.92) !important; }
      [data-testid="stMainBlockContainer"] {
        max-width: 1440px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
      }
      [data-testid="stSidebar"] {
        background: #fff !important;
        border-right: 1px solid var(--rfm-border);
      }
      [data-testid="stSidebar"] * { color: #334155; }
      section[data-testid="stSidebar"] .sidebar-brand-title { color: #fff !important; }
      section[data-testid="stSidebar"] .sidebar-brand-sub { color: #dbeafe !important; }
      section[data-testid="stSidebar"] .sidebar-brand-icon { color: #fff !important; }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #64748b;
      }
      h1, h2, h3, h4, p, label, [data-testid="stCaptionContainer"] {
        color: var(--rfm-ink);
      }
      [data-testid="stMetric"] {
        background: #fff !important;
        border: 1px solid var(--rfm-border) !important;
        border-radius: 14px !important;
        padding: 1rem 1.1rem !important;
        box-shadow: 0 3px 12px rgba(15,23,42,.045) !important;
      }
      [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
        color: #64748b !important;
      }
      [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
        color: #0f172a !important;
        font-weight: 750 !important;
      }
      [data-testid="stPlotlyChart"], [data-testid="stDataFrame"],
      [data-testid="stTable"] {
        background: #fff;
        border: 1px solid var(--rfm-border);
        border-radius: 12px;
        overflow: hidden;
      }
      .stButton > button, .stDownloadButton > button {
        border-radius: 9px !important;
        font-weight: 600 !important;
        min-height: 2.45rem;
        transition: all .16s ease;
      }
      .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: #93c5fd !important;
        color: #1d4ed8 !important;
        box-shadow: 0 3px 10px rgba(37,99,235,.09);
      }
      button[kind="primary"] {
        background: #2563eb !important;
        border-color: #2563eb !important;
        color: #fff !important;
      }
      [data-testid="stDialog"], [role="dialog"] {
        background: #fff !important;
        color: #0f172a !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 18px !important;
        box-shadow: 0 24px 70px rgba(15,23,42,.22) !important;
      }
      [data-testid="stDialog"] [data-testid="stMarkdownContainer"],
      [role="dialog"] [data-testid="stMarkdownContainer"] {
        color: #334155 !important;
      }
      [data-testid="stDialog"] h1, [data-testid="stDialog"] h2,
      [data-testid="stDialog"] h3, [role="dialog"] h1,
      [role="dialog"] h2, [role="dialog"] h3 {
        color: #0f172a !important;
      }
      [data-testid="stDialog"] p, [role="dialog"] p {
        color: #475569 !important;
      }
      [data-testid="stDialog"] [data-testid="stMarkdownContainer"] strong,
      [role="dialog"] [data-testid="stMarkdownContainer"] strong {
        color: #0f172a !important;
      }
      [data-testid="stDialog"] button[aria-label="Close"],
      [role="dialog"] button[aria-label="Close"] {
        color: #475569 !important;
      }
      hr { border-color: #e2e8f0 !important; }
      @media (max-width: 768px) {
        [data-testid="stMainBlockContainer"] {
          padding-left: 1rem;
          padding-right: 1rem;
        }
        [data-testid="stMetric"] { padding: .8rem !important; }
      }
      @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { transition: none !important; animation: none !important; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Automatic Session State Initialization ─────────────────────────────────────
if (
    "valid_df" not in st.session_state
    or st.session_state["valid_df"] is None
    or "rfm_df" not in st.session_state
    or st.session_state["rfm_df"] is None
):
    if Path(DEFAULT_DATASET_PATH).exists():
        process_and_cache_dataset(DEFAULT_DATASET_PATH, source_label="Default Synthetic Dataset")

# ── About This Project Modal (Native Streamlit Dialog) ────────────────────────
@st.dialog("About This Project")
def show_about_modal() -> None:
    """
    Render a clean, modern, balanced white modal dialog for project and academic attributions.
    """
    st.markdown(
        f"""
        <div style="padding: 0.25rem 0 0.5rem 0;">
            <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #2563EB; margin-bottom: 0.25rem;">
                MCA Capstone Project • Batch 2024–2026
            </div>
            <h2 style="margin: 0; font-size: 1.35rem; font-weight: 700; color: #0F172A; letter-spacing: -0.01em;">
                Customer RFM Analysis Dashboard
            </h2>
            <p style="margin: 0.35rem 0 1rem 0; font-size: 0.85rem; color: #64748B; line-height: 1.45;">
                An enterprise-grade customer intelligence and behavioral segmentation platform developed for 
                <strong>ABC Retail Solutions Pvt. Ltd., Noida</strong> to mitigate churn and optimize customer lifetime value.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.markdown(
            f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.85rem; font-size: 0.82rem; height: 100%;">
                <div style="font-weight: 700; color: #0F172A; margin-bottom: 0.35rem; display: flex; align-items: center; gap: 0.35rem;">
                    <span>🎓</span> Academic Details
                </div>
                <div style="color: #475569; line-height: 1.5;">
                    <strong>Student:</strong> {STUDENT_NAME}<br/>
                    <strong>Roll No:</strong> <code>{ROLL_NUMBER}</code><br/>
                    <strong>Programme:</strong> {PROGRAMME}<br/>
                    <strong>Institution:</strong> {INSTITUTION}, Ghaziabad<br/>
                    <strong>Faculty Mentor:</strong> {MENTOR}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_meta2:
        st.markdown(
            f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.85rem; font-size: 0.82rem; height: 100%;">
                <div style="font-weight: 700; color: #0F172A; margin-bottom: 0.35rem; display: flex; align-items: center; gap: 0.35rem;">
                    <span>🏢</span> Business Scenario
                </div>
                <div style="color: #475569; line-height: 1.5;">
                    <strong>Organization:</strong> ABC Retail Solutions Pvt. Ltd.<br/>
                    <strong>Location:</strong> Noida, NCR, India<br/>
                    <strong>Division:</strong> Omnichannel Retail & E-Commerce<br/>
                    <strong>Strategic Goal:</strong> Churn Mitigation & RFM Segmentation
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.85rem; font-size: 0.8rem; color: #475569;">
            <div style="font-weight: 700; color: #0F172A; margin-bottom: 0.3rem;">⚙️ Architecture & Quality Assurance</div>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.4rem;">
                <span style="background: #F1F5F9; border: 1px solid #E2E8F0; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">Python</span>
                <span style="background: #F1F5F9; border: 1px solid #E2E8F0; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">Streamlit</span>
                <span style="background: #F1F5F9; border: 1px solid #E2E8F0; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">Pandas & NumPy</span>
                <span style="background: #F1F5F9; border: 1px solid #E2E8F0; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">Plotly Visuals</span>
                <span style="background: #F1F5F9; border: 1px solid #E2E8F0; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">SQLite Persistence</span>
                <span style="background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">Automated test suite</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("Close", use_container_width=True):
        st.rerun()


# ── Sidebar Navigation & Controls ─────────────────────────────────────────────
PAGES = {
    "🏠  Home / Overview": "home",
    "📂  Data Upload": "data_upload",
    "✅  Data Validation": "data_validation",
    "🔍  Exploratory Data Analysis": "eda_page",
    "📈  RFM Analysis": "rfm_analysis",
    "🎯  Customer Segmentation": "segmentation_page",
    "👤  Customer Details": "customer_details",
    "💰  Revenue Analysis": "revenue_analysis",
    "💡  Business Insights": "business_insights",
}

# Keep the selected page in session state so card-style buttons behave like
# persistent navigation rather than one-shot actions.
if "selected_page_key" not in st.session_state:
    st.session_state["selected_page_key"] = "home"

with st.sidebar:
    # ── 1. Clean Brand Header ──
    st.markdown(
        """
        <div class="sidebar-brand-card">
            <div class="sidebar-brand-icon">📊</div>
            <div class="sidebar-brand-info">
                <div class="sidebar-brand-title">Customer RFM Analysis</div>
                <div class="sidebar-brand-sub">ABC Retail Solutions • Analytics</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── 2. Modern grouped navigation cards ──
    navigation_groups = {
        "MAIN": [
            ("🏠", "Home / Overview", "home"),
            ("📂", "Data Upload", "data_upload"),
            ("✅", "Data Validation", "data_validation"),
        ],
        "ANALYSIS": [
            ("📊", "Exploratory Data Analysis", "eda_page"),
            ("📈", "RFM Analysis", "rfm_analysis"),
            ("🎯", "Customer Segmentation", "segmentation_page"),
        ],
        "BUSINESS": [
            ("👤", "Customer Details", "customer_details"),
            ("₹", "Revenue Analysis", "revenue_analysis"),
            ("💡", "Business Insights", "business_insights"),
        ],
    }
    for group_name, items in navigation_groups.items():
        st.markdown(f'<div class="sidebar-nav-heading">{group_name}</div>', unsafe_allow_html=True)
        for icon, label, page_key in items:
            is_active = st.session_state["selected_page_key"] == page_key
            if st.button(
                f"{icon}   {label}",
                key=f"nav_{page_key}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state["selected_page_key"] = page_key
                st.rerun()
    st.divider()

    # ── 3. Active Telemetry Indicator ──
    rfm_df = st.session_state.get("rfm_df")
    if rfm_df is not None and not rfm_df.empty:
        cust_cnt = len(rfm_df)
        total_rev = float(rfm_df["monetary"].sum())
        st.markdown(
            f"""
            <div class="sidebar-telemetry-box">
                <div class="sidebar-telemetry-status">
                    <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #16A34A;"></span>
                    <span>Active Analytical Cache</span>
                </div>
                <div style="display: flex; justify-content: space-between; color: #475569; margin-top: 0.35rem;">
                    <span>Customers:</span>
                    <strong style="color: #0F172A;">{cust_cnt:,}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; color: #475569; margin-top: 0.15rem;">
                    <span>Total Revenue:</span>
                    <strong style="color: #0F172A;">₹{total_rev:,.0f}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── 4. Quick Actions ──
    if st.button("🔄 Reload Demo Dataset", use_container_width=True, help="Reset analytical session and load clean 5,000 synthetic transactions"):
        st.session_state.clear()
        if Path(DEFAULT_DATASET_PATH).exists():
            process_and_cache_dataset(DEFAULT_DATASET_PATH, source_label="Default Synthetic Dataset")
        st.rerun()

    # ── 5. About This Project Button (Modal Dialog) ──
    if st.button("ℹ️ About This Project", use_container_width=True, help="View project academic attributions, mentor guidance, and architecture details"):
        show_about_modal()

    # ── 6. Minimal Footer ──
    st.markdown(
        f"""
        <div style="font-size: 0.72rem; color: #94A3B8; text-align: center; margin-top: 1rem; border-top: 1px solid #E2E8F0; padding-top: 0.65rem;">
            {STUDENT_NAME} • {ROLL_NUMBER}<br/>
            ABES Engineering College
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Dynamic Page Routing ───────────────────────────────────────────────────────
page_key = st.session_state.get("selected_page_key", "home")

try:
    if page_key == "home":
        from src.pages.home import render
        render()
    elif page_key == "data_upload":
        from src.pages.data_upload import render
        render()
    elif page_key == "data_validation":
        from src.pages.data_validation import render
        render()
    elif page_key == "eda_page":
        from src.pages.eda_page import render
        render()
    elif page_key == "rfm_analysis":
        from src.pages.rfm_analysis import render
        render()
    elif page_key == "segmentation_page":
        from src.pages.segmentation_page import render
        render()
    elif page_key == "customer_details":
        from src.pages.customer_details import render
        render()
    elif page_key == "revenue_analysis":
        from src.pages.revenue_analysis import render
        render()
    elif page_key == "business_insights":
        from src.pages.business_insights import render
        render()
except Exception as e:
    st.error(f"❌ An error occurred while rendering **{selected_page}**: {e}")
    st.exception(e)
