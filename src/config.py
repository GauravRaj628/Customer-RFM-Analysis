"""
src/config.py — Shared constants and configuration.

All business rules, column names, segment maps, and defaults
are defined here so every module reads from one source of truth.
"""

from __future__ import annotations

# ── Dataset ───────────────────────────────────────────────────────────────────
DEFAULT_DATASET_PATH = "data/STEP_10_Dataset/raw/retail_transactions.csv"
DATABASE_PATH = "data/rfm_analysis.db"

# ── Column Names ──────────────────────────────────────────────────────────────
COL_TRANSACTION_ID   = "transaction_id"
COL_CUSTOMER_ID      = "customer_id"
COL_CUSTOMER_NAME    = "customer_name"
COL_ORDER_ID         = "order_id"
COL_DATE             = "transaction_date"
COL_CATEGORY         = "product_category"
COL_PRODUCT          = "product_name"
COL_QUANTITY         = "quantity"
COL_UNIT_PRICE       = "unit_price"
COL_AMOUNT           = "transaction_amount"
COL_STATUS           = "transaction_status"
COL_PAYMENT          = "payment_method"
COL_REGION           = "store_region"
COL_CITY             = "city"

REQUIRED_COLUMNS = [
    COL_TRANSACTION_ID,
    COL_CUSTOMER_ID,
    COL_ORDER_ID,
    COL_DATE,
    COL_AMOUNT,
    COL_STATUS,
]

# ── Valid Transaction Statuses ────────────────────────────────────────────────
VALID_STATUSES = {"completed", "valid"}
INVALID_STATUSES = {"returned", "cancelled", "pending", "failed"}

# ── RFM Scoring ───────────────────────────────────────────────────────────────
RFM_BINS = 5                 # number of quantile bins
RFM_SCORE_MIN = 1
RFM_SCORE_MAX = 5
RFM_COMBINED_MIN = 3         # 1+1+1
RFM_COMBINED_MAX = 15        # 5+5+5

# ── Segment Mapping (RFM_Score → Segment Name) ────────────────────────────────
SEGMENT_MAP: dict[tuple[int, int], str] = {
    (13, 15): "Champions",
    (10, 12): "Loyal Customers",
    (7,  9) : "Potential Loyalists",
    (4,  6) : "At-Risk Customers",
    (3,  3) : "Lost Customers",
}

SEGMENT_ORDER = [
    "Champions",
    "Loyal Customers",
    "Potential Loyalists",
    "At-Risk Customers",
    "Lost Customers",
]

SEGMENT_COLOURS = {
    "Champions":           "#2ECC71",
    "Loyal Customers":     "#3498DB",
    "Potential Loyalists": "#F39C12",
    "At-Risk Customers":   "#E74C3C",
    "Lost Customers":      "#95A5A6",
}

# ── Activity Bands (days since last purchase) ─────────────────────────────────
ACTIVITY_RECENT   = (0,  30)   # inclusive
ACTIVITY_AT_RISK  = (31, 90)
ACTIVITY_INACTIVE = (91, None) # None = no upper bound

ACTIVITY_LABELS = {
    "Recent":   "🟢 Recent",
    "At-risk":  "🟡 At-risk",
    "Inactive": "🔴 Inactive",
}

ACTIVITY_COLOURS = {
    "Recent":   "#2ECC71",
    "At-risk":  "#F39C12",
    "Inactive": "#E74C3C",
}

# ── Application Metadata ──────────────────────────────────────────────────────
APP_TITLE    = "Customer RFM Analysis"
APP_SUBTITLE = "ABC Retail Solutions Pvt. Ltd., Noida"
STUDENT_NAME = "Gaurav Raj"
ROLL_NUMBER  = "2500320140054"
PROGRAMME    = "MCA 2nd Year"
INSTITUTION  = "ABES Engineering College"
MENTOR       = "Kalpana Diwedi"
