"""
tests/test_app_integration.py — End-to-end integration test verifying full multi-page navigation.
Customer RFM Analysis
"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

from src.config import STUDENT_NAME, ROLL_NUMBER


@pytest.fixture(scope="module")
def app_runner():
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)
    at.run()
    assert not at.exception, f"Initial boot failed: {at.exception}"
    return at


@pytest.mark.parametrize(
    "page_keyword",
    [
        "Home",
        "Data Upload",
        "Data Validation",
        "Exploratory Data Analysis",
        "RFM Analysis",
        "Customer Segmentation",
        "Customer Details",
        "Revenue Analysis",
        "Business Insights",
    ],
)
def test_all_pages_render_without_exception(page_keyword):
    """Verify that every single page in the application renders without unhandled exceptions."""
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)
    at.run()
    assert not at.exception

    # Select target page from radio options
    radio = at.sidebar.radio[0]
    matched_options = [opt for opt in radio.options if page_keyword in opt]
    assert len(matched_options) == 1, f"Option for '{page_keyword}' not found in {radio.options}"

    target_option = matched_options[0]
    radio.set_value(target_option).run()

    # Assert no unhandled exceptions on the target page
    assert not at.exception, f"Exception occurred on page '{target_option}': {at.exception}"
