"""
tests/test_eda_page.py — Unit and integration tests for UI-04 EDA Screen.
Customer RFM Analysis
"""

from pathlib import Path
import pytest
import pandas as pd
import plotly.graph_objects as go
from streamlit.testing.v1 import AppTest

from src.pages.eda_page import (
    render,
    build_monthly_trend_chart,
    build_category_bar_chart,
    build_spending_histogram,
    build_payment_donut,
    build_region_bar,
)
from src.data_loader import load_data
from src.data_validator import validate_data
from src.eda import (
    compute_monthly_revenue,
    compute_category_breakdown,
    compute_transaction_distribution,
    compute_payment_method_breakdown,
    compute_regional_breakdown,
)
from src.config import DEFAULT_DATASET_PATH


@pytest.fixture(scope="module")
def valid_df():
    raw_df = load_data(DEFAULT_DATASET_PATH)
    valid, _, _ = validate_data(raw_df)
    return valid


def test_eda_page_imports():
    """Verify eda_page exports required components."""
    import src.pages.eda_page as eda_module
    assert hasattr(eda_module, "render")
    assert callable(eda_module.render)
    assert hasattr(eda_module, "build_monthly_trend_chart")
    assert hasattr(eda_module, "build_category_bar_chart")


def test_build_monthly_trend_chart(valid_df):
    """Verify monthly trend chart builds valid figure."""
    monthly_df = compute_monthly_revenue(valid_df)
    fig = build_monthly_trend_chart(monthly_df)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2  # bar + line


def test_build_category_bar_chart(valid_df):
    """Verify category bar chart builds valid figure."""
    cat_df = compute_category_breakdown(valid_df)
    fig = build_category_bar_chart(cat_df)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1


def test_build_spending_histogram(valid_df):
    """Verify spending distribution histogram builds valid figure."""
    txn_dist_df = compute_transaction_distribution(valid_df)
    fig = build_spending_histogram(txn_dist_df)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1


def test_build_payment_donut(valid_df):
    """Verify payment method donut builds valid figure."""
    pay_df = compute_payment_method_breakdown(valid_df)
    fig = build_payment_donut(pay_df)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1


def test_build_region_bar(valid_df):
    """Verify regional performance bar chart builds valid figure."""
    reg_df = compute_regional_breakdown(valid_df)
    fig = build_region_bar(reg_df)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1


def test_eda_page_apptest_render():
    """Verify EDA screen renders cleanly inside Streamlit AppTest."""
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)

    at.run()
    assert not at.exception

    # Select "🔍  Exploratory Data Analysis" from sidebar radio
    sidebar_radio = at.sidebar.radio[0]
    eda_option = [opt for opt in sidebar_radio.options if "Exploratory Data Analysis" in opt][0]
    sidebar_radio.set_value(eda_option).run()

    # Verify no unhandled exceptions
    assert not at.exception, f"AppTest raised an exception on EDA Page: {at.exception}"

    # Verify KPI metrics rendered
    metric_labels = [m.label for m in at.metric]
    assert any("Total Valid Revenue" in label for label in metric_labels)
    assert any("Mean Order Value" in label for label in metric_labels)
    assert any("Avg Spend / Customer" in label for label in metric_labels)

    # Verify leaderboard dataframe rendered
    assert len(at.dataframe) >= 1
