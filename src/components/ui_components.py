"""
src/components/ui_components.py — Shared UI widgets and Plotly chart builders.
Customer RFM Analysis

Provides consistent styling, KPI metric cards, status badges, and interactive
Plotly visualization builders across all 9 dashboard screens.
"""

from __future__ import annotations

from typing import Any
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.config import (
    APP_TITLE,
    APP_SUBTITLE,
    STUDENT_NAME,
    ROLL_NUMBER,
    SEGMENT_COLOURS,
    ACTIVITY_COLOURS,
    ACTIVITY_LABELS,
)

# Shared typography and chart layout configuration
FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"


# ── Page Header & Banners ─────────────────────────────────────────────────────

def render_page_header(title: str, subtitle: str = "", breadcrumb: str = "Analytics") -> None:
    """
    Render standardized enterprise page header with breadcrumb, metadata, and zero overflow.
    """
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem; padding-bottom: 0.85rem; border-bottom: 1px solid #E2E8F0;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.75rem;">
                <div style="flex: 1; min-width: 280px;">
                    <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; color: #2563EB; margin-bottom: 0.25rem;">
                        {breadcrumb} &nbsp;›&nbsp; <span style="color: #64748B;">{title}</span>
                    </div>
                    <h1 style="margin: 0; padding: 0; font-size: 1.75rem; font-weight: 700; color: #0F172A; letter-spacing: -0.02em; line-height: 1.25;">
                        {title}
                    </h1>
                    <p style="margin: 0.35rem 0 0 0; color: #64748B; font-size: 0.88rem; line-height: 1.4;">
                        {subtitle or APP_SUBTITLE}
                    </p>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 0.45rem 0.85rem; border-radius: 8px; font-size: 0.75rem; color: #334155; box-shadow: 0 1px 2px rgba(0,0,0,0.03); text-align: right;">
                    <div style="font-weight: 600; color: #0F172A;">{STUDENT_NAME} <span style="color: #94A3B8;">•</span> {ROLL_NUMBER}</div>
                    <div style="color: #64748B; font-size: 0.72rem;">ABC Retail Solutions Pvt. Ltd., Noida</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    label: str,
    value: Any,
    delta: str | None = None,
    icon: str | None = None,
    help_text: str | None = None,
) -> None:
    """
    Render a clean metric KPI block with optional delta and icon.
    Uses st.metric for robust Streamlit AppTest compatibility while benefiting from custom CSS styling.
    """
    display_label = f"{icon} {label}" if icon else label
    st.metric(
        label=display_label,
        value=value,
        delta=delta,
        help=help_text,
    )


def render_segment_badge(segment_name: str) -> str:
    """
    Generate HTML badge markup with segment-specific brand color.
    """
    color = SEGMENT_COLOURS.get(segment_name, "#95A5A6")
    return (
        f'<span style="background-color: {color}; color: #FFFFFF; '
        f'padding: 3px 10px; border-radius: 12px; font-size: 0.78rem; '
        f'font-weight: 600; letter-spacing: 0.2px; display: inline-block;">{segment_name}</span>'
    )


def render_activity_badge(activity_band: str) -> str:
    """
    Generate HTML badge markup with activity band color.
    """
    color = ACTIVITY_COLOURS.get(activity_band, "#95A5A6")
    label = ACTIVITY_LABELS.get(activity_band, activity_band)
    return (
        f'<span style="background-color: {color}1A; color: {color}; '
        f'border: 1px solid {color}4D; padding: 2px 8px; border-radius: 6px; '
        f'font-size: 0.75rem; font-weight: 600; display: inline-block;">{label}</span>'
    )


def render_data_quality_banner(quality_report: dict[str, Any]) -> None:
    """
    Render callout banner displaying data hygiene score and row counts in modern Stripe-like alert style.
    """
    score = quality_report.get("data_quality_score", 100.0)
    total = quality_report.get("total_records", 0)
    valid = quality_report.get("valid_records", 0)
    invalid = quality_report.get("invalid_records", 0)

    if score >= 90.0:
        bg_color = "#F0FDF4"
        border_color = "#BBF7D0"
        text_color = "#166534"
        badge_color = "#16A34A"
        icon = "✅"
        status_text = "Optimal Data Hygiene"
    elif score >= 75.0:
        bg_color = "#FFFBEB"
        border_color = "#FDE68A"
        text_color = "#92400E"
        badge_color = "#D97706"
        icon = "⚠️"
        status_text = "Moderate Hygiene Warnings"
    else:
        bg_color = "#FEF2F2"
        border_color = "#FECACA"
        text_color = "#991B1B"
        badge_color = "#DC2626"
        icon = "❌"
        status_text = "Action Required: High Anomaly Rate"

    st.markdown(
        f"""
        <div style="background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 10px;
                    padding: 0.85rem 1.25rem; margin-bottom: 1.25rem; display: flex;
                    justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.65rem;">
                <span style="font-size: 1.25rem;">{icon}</span>
                <div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: {text_color};">
                        {status_text} • Data Quality Score: {score:.1f}%
                    </div>
                    <div style="font-size: 0.78rem; color: #64748B; margin-top: 0.15rem;">
                        Verified against 7 enterprise integrity rules (Missing IDs, Negative Spend, Invalid Dates, etc.)
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 1rem; font-size: 0.8rem; color: #334155;">
                <div>Total Records: <strong>{total:,}</strong></div>
                <div style="color: #16A34A;">Valid: <strong>{valid:,}</strong></div>
                <div style="color: #DC2626;">Flagged: <strong>{invalid:,}</strong></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


render_quality_banner = render_data_quality_banner


def render_empty_state(message: str, icon: str = "📭") -> None:
    """
    Render a clean empty state placeholder.
    """
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2.75rem 1.5rem; background-color: #FFFFFF;
                    border: 1px dashed #CBD5E1; border-radius: 10px; margin: 1.25rem 0; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
            <div style="font-size: 2.25rem; margin-bottom: 0.5rem; opacity: 0.85;">{icon}</div>
            <div style="font-size: 0.95rem; color: #334155; font-weight: 600;">{message}</div>
            <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.25rem;">Upload or reload the transaction dataset to populate this section.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Interactive Plotly Chart Builders ─────────────────────────────────────────

def build_segment_donut(
    segment_summary: pd.DataFrame,
    values_col: str = "customer_count",
    title: str = "Customer Distribution by Segment",
) -> go.Figure:
    """
    Create a polished Plotly donut chart for customer or revenue segment share.
    """
    if segment_summary.empty:
        return go.Figure()

    colors = [
        SEGMENT_COLOURS.get(seg, "#95A5A6")
        for seg in segment_summary["customer_segment"]
    ]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=segment_summary["customer_segment"],
                values=segment_summary[values_col],
                hole=0.55,
                marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
                textinfo="percent+label",
                textfont=dict(family=FONT_FAMILY, size=11),
                hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        template="plotly_white",
        title=dict(text=title, font=dict(family=FONT_FAMILY, size=15, color="#0F172A")),
        font=dict(family=FONT_FAMILY),
        margin=dict(t=45, b=25, l=20, r=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(family=FONT_FAMILY, size=11, color="#475569"),
        ),
        height=380,
    )
    return fig


def build_rfm_3d_scatter(rfm_df: pd.DataFrame) -> go.Figure:
    """
    Create an interactive 3D scatter plot of Recency vs Frequency vs Monetary.
    """
    if rfm_df.empty:
        return go.Figure()

    fig = px.scatter_3d(
        rfm_df,
        x="recency_days",
        y="frequency",
        z="monetary",
        color="customer_segment",
        color_discrete_map=SEGMENT_COLOURS,
        hover_name="customer_name",
        hover_data={
            "customer_id": True,
            "rfm_cell": True,
            "recency_days": True,
            "frequency": True,
            "monetary": ":,.2f",
            "customer_segment": False,
        },
        opacity=0.85,
        title="3D RFM Customer Space (Recency × Frequency × Monetary)",
    )

    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT_FAMILY),
        title=dict(font=dict(family=FONT_FAMILY, size=15, color="#0F172A")),
        scene=dict(
            xaxis=dict(title="Recency (Days)", gridcolor="#F1F5F9", backgroundcolor="#FFFFFF"),
            yaxis=dict(title="Frequency (Orders)", gridcolor="#F1F5F9", backgroundcolor="#FFFFFF"),
            zaxis=dict(title="Monetary Spend (₹)", gridcolor="#F1F5F9", backgroundcolor="#FFFFFF"),
        ),
        margin=dict(t=45, b=20, l=20, r=20),
        height=520,
    )
    return fig


def build_recency_histogram(rfm_df: pd.DataFrame) -> go.Figure:
    """
    Histogram of Recency Days with activity band threshold markers (30d and 90d).
    """
    if rfm_df.empty:
        return go.Figure()

    fig = px.histogram(
        rfm_df,
        x="recency_days",
        nbins=30,
        color="activity_band",
        color_discrete_map=ACTIVITY_COLOURS,
        title="Recency Distribution with Activity Thresholds",
        labels={"recency_days": "Days Since Last Purchase", "count": "Customer Count"},
    )

    # Vertical threshold line at 30 days (Recent -> At-risk)
    fig.add_vline(
        x=30,
        line_dash="dash",
        line_color="#D97706",
        annotation_text="30d (At-Risk)",
        annotation_position="top left",
        annotation_font=dict(family=FONT_FAMILY, size=11, color="#D97706"),
    )
    # Vertical threshold line at 90 days (At-risk -> Inactive)
    fig.add_vline(
        x=90,
        line_dash="dash",
        line_color="#DC2626",
        annotation_text="90d (Inactive)",
        annotation_position="top right",
        annotation_font=dict(family=FONT_FAMILY, size=11, color="#DC2626"),
    )

    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT_FAMILY),
        title=dict(font=dict(family=FONT_FAMILY, size=15, color="#0F172A")),
        xaxis=dict(gridcolor="#F1F5F9", title_font=dict(size=12, color="#475569")),
        yaxis=dict(gridcolor="#F1F5F9", title_font=dict(size=12, color="#475569")),
        bargap=0.08,
        margin=dict(t=45, b=25, l=20, r=20),
        legend=dict(font=dict(family=FONT_FAMILY, size=11, color="#475569")),
        height=380,
    )
    return fig


def build_rfm_heatmap(rfm_df: pd.DataFrame) -> go.Figure:
    """
    2D Heatmap of average Monetary spend indexed by R_Score (rows) vs F_Score (cols).
    """
    if rfm_df.empty or "r_score" not in rfm_df.columns:
        return go.Figure()

    matrix = (
        rfm_df.groupby(["r_score", "f_score"])["monetary"]
        .mean()
        .unstack(level="f_score")
        .fillna(0.0)
    )

    fig = go.Figure(
        data=go.Heatmap(
            z=matrix.values,
            x=[f"F = {col}" for col in matrix.columns],
            y=[f"R = {idx}" for idx in matrix.index],
            colorscale="Blues",
            text=[[f"₹{val:,.0f}" for val in row] for row in matrix.values],
            texttemplate="%{text}",
            textfont=dict(family=FONT_FAMILY, size=11),
            colorbar=dict(title=dict(text="Avg ₹", font=dict(family=FONT_FAMILY, size=11))),
            hovertemplate="<b>%{y} | %{x}</b><br>Avg Spend: ₹%{z:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT_FAMILY),
        title=dict(text="RFM Grid: Average Spend by Recency vs Frequency Score", font=dict(family=FONT_FAMILY, size=15, color="#0F172A")),
        xaxis=dict(title="Frequency Score (1=Low, 5=High)", title_font=dict(size=12, color="#475569")),
        yaxis=dict(title="Recency Score (1=Old, 5=Recent)", title_font=dict(size=12, color="#475569")),
        margin=dict(t=45, b=25, l=20, r=20),
        height=400,
    )
    return fig


def build_revenue_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color_col: str | None = None,
) -> go.Figure:
    """
    Standardized interactive bar chart for revenue breakdowns.
    """
    if df.empty:
        return go.Figure()

    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        text_auto=".2s",
    )

    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT_FAMILY),
        title=dict(font=dict(family=FONT_FAMILY, size=15, color="#0F172A")),
        xaxis=dict(gridcolor="#F1F5F9", title_font=dict(size=12, color="#475569")),
        yaxis=dict(gridcolor="#F1F5F9", title_font=dict(size=12, color="#475569")),
        margin=dict(t=45, b=25, l=20, r=20),
        height=380,
        xaxis_tickangle=-30 if len(df) > 6 else 0,
    )
    return fig
