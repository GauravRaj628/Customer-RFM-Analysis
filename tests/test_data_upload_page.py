"""
tests/test_data_upload_page.py — Unit and integration tests for UI-02 Data Upload Screen.
Customer RFM Analysis
"""

from pathlib import Path
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from src.pages.data_upload import process_and_cache_dataset, render
from src.config import DEFAULT_DATASET_PATH, REQUIRED_COLUMNS


def test_data_upload_imports():
    """Verify data_upload page exports required functions."""
    import src.pages.data_upload as upload_module
    assert hasattr(upload_module, "render")
    assert callable(upload_module.render)
    assert hasattr(upload_module, "process_and_cache_dataset")


def test_process_and_cache_dataset():
    """Verify processing pipeline caches raw, valid, and RFM data in session state."""
    st.session_state.clear()
    assert "raw_df" not in st.session_state

    success = process_and_cache_dataset(DEFAULT_DATASET_PATH, source_label="Test Run")
    assert success is True
    assert "raw_df" in st.session_state
    assert len(st.session_state["raw_df"]) == 5000
    assert "valid_df" in st.session_state
    assert len(st.session_state["valid_df"]) == 4600
    assert "rfm_df" in st.session_state
    assert len(st.session_state["rfm_df"]) == 531
    assert "quality_report" in st.session_state


def test_data_upload_apptest_render():
    """Verify Data Upload page renders cleanly inside Streamlit AppTest."""
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)

    # Pre-select Data Upload page in the sidebar radio
    at.run()
    assert not at.exception

    # Select "📂  Data Upload" from sidebar radio
    sidebar_radio = at.sidebar.radio[0]
    upload_option = [opt for opt in sidebar_radio.options if "Data Upload" in opt][0]
    sidebar_radio.set_value(upload_option).run()

    # Verify no unhandled exceptions
    assert not at.exception, f"AppTest raised an exception on Data Upload: {at.exception}"

    # Verify metrics rendered
    metric_labels = [m.label for m in at.metric]
    assert any("Total Rows" in label for label in metric_labels)
    assert any("Unique Customers" in label for label in metric_labels)
    assert any("Unique Orders" in label for label in metric_labels)

    # Verify dataframes rendered (schema table and preview table)
    assert len(at.dataframe) >= 2
