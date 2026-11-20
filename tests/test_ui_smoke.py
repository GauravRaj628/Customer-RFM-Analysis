"""
tests/test_ui_smoke.py — Deep interactive UI smoke tests using Streamlit AppTest.
Customer RFM Analysis

Verifies that user interactions (slider changes, dropdown filtering, button clicks,
and recalculations) update element trees cleanly without exceptions.
"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def app_instance():
    """Create a fresh AppTest instance pointing to app.py."""
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)
    at.run()
    assert not at.exception, f"AppTest initialization failed: {at.exception}"
    return at


def test_smoke_data_upload_slider_interaction(app_instance):
    """Verify that moving the preview row slider in Data Upload works cleanly."""
    at = app_instance
    radio = at.sidebar.radio[0]
    upload_opt = [opt for opt in radio.options if "Data Upload" in opt][0]
    radio.set_value(upload_opt).run()
    assert not at.exception

    # Find the row limit slider
    assert len(at.slider) >= 1
    row_slider = at.slider[0]
    # Set value from default 20 to 50
    row_slider.set_value(50).run()

    assert not at.exception
    # Ensure dataframes still render
    assert len(at.dataframe) >= 2


def test_smoke_data_validation_filter_interaction(app_instance):
    """Verify selecting anomaly categories in Data Validation updates the table."""
    at = app_instance
    radio = at.sidebar.radio[0]
    val_opt = [opt for opt in radio.options if "Data Validation" in opt][0]
    radio.set_value(val_opt).run()
    assert not at.exception

    # Selectbox for filtering anomalies
    assert len(at.selectbox) >= 1
    issue_selector = at.selectbox[0]
    assert len(issue_selector.options) >= 2

    # Switch to the second option (first specific anomaly category)
    target_category = issue_selector.options[1]
    issue_selector.set_value(target_category).run()

    assert not at.exception
    assert len(at.dataframe) >= 2
    assert len(at.download_button) >= 1


def test_smoke_rfm_recalculate_interaction(app_instance):
    """Verify clicking 'Recalculate RFM Scores' on the RFM screen triggers re-scoring."""
    at = app_instance
    radio = at.sidebar.radio[0]
    rfm_opt = [opt for opt in radio.options if "RFM Analysis" in opt][0]
    radio.set_value(rfm_opt).run()
    assert not at.exception

    # Find recalculate button
    recalc_btns = [btn for btn in at.button if "Recalculate RFM Scores" in btn.label]
    assert len(recalc_btns) == 1

    # Click button and verify execution
    recalc_btns[0].click().run()
    assert not at.exception

    # Metric cards should remain visible and valid
    assert len(at.metric) >= 4


def test_smoke_segmentation_filter_interaction(app_instance):
    """Verify filtering by segment cohorts updates the customer list table."""
    at = app_instance
    radio = at.sidebar.radio[0]
    seg_opt = [opt for opt in radio.options if "Customer Segmentation" in opt][0]
    radio.set_value(seg_opt).run()
    assert not at.exception

    # Find cohort selectbox
    assert len(at.selectbox) >= 1
    seg_selector = at.selectbox[0]

    # Select "Champions" cohort
    champions_opt = [opt for opt in seg_selector.options if "Champions" in opt][0]
    seg_selector.set_value(champions_opt).run()
    assert not at.exception

    # Switch to "At-Risk Customers" cohort
    at_risk_opt = [opt for opt in seg_selector.options if "At-Risk" in opt][0]
    seg_selector.set_value(at_risk_opt).run()
    assert not at.exception

    assert len(at.dataframe) >= 2
    assert len(at.download_button) >= 1


def test_smoke_customer_details_selection_interaction(app_instance):
    """Verify selecting a different customer profile loads that customer's history."""
    at = app_instance
    radio = at.sidebar.radio[0]
    cd_opt = [opt for opt in radio.options if "Customer Details" in opt][0]
    radio.set_value(cd_opt).run()
    assert not at.exception

    # Customer selector selectbox
    assert len(at.selectbox) >= 1
    cust_selector = at.selectbox[0]
    assert len(cust_selector.options) >= 2

    # Switch to second customer in list
    second_customer = cust_selector.options[1]
    cust_selector.set_value(second_customer).run()
    assert not at.exception

    # Metrics and history table must render for the new customer
    assert len(at.metric) >= 4
    assert len(at.dataframe) >= 1
    assert len(at.download_button) >= 1
