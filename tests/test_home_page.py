"""
tests/test_home_page.py — Unit and integration tests for UI-01 Home Screen.
Customer RFM Analysis
"""

from pathlib import Path
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from src.pages.home import ensure_demo_data_loaded, render
from src.config import STUDENT_NAME, ROLL_NUMBER, INSTITUTION


def test_home_page_imports():
    """Verify home page module and render function exist and are callable."""
    import src.pages.home as home_module
    assert hasattr(home_module, "render")
    assert callable(home_module.render)
    assert hasattr(home_module, "ensure_demo_data_loaded")


def test_ensure_demo_data_loaded():
    """Verify demo data loader successfully loads RFM data into session state."""
    # Clear state first
    st.session_state.clear()
    assert "rfm_df" not in st.session_state

    ensure_demo_data_loaded()

    assert "rfm_df" in st.session_state
    assert st.session_state["rfm_df"] is not None
    assert len(st.session_state["rfm_df"]) > 0
    assert "segment_summary" in st.session_state
    assert len(st.session_state["segment_summary"]) > 0


def test_home_page_apptest_render():
    """Verify the home screen renders without exceptions via Streamlit AppTest."""
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)
    at.run()

    # Verify no unhandled exceptions occurred
    assert not at.exception, f"AppTest raised an exception: {at.exception}"

    # Verify key text and elements are present
    text_content = " ".join([m.value for m in at.markdown])
    assert STUDENT_NAME in text_content
    assert ROLL_NUMBER in text_content

    # Verify metric cards are rendered
    assert len(at.metric) >= 4
    metric_labels = [m.label for m in at.metric]
    assert any("Total Customers" in label for label in metric_labels)
    assert any("Total Revenue" in label for label in metric_labels)

