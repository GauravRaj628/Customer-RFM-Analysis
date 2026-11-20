"""
tests/test_customer_details_page.py — Unit and integration tests for UI-07 Customer Details Screen.
Customer RFM Analysis
"""

from pathlib import Path
import pytest
import pandas as pd
import plotly.graph_objects as go
from streamlit.testing.v1 import AppTest

from src.pages.customer_details import render, build_customer_category_donut
from src.data_loader import load_data
from src.data_validator import validate_data
from src.config import DEFAULT_DATASET_PATH, COL_CUSTOMER_ID


@pytest.fixture(scope="module")
def sample_cust_txns():
    raw = load_data(DEFAULT_DATASET_PATH)
    valid, _, _ = validate_data(raw)
    first_cust = valid[COL_CUSTOMER_ID].iloc[0]
    return valid[valid[COL_CUSTOMER_ID] == first_cust]


def test_customer_details_imports():
    """Verify customer_details module exports render and chart builders."""
    import src.pages.customer_details as cd_module
    assert hasattr(cd_module, "render")
    assert callable(cd_module.render)
    assert hasattr(cd_module, "build_customer_category_donut")


def test_build_customer_category_donut(sample_cust_txns):
    """Verify customer category donut generates valid Plotly figure."""
    fig = build_customer_category_donut(sample_cust_txns)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1


def test_customer_details_apptest_render():
    """Verify Customer Details screen renders cleanly inside Streamlit AppTest."""
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)

    at.run()
    assert not at.exception

    # Select "👤  Customer Details" from sidebar radio
    sidebar_radio = at.sidebar.radio[0]
    cd_option = [opt for opt in sidebar_radio.options if "Customer Details" in opt][0]
    sidebar_radio.set_value(cd_option).run()

    # Verify no unhandled exceptions
    assert not at.exception, f"AppTest raised an exception on Customer Details: {at.exception}"

    # Verify KPI metrics
    metric_labels = [m.label for m in at.metric]
    assert any("Lifetime Spend" in label for label in metric_labels)
    assert any("Completed Orders" in label for label in metric_labels)
    assert any("Days Since Purchase" in label for label in metric_labels)
    assert any("RFM Score & Cell" in label for label in metric_labels)

    # Verify customer history dataframe rendered
    assert len(at.dataframe) >= 1

    # Verify download button rendered
    assert len(at.download_button) >= 1
