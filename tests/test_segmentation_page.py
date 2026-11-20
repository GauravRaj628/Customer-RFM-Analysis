"""
tests/test_segmentation_page.py — Unit and integration tests for UI-06 Customer Segmentation Screen.
Customer RFM Analysis
"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

from src.pages.segmentation_page import render, SEGMENT_STRATEGIES
from src.config import SEGMENT_ORDER


def test_segmentation_page_imports():
    """Verify segmentation_page exports render and strategy definitions."""
    import src.pages.segmentation_page as seg_module
    assert hasattr(seg_module, "render")
    assert callable(seg_module.render)
    assert hasattr(seg_module, "SEGMENT_STRATEGIES")


def test_segment_strategies_structure():
    """Verify strategies exist for all official business segments."""
    for segment in SEGMENT_ORDER:
        assert segment in SEGMENT_STRATEGIES
        strat = SEGMENT_STRATEGIES[segment]
        assert "tagline" in strat
        assert "description" in strat
        assert "actions" in strat
        assert len(strat["actions"]) >= 2


def test_segmentation_page_apptest_render():
    """Verify Customer Segmentation screen renders cleanly inside Streamlit AppTest."""
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)

    at.run()
    assert not at.exception

    # Select "🎯  Customer Segmentation" from sidebar radio
    sidebar_radio = at.sidebar.radio[0]
    seg_option = [opt for opt in sidebar_radio.options if "Customer Segmentation" in opt][0]
    sidebar_radio.set_value(seg_option).run()

    # Verify no unhandled exceptions
    assert not at.exception, f"AppTest raised an exception on Segmentation Page: {at.exception}"

    # Verify metric cards
    metric_labels = [m.label for m in at.metric]
    assert any("Champions" in label for label in metric_labels)
    assert any("Loyal Customers" in label for label in metric_labels)
    assert any("At-Risk Customers" in label for label in metric_labels)
    assert any("Lost Customers" in label for label in metric_labels)

    # Verify dataframes rendered (benchmark table + customer table)
    assert len(at.dataframe) >= 2

    # Verify download button rendered
    assert len(at.download_button) >= 1
