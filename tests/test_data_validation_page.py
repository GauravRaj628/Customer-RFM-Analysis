"""
tests/test_data_validation_page.py — Unit and integration tests for UI-03 Data Validation Screen.
Customer RFM Analysis
"""

from pathlib import Path
import pytest
import plotly.graph_objects as go
from streamlit.testing.v1 import AppTest

from src.pages.data_validation import (
    render,
    build_validation_donut,
    build_completeness_bar,
)


def test_data_validation_imports():
    """Verify data_validation exports required components."""
    import src.pages.data_validation as val_module
    assert hasattr(val_module, "render")
    assert callable(val_module.render)
    assert hasattr(val_module, "build_validation_donut")
    assert hasattr(val_module, "build_completeness_bar")


def test_build_validation_donut():
    """Verify validation donut chart generates valid Plotly figure."""
    fig = build_validation_donut(valid_count=4600, invalid_count=400)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].values == (4600, 400)


def test_build_completeness_bar():
    """Verify completeness horizontal bar chart generates valid Plotly figure."""
    mock_completeness = {
        "customer_id": 100.0,
        "transaction_amount": 98.5,
        "product_category": 95.0,
    }
    fig = build_completeness_bar(mock_completeness)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1


def test_data_validation_apptest_render():
    """Verify Data Validation screen renders cleanly inside Streamlit AppTest."""
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)

    at.run()
    assert not at.exception

    # Select "✅  Data Validation" from sidebar radio
    sidebar_radio = at.sidebar.radio[0]
    val_option = [opt for opt in sidebar_radio.options if "Data Validation" in opt][0]
    sidebar_radio.set_value(val_option).run()

    # Verify no unhandled exceptions
    assert not at.exception, f"AppTest raised an exception on Data Validation: {at.exception}"

    # Verify metric cards
    metric_labels = [m.label for m in at.metric]
    assert any("Data Quality Score" in label for label in metric_labels)
    assert any("Eligible Transactions" in label for label in metric_labels)
    assert any("Flagged Anomalies" in label for label in metric_labels)

    # Verify dataframes rendered (anomaly summary & flagged records)
    assert len(at.dataframe) >= 2

    # Verify download button rendered
    assert len(at.download_button) >= 1
