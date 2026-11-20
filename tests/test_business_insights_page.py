"""
tests/test_business_insights_page.py — Unit and integration tests for UI-09 Business Insights Screen.
Customer RFM Analysis
"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

from src.pages.business_insights import render, generate_executive_brief_markdown, PLAYBOOK
from src.data_loader import load_data
from src.data_validator import validate_data
from src.rfm_calculator import calculate_rfm, score_rfm
from src.segmentation import assign_segments, compute_segment_summary
from src.config import DEFAULT_DATASET_PATH, STUDENT_NAME, ROLL_NUMBER, SEGMENT_ORDER


@pytest.fixture(scope="module")
def prepared_rfm_data():
    raw = load_data(DEFAULT_DATASET_PATH)
    valid, _, _ = validate_data(raw)
    rfm_raw = calculate_rfm(valid)
    rfm_scored = score_rfm(rfm_raw)
    rfm_final = assign_segments(rfm_scored)
    seg_summary = compute_segment_summary(rfm_final)
    return rfm_final, seg_summary


def test_business_insights_imports():
    """Verify business_insights exports render, brief generator, and playbook."""
    import src.pages.business_insights as bi_module
    assert hasattr(bi_module, "render")
    assert callable(bi_module.render)
    assert hasattr(bi_module, "generate_executive_brief_markdown")
    assert hasattr(bi_module, "PLAYBOOK")


def test_playbook_structure():
    """Verify playbook contains tactics and channel guidance for all segments."""
    for seg in SEGMENT_ORDER:
        assert seg in PLAYBOOK
        entry = PLAYBOOK[seg]
        assert "channels" in entry
        assert "offer_strategy" in entry
        assert "tactics" in entry
        assert len(entry["tactics"]) >= 2


def test_generate_executive_brief_markdown(prepared_rfm_data):
    """Verify executive brief markdown generation compiles student metadata and tables."""
    rfm_df, seg_summary = prepared_rfm_data
    brief = generate_executive_brief_markdown(rfm_df, seg_summary)

    assert STUDENT_NAME in brief
    assert ROLL_NUMBER in brief
    assert "Executive Performance Dashboard" in brief
    assert "Champions" in brief
    assert "Lost Customers" in brief


def test_business_insights_apptest_render():
    """Verify Business Insights screen renders cleanly inside Streamlit AppTest."""
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)

    at.run()
    assert not at.exception

    # Select "💡  Business Insights" from sidebar radio
    sidebar_radio = at.sidebar.radio[0]
    bi_option = [opt for opt in sidebar_radio.options if "Business Insights" in opt][0]
    sidebar_radio.set_value(bi_option).run()

    # Verify no unhandled exceptions
    assert not at.exception, f"AppTest raised an exception on Business Insights: {at.exception}"

    # Verify KPI metrics
    metric_labels = [m.label for m in at.metric]
    assert any("Recoverable Revenue" in label for label in metric_labels)
    assert any("Top 20% Revenue Share" in label for label in metric_labels)
    assert any("Churn Exposure Rate" in label for label in metric_labels)
    assert any("Projected Retention ROI" in label for label in metric_labels)

    # Verify download button rendered
    assert len(at.download_button) >= 1
