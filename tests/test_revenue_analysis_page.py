"""
tests/test_revenue_analysis_page.py — Unit and integration tests for UI-08 Revenue Analysis Screen.
Customer RFM Analysis
"""

from pathlib import Path
import pytest
import pandas as pd
import plotly.graph_objects as go
from streamlit.testing.v1 import AppTest

from src.pages.revenue_analysis import (
    render,
    compute_pareto_curve,
    build_pareto_chart,
    build_segment_timeline_chart,
    build_cohort_heatmap,
)
from src.data_loader import load_data
from src.data_validator import validate_data
from src.rfm_calculator import calculate_rfm, score_rfm
from src.segmentation import assign_segments, compute_revenue_by_segment, compute_cohort_revenue
from src.config import DEFAULT_DATASET_PATH


@pytest.fixture(scope="module")
def prepared_data():
    raw = load_data(DEFAULT_DATASET_PATH)
    valid, _, _ = validate_data(raw)
    rfm_raw = calculate_rfm(valid)
    rfm_scored = score_rfm(rfm_raw)
    rfm_final = assign_segments(rfm_scored)
    return valid, rfm_final


def test_revenue_analysis_imports():
    """Verify revenue_analysis exports required functions."""
    import src.pages.revenue_analysis as rev_module
    assert hasattr(rev_module, "render")
    assert callable(rev_module.render)
    assert hasattr(rev_module, "compute_pareto_curve")
    assert hasattr(rev_module, "build_pareto_chart")


def test_compute_pareto_curve(prepared_data):
    """Verify Pareto curve calculations and concentration ratios."""
    _, rfm = prepared_data
    curve_df, top_10, top_20, gini = compute_pareto_curve(rfm)

    assert not curve_df.empty
    assert "pct_customers" in curve_df.columns
    assert "pct_revenue" in curve_df.columns
    assert 0.0 <= top_10 <= top_20 <= 100.0
    assert 0.0 <= gini <= 1.0


def test_build_pareto_chart(prepared_data):
    """Verify Pareto chart generates valid Plotly figure."""
    _, rfm = prepared_data
    curve_df, _, top_20, _ = compute_pareto_curve(rfm)
    fig = build_pareto_chart(curve_df, top_20)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 2


def test_build_segment_timeline_chart(prepared_data):
    """Verify segment timeline chart generates valid Plotly figure."""
    valid, rfm = prepared_data
    seg_rev = compute_revenue_by_segment(rfm, valid)
    fig = build_segment_timeline_chart(seg_rev)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1


def test_build_cohort_heatmap(prepared_data):
    """Verify cohort heatmap generates valid Plotly figure."""
    valid, _ = prepared_data
    cohort_matrix = compute_cohort_revenue(valid)
    fig = build_cohort_heatmap(cohort_matrix)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1


def test_revenue_analysis_apptest_render():
    """Verify Revenue Analysis screen renders cleanly inside Streamlit AppTest."""
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)

    at.run()
    assert not at.exception

    # Select "💰  Revenue Analysis" from sidebar radio
    sidebar_radio = at.sidebar.radio[0]
    rev_option = [opt for opt in sidebar_radio.options if "Revenue Analysis" in opt][0]
    sidebar_radio.set_value(rev_option).run()

    # Verify no unhandled exceptions
    assert not at.exception, f"AppTest raised an exception on Revenue Analysis: {at.exception}"

    # Verify KPI metrics
    metric_labels = [m.label for m in at.metric]
    assert any("Total Valid Revenue" in label for label in metric_labels)
    assert any("Top 20% Revenue Share" in label for label in metric_labels)
    assert any("Top 10% Revenue Share" in label for label in metric_labels)
    assert any("Gini Concentration Ratio" in label for label in metric_labels)

    # Verify tier distribution dataframe rendered
    assert len(at.dataframe) >= 1
