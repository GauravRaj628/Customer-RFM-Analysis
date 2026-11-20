"""
tests/test_ui_components.py — Unit tests for UI components and Plotly chart builders.
Customer RFM Analysis
"""

import pytest
import pandas as pd
import plotly.graph_objects as go
from src.components.ui_components import (
    render_segment_badge,
    render_activity_badge,
    build_segment_donut,
    build_rfm_3d_scatter,
    build_recency_histogram,
    build_rfm_heatmap,
    build_revenue_bar,
)
from src.rfm_calculator import calculate_rfm, score_rfm
from src.segmentation import assign_segments, compute_segment_summary


def test_render_segment_badge():
    """Verify segment badge HTML markup and color inclusion."""
    badge = render_segment_badge("Champions")
    assert "Champions" in badge
    assert "#2ECC71" in badge
    assert "<span" in badge


def test_render_activity_badge():
    """Verify activity band badge HTML markup and icon label."""
    badge_recent = render_activity_badge("Recent")
    assert "Recent" in badge_recent
    badge_inactive = render_activity_badge("Inactive")
    assert "Inactive" in badge_inactive


def test_build_segment_donut(sample_valid_df):
    """Verify segment donut chart trace configuration."""
    rfm = calculate_rfm(sample_valid_df)
    scored = score_rfm(rfm)
    segmented = assign_segments(scored)
    summary = compute_segment_summary(segmented)

    fig = build_segment_donut(summary)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "pie"
    assert fig.data[0].hole == 0.55


def test_build_rfm_3d_scatter(sample_valid_df):
    """Verify 3D scatter chart configuration."""
    rfm = calculate_rfm(sample_valid_df)
    scored = score_rfm(rfm)
    segmented = assign_segments(scored)

    fig = build_rfm_3d_scatter(segmented)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1
    assert fig.data[0].type == "scatter3d"


def test_build_recency_histogram(sample_valid_df):
    """Verify recency histogram and activity threshold vertical lines."""
    rfm = calculate_rfm(sample_valid_df)
    scored = score_rfm(rfm)
    segmented = assign_segments(scored)

    fig = build_recency_histogram(segmented)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1
    assert fig.data[0].type == "histogram"
    # Verify shape lines at 30 and 90 days exist
    assert len(fig.layout.shapes) >= 2


def test_build_rfm_heatmap(sample_valid_df):
    """Verify RFM matrix heatmap builder."""
    rfm = calculate_rfm(sample_valid_df)
    scored = score_rfm(rfm)
    segmented = assign_segments(scored)

    fig = build_rfm_heatmap(segmented)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "heatmap"


def test_build_revenue_bar():
    """Verify revenue bar chart builder."""
    df = pd.DataFrame({
        "category": ["Electronics", "Clothing"],
        "revenue": [50000.0, 30000.0],
    })
    fig = build_revenue_bar(df, "category", "revenue", "Revenue Test")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "bar"


def test_empty_chart_builders():
    """Verify chart builders gracefully return empty Figure when passed empty DataFrame."""
    empty_df = pd.DataFrame()
    assert isinstance(build_segment_donut(empty_df), go.Figure)
    assert isinstance(build_rfm_3d_scatter(empty_df), go.Figure)
    assert isinstance(build_recency_histogram(empty_df), go.Figure)
    assert isinstance(build_rfm_heatmap(empty_df), go.Figure)
    assert isinstance(build_revenue_bar(empty_df, "x", "y", "t"), go.Figure)
