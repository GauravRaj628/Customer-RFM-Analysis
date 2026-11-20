"""
tests/conftest.py — Shared pytest fixtures for Customer RFM Analysis.

Fixtures defined here are automatically available to all test modules.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is on PYTHONPATH so `import src` works
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import pandas as pd
from datetime import date


# ---------------------------------------------------------------------------
# Minimal valid DataFrame fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_valid_df() -> pd.DataFrame:
    """10-row fully valid transaction DataFrame."""
    return pd.DataFrame({
        "transaction_id":    [f"TXN{i:06d}" for i in range(1, 11)],
        "customer_id":       ["CUST0001"] * 4 + ["CUST0002"] * 3 + ["CUST0003"] * 3,
        "customer_name":     ["Gaurav Raj"] * 4 + ["Priya Sharma"] * 3 + ["Rahul Gupta"] * 3,
        "order_id":          [f"ORD{i:05d}" for i in [1, 1, 2, 3, 4, 4, 5, 6, 7, 7]],
        "transaction_date":  pd.to_datetime([
            "2024-01-15", "2024-01-15", "2024-03-20", "2024-06-10",
            "2024-02-28", "2024-02-28", "2024-07-05",
            "2023-11-01", "2024-05-15", "2024-05-15",
        ]),
        "product_category":  ["Electronics", "Clothing", "Groceries", "Electronics",
                              "Clothing", "Home & Kitchen", "Sports & Fitness",
                              "Books & Stationery", "Health & Beauty", "Toys & Baby"],
        "product_name":      ["Smartphone", "Jeans", "Rice (5 kg)", "Laptop",
                              "Men's T-Shirt", "Pressure Cooker", "Yoga Mat",
                              "Novel", "Face Wash", "Building Blocks"],
        "quantity":          [1, 2, 3, 1, 2, 1, 1, 2, 3, 1],
        "unit_price":        [25000.0, 1200.0, 300.0, 55000.0,
                              499.0, 1500.0, 999.0, 350.0, 199.0, 599.0],
        "transaction_amount":[25000.0, 2400.0, 900.0, 55000.0,
                              998.0, 1500.0, 999.0, 700.0, 597.0, 599.0],
        "transaction_status":["completed"] * 10,
        "payment_method":    ["UPI", "Credit Card", "Cash", "Debit Card",
                              "UPI", "Net Banking", "UPI", "Cash", "UPI", "Credit Card"],
        "store_region":      ["North"] * 4 + ["South"] * 3 + ["West"] * 3,
        "city":              ["Noida", "Noida", "Noida", "Noida",
                              "Chennai", "Chennai", "Chennai",
                              "Mumbai", "Mumbai", "Mumbai"],
    })


@pytest.fixture
def sample_mixed_df(sample_valid_df) -> pd.DataFrame:
    """DataFrame with 2 invalid rows appended to the valid set."""
    import numpy as np
    invalid_rows = pd.DataFrame({
        "transaction_id":    ["TXN000011", "TXN000012"],
        "customer_id":       ["CUST0001",  "CUST0002"],
        "customer_name":     ["Gaurav Raj","Priya Sharma"],
        "order_id":          ["ORD00008",  "ORD00009"],
        "transaction_date":  [pd.NaT,      pd.Timestamp("2024-04-01")],
        "product_category":  ["Electronics","Clothing"],
        "product_name":      ["Earphones", "Saree"],
        "quantity":          [0,           1],
        "unit_price":        [999.0,       1500.0],
        "transaction_amount":[-999.0,      1500.0],
        "transaction_status":["completed", "cancelled"],
        "payment_method":    ["UPI",       "Cash"],
        "store_region":      ["North",     "South"],
        "city":              ["Noida",     "Chennai"],
    })
    return pd.concat([sample_valid_df, invalid_rows], ignore_index=True)


@pytest.fixture
def reference_date() -> date:
    """Standard reference date for RFM tests: one day after last valid txn."""
    return date(2024, 7, 6)   # 2024-07-05 is the latest valid date + 1 day
