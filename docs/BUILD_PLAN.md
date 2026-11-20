# Customer RFM Analysis — BUILD PLAN (STEP 14)

> **Purpose:** This file is the authoritative AI/developer build input for STEP 15. Follow one BUILD task at a time, in order. Do not start the next task until the current task is checked and accepted.

## 1. Project summary (10 lines)

1. Customer RFM Analysis is a decision-support analytics application for synthetic retail/e-commerce transaction data.
2. It calculates Recency, Frequency and Monetary measures for each eligible customer.
3. Frequency counts distinct valid order IDs, not transaction line rows.
4. Monetary sums valid transaction amounts within the selected analysis period.
5. RFM values are converted into documented 1–5 scores and one documented segment per eligible customer.
6. Initial activity bands are 0–30 days recent, 31–90 days at-risk and more than 90 days inactive.
7. The product provides EDA, descriptive statistics, segment distribution, revenue comparison and customer-level exploration.
8. Nine approved Streamlit screens (UI-01 to UI-09) answer ten operational questions (OQ-01 to OQ-10).
9. Recommendations are advisory and evidence-based; no campaigns, CRM automation or predictive churn are in scope.
10. All sample data is synthetic; deployment is planned for Streamlit Community Cloud with SQLite persistence treated as ephemeral.

## 2. Source documents and project artefacts

Read the relevant source documents before each task. The links below are relative to the project root:

- [STEP 1 — Project Understanding](docs/01_name_customer_rfm_understanding.docx)
- [STEP 2 — HMW Statements](docs/02_name_hmw_statements.docx)
- [STEP 3 — Needs Analysis](docs/03_name_needs_analysis.docx)
- [STEP 4 — Traceability Matrix (final RTM)](docs/04_Traceability_Matrix.xlsx)
- [STEP 5 — BRD](docs/05_BRD.docx)
- [STEP 6 — PRD](docs/06_Product_Requirements_Document_PRD.docx)
- [STEP 7 — TRD](docs/07_TRD.docx)
- [STEP 8 — Database Design](docs/08_Database_Design.xlsx)
- [STEP 9 — ER Diagram (Word)](docs/09_ER_Diagram.docx)
- [STEP 9 — ER Diagram (PNG)](docs/09_ER_Diagram.png)
- [STEP 10 — Dataset workbook](data/STEP_10_Dataset/customer_rfm_data.xlsx)
- [STEP 10 — SQLite database](data/STEP_10_Dataset/app.db)
- [STEP 10 — Generator](src/generate_data.py)
- [STEP 10 — Validation report](data/STEP_10_Dataset/validation_report.txt)
- [STEP 11 — User Stories](docs/11_User_Stories.docx)
- [STEP 12 — UI Framework](docs/12_UI_Framework.docx)
- [STEP 13 — Test Cases](docs/13_Test_Cases.docx)
- [STEP 13 — Automated tests: data](tests/test_data.py)
- [STEP 13 — Automated tests: analysis](tests/test_analysis.py)
- [STEP 13 — Automated tests: app](tests/test_app.py)

### ID governance

- Preserve OQ-01–OQ-10, HMW-01–HMW-12, BR-01–BR-12, SH-01–SH-08, F-01–F-14, FR-01–FR-20, NFR-01–NFR-10, US-01–US-18, UI-01–UI-09, TC-F-01–TC-F-28 and TC-T-01–TC-T-18 exactly. Never renumber or invent a business requirement.
- The approved UI register is UI-01 Overview, UI-02 Upload, UI-03 Validation, UI-04 EDA, UI-05 RFM, UI-06 Segmentation, UI-07 Customer Details, UI-08 Revenue, UI-09 Business Insights.
- The TRD uses Python 3.12, pandas, NumPy, SciPy/statsmodels where justified, Plotly, Streamlit, SQLite, pytest, Streamlit AppTest, GitHub and Streamlit Community Cloud.
- The project is synthetic-data-only. Do not request or persist real customer PII.


## 3. Final folder structure

```text
Customer_RFM_Analysis/
├── app.py
├── requirements.txt
├── README.md
├── BUILD_PLAN.md
├── .gitignore
├── .streamlit/
│   └── config.toml
├── docs/
│   ├── 01_name_customer_rfm_understanding.docx
│   ├── 02_name_hmw_statements.docx
│   ├── 03_name_needs_analysis.docx
│   ├── 04_Traceability_Matrix.xlsx
│   ├── 05_BRD.docx
│   ├── 06_Product_Requirements_Document_PRD.docx
│   ├── 07_TRD.docx
│   ├── 08_Database_Design.xlsx
│   ├── 09_ER_Diagram.docx
│   ├── 09_ER_Diagram.png
│   ├── 11_User_Stories.docx
│   ├── 12_UI_Framework.docx
│   ├── 13_Test_Cases.docx
│   └── 14_BUILD_PLAN.docx
├── data/
│   ├── STEP_10_Dataset/
│   │   ├── customer_rfm_data.xlsx
│   │   ├── customer_master.csv
│   │   ├── segment_master.csv
│   │   ├── analysis_run.csv
│   │   ├── transaction_fact.csv
│   │   ├── customer_rfm_fact.csv
│   │   ├── app.db
│   │   ├── validation_report.txt
│   │   └── validation_report.json
│   └── app.db                 # runtime canonical SQLite DB (created/copied by app)
├── src/
│   ├── __init__.py
│   ├── ui.py
│   ├── state.py
│   ├── components.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── validator.py
│   │   ├── cleaner.py
│   │   ├── database.py
│   │   └── repository.py
│   └── analysis/
│       ├── __init__.py
│       ├── eda.py
│       ├── statistics.py
│       ├── rfm.py
│       ├── scoring.py
│       ├── segmentation.py
│       ├── segments.py
│       ├── revenue.py
│       └── insights.py
├── pages/
│   ├── 1_Data_Upload.py
│   ├── 2_Exploratory_Analysis.py
│   ├── 3_RFM_Analysis.py
│   ├── 4_Customer_Segmentation.py
│   ├── 5_Customer_Details.py
│   ├── 6_Revenue_Analysis.py
│   ├── 7_Business_Insights.py
│   └── 8_Data_Validation.py
└── tests/
    ├── test_data.py
    ├── test_analysis.py
    ├── test_app.py
    └── conftest.py
```

> Note: Streamlit's `app.py` is UI-01. The page filenames above are implementation filenames; they do not create or renumber UI IDs. UI-03 remains the approved Data Validation screen even though it is scheduled after insights in the build sequence.


## 4. Build tasks — execute one at a time


### BUILD-01 — Project environment and dependency baseline

**Goal:** Create a reproducible Python 3.12 project environment, requirements.txt, package folders and Streamlit configuration. Verify the proposed pinned stack before coding.

**Files:** `requirements.txt; .gitignore; app.py (minimal placeholder only); src/__init__.py; src/data/__init__.py; src/analysis/__init__.py; tests/; .streamlit/config.toml`

**User stories / feature IDs:** US-18; F-01 to F-14 (foundation)

**How to check:** Create/activate Python 3.12 venv; install requirements; run `python -c "import streamlit,pandas,numpy,plotly,scipy,statsmodels,openpyxl"`; `python -m pytest -q` (database tests may pass; analysis/UI tests may skip until their modules/pages are built).

**Tests / acceptance checks:** TC-T-13 (basic entry point later); TC-T-15 baseline startup later; clean-install check TA-01. Do not claim full suite passes yet.

**Exact AI prompt (copy as-is):**

```text
You are implementing BUILD-01 of the Customer RFM Analysis project. Read docs/07_TRD.docx, docs/06_Product_Requirements_Document_PRD.docx and docs/13_Test_Cases.docx first. Use Python 3.12. Create a clean requirements.txt using the TRD's proposed pinned dependencies: streamlit==1.50.0, pandas==2.3.3, numpy==2.3.4, scipy==1.16.3, statsmodels==0.14.5, plotly==6.3.1, openpyxl==3.1.5, pytest==8.4.2. Verify compatibility on Python 3.12; if a pin is unavailable/incompatible, do not silently change it—report the exact conflict and propose the smallest version adjustment for approval. Create package __init__.py files and a minimal app.py placeholder that starts Streamlit. Add .gitignore for venv, __pycache__, pytest cache, secrets, local database and generated caches, while keeping the supplied synthetic sample data tracked if the project baseline requires it. Preserve .streamlit/config.toml. Do not implement business logic or change any IDs. Return changed files, exact install commands, verification output and any dependency issue.
```


### BUILD-02 — Data loader and source schema handling

**Goal:** Load supported CSV/XLSX uploads and the STEP 10 SQLite/sample files without modifying source values.

**Files:** `src/data/loader.py; src/data/__init__.py; tests/test_data.py (only compatible refinements if needed)`

**User stories / feature IDs:** US-01, US-02; F-01, F-02

**How to check:** Valid CSV and XLSX load; unsupported extension and malformed files return actionable errors; preview dimensions reconcile; default sample path resolves `data/STEP_10_Dataset/` and future canonical DB path `data/app.db` is supported.

**Tests / acceptance checks:** TC-F-01, TC-F-02, TC-F-03; TC-T-01, TC-T-02.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-02 only. Read docs/06_Product_Requirements_Document_PRD.docx Sections 5, 6 and 10; docs/07_TRD.docx Sections 2, 4 and 5; and docs/13_Test_Cases.docx. Create src/data/loader.py with small, testable functions to read CSV and Excel uploads and load the provided synthetic sample data. Support the mandatory fields Customer ID, Transaction/Order ID, Purchase Date and Transaction Amount. Preserve source values; do not silently rename or overwrite columns except through an explicit, documented alias map. Return structured, user-safe errors for unsupported/corrupt files. Include row/column dimensions and a preview helper. Resolve the sample dataset in data/STEP_10_Dataset/; support data/app.db as the canonical future SQLite path without breaking the current sample location. Do not implement cleaning, RFM calculations, UI pages or database writes yet. Keep identifiers unchanged. Run the relevant existing tests and report results.
```


### BUILD-03 — Validation and controlled cleaning

**Goal:** Implement required-field/type checks, duplicate diagnostics, eligibility rules, retained/excluded counts and an auditable cleaning summary.

**Files:** `src/data/validator.py; src/data/cleaner.py; tests/test_data.py`

**User stories / feature IDs:** US-03, US-18; F-03

**How to check:** Missing mandatory columns block analysis; missing IDs/date/amount are counted; invalid date/amount are flagged; exact duplicate events are distinguished from valid multi-line orders; retained + excluded = input rows; each exclusion has a reason.

**Tests / acceptance checks:** TC-F-04, TC-F-05, TC-F-06, TC-F-24, TC-F-28; TC-T-05.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-03 only. Read the PRD data requirements and data-quality rules, TRD validation/cleaning standards, Step 10 validation report and Step 13 tests. Create src/data/validator.py and src/data/cleaner.py. Mandatory fields are Customer ID, Transaction/Order ID, Purchase Date and Transaction Amount. Report missing columns separately from missing/blank row values, invalid dates, non-numeric amounts, exact duplicate source rows and potential duplicate-order keys. Do not mistake multiple product lines sharing one order_id for duplicate orders. Never replace unknown amount with zero or invent customer/order IDs. Keep original input unchanged and return a cleaned copy plus structured issue counts, retained/excluded counts and per-row exclusion reasons. Follow the established sample's status/duplicate rules and document any ambiguous policy rather than guessing. Ensure retained + excluded reconciles to input count. Implement no UI. Run TC-T-05 and relevant test_data tests; report unresolved policy choices.
```


### BUILD-04 — EDA and descriptive statistics functions

**Goal:** Build pure, reusable summaries for dataset profile, distributions and descriptive statistics.

**Files:** `src/analysis/eda.py; src/analysis/statistics.py; tests/test_analysis.py`

**User stories / feature IDs:** US-04, US-14, US-17; F-04, F-14

**How to check:** Counts, distinct customers, date range, amount summaries and descriptive statistics are reproducible; known vector [1,2,3,4] gives count 4, mean 2.5, median 2.5, min 1, max 4, sample std≈1.290994 (ddof=1).

**Tests / acceptance checks:** TC-F-07, TC-F-08, TC-F-20; TC-T-12.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-04 only. Read the PRD FR-07, FR-08 and FR-20; TRD OQ/statistics methods; Step 13 test fixtures. Create pure functions in src/analysis/eda.py and src/analysis/statistics.py. EDA must report valid row count, distinct customer count, analysis date range, valid transaction amount total and appropriate distributions. Descriptive statistics must include count, mean, median, min, max and sample standard deviation where meaningful, with explicit ddof=1 and null/empty handling. Use pandas/NumPy; use SciPy or statsmodels only when justified by a specific OQ, not for decorative inferential tests. Preserve units/currency metadata and do not infer unsupported business causes. Add deterministic unit tests for [1,2,3,4]. Do not build charts or pages yet.
```


### BUILD-05 — RFM calculation, scoring and segmentation engine

**Goal:** Implement accurate Recency, distinct-order Frequency, Monetary, 1–5 scoring, activity bands and one-segment assignment.

**Files:** `src/analysis/rfm.py; src/analysis/scoring.py; src/analysis/segmentation.py; tests/test_analysis.py`

**User stories / feature IDs:** US-05, US-06, US-07, US-08, US-09; F-05 to F-09

**How to check:** Tiny known fixture: C1 recency=4 days as of 2026-01-11, frequency=2 distinct orders, monetary=175. Scores 1–5; Recency reversed; one segment per eligible customer; activity bands 0–30/31–90/>90.

**Tests / acceptance checks:** TC-F-09 to TC-F-14; TC-T-06 to TC-T-10.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-05 only. Read the BRD business rules, PRD FR-09 to FR-14, TRD RFM aggregation/scoring rules, STEP 8 database design, STEP 9 ERD and STEP 13 deterministic fixtures. Create pure functions in src/analysis/rfm.py, scoring.py and segmentation.py. Recency is whole days from the run's reference_date to each customer's latest valid purchase date. Frequency counts DISTINCT valid order_id per customer, never line-item rows. Monetary sums valid transaction_amount for the selected analysis period only. Exclude rows already marked invalid by the cleaner. Default reference date is one day after latest valid purchase date unless user selects a reporting date. Score dimensions 1–5 where sample size supports quantiles; Recency direction is reversed so lower recency gets higher score; document small-sample/tie handling deterministically. Apply the approved segment definitions from the database/PRD and ensure each eligible customer receives exactly one segment. Activity bands: 0–30 recent, 31–90 at-risk, >90 inactive. Do not add churn prediction or campaign execution. Update tests/test_analysis.py to test the documented interfaces while preserving all test IDs. Run TC-T-06 through TC-T-10.
```


### BUILD-06 — Segment and revenue aggregation functions

**Goal:** Create reconciled segment distribution and segment revenue summaries.

**Files:** `src/analysis/segments.py; src/analysis/revenue.py; tests/test_analysis.py`

**User stories / feature IDs:** US-11, US-12, US-13; F-11, F-12

**How to check:** Segment counts reconcile to eligible customers; percentages total 100% subject to rounding; segment revenue sums to valid revenue for the same period.

**Tests / acceptance checks:** TC-F-17, TC-F-18, TC-F-22; TC-T-11.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-06 only. Read PRD FR-17 and FR-18, TRD OQ-08/OQ-09, database design and test catalogue. Create reusable segment distribution and revenue aggregation functions. Segment count and percent must reconcile to eligible customer population. Revenue by segment must be derived from valid transaction amounts joined through the approved customer-to-segment mapping and selected analysis_run; total segment revenue must reconcile to valid revenue for that same period/run. Avoid double counting line items or customer RFM joins. Return tidy DataFrames suitable for Plotly and tables. Add tests for totals, shares and sorting. Do not build UI pages.
```


### BUILD-07 — SQLite persistence and analysis-run service

**Goal:** Integrate the approved five-table schema, safe writes/reads and joined customer RFM view.

**Files:** `src/data/database.py; src/data/repository.py; data/app.db (runtime-created or copied from supplied sample); tests/test_data.py`

**User stories / feature IDs:** US-01, US-03, US-17; F-01, F-03, F-05 to F-12

**How to check:** DDL matches Step 8 data dictionary and Step 9 ERD; FK enforcement enabled per connection; PK/FK checks pass; run metadata and derived outputs are scoped by run_id.

**Tests / acceptance checks:** TC-T-01 to TC-T-04; TC-T-18 where repository/export metadata applies.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-07 only. Read docs/08_Database_Design.xlsx and docs/09_ER_Diagram.docx before writing SQL. Implement SQLite connection/repository helpers that preserve the approved five entities: customer_master, segment_master, analysis_run, transaction_fact and customer_rfm_fact, with the ERD's relationships and composite key (run_id, customer_id) for customer RFM snapshots. Enable PRAGMA foreign_keys=ON on every connection. Use transactions and parameterized SQL; never concatenate user input into SQL. Keep the joined analysis view aligned with the approved design. The Step 10 SQLite_DDL sheet was noted as potentially incomplete; treat the data dictionaries/ERD as the schema authority and record any discrepancy rather than silently changing the logical model. Use data/app.db as the runtime canonical path; the bundled sample remains data/STEP_10_Dataset/app.db. Verify row counts, unique keys and foreign_key_check. Do not promise persistent SQLite writes on Streamlit Community Cloud; document ephemeral storage.
```


### BUILD-08 — Shared Streamlit UI components and session state

**Goal:** Build the common header, KPI cards, chart cards, insight boxes, filter state and navigation helpers.

**Files:** `src/ui.py; src/state.py; src/components.py; .streamlit/config.toml`

**User stories / feature IDs:** US-10, US-11, US-17, US-18; UI-01 to UI-09 foundation

**How to check:** Existing Tailwind iframe header/KPI starter works; native Streamlit fallback works; filters use stable session keys; changing source clears stale data/cache/errors; optional fields are detected before showing filters.

**Tests / acceptance checks:** TC-T-17; TC-F-21, TC-F-22, TC-F-24, TC-F-26.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-08 only. Read docs/12_UI_Framework.docx and docs/07_TRD.docx UI standards. Reuse and review the existing src/ui.py starter rather than replacing it blindly. Provide shared header, KPI card, chart card, insight box, status badge, filter group, active-filter count and reset helpers. Tailwind CDN is confined to the iframe; Streamlit controls remain native and accessible. Preserve the Streamlit 1.50.0 compatibility fallback to streamlit.components.v1.iframe because st.iframe is only available in later versions; do not remove the fallback unless requirements are explicitly upgraded and verified. Use st.session_state with namespaced stable keys. On new upload, clear old valid_df, rfm_df, cached outputs and stale errors. Optional region/category fields must only create controls when present. Use theme colors from .streamlit/config.toml. Do not add new screen IDs.
```


### BUILD-09 — UI-01 Home / Overview page

**Goal:** Build the landing page with dataset/run status and high-level customer/revenue KPIs.

**Files:** `app.py; pages/ (or Streamlit home entry point); src/ui.py`

**User stories / feature IDs:** US-11, US-17; F-04, F-11, F-12

**How to check:** Home opens, shows status and synthetic-data notice; KPI values match underlying filtered/current run; navigation is available; period/reference date visible where relevant.

**Tests / acceptance checks:** TC-F-22, TC-F-26; TC-T-13.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-09 only: UI-01 Home / Overview. Read PRD UI-01 and related FRs, Step 11 stories US-11/US-17, Step 12 wireframe, and Step 13 tests. Use shared UI components. Display project title, synthetic dataset status, current analysis/run status, navigation, and KPI cards only when a valid analysis exists. KPIs must be computed from current run and active applicable filters; never hard-code sample figures. Show analysis period, reference date and currency when available. Provide a friendly empty state before upload. No RFM logic belongs in app.py. Ensure app.py starts cleanly and UI-01 renders under AppTest.
```


### BUILD-10 — UI-02 Data Upload page

**Goal:** Provide supported file upload, guidance, preview and session source replacement.

**Files:** `pages/1_Data_Upload.py; src/data/loader.py; src/state.py`

**User stories / feature IDs:** US-01, US-02, US-18; F-01, F-02

**How to check:** CSV/XLSX accepted; missing required columns and invalid files produce clear errors; preview shows source dimensions; new upload clears previous analysis.

**Tests / acceptance checks:** TC-F-01, TC-F-02, TC-F-03, TC-F-24, TC-F-28.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-10 only: UI-02 Data Upload. Read the approved UI-02 screen definition, US-01, US-02 and US-18 acceptance criteria, FR-01 to FR-03 and test cases. Use the loader functions; do not duplicate parsing logic in the page. Accept supported CSV/XLSX only, display mandatory fields and format guidance, show upload status and preview rows/column names/dimensions. On replacing a file, invalidate all old analysis state and cached results before processing the new file. Missing mandatory columns block analysis with named fields. Unsupported/corrupt file errors are recoverable and must not leave old results appearing current. Keep controls native Streamlit. Run related TC-F tests.
```


### BUILD-11 — UI-04 Exploratory Data Analysis page

**Goal:** Show dataset profile, transaction/customer totals, date range, amount distributions and descriptive statistics.

**Files:** `pages/2_Exploratory_Analysis.py; src/analysis/eda.py; src/analysis/statistics.py`

**User stories / feature IDs:** US-04, US-14, US-17; F-04, F-14

**How to check:** EDA metrics reconcile to valid rows; descriptive stats match known fixture; charts have readable labels/units; analysis context visible.

**Tests / acceptance checks:** TC-F-07, TC-F-08, TC-F-20, TC-F-27; TC-T-12.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-11 only: UI-04 Exploratory Data Analysis. Read UI-04 specification, US-04/US-14/US-17 and FR-07/FR-08/FR-20. Use the EDA/statistics pure functions. Show valid transaction count, distinct customer count, date range, amount total and distributions. Provide descriptive statistics table (count, mean, median, min, max, sample standard deviation) where meaningful. Plotly charts must include title, axis labels, units and tooltips; optional category/region breakdowns appear only if those columns exist. Clearly label synthetic data. Show analysis period, reference date and currency. No calculations should be embedded in the page.
```


### BUILD-12 — UI-05 RFM Analysis page

**Goal:** Present customer-level R/F/M measures, score definitions, run context and activity band summaries.

**Files:** `pages/3_RFM_Analysis.py; src/analysis/rfm.py; src/analysis/scoring.py`

**User stories / feature IDs:** US-05, US-06, US-07, US-08, US-17; F-05 to F-08

**How to check:** Recency/Frequency/Monetary reconcile; score directions and 1–5 bounds correct; period/reference date and currency displayed.

**Tests / acceptance checks:** TC-F-09, TC-F-10, TC-F-11, TC-F-12, TC-F-14, TC-F-20; TC-T-06 to TC-T-09.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-12 only: UI-05 RFM Analysis. Read UI-05 specification, stories US-05 through US-08 and US-17, FR-09 to FR-12 and TRD RFM rules. Present Recency in days, Frequency as distinct valid orders, Monetary as valid spend, R/F/M score definitions and customer-level table. Explain reference date and selected analysis period separately. Show activity bands using the agreed 0–30 recent, 31–90 at-risk and >90 inactive rules. Never count order lines as separate orders; never include excluded transactions. Use the engine functions only. Provide readable units, sorting and clear empty states. Run linked functional/unit tests.
```


### BUILD-13 — UI-06 Customer Segmentation page

**Goal:** Display documented segment definitions, customer counts, percentages and segment exploration.

**Files:** `pages/4_Customer_Segmentation.py; src/analysis/segmentation.py; src/analysis/segments.py`

**User stories / feature IDs:** US-09, US-12; F-09, F-11

**How to check:** Exactly one segment per eligible customer; segment counts and percentages reconcile; segment selection drives detail context.

**Tests / acceptance checks:** TC-F-13, TC-F-17, TC-F-21; TC-T-10, TC-T-11.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-13 only: UI-06 Customer Segmentation. Read approved segment definitions from PRD/database design and Step 12 UI specification; use US-09 and US-12 acceptance criteria. Display every configured segment with a clear description, count and percentage. Use a sorted horizontal bar chart (and optional 100% stacked comparison only if useful) with a reconciled table. Selecting a segment should make the selection available to customer details through shared state/query parameters without duplicating calculations. Confirm every eligible customer has exactly one segment. Do not invent segment names or thresholds; follow the approved data dictionary/rules.
```


### BUILD-14 — UI-07 Customer Details page

**Goal:** Enable customer search, filters and inspection of customer-level RFM outputs.

**Files:** `pages/5_Customer_Details.py; src/state.py; src/analysis/*`

**User stories / feature IDs:** US-10; F-10

**How to check:** Search and segment/activity/score filters return only matching customers; reset restores full result; empty result message appears.

**Tests / acceptance checks:** TC-F-15, TC-F-16, TC-F-21, TC-F-23, TC-F-25.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-14 only: UI-07 Customer Details. Read PRD UI-07/FR-15/FR-16, US-10 and UI Framework. Show only synthetic customer IDs plus Recency, Frequency, Monetary, R/F/M scores and segment. Provide customer search and relevant segment/activity/score filters; expose optional region/category filters only if columns exist. All selected filters must combine correctly and update the table and dependent KPI/chart outputs. Include reset and a clear empty state. Provide a download of the currently filtered result with analysis period, reference date, currency and rules version in metadata/note. Do not display or request real PII.
```


### BUILD-15 — UI-08 Revenue Analysis page

**Goal:** Compare revenue contribution by segment and reconcile segment totals to valid revenue.

**Files:** `pages/6_Revenue_Analysis.py; src/analysis/revenue.py`

**User stories / feature IDs:** US-13, US-14, US-17; F-12, F-14

**How to check:** Sorted segment revenue bar and table; totals reconcile to valid transaction amount; period/currency labels correct.

**Tests / acceptance checks:** TC-F-08, TC-F-18, TC-F-20, TC-F-22, TC-F-25, TC-F-27; TC-T-11, TC-T-12.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-15 only: UI-08 Revenue Analysis. Read UI-08, US-13/US-14/US-17, FR-18/FR-20 and OQ-09 chart guidance. Display sorted horizontal segment revenue bars and a table with segment, customer count and revenue where meaningful. Revenue must be calculated for the same analysis_run and selected period, use valid transaction amounts only, and reconcile to the valid total. Display currency from dataset/run metadata; never hard-code INR for arbitrary uploads. Include optional comparison/trend only where date data supports it. Keep exact totals available in a table.
```


### BUILD-16 — UI-09 Business Insights page

**Goal:** Provide at least three evidence-based, advisory retention/loyalty recommendations and at-risk/inactive summaries.

**Files:** `pages/7_Business_Insights.py; src/analysis/insights.py`

**User stories / feature IDs:** US-15, US-16; F-13

**How to check:** At least three recommendations each cite observed segment/RFM evidence; at-risk/inactive lists follow recency bands; no campaign automation or predictive claims.

**Tests / acceptance checks:** TC-F-14, TC-F-19, TC-F-21; TC-T-10, TC-T-11.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-16 only: UI-09 Business Insights. Read PRD FR-13/FR-14/FR-19, BR-04/BR-09/BR-10, stories US-15/US-16 and OQ-05/OQ-06/OQ-07/OQ-10. Create at least three advisory recommendations tied explicitly to observed RFM score, segment, recency, customer count or revenue evidence. Show at-risk (31–90 days) and inactive (>90 days) summaries using the agreed thresholds. Clearly explain why each group is highlighted and include a caution that historical RFM does not prove customer intent or predict return. Do not trigger campaigns, send offers or claim predictive churn. Avoid unsupported causal language.
```


### BUILD-17 — UI-03 Data Validation / Quality page

**Goal:** Expose schema checks, missing/invalid/duplicate counts, exclusions and data-quality reasons.

**Files:** `pages/8_Data_Validation.py; src/data/validator.py; src/data/cleaner.py`

**User stories / feature IDs:** US-03, US-18; F-03

**How to check:** Missing mandatory columns block analysis; issue counts and retained/excluded reconcile; duplicate line items are not misclassified; error is recoverable.

**Tests / acceptance checks:** TC-F-04, TC-F-05, TC-F-06, TC-F-24, TC-F-28; TC-T-05.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-17 only: UI-03 Data Validation. Read UI-03, FR-02/FR-04/FR-05/FR-06, stories US-03/US-18 and the Step 10 validation report. Present schema status, missing values by mandatory field, invalid dates/amounts, duplicate diagnostics, retained/excluded counts and exclusion reasons. Retained + excluded must reconcile to input rows. Clearly distinguish exact duplicate source events from legitimate multi-line orders. If mandatory columns are absent, block downstream analysis and name the missing fields. A failed re-upload must never leave stale results labelled current. Use validator/cleaner outputs; do not recompute rules in the page.
```


### BUILD-18 — Operational-question chart coverage and navigation polish

**Goal:** Verify all ten OQs have a correct visual/table answer and all nine screen IDs are reachable with consistent shared filters.

**Files:** `pages/*.py; src/ui.py; src/state.py`

**User stories / feature IDs:** All US-01 to US-18; F-01 to F-14

**How to check:** OQ-01 to OQ-10 visible answers; all UI-01 to UI-09 reachable; filters update all relevant KPIs/charts/tables; empty states and phone-width layout usable.

**Tests / acceptance checks:** TC-F-15 to TC-F-27; TC-F-26; TC-T-14; TC-T-17.

**Exact AI prompt (copy as-is):**

```text
Perform BUILD-18 as an integration/polish task only. Read docs/12_UI_Framework.docx OQ chart mapping and all nine screen definitions. Verify OQ-01 to OQ-10 are answered by appropriate charts plus auditable tables; use the approved chart choices and do not invent a new OQ or UI ID. Check navigation, filter consistency, active filter/reset state, optional-field guards, empty results, phone-width layout, readable labels and accessible text equivalents. Confirm UI-01 to UI-09 are all reachable. Fix only integration issues; do not refactor working business logic without a failing test and explanation. Report OQ-to-screen-to-test coverage.
```


### BUILD-19 — Complete automated and functional test execution

**Goal:** Run all 46 planned cases, complete missing unit/integration/AppTest coverage and fix defects without changing approved requirements.

**Files:** `tests/test_data.py; tests/test_analysis.py; tests/test_app.py; tests/conftest.py; docs/13_Test_Cases.docx (execution evidence/status updates)`

**User stories / feature IDs:** All US-01 to US-18; all F-01 to F-14

**How to check:** pytest suite passes; AppTest starts and every page renders; all functional cases executed with evidence; startup target <3s measured; 50k-row processing target <=10s measured.

**Tests / acceptance checks:** TC-F-01 to TC-F-28; TC-T-01 to TC-T-18.

**Exact AI prompt (copy as-is):**

```text
Perform BUILD-19 testing and defect resolution. Read the entire docs/13_Test_Cases.docx and current RTM. Run every technical test TC-T-01 to TC-T-18 and execute all functional cases TC-F-01 to TC-F-28 against the app. Add integration fixtures/conftest where necessary, but preserve every test ID and expected business rule. Fix code defects, not the tests' expected results, unless a documented source-baseline contradiction is proven and escalated for approval. Verify SQLite integrity, calculation fixtures, all page renders, filters, empty states, exports and recoverable upload errors. Measure AppTest startup target <3 seconds and PRD NFR-01 validation/RFM processing <=10 seconds for up to 50,000 synthetic rows on the agreed machine; record machine, versions, cold/warm state and timing. Update execution status and evidence in the test document; do not mark any test Pass without proof. Report all failures/limitations transparently.
```


### BUILD-20 — README and local operating runbook

**Goal:** Write a complete project README with architecture, setup, run/test commands, data dictionary summary, screenshots and limitations.

**Files:** `README.md; requirements.txt; docs/ (links to approved artefacts)`

**User stories / feature IDs:** US-01 to US-18 (user guidance); F-01 to F-14

**How to check:** A new developer can create venv, install, launch app, run tests and understand sample data, RFM rules and limitations using README only.

**Tests / acceptance checks:** TA-01, TA-02; verify install/run/test commands manually.

**Exact AI prompt (copy as-is):**

```text
Implement BUILD-20 documentation only. Read all docs/01 through docs/13, current source tree, requirements.txt and test outputs. Create a comprehensive README.md with project purpose, ten-line summary, feature list, personas, OQ coverage, architecture, folder tree, Python 3.12 setup, exact Windows PowerShell and generic terminal commands, app launch, pytest commands, sample synthetic data location, database schema summary, RFM formulas/reference date/recency bands/scoring/segment rule explanation, screenshots section, deployment link placeholder, known limitations and document links. State clearly that SQLite Community Cloud storage may be ephemeral and all data is synthetic. Do not claim deployment is complete or tests pass unless evidence confirms it. Keep the documentation consistent with the approved IDs and source docs.
```


### BUILD-21 — GitHub hygiene and Streamlit Community Cloud deployment

**Goal:** Prepare a clean repository, deploy the tested app and document the live URL and runtime limitations.

**Files:** `.gitignore; requirements.txt; README.md; app.py; pages/; src/; .streamlit/config.toml; GitHub repository settings`

**User stories / feature IDs:** US-01 to US-18; F-01 to F-14

**How to check:** Clean Python 3.12 build; secrets excluded; deployed app opens; sample data loads or user can upload; all pages reachable; ephemeral SQLite limitation documented.

**Tests / acceptance checks:** TA-01 to TA-05; TC-T-13, TC-T-14, TC-T-16; deployment readiness checklist in TRD.

**Exact AI prompt (copy as-is):**

```text
Perform BUILD-21 deployment only after BUILD-19 is green. Read docs/07_TRD.docx deployment requirements and docs/13_Test_Cases.docx evidence. Check Git status, .gitignore, secrets, synthetic-only data and requirements. Do not commit API keys, personal data, local caches or unintended DB files. Push the approved project to the user's GitHub repository only after confirming the target repository/branch. Configure Streamlit Community Cloud to use app.py and the approved requirements. Deploy, inspect build logs, open the live URL, test upload and all nine pages, and record the exact deployed URL and date in README. Document sleep/quota limits and that local SQLite persistence is ephemeral on Community Cloud; do not promise durable storage. If deployment credentials or user confirmation are required, stop and ask rather than inventing access.
```


## 5. Definition of Done (project-level)

- [ ] All Must business requirements BR-01 to BR-09 (and BR-12 as prioritised in the approved BRD/RTM) are implemented and accepted; Should/Could requirements are implemented only where planned and feasible. Do not reinterpret priorities—use the RTM.
- [ ] All ten operational questions OQ-01 to OQ-10 have a visible, auditable answer via a chart and/or table.
- [ ] All 20 functional requirements FR-01 to FR-20 are implemented or explicitly dispositioned against the approved PRD; all Must NFRs are met or a documented limitation is approved.
- [ ] All eligible customers receive valid Recency, distinct-order Frequency, Monetary, documented scores and exactly one segment.
- [ ] Data quality findings, exclusions and reasons are transparent; retained + excluded rows reconcile to input.
- [ ] All planned automated technical tests TC-T-01 to TC-T-18 pass; all functional cases TC-F-01 to TC-F-28 are executed and have evidence/status recorded. No critical/high defect remains open.
- [ ] AppTest confirms the app starts and every approved screen renders. Measure the <3-second startup target separately from PRD NFR-01 processing target of <=10 seconds for up to 50,000 rows.
- [ ] All nine approved UI screens UI-01 to UI-09 are reachable and usable; shared filters update applicable KPIs, charts and tables consistently.
- [ ] README includes install/run/test instructions, architecture, data/RFM rules, document links, screenshots or placeholders, limitations and deployment URL once live.
- [ ] Application is deployed to Streamlit Community Cloud and the live URL is verified. Document free-tier availability limits and ephemeral SQLite storage; do not promise durable persistence.
- [ ] Only synthetic data is used; no secrets, real PII or unintended local files are committed.

## 6. Commands (Windows PowerShell)

```powershell
# 1) Open project root in VS Code, then create virtual environment
py -3.12 -m venv .venv

# 2) Activate environment
.\.venv\Scripts\Activate.ps1

# 3) Upgrade pip and install pinned dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4) Run the Streamlit app
python -m streamlit run app.py

# 5) Run all automated tests
python -m pytest -q

# 6) Run focused test modules
python -m pytest tests/test_data.py -q
python -m pytest tests/test_analysis.py -q
python -m pytest tests/test_app.py -q

# 7) Optional test report
python -m pytest -q --junitxml=test-results.xml
```

### Generic terminal equivalents

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
python -m pytest -q
```

> Use Python 3.12 as specified in the TRD. Verify the proposed dependency pins with a clean install before freezing requirements. The Streamlit 1.50.0 baseline needs the compatibility fallback already present in `src/ui.py` for iframe rendering; `st.iframe` is not available on that pin.


## 7. Viva notes — 10 likely questions

1. **Q: What is RFM analysis?**  
   **A:** A customer analysis method using Recency (how recently a customer purchased), Frequency (distinct valid orders) and Monetary (valid spend).

2. **Q: Why does Frequency count distinct Order IDs?**  
   **A:** A single order may contain multiple line items; counting rows would overstate purchase frequency.

3. **Q: How is Recency calculated?**  
   **A:** Whole-day difference between the analysis reference date and the customer's latest valid purchase date.

4. **Q: Why use a reference date one day after the latest valid purchase by default?**  
   **A:** It provides a consistent as-of date so the most recent purchase is not assigned an artificial negative or zero-day reporting offset.

5. **Q: What is the difference between a transaction line and an order?**  
   **A:** A transaction line is an item-level record; several lines can share one Order ID and together represent one purchase.

6. **Q: Why do we validate and clean data before RFM?**  
   **A:** Missing IDs, invalid dates or amounts and duplicate source events can distort customer measures and segment assignment.

7. **Q: What is the purpose of RFM scoring and segmentation?**  
   **A:** Scoring makes the three measures comparable; segmentation groups customers under documented behavioural rules for interpretation.

8. **Q: Why use SQLite in this project?**  
   **A:** It provides a lightweight relational store for analysis runs, transactions and customer-level RFM snapshots without requiring a separate database server.

9. **Q: What is the role of pytest and Streamlit AppTest?**  
   **A:** pytest checks data and analytical functions; AppTest verifies Streamlit startup and page/widget behaviour programmatically.

10. **Q: What are the main deployment limitations?**  
   **A:** Streamlit Community Cloud free-tier availability can vary and local SQLite storage is ephemeral across instance restarts; durable persistence is not guaranteed.


## 8. Build execution protocol

1. Start with BUILD-01 only. Read the prompt and source docs before editing.
2. Make the smallest change that completes the task; do not build multiple tasks together.
3. Run the task's checks and tests. Capture command output and changed-file list.
4. If a test fails, fix the implementation or report a genuine source conflict; never weaken expected assertions just to obtain a green run.
5. Update this plan only if an approved decision changes. Preserve IDs and add a short change note.
6. Stop and report completion, files changed, tests run/results and any blocker. Wait for the user to request the next BUILD task.


## 9. Known constraints and source-baseline cautions

- Step 8 database design and Step 9 ERD define five entities: customer_master, segment_master, analysis_run, transaction_fact and customer_rfm_fact. Follow the data dictionaries/ERD; the earlier lifecycle notes flagged that the SQLite_DDL worksheet may not contain the complete DDL.

- The Step 10 dataset contains 30 customer rows, 8 segment rows, 1 analysis run, 200 transaction lines and 30 customer RFM snapshots (269 planned/actual records across tables). The joined view contains 30 rows and 36 columns.

- Step 10 quality notes include optional missing values, a duplicate source event, one high-ticket Electronics transaction, and returned/cancelled transactions excluded under the sample rules. Do not treat these as new business rules; preserve the validation report and explain exclusions.

- The Step 13 test document sets all cases initially to Not run. Database checks were previously reported as 10 passed, 2 skipped and 0 failed in one local test attempt; re-run them in the final Python 3.12 environment and do not rely on that historical run as final sign-off.

- The current Step 10 database is stored at data/STEP_10_Dataset/app.db; the TRD's runtime canonical path is data/app.db. BUILD-07 must implement a deliberate canonical-path strategy and retain compatibility with the supplied sample file.
