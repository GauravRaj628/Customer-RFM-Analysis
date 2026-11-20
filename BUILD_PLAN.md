# BUILD_PLAN.md — Customer RFM Analysis
## Authoritative Development Sequence

**Project:** Customer RFM Analysis  
**Student:** Gaurav Raj | Roll: 2500320140054  
**Programme:** MCA 2nd Year | ABES Engineering College  
**Mentor:** Kalpana Diwedi  
**Business Scenario:** ABC Retail Solutions Pvt. Ltd., Noida  

---

## Technology Stack
- Python 3.12
- Streamlit ≥ 1.32
- Pandas ≥ 2.1 | NumPy ≥ 1.26
- Plotly ≥ 5.19
- SciPy ≥ 1.12 | Statsmodels ≥ 0.14
- SQLite (stdlib)
- Pytest ≥ 8.0 | Streamlit AppTest
- Faker ≥ 24 (dataset generation only)

---

## Project Architecture

```
Customer RFM Analysis/
│
├── BUILD_PLAN.md                  ← this file (authoritative)
├── app.py                         ← Streamlit entry point
├── requirements.txt
├── .gitignore
├── README.md
│
├── docs/                          ← project documentation
│
├── data/
│   └── STEP_10_Dataset/
│       ├── raw/
│       │   └── retail_transactions.csv
│       └── generate_dataset.py
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py             ← BUILD-02
│   ├── data_validator.py          ← BUILD-03
│   ├── eda.py                     ← BUILD-04
│   ├── rfm_calculator.py          ← BUILD-05
│   ├── segmentation.py            ← BUILD-06
│   ├── database.py                ← BUILD-07
│   ├── config.py                  ← shared constants
│   ├── components/
│   │   ├── __init__.py
│   │   └── ui_components.py       ← BUILD-08
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── home.py                ← BUILD-09
│   │   ├── data_upload.py         ← BUILD-10
│   │   ├── data_validation.py     ← BUILD-11
│   │   ├── eda_page.py            ← BUILD-12
│   │   ├── rfm_analysis.py        ← BUILD-13
│   │   ├── segmentation_page.py   ← BUILD-14
│   │   ├── customer_details.py    ← BUILD-15
│   │   ├── revenue_analysis.py    ← BUILD-16
│   │   └── business_insights.py   ← BUILD-17
│   └── analytics/
│       ├── __init__.py
│       └── stats_helpers.py       ← statistical utilities
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_data_loader.py        ← BUILD-02 tests
    ├── test_data_validator.py     ← BUILD-03 tests
    ├── test_rfm_calculator.py     ← BUILD-05 tests
    ├── test_segmentation.py       ← BUILD-06 tests
    ├── test_database.py           ← BUILD-07 tests
    └── test_ui_smoke.py           ← BUILD-19 UI tests
```

---

## Business Rules (Non-Negotiable)

| Rule | Detail |
|------|--------|
| Frequency | Count of **distinct Order IDs** per customer |
| Monetary | Sum of **valid** transaction amounts only |
| Recency | Days between reference date and customer's **latest valid purchase** |
| Reference date | 1 day after the latest valid purchase date (default) |
| RFM scores | 1–5 (where sample permits); Recency score is **reversed** |
| Segments | Every eligible customer gets exactly **one** segment |
| Activity bands | 0–30 days → Recent; 31–90 → At-risk; >90 → Inactive |
| Invalid rows | Excluded from RFM; reported in Data Validation screen |
| Data | Synthetic only; no real PII |
| Recommendations | Advisory text only; no automated campaign triggers |

---

## Approved Screens

| Screen ID | Name |
|-----------|------|
| UI-01 | Home / Overview |
| UI-02 | Data Upload |
| UI-03 | Data Validation |
| UI-04 | Exploratory Data Analysis |
| UI-05 | RFM Analysis |
| UI-06 | Customer Segmentation |
| UI-07 | Customer Details |
| UI-08 | Revenue Analysis |
| UI-09 | Business Insights |

---

## BUILD Tasks

---

### BUILD-01 — Environment Setup
**Goal:** Create the full project skeleton, synthetic dataset, and verify the Python environment.

**Deliverables:**
- `requirements.txt` with pinned dependencies
- `.gitignore`
- `app.py` — Streamlit entry point (skeleton with page routing)
- `src/__init__.py`, `src/config.py`, all `__init__.py` files
- `data/STEP_10_Dataset/generate_dataset.py` — synthetic data generator
- `data/STEP_10_Dataset/raw/retail_transactions.csv` — 5 000 rows, ≥ 500 customers
- `tests/__init__.py`, `tests/conftest.py`
- Python + pip version confirmed
- `pip install -r requirements.txt` succeeds

**Synthetic Dataset Columns:**
`transaction_id, customer_id, customer_name, order_id, transaction_date, product_category, product_name, quantity, unit_price, transaction_amount, transaction_status, payment_method, store_region, city`

**Dataset Rules:**
- Date range: 2023-01-01 to 2024-12-31
- 500–600 unique customers; 1 500–2 500 unique orders
- 5 000 transaction rows total
- ~8% invalid rows: negative amounts, null dates, zero quantities, cancelled/returned status
- Realistic Indian retail scenario (ABC Retail Solutions, Noida)
- Reproducible with `random_state=42`

**Tests:** None required for BUILD-01 (smoke test only — import src package).

**Stop condition:** `python -c "import src"` exits 0; dataset CSV exists with ≥ 5 000 rows.

---

### BUILD-02 — Data Loader
**Goal:** Implement `src/data_loader.py` — load CSV into a typed Pandas DataFrame.

**Deliverables:**
- `src/data_loader.py` with `load_data(filepath) -> pd.DataFrame`
- Correct dtype inference and date parsing
- `tests/test_data_loader.py` — ≥ 5 test cases

**Key functions:**
```python
load_data(filepath: str | Path) -> pd.DataFrame
get_dataset_summary(df: pd.DataFrame) -> dict
```

**Stop condition:** `pytest tests/test_data_loader.py -v` — all pass.

---

### BUILD-03 — Data Validation and Cleaning
**Goal:** Implement `src/data_validator.py` — classify rows as valid/invalid and produce a data quality report.

**Deliverables:**
- `src/data_validator.py`
- `tests/test_data_validator.py` — ≥ 8 test cases

**Key functions:**
```python
validate_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]
# returns: valid_df, invalid_df, quality_report
```

**Validation rules:**
- transaction_amount > 0
- transaction_date not null and within plausible range
- quantity ≥ 1
- customer_id not null
- order_id not null
- transaction_status in ('completed', 'valid') → valid row
- Flag but do not drop: 'returned', 'cancelled' (included in invalid set)

**Stop condition:** `pytest tests/test_data_validator.py -v` — all pass.

---

### BUILD-04 — EDA and Descriptive Statistics
**Goal:** Implement `src/eda.py` — descriptive statistics and chart data for the EDA screen.

**Deliverables:**
- `src/eda.py`
- No separate test file required; functions must be deterministic given same input.

**Key functions:**
```python
compute_summary_stats(df: pd.DataFrame) -> dict
compute_monthly_revenue(df: pd.DataFrame) -> pd.DataFrame
compute_category_breakdown(df: pd.DataFrame) -> pd.DataFrame
compute_top_customers(df: pd.DataFrame, n: int = 10) -> pd.DataFrame
compute_transaction_distribution(df: pd.DataFrame) -> pd.DataFrame
```

**Stop condition:** Functions importable; return correct types on the synthetic dataset.

---

### BUILD-05 — RFM Calculation and Scoring
**Goal:** Implement `src/rfm_calculator.py` — calculate R, F, M values and assign 1–5 scores.

**Deliverables:**
- `src/rfm_calculator.py`
- `tests/test_rfm_calculator.py` — ≥ 10 test cases

**Key functions:**
```python
calculate_rfm(df: pd.DataFrame, reference_date: date | None = None) -> pd.DataFrame
score_rfm(rfm_df: pd.DataFrame) -> pd.DataFrame
compute_rfm_summary(rfm_df: pd.DataFrame) -> dict
```

**Scoring rules:**
- Use `pd.qcut` with duplicates='drop'; fall back to equal-width if fewer than 5 unique values.
- R score reversed: lower recency days → higher score.
- RFM_Score = R_Score + F_Score + M_Score (range 3–15).
- Activity band derived from recency_days.

**Stop condition:** `pytest tests/test_rfm_calculator.py -v` — all pass.

---

### BUILD-06 — Segment and Revenue Aggregation
**Goal:** Implement `src/segmentation.py` — assign customer segments and aggregate revenue.

**Deliverables:**
- `src/segmentation.py`
- `tests/test_segmentation.py` — ≥ 8 test cases

**Segment mapping (RFM_Score → Segment):**

| RFM Score | Segment |
|-----------|---------|
| 13–15 | Champions |
| 10–12 | Loyal Customers |
| 7–9 | Potential Loyalists |
| 4–6 | At-Risk Customers |
| 3 | Lost Customers |

**Key functions:**
```python
assign_segments(rfm_df: pd.DataFrame) -> pd.DataFrame
compute_segment_summary(rfm_df: pd.DataFrame) -> pd.DataFrame
compute_revenue_by_segment(rfm_df: pd.DataFrame, valid_df: pd.DataFrame) -> pd.DataFrame
compute_cohort_revenue(valid_df: pd.DataFrame) -> pd.DataFrame
```

**Stop condition:** `pytest tests/test_segmentation.py -v` — all pass.

---

### BUILD-07 — SQLite Integration
**Goal:** Implement `src/database.py` — persist and query RFM results in SQLite.

**Deliverables:**
- `src/database.py`
- `tests/test_database.py` — ≥ 6 test cases
- Database file: `data/rfm_analysis.db` (created at runtime)

**Key functions:**
```python
init_db(db_path: str = "data/rfm_analysis.db") -> sqlite3.Connection
save_rfm_results(conn, rfm_df: pd.DataFrame) -> None
load_rfm_results(conn) -> pd.DataFrame
save_segment_summary(conn, segment_df: pd.DataFrame) -> None
load_segment_summary(conn) -> pd.DataFrame
```

**Rules:**
- Parameterised queries only.
- Tables: `rfm_results`, `segment_summary`, `analysis_runs`.
- Each analysis run is logged with timestamp and reference date.

**Stop condition:** `pytest tests/test_database.py -v` — all pass.

---

### BUILD-08 — Shared UI Components
**Goal:** Implement `src/components/ui_components.py` — reusable Streamlit widgets and chart builders.

**Deliverables:**
- `src/components/ui_components.py`

**Key components:**
```python
render_kpi_card(label, value, delta=None, icon=None)
render_segment_badge(segment_name: str)
render_activity_badge(activity_band: str)
render_data_quality_banner(quality_report: dict)
build_rfm_scatter(rfm_df: pd.DataFrame) -> go.Figure
build_segment_donut(segment_summary: pd.DataFrame) -> go.Figure
build_revenue_bar(revenue_df: pd.DataFrame) -> go.Figure
build_recency_histogram(rfm_df: pd.DataFrame) -> go.Figure
render_empty_state(message: str, icon: str = "📭")
render_page_header(title: str, subtitle: str = "")
```

**Stop condition:** Module importable; no Streamlit errors on import.

---

### BUILD-09 — UI-01 Home / Overview Screen
**Goal:** Implement `src/pages/home.py`.

**Content:**
- Project title, student info, mentor, institution
- KPI cards: total customers, total orders, total revenue, date range
- Segment distribution donut chart
- Activity band summary
- Navigation quick-links to all other screens

**Stop condition:** Screen renders without error in Streamlit AppTest.

---

### BUILD-10 — UI-02 Data Upload Screen
**Goal:** Implement `src/pages/data_upload.py`.

**Content:**
- File uploader (CSV, XLSX) with size limit guidance
- Use default synthetic dataset if no file uploaded
- Preview first 20 rows
- Column mapping confirmation
- Dataset summary stats (rows, columns, date range, customer count)

**Stop condition:** Screen renders; default dataset loads correctly.

---

### BUILD-11 — UI-03 Data Validation Screen
**Goal:** Implement `src/pages/data_validation.py`.

**Content:**
- Overall data quality score (% valid rows)
- Quality report table: issue type, count, % affected
- Invalid rows viewer (paginated, downloadable)
- Valid vs invalid pie chart
- Column-level completeness bar chart

**Stop condition:** Screen renders; quality report displays correctly.

---

### BUILD-12 — UI-04 EDA Screen
**Goal:** Implement `src/pages/eda_page.py`.

**Content:**
- Monthly revenue trend (line chart)
- Revenue by product category (bar chart)
- Transaction amount distribution (histogram)
- Top 10 customers by revenue (horizontal bar)
- Payment method breakdown (donut)
- Store region heatmap or bar

**Stop condition:** Screen renders; all 6 charts display.

---

### BUILD-13 — UI-05 RFM Analysis Screen
**Goal:** Implement `src/pages/rfm_analysis.py`.

**Content:**
- Reference date selector (default: max_date + 1 day)
- RFM summary KPIs: avg R, avg F, avg M
- RFM 3D scatter (R vs F vs M, coloured by segment)
- R / F / M distribution histograms
- RFM score heatmap (R_Score vs F_Score)
- Downloadable RFM table

**Stop condition:** Screen renders; reference date changes recalculate RFM.

---

### BUILD-14 — UI-06 Customer Segmentation Screen
**Goal:** Implement `src/pages/segmentation_page.py`.

**Content:**
- Segment overview table (count, % share, avg RFM scores, avg revenue)
- Segment donut chart
- Segment comparison bar charts (avg R, F, M per segment)
- Segment filter to explore individual segment members
- Segment-level advisory recommendations

**Stop condition:** Screen renders; segment filter works.

---

### BUILD-15 — UI-07 Customer Details Screen
**Goal:** Implement `src/pages/customer_details.py`.

**Content:**
- Customer search / select dropdown
- Customer KPI cards: segment, activity band, R/F/M values and scores
- Purchase history table (all valid transactions)
- Monthly spend trend for selected customer
- Peer comparison: customer vs segment average

**Stop condition:** Screen renders; customer lookup returns correct data.

---

### BUILD-16 — UI-08 Revenue Analysis Screen
**Goal:** Implement `src/pages/revenue_analysis.py`.

**Content:**
- Revenue by segment (stacked bar)
- Monthly revenue by segment (line, multi-series)
- Cohort revenue heatmap (first-purchase month vs revenue)
- Revenue concentration (top 20% of customers = what % of revenue)
- Regional revenue breakdown

**Stop condition:** Screen renders; all charts display.

---

### BUILD-17 — UI-09 Business Insights Screen
**Goal:** Implement `src/pages/business_insights.py`.

**Content:**
- Automated textual summary: key findings per segment
- Prioritised recommendations (advisory only)
- Risk flags: segments with declining revenue
- Retention strategy table (segment → suggested action)
- Export insights as PDF or text (optional)

**Stop condition:** Screen renders; insights generated from real data.

---

### BUILD-18 — Integration and Navigation
**Goal:** Wire all pages into `app.py` with sidebar navigation and shared session state.

**Deliverables:**
- Complete `app.py` with `st.sidebar` navigation
- Shared `st.session_state` for `valid_df`, `rfm_df`, `segment_df`
- Page routing to all 9 screens
- Consistent page config (title, icon, layout=wide)

**Stop condition:** `streamlit run app.py` — all 9 pages accessible without errors.

---

### BUILD-19 — Automated and Functional Testing
**Goal:** Complete test suite with ≥ 90% logic coverage.

**Deliverables:**
- All `tests/test_*.py` files complete
- `tests/test_ui_smoke.py` using Streamlit AppTest
- `pytest --tb=short -q` — all tests pass
- Coverage report: `pytest --cov=src`

**Stop condition:** All tests pass; coverage ≥ 70%.

---

### BUILD-20 — README Documentation
**Goal:** Write `README.md` — professional project documentation.

**Content:**
- Project overview and screenshots (placeholder)
- Installation and local run instructions
- Architecture diagram (ASCII)
- RFM methodology explanation
- Segment definitions
- File structure
- Test run instructions
- Deployment guide

**Stop condition:** README complete and accurate.

---

### BUILD-21 — GitHub and Deployment
**Goal:** Push to GitHub; deploy to Streamlit Community Cloud.

**Deliverables:**
- Git repository initialised with clean history
- `.gitignore` correct (no venv, no .db, no __pycache__)
- GitHub repository created and pushed
- `streamlit_app.py` or deployment config (if needed)
- Streamlit Community Cloud app deployed
- Deployment URL confirmed working

**Stop condition:** Live deployment URL accessible; app functions end-to-end.

---

*End of BUILD_PLAN.md*
