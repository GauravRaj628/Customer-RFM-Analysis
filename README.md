# 📊 Customer RFM Analysis & Strategic Segmentation Dashboard

> **Enterprise-Grade Retail Analytics & Customer Intelligence Platform**  
> *Academic Project — MCA 2nd Year, ABES Engineering College, Ghaziabad*

[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.14-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-2.1%2B%20%7C%203.0%2B-150458.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.19%2B%20%7C%207.1%2B-3F4F75.svg?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Pytest](https://img.shields.io/badge/Tests-110%20Passed-brightgreen.svg?logo=pytest&logoColor=white)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎓 Academic & Industry Attribution

- **Student Researcher:** Gaurav Raj
- **University Roll Number:** `2500320140054`
- **Academic Programme:** Master of Computer Applications (MCA) — 2nd Year
- **Department & Institution:** Department of Computer Applications, ABES Engineering College, Ghaziabad, Uttar Pradesh, India
- **Faculty Mentor & Supervisor:** Prof. Kalpana Diwedi
- **Client & Business Scenario:** ABC Retail Solutions Pvt. Ltd., Noida (Omnichannel Retail & E-Commerce Division)

---

## 📌 Executive Summary & Business Problem

In an omnichannel retail environment, **ABC Retail Solutions Pvt. Ltd.** faced escalating customer acquisition costs (CAC) paired with declining customer retention and repeat purchase velocity. Without automated customer behavioral telemetry:
1. Marketing campaigns were sent as one-size-fits-all blasts, creating promotional fatigue and unbudgeted discounts.
2. High-value VIP customers ("Champions") were neglected after major transactions, while churn-risk cohorts went unnoticed until after customer departure.
3. Transactional data had anomalies (missing IDs, negative order totals, refunded transactions, and future-dated records) that contaminated strategic reporting.

### The Solution:
This project delivers a **full-lifecycle, automated RFM (Recency, Frequency, Monetary) intelligence platform** built on Streamlit, Pandas, Plotly, and SQLite. It provides end-to-end data auditing, algorithmic customer quintile scoring, 5-tier behavioral segmentation, Pareto revenue concentration tracking, and automated 90-day retention campaign roadmaps.

---

## 🌟 System Architecture & Pipeline

```
 ┌────────────────────────────────────────────────────────┐
 │            1. Data Ingestion & Sanitization            │
 │   - Raw CSV Ingestion (5,000+ Transactions)            │
 │   - Schema Validation & Data Type Coercion             │
 └──────────────────────────┬─────────────────────────────┘
                            │
 ┌──────────────────────────▼─────────────────────────────┐
 │            2. Data Quality & Anomaly Engine            │
 │   - Partitioning Valid vs. Invalid Anomaly Records     │
 │   - 7 Anomaly Checks (Missing, Negative, Nulls, Dates) │
 │   - Comprehensive Data Quality Scoring (0-100%)        │
 └──────────────────────────┬─────────────────────────────┘
                            │
 ┌──────────────────────────▼─────────────────────────────┐
 │       3. RFM Calculation & Quintile Scoring Engine     │
 │   - Cut-off Reference Date Computation                 │
 │   - Recency (Days), Frequency (Orders), Monetary ($)   │
 │   - qcut() Quintile Scores (1 to 5; Inverted Recency)  │
 │   - Activity Status Assignment (Active/Inactive/Churn) │
 └──────────────────────────┬─────────────────────────────┘
                            │
 ┌──────────────────────────▼─────────────────────────────┐
 │       4. Segmentation & Strategy Allocation Matrix     │
 │   - Rule-Based 5-Tier Segment Classification           │
 │   - Cohort Revenue Velocity & Cross-Tab Analysis       │
 │   - Segment-Specific Marketing Actions & Retention     │
 └──────────────────────────┬─────────────────────────────┘
                            │
 ┌──────────────────────────▼─────────────────────────────┐
 │       5. Persistence Layer & Analytics UI              │
 │   - SQLite Analytical Cache (analysis_runs, rfm_df)    │
 │   - Interactive 9-Screen Streamlit Web Dashboard       │
 │   - 10+ Interactive Plotly Visualizations              │
 └────────────────────────────────────────────────────────┘
```

---

## 📐 RFM Methodology & Scoring Rules

### 1. Metric Formulations
Given a dynamic analysis cutoff reference date $T_{\text{ref}}$:
- **Recency ($R$):** $T_{\text{ref}} - \max(T_{\text{transaction}})$ in days. (Lower is superior).
- **Frequency ($F$):** Total count of unique, valid transactions $\sum \text{Orders}$. (Higher is superior).
- **Monetary ($M$):** Total aggregated net monetary value $\sum \text{Amount}$ across all purchases. (Higher is superior).

### 2. Quintile Scoring Mechanics ($1$ to $5$)
Each customer receives a quintile score between $1$ (lowest) and $5$ (highest) using `pandas.qcut` (with robust rank fallback):
- **Recency Score ($R_{\text{score}}$):** Inverted quintile ($5 = \text{most recent}$, $1 = \text{least recent / dormant}$).
- **Frequency Score ($F_{\text{score}}$):** Direct quintile ($5 = \text{highest order frequency}$, $1 = \text{single order}$).
- **Monetary Score ($M_{\text{score}}$):** Direct quintile ($5 = \text{highest spending}$, $1 = \text{lowest spending}$).
- **Composite RFM Score:** 3-digit behavioral code, e.g., `555` (Top Tier) or `111` (Dormant).

### 3. Customer Segments Classification

| Segment Name | Identification Criteria | Strategic Business Objective | Retention Playbook |
| :--- | :--- | :--- | :--- |
| **🏆 Champions** | $R \ge 4$ and $F \ge 4$ and $M \ge 4$ | Highest LTV, brand advocates | VIP perks, early product access, zero discounting |
| **💎 Loyal Customers** | $R \ge 3$ and $F \ge 3$ and $M \ge 3$ | Consistent repeat buyers | Loyalty tier acceleration, personalized bundles |
| **🌱 Potential Loyalists** | $R \ge 4$ and $F \le 2$ | Recent first/second-time buyers | Welcome onboarding series, second-order incentives |
| **⚠️ At Risk** | $R \le 2$ and $F \ge 2$ | Previously frequent, now dormant | Win-back surveys, personalized re-engagement offers |
| **💤 Lost Customers** | $R = 1$ and $F = 1$ | Inactive long-term churners | Low-cost automated email reactivation or purge |

### 4. Behavioral Activity Bands
- **Active:** Recency $\le 30$ days (Engaged customer base).
- **Inactive:** Recency $31 - 90$ days (Lapsing window).
- **Churned:** Recency $> 90$ days (Dormant / critical churn state).

---

## 🖥️ Interactive 9-Screen Dashboard Walkthrough

The platform features an enterprise UI built with **Streamlit** and styled using responsive CSS cards and custom Plotly themes:

1. **🏠 Screen 01 — Executive Home:** High-level executive KPI cards (Active Customers, Total Net Revenue, Average Order Value, Churn Rate), portfolio composition donut chart, active/inactive split, and technical architecture summary.
2. **📂 Screen 02 — Data Upload & Ingestion:** File uploader for custom CSV datasets, instant one-click loader for the built-in 5,000-record demo dataset, automated column schema validation checklist, and interactive raw table preview.
3. **🛡️ Screen 03 — Data Quality & Anomaly Audit:** Real-time data quality score banner (0–100%), valid vs. anomalous transaction distribution, column-wise completeness inspection, paginated anomaly audit table, and CSV anomaly export for audit trails.
4. **📈 Screen 04 — Exploratory Data Analysis (EDA):** Dual-axis monthly revenue and order volume velocity chart, product category sales breakdown, transaction amount distribution histograms, regional revenue mapping, and top 10 customer leaderboard.
5. **🎯 Screen 05 — RFM Analysis & Recency Engine:** Interactive cut-off date picker, dynamic recalculate engine with automatic SQLite caching, 3D RFM interactive scatter space, recency histogram with 30-day/90-day threshold indicators, $5 \times 5$ RFM heatmaps, and R/F/M distribution plots.
6. **👥 Screen 06 — Customer Segmentation:** Segment KPI summary cards, customer headcount distribution donut, revenue contribution bar chart, segment benchmark table, cohort deep-dive selector, and filtered customer list with CSV download.
7. **👤 Screen 07 — Customer 360° Profile:** Individual customer selector with instant search, demographic profile badge, lifetime KPI metrics, R/F/M visual progress gauges, category spending donut, behavioral highlights, and complete historical transaction timeline.
8. **💰 Screen 08 — Revenue Concentration & Pareto Analysis:** Top 10% and 20% revenue share cards, Gini concentration index calculator, Lorenz 80/20 curve with equality benchmark, segment revenue over time, acquisition cohort heatmap, and spend tier distribution.
9. **💡 Screen 09 — Business Insights & Retention Playbooks:** Recoverable revenue KPI metrics, 5-tab segment-specific retention and marketing action plans, phased 90-day churn mitigation roadmap, and one-click Executive Brief markdown report generator with export capability.

---

## 📁 Repository Directory Structure

```
Customer RFM Analysis/
│
├── app.py                              # Streamlit application entry point & router
├── BUILD_PLAN.md                       # Comprehensive 21-task technical blueprint
├── requirements.txt                    # Project production dependencies
├── README.md                           # Master documentation (this file)
├── .gitignore                          # Git exclusion rules
│
├── data/
│   ├── STEP_10_Dataset/
│   │   ├── raw/
│   │   │   └── retail_transactions.csv # 5,000-row synthetic retail dataset
│   │   └── generate_dataset.py         # Reproducible dataset generator script
│   └── rfm_analysis.db                 # SQLite analytical persistence cache
│
├── src/
│   ├── __init__.py                     # Module package marker
│   ├── config.py                       # Global paths, column names, segment rules
│   ├── data_loader.py                  # Robust CSV parsing & summary stats
│   ├── data_validator.py               # 7-rule anomaly detection engine
│   ├── eda.py                          # Aggregation & statistical analysis module
│   ├── rfm_calculator.py               # RFM metrics computation & quintile scoring
│   ├── segmentation.py                 # Multi-segment allocation & cohort analytics
│   ├── database.py                     # Parameterized SQLite persistence layer
│   │
│   ├── components/
│   │   ├── __init__.py
│   │   └── ui_components.py            # Reusable Plotly charts, KPI cards, badges
│   │
│   └── pages/
│       ├── __init__.py
│       ├── home.py                     # UI-01: Executive summary
│       ├── data_upload.py              # UI-02: Data upload & schema verification
│       ├── data_validation.py          # UI-03: Quality audit & anomaly table
│       ├── eda_page.py                 # UI-04: Exploratory data analysis
│       ├── rfm_analysis.py             # UI-05: RFM score engine & 3D scatter
│       ├── segmentation_page.py        # UI-06: Customer segments & export
│       ├── customer_details.py         # UI-07: Customer 360° timeline
│       ├── revenue_analysis.py         # UI-08: Pareto 80/20 & cohort heatmaps
│       └── business_insights.py        # UI-09: Retention playbooks & briefs
│
└── tests/
    ├── __init__.py
    ├── conftest.py                     # Shared pytest fixtures & test datasets
    ├── test_data_loader.py             # 8 unit tests for CSV ingestion
    ├── test_data_validator.py          # 10 unit tests for anomaly detection
    ├── test_eda.py                     # 8 unit tests for EDA aggregations
    ├── test_rfm_calculator.py          # 11 unit tests for RFM math & scoring
    ├── test_segmentation.py            # 8 unit tests for segment rules & cohorts
    ├── test_database.py                # 7 unit tests for SQLite tables & queries
    ├── test_ui_components.py           # 8 unit tests for Plotly renderers
    ├── test_home_page.py               # 3 unit tests for Home screen logic
    ├── test_data_upload_page.py        # 3 unit tests for Ingestion UI logic
    ├── test_data_validation_page.py    # 4 unit tests for Validation UI logic
    ├── test_eda_page.py                # 7 unit tests for EDA visualizations
    ├── test_rfm_analysis_page.py       # 3 unit tests for RFM UI calculations
    ├── test_segmentation_page.py       # 3 unit tests for Segmentation screen
    ├── test_customer_details_page.py   # 3 unit tests for Customer 360 view
    ├── test_revenue_analysis_page.py   # 6 unit tests for Pareto & Gini calculations
    ├── test_business_insights_page.py  # 4 unit tests for Playbook generation
    ├── test_app_integration.py         # 9 integration tests via Streamlit AppTest
    └── test_ui_smoke.py                # 5 deep UI interaction smoke tests
```

---

## 🛠️ Technology Stack & Dependencies

| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Language** | Python | `3.12+` / `3.14` | Primary runtime environment |
| **Web Framework** | Streamlit | `^1.32.0` | Reactive web UI and interactive dashboard controls |
| **Data Processing** | Pandas & NumPy | `^2.1.0` / `^1.26.0` | Ingestion, vector math, quintile ranking, aggregations |
| **Visualizations** | Plotly | `^5.19.0` | Interactive 2D/3D charts, heatmaps, donuts, timelines |
| **Database** | SQLite3 | Built-in | Local relational persistence for RFM runs and audit logs |
| **Testing** | Pytest & AppTest | `^8.0.0` | Comprehensive unit, integration, and UI smoke testing |
| **Data Generation** | Faker | `^24.0.0` | Realistic synthetic e-commerce transactions generation |

---

## 🚀 Installation & Local Quickstart

### Prerequisites
- Python 3.10+ (tested through Python 3.14 on Windows, macOS, and Linux)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Gaurav-Raj-2003/Customer-RFM-Analysis.git
cd "Customer RFM Analysis"
```

### 2. Set Up a Virtual Environment
```bash
# On Linux / macOS:
python3 -m venv venv
source venv/bin/activate

# On Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

### 4. (Optional) Re-generate Synthetic Dataset
If you wish to re-generate the 5,000 transaction dataset:
```bash
python data/STEP_10_Dataset/generate_dataset.py
```

### 5. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 🧪 Automated Testing Suite

The repository features a rigorous test suite comprising **110 automated tests** covering data integrity, algorithmic correctness, SQL persistence, Plotly figure generation, and end-to-end Streamlit page interactions.

To execute the full test suite:
```bash
pytest tests/ -v
```

### Test Suite Distribution

```
============================= test session results =============================
tests/test_data_loader.py            8 passed
tests/test_data_validator.py        10 passed
tests/test_eda.py                    8 passed
tests/test_rfm_calculator.py        11 passed
tests/test_segmentation.py           8 passed
tests/test_database.py               7 passed
tests/test_ui_components.py          8 passed
tests/test_home_page.py              3 passed
tests/test_data_upload_page.py       3 passed
tests/test_data_validation_page.py   4 passed
tests/test_eda_page.py               7 passed
tests/test_rfm_analysis_page.py      3 passed
tests/test_segmentation_page.py      3 passed
tests/test_customer_details_page.py  3 passed
tests/test_revenue_analysis_page.py  6 passed
tests/test_business_insights_page.py 4 passed
tests/test_app_integration.py        9 passed
tests/test_ui_smoke.py               5 passed
--------------------------------------------------------------------------------
TOTAL: 110 passed in ~18 seconds (100% pass rate)
================================================================================
```

---

## ☁️ Deployment Guide (Streamlit Community Cloud)

1. **Push to GitHub:** Ensure your latest commits are pushed to your remote repository:
   ```bash
   git add .
   git commit -m "Production release: Complete Customer RFM Analysis Dashboard"
   git push origin main
   ```
2. **Connect Streamlit Cloud:**
   - Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
   - Click **New app** and select your GitHub repository (`Customer-RFM-Analysis`).
   - Set the Main file path to: `app.py`.
   - Set the Branch to: `main`.
3. **Deploy:** Click **Deploy!** The cloud runner will automatically parse `requirements.txt` and launch the application.

---

## 📜 Academic Integrity & License

This project was conceived and developed by **Gaurav Raj** as part of the MCA 2nd Year curriculum at **ABES Engineering College**, Ghaziabad, under the academic mentorship of **Prof. Kalpana Diwedi**.

Distributed under the **MIT License**. See `LICENSE` for more information.
