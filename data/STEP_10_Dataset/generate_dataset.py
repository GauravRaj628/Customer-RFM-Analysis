"""
generate_dataset.py — Synthetic Retail Transaction Dataset Generator
ABC Retail Solutions Pvt. Ltd., Noida

Generates a reproducible 5 000-row synthetic retail transaction dataset
suitable for Customer RFM Analysis.

Usage:
    python data/STEP_10_Dataset/generate_dataset.py

Output:
    data/STEP_10_Dataset/raw/retail_transactions.csv

Business Rules Encoded:
- 500–600 unique customers
- 1 500–2 500 unique orders
- Date range: 2023-01-01 to 2024-12-31
- ~8% invalid rows (negative amounts, null dates, zero qty, bad status)
- Realistic Indian retail scenario
- Reproducible with RANDOM_STATE = 42
"""

from __future__ import annotations

import os
import sys
import random
import csv
from datetime import date, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Seed & Constants
# ---------------------------------------------------------------------------
RANDOM_STATE = 42
random.seed(RANDOM_STATE)

try:
    import numpy as np
    np.random.seed(RANDOM_STATE)
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from faker import Faker
    fake = Faker("en_IN")
    fake.seed_instance(RANDOM_STATE)
    HAS_FAKER = True
except ImportError:
    HAS_FAKER = False

TOTAL_ROWS       = 5_000
NUM_CUSTOMERS    = 550
NUM_ORDERS       = 2_000
INVALID_RATIO    = 0.08   # ~8 % invalid rows
DATE_START       = date(2023, 1, 1)
DATE_END         = date(2024, 12, 31)
DATE_RANGE_DAYS  = (DATE_END - DATE_START).days

OUTPUT_PATH = Path(__file__).parent / "raw" / "retail_transactions.csv"

# ---------------------------------------------------------------------------
# Reference Data
# ---------------------------------------------------------------------------
PRODUCT_CATEGORIES = {
    "Electronics":    [
        ("Smartphone", 8_999, 49_999),
        ("Laptop",     25_000, 89_999),
        ("Tablet",     7_999, 29_999),
        ("Earphones",  499,   3_999),
        ("Smartwatch", 2_999, 15_999),
    ],
    "Clothing": [
        ("Men's T-Shirt", 299, 1_499),
        ("Women's Kurti", 399, 2_499),
        ("Jeans",         799, 3_499),
        ("Jacket",        999, 5_999),
        ("Saree",         599, 8_999),
    ],
    "Groceries": [
        ("Rice (5 kg)",      250,  450),
        ("Cooking Oil (1L)", 120,  220),
        ("Dal (1 kg)",       80,   180),
        ("Wheat Flour (5kg)",200,  350),
        ("Sugar (1 kg)",     40,   80),
    ],
    "Home & Kitchen": [
        ("Pressure Cooker",  699, 3_499),
        ("Mixer Grinder",   1_499, 4_999),
        ("Non-stick Pan",    399, 1_999),
        ("Dinner Set",       999, 4_499),
        ("Water Bottle",     149, 799),
    ],
    "Sports & Fitness": [
        ("Yoga Mat",         499, 1_999),
        ("Dumbbell Set",    1_499, 5_999),
        ("Badminton Racket", 299, 2_499),
        ("Cricket Bat",      799, 4_999),
        ("Cycling Helmet",   599, 2_999),
    ],
    "Books & Stationery": [
        ("Novel",            150, 499),
        ("Textbook",         350, 1_499),
        ("Notebook Set",     99,  399),
        ("Pen Set",          49,  249),
        ("Art Supplies",     299, 1_499),
    ],
    "Health & Beauty": [
        ("Face Wash",        99,  599),
        ("Shampoo (200ml)", 149,  499),
        ("Moisturiser",     199,  999),
        ("Perfume",         499, 3_499),
        ("Vitamin Tablets", 299, 1_499),
    ],
    "Toys & Baby": [
        ("Building Blocks",  399, 1_999),
        ("Soft Toy",         249, 1_499),
        ("Board Game",       499, 2_499),
        ("Remote Car",       799, 3_999),
        ("Baby Clothes Set", 399, 1_499),
    ],
}

CATEGORIES         = list(PRODUCT_CATEGORIES.keys())
CATEGORY_WEIGHTS   = [0.20, 0.18, 0.15, 0.12, 0.10, 0.08, 0.10, 0.07]

PAYMENT_METHODS    = ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking", "EMI"]
PAYMENT_WEIGHTS    = [0.38, 0.22, 0.18, 0.10, 0.07, 0.05]

STORE_REGIONS = {
    "North": ["Noida", "Delhi", "Gurgaon", "Faridabad", "Lucknow", "Agra"],
    "South": ["Bengaluru", "Chennai", "Hyderabad", "Coimbatore", "Kochi"],
    "East":  ["Kolkata", "Bhubaneswar", "Patna", "Ranchi"],
    "West":  ["Mumbai", "Pune", "Ahmedabad", "Surat", "Jaipur"],
}
REGION_LIST   = list(STORE_REGIONS.keys())
REGION_WEIGHTS = [0.35, 0.30, 0.15, 0.20]

VALID_STATUSES   = ["completed", "completed", "completed", "completed", "valid"]
INVALID_STATUSES = ["returned", "cancelled", "pending", "failed"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _weighted_choice(options: list, weights: list):
    """Pure-stdlib weighted random choice."""
    total = sum(weights)
    r = random.uniform(0, total)
    cumulative = 0
    for opt, w in zip(options, weights):
        cumulative += w
        if r <= cumulative:
            return opt
    return options[-1]


def _random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def _indian_name() -> str:
    if HAS_FAKER:
        return fake.name()
    first_names = [
        "Aarav","Aditya","Akash","Amit","Ananya","Anjali","Arjun","Deepak",
        "Gaurav","Ishaan","Karan","Kavya","Meena","Mohit","Nisha","Pooja",
        "Priya","Rahul","Riya","Rohit","Sakshi","Sanjay","Shreya","Siddharth",
        "Sunita","Suresh","Tanisha","Vikram","Vikas","Zara",
    ]
    last_names = [
        "Agarwal","Bose","Chakraborty","Chaudhary","Ghosh","Gupta","Iyer",
        "Joshi","Kapoor","Kumar","Mehta","Mishra","Nair","Patel","Rao",
        "Reddy","Sharma","Singh","Sinha","Verma","Yadav",
    ]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


# ---------------------------------------------------------------------------
# Generate Customer & Order Pools
# ---------------------------------------------------------------------------

def build_customers(n: int) -> list[dict]:
    """Return a list of customer dicts with id, name, region, city."""
    customers = []
    for i in range(1, n + 1):
        region = _weighted_choice(REGION_LIST, REGION_WEIGHTS)
        city   = random.choice(STORE_REGIONS[region])
        customers.append({
            "customer_id":   f"CUST{i:04d}",
            "customer_name": _indian_name(),
            "store_region":  region,
            "city":          city,
        })
    return customers


def build_orders(n: int, customers: list[dict]) -> list[dict]:
    """Return a list of order dicts linked to customers."""
    orders = []
    for i in range(1, n + 1):
        cust = random.choice(customers)
        orders.append({
            "order_id":    f"ORD{i:05d}",
            "customer_id": cust["customer_id"],
            "order_date":  _random_date(DATE_START, DATE_END),
        })
    return orders


# ---------------------------------------------------------------------------
# Generate Transaction Rows
# ---------------------------------------------------------------------------

def build_transactions(
    total_rows: int,
    customers: list[dict],
    orders: list[dict],
    invalid_ratio: float,
) -> list[dict]:
    """
    Generate `total_rows` synthetic retail transaction rows.

    ~invalid_ratio of rows will have one or more data quality issues:
    negative/zero amount, null date, zero quantity, or invalid status.
    """
    num_invalid = int(total_rows * invalid_ratio)
    invalid_indices = set(random.sample(range(total_rows), num_invalid))

    # Build lookup: customer_id → customer dict
    cust_map = {c["customer_id"]: c for c in customers}

    rows: list[dict] = []

    for i in range(total_rows):
        order      = random.choice(orders)
        cust       = cust_map[order["customer_id"]]

        category   = _weighted_choice(CATEGORIES, CATEGORY_WEIGHTS)
        products   = PRODUCT_CATEGORIES[category]
        prod_name, price_low, price_high = random.choice(products)

        quantity   = random.randint(1, 5)
        unit_price = round(random.uniform(price_low, price_high), 2)
        amount     = round(quantity * unit_price, 2)
        status     = random.choice(VALID_STATUSES)
        txn_date   = order["order_date"]
        payment    = _weighted_choice(PAYMENT_METHODS, PAYMENT_WEIGHTS)

        # ── Inject invalidity ──────────────────────────────────────────────
        if i in invalid_indices:
            issue = random.choice(["neg_amount", "null_date", "zero_qty", "bad_status", "neg_amount"])
            if issue == "neg_amount":
                amount = round(-abs(amount), 2)
            elif issue == "null_date":
                txn_date = None
            elif issue == "zero_qty":
                quantity = 0
                amount   = 0.0
            elif issue == "bad_status":
                status = random.choice(INVALID_STATUSES)

        rows.append({
            "transaction_id":    f"TXN{i + 1:06d}",
            "customer_id":       cust["customer_id"],
            "customer_name":     cust["customer_name"],
            "order_id":          order["order_id"],
            "transaction_date":  str(txn_date) if txn_date else "",
            "product_category":  category,
            "product_name":      prod_name,
            "quantity":          quantity,
            "unit_price":        unit_price,
            "transaction_amount":amount,
            "transaction_status":status,
            "payment_method":    payment,
            "store_region":      cust["store_region"],
            "city":              cust["city"],
        })

    return rows


# ---------------------------------------------------------------------------
# Write CSV
# ---------------------------------------------------------------------------

FIELDNAMES = [
    "transaction_id", "customer_id", "customer_name", "order_id",
    "transaction_date", "product_category", "product_name",
    "quantity", "unit_price", "transaction_amount",
    "transaction_status", "payment_method", "store_region", "city",
]


def write_csv(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("  Customer RFM Analysis — Synthetic Dataset Generator")
    print("  ABC Retail Solutions Pvt. Ltd., Noida")
    print("=" * 60)
    print(f"  Random state : {RANDOM_STATE}")
    print(f"  Customers    : {NUM_CUSTOMERS}")
    print(f"  Orders       : {NUM_ORDERS}")
    print(f"  Total rows   : {TOTAL_ROWS}")
    print(f"  Invalid ~    : {int(TOTAL_ROWS * INVALID_RATIO)} rows ({INVALID_RATIO*100:.0f}%)")
    print(f"  Date range   : {DATE_START} to {DATE_END}")
    print(f"  Output       : {OUTPUT_PATH}")
    print("-" * 60)

    print("Building customer pool...")
    customers = build_customers(NUM_CUSTOMERS)

    print("Building order pool...")
    orders = build_orders(NUM_ORDERS, customers)

    print("Generating transactions...")
    rows = build_transactions(TOTAL_ROWS, customers, orders, INVALID_RATIO)

    print(f"Writing CSV to {OUTPUT_PATH} ...")
    write_csv(rows, OUTPUT_PATH)

    # ── Verification ──────────────────────────────────────────────────────
    with open(OUTPUT_PATH, encoding="utf-8") as f:
        actual_rows = sum(1 for _ in f) - 1  # subtract header

    # Count unique customers in output
    unique_custs = len({r["customer_id"] for r in rows})
    unique_orders = len({r["order_id"] for r in rows})
    invalid_count = sum(
        1 for r in rows
        if r["transaction_amount"] <= 0
        or not r["transaction_date"]
        or r["quantity"] <= 0
        or r["transaction_status"] in set(INVALID_STATUSES)
    )

    print()
    print("✅ Dataset generated successfully!")
    print(f"   Rows written        : {actual_rows:,}")
    print(f"   Unique customers    : {unique_custs:,}")
    print(f"   Unique orders       : {unique_orders:,}")
    print(f"   Invalid rows        : {invalid_count:,} ({invalid_count/actual_rows*100:.1f}%)")
    print(f"   File size           : {OUTPUT_PATH.stat().st_size / 1024:.1f} KB")
    print()


if __name__ == "__main__":
    main()
