"""
tests/test_rfm_analysis_page.py — Unit and integration tests for UI-05 RFM Analysis Screen.
Customer RFM Analysis
"""

from pathlib import Path
import pytest
import pandas as pd
import plotly.graph_objects as go
from streamlit.testing.v1 import AppTest

from src.pages.rfm_analysis import render, build_score_bar


def test_rfm_analysis_imports():
    """Verify rfm_analysis exports required functions."""
    import src.pages.rfm_analysis as rfm_module
    assert hasattr(rfm_module, "render")
    assert callable(rfm_module.render)
    assert hasattr(rfm_module, "build_score_bar")


def test_build_score_bar():
    """Verify score distribution bar chart returns valid Plotly figure."""
    scores = pd.Series([1, 2, 2, 3, 3, 3, 4, 4, 5, 5])
    fig = build_score_bar(scores, "Test Score", "#3498DB")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert len(fig.data[0].x) == 5


def test_rfm_analysis_apptest_render():
    """Verify RFM Analysis screen renders cleanly inside Streamlit AppTest."""
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)

    at.run()
    assert not at.exception

    # Select "📈  RFM Analysis" from sidebar radio
    sidebar_radio = at.sidebar.radio[0]
    rfm_option = [opt for opt in sidebar_radio.options if "RFM Analysis" in opt][0]
    sidebar_radio.set_value(rfm_option).run()

    # Verify no unhandled exceptions
    assert not at.exception, f"AppTest raised an exception on RFM Analysis: {at.exception}"

    # Verify KPI metrics
    metric_labels = [m.label for m in at.metric]
    assert any("Median Recency" in label for label in metric_labels)
    assert any("Median Frequency" in label for label in metric_labels)
    assert any("Median Monetary" in label for label in metric_labels)
    assert any("Avg Combined Score" in label for label in metric_labels)

    # Verify button for recalculation exists
    assert any("Recalculate RFM Scores" in btn.label for btn in at.button)
