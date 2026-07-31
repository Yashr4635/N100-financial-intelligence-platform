<div align="center">

# 📈 N100 Financial Intelligence Platform

### Enterprise-Grade Financial Analytics System for NIFTY 100 Companies

**ETL Automation • Data Validation • Financial Ratio Engine • Health Scoring • Sector Analytics • Peer Comparison • Radar Chart Engine • Valuation Engine • Investment Screening • Interactive Dashboard**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Engine-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Data%20Warehouse-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Visualizations-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![Pytest](https://img.shields.io/badge/Pytest-Tested-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Build](https://img.shields.io/badge/Build-Passing-brightgreen?style=flat-square)](#-testing)
[![Tests](https://img.shields.io/badge/Tests-47%20Passed-success?style=flat-square)](#-testing)
[![Maintenance](https://img.shields.io/badge/Maintained-Yes-blue?style=flat-square)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-ff69b4.svg?style=flat-square)](#-contributing)

[**🚀 Live Demo**](https://n100-financial-intelligence-platform-xwvsj4aaugscczp2uv4vyy.streamlit.app/) · [**📖 Documentation**](#-table-of-contents) · [**🐛 Report Bug**](https://github.com/Yashr4635/N100-financial-intelligence-platform/issues) · [**✨ Request Feature**](https://github.com/Yashr4635/N100-financial-intelligence-platform/issues)

</div>

---

## 📚 Table of Contents

- [Overview](#-overview)
- [Key Highlights](#-key-highlights)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Code Architecture](#-code-architecture)
- [Datasets](#-datasets-processed)
- [Database Schema](#-database-schema)
- [Data Quality Validation](#-data-quality-validation)
- [Analytics Modules](#-analytics-modules)
- [Dashboard](#-dashboard)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Usage](#-usage)
- [Outputs Generated](#-outputs-generated)
- [Testing](#-testing)
- [Code Quality](#-code-quality)
- [Deployment](#-deployment)
- [Performance Highlights](#-performance-highlights)
- [Roadmap](#-roadmap--future-improvements)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## 🧭 Overview

The **N100 Financial Intelligence Platform** is an end-to-end financial analytics system built with **Python, SQLite, Pandas, and Streamlit**. It transforms raw, messy Excel exports of NIFTY 100 company financials into a clean, validated, queryable data warehouse — then layers on a full analytics stack: financial ratios, company health scoring, sector benchmarking, peer comparison, radar-chart visual profiling, a valuation engine, an investment screener, and a live interactive multi-page dashboard.

It automates:

| Stage | Capability |
|---|---|
| 🔄 | ETL Pipeline |
| 🧪 | Data Validation |
| 📊 | Financial Ratio Calculation |
| 💯 | Company Health Score |
| 🏭 | Sector Analytics |
| 🤝 | Peer Comparison |
| 🕸️ | Radar Chart Generation |
| 💰 | Valuation Analysis |
| 🔎 | Investment Screening |
| 🖥️ | Interactive Dashboard |

---

## 🌟 Key Highlights

<div align="center">

| 📁 12 Datasets | 🏢 92 Companies | 🏭 10 Sectors | 📈 1,184 Records | 🗄️ 12 SQLite Tables | ✅ 16 Validation Rules | 🕸️ 92 Radar Charts |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Excel sources ingested | NIFTY 100 coverage | Fully benchmarked | Loaded & validated | Relational warehouse | Data quality gates | Auto-generated PNGs |

</div>

---

## ✨ Features

- ✅ **Automated ETL Pipeline** — extraction, normalization, validation, and loading, fully scripted
- ✅ **Smart Excel Loader** — automatic header detection, multi-sheet support, dynamic loading, resilient error handling
- ✅ **Dataset Normalization** — consistent schema, null handling, duplicate removal, type coercion
- ✅ **16 Data Quality Validation Rules** — with automated failure reporting
- ✅ **SQLite Data Warehouse** — 12 relational tables, SQL-queryable
- ✅ **Financial Ratio Engine** — ROE, margins, leverage, and quality scoring
- ✅ **Health Score Engine** — weighted 0–100 company health scoring
- ✅ **Sector Analytics** — sector-level performance benchmarking
- ✅ **Peer Comparison Engine** — cross-company benchmarking within sector/peer groups
- ✅ **Radar Chart Engine** — auto-generated multi-metric visual company profiles (92 PNGs)
- ✅ **Valuation Engine** — valuation summary generation with flagged over/undervaluation signals
- ✅ **Investment Screener** — rules-based company shortlisting
- ✅ **Reporting Engine** — executive summary and analytics summary exports
- ✅ **Interactive Streamlit Dashboard** — 8-page, Plotly-powered, multi-page, filterable
- ✅ **Unit Testing** — Pytest coverage across core modules
- ✅ **Error Handling & Logging** — structured logs across the pipeline
- ✅ **Config-Driven Architecture** — no hardcoded paths or thresholds

---

## 🛠 Tech Stack

<div align="center">

| Category | Tools |
|---|---|
| **Language** | ![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white) |
| **Data Processing** | ![Pandas](https://img.shields.io/badge/-Pandas-150458?style=flat-square&logo=pandas&logoColor=white) ![NumPy](https://img.shields.io/badge/-NumPy-013243?style=flat-square&logo=numpy&logoColor=white) |
| **Storage** | ![SQLite](https://img.shields.io/badge/-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) |
| **Visualization** | ![Plotly](https://img.shields.io/badge/-Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white) |
| **Dashboard** | ![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) |
| **File I/O** | ![OpenPyXL](https://img.shields.io/badge/-OpenPyXL-217346?style=flat-square&logo=microsoft-excel&logoColor=white) |
| **Testing** | ![Pytest](https://img.shields.io/badge/-Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white) |
| **Code Quality** | ![Black](https://img.shields.io/badge/-Black-000000?style=flat-square&logo=python&logoColor=white) ![Ruff](https://img.shields.io/badge/-Ruff-D7FF64?style=flat-square&logo=ruff&logoColor=black) |
| **Version Control** | ![Git](https://img.shields.io/badge/-Git-F05032?style=flat-square&logo=git&logoColor=white) ![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github&logoColor=white) |

</div>

---

## 🏗 Architecture

```text
                ┌────────────────────┐
                │   Raw Excel Files   │
                │  (12 datasets)      │
                └──────────┬─────────┘
                           │
                           ▼
                ┌────────────────────┐
                │   Excel Loader      │  ← header detection, multi-sheet
                └──────────┬─────────┘
                           │
                           ▼
                ┌────────────────────┐
                │   Normalizer        │  ← cleaning, schema, dedup
                └──────────┬─────────┘
                           │
                           ▼
                ┌────────────────────┐
                │   Validator         │  ← 16 quality rules
                └──────────┬─────────┘
                           │
                           ▼
                ┌────────────────────┐
                │   SQLite Database   │  ← nifty100.db (12 tables)
                └──────────┬─────────┘
                           │
                           ▼
                ┌──────────────────────────────────────────────┐
                │               Analytics Engine                 │
                │  Ratios · Health Score · Sector · Peer         │
                │  Comparison · Radar Charts · Valuation         │
                └──────────┬───────────────────────────────────┘
                           │
                           ▼
                ┌────────────────────┐
                │   Reporting Layer   │  ← CSV / XLSX exports
                └──────────┬─────────┘
                           │
                           ▼
                ┌────────────────────┐
                │   Streamlit         │
                │   8-Page Dashboard  │
                └────────────────────┘
```

---

## 📂 Project Structure

```text
N100-Financial-Intelligence-Platform/
│
├── dashboard/
│   └── app.py                       # Streamlit entry point
│
├── src/
│   ├── etl/                         # Loading, normalization, validation
│   ├── database/                    # SQLite connection & schema logic
│   ├── analytics/                   # Ratios, health score, sector, peer,
│   │                                 # radar chart, valuation, screener
│   ├── dashboard/                   # Dashboard page components
│   └── utils/                       # Shared helpers, config, logging
│
├── database/
│   └── nifty100.db                  # Generated SQLite warehouse
│
├── data/
│   ├── raw/                         # Original Excel exports
│   ├── processed/                   # Cleaned intermediate data
│   └── output/                      # Final load-ready datasets
│
├── outputs/
│   ├── financial_ratios_calculated.csv
│   ├── company_health_scores.csv
│   ├── sector_analysis.csv
│   ├── investment_screener.csv
│   ├── peer_comparison.csv
│   ├── analytics_summary.xlsx
│   ├── executive_summary.csv
│   ├── valuation_summary.xlsx
│   ├── valuation_flags.csv
│   └── radar_charts/                # 92 auto-generated PNGs
│
├── reports/
│   ├── validation_failures.csv      # Data quality failure log
│   └── load_audit.csv               # ETL load audit trail
│
├── sql/
│   ├── schema.sql                   # Table definitions
│   └── exploratory_queries.sql      # Analyst SQL queries
│
├── tests/
│   ├── test_loader.py
│   ├── test_normalizer.py
│   ├── test_validator.py
│   └── test_database.py
│
├── docs/
│   └── screenshots/
│       ├── home.png
│       ├── company_profile.png
│       ├── investment_screener.png
│       ├── peer_comparison.png
│       ├── financial_trends.png
│       ├── sector_dashboard.png
│       ├── capital_allocation.png
│       └── reports.png
│
├── requirements.txt
└── README.md
```

| Folder | Purpose |
|---|---|
| `dashboard/` | Streamlit application entry point |
| `src/etl/` | Excel loading, normalization, and validation logic |
| `src/database/` | Database connection, schema creation, and load routines |
| `src/analytics/` | Financial ratio engine, health scoring, sector analytics, peer comparison, radar chart engine, valuation engine, screener |
| `src/dashboard/` | Reusable UI components for dashboard pages |
| `src/utils/` | Configuration, logging, and shared utility functions |
| `database/` | Generated SQLite data warehouse |
| `data/` | Raw, processed, and output-stage datasets |
| `outputs/` | Final analytics exports (CSV, XLSX, radar chart PNGs) |
| `reports/` | Auto-generated validation and audit reports |
| `sql/` | Schema definitions and exploratory SQL |
| `tests/` | Pytest unit test suite |
| `docs/` | Documentation assets and dashboard screenshots |

---

## 🧩 Code Architecture

| Module | Responsibility |
|---|---|
| **`src/etl/`** | Reads raw Excel files, detects headers dynamically, normalizes schemas, and applies the 16-rule validation engine before loading. |
| **`src/database/`** | Manages the SQLite connection, applies `schema.sql`, and performs idempotent, auditable loads into the warehouse. |
| **`src/analytics/`** | Houses the Financial Ratio Engine, Health Score Engine, Sector Analytics, Peer Comparison Engine, Radar Chart Engine, Valuation Engine, and Investment Screener logic. |
| **`src/utils/`** | Centralizes configuration, path management, and structured logging used across all modules. |
| **`src/dashboard/`** | Provides the page-level components (Home, Company Profile, Investment Screener, Peer Comparison, Financial Trends, Sector Dashboard, Capital Allocation, Reports) consumed by `dashboard/app.py`. |

---

## 📊 Datasets Processed

<div align="center">

| # | Dataset | Source File |
|---|---|---|
| 1 | Companies | `companies.xlsx` |
| 2 | Balance Sheet | `balancesheet.xlsx` |
| 3 | Cash Flow | `cashflow.xlsx` |
| 4 | Profit & Loss | `profitandloss.xlsx` |
| 5 | Financial Ratios | `financial_ratios.xlsx` |
| 6 | Market Capitalization | `market_cap.xlsx` |
| 7 | Stock Prices | `stock_prices.xlsx` |
| 8 | Sectors | `sectors.xlsx` |
| 9 | Peer Groups | `peer_groups.xlsx` |
| 10 | Analysis | `analysis.xlsx` |
| 11 | Documents | `documents.xlsx` |
| 12 | Pros & Cons | `prosandcons.xlsx` |

</div>

---

## 🗄 Database Schema

SQLite warehouse: **`database/nifty100.db`**

<div align="center">

| Table | Description |
|---|---|
| `companies` | Master company reference data |
| `balancesheet` | Balance sheet line items by company/year |
| `cashflow` | Cash flow statement line items |
| `profitandloss` | P&L statement line items |
| `financial_ratios` | Pre-computed and derived financial ratios |
| `market_cap` | Market capitalization history |
| `stock_prices` | Historical OHLCV stock price data |
| `sectors` | Sector and industry classifications |
| `peer_groups` | Company peer-group mappings |
| `analysis` | Analyst commentary and metrics |
| `documents` | Linked filings and disclosures |
| `prosandcons` | Qualitative pros/cons per company |

</div>

Explore the warehouse via `sql/exploratory_queries.sql` or any SQLite client.

---

## ✅ Data Quality Validation

The pipeline enforces **16 automated validation rules** before any data reaches the warehouse:

<table>
<tr>
<td valign="top" width="50%">

**Structural Checks**
- Empty dataset detection
- Duplicate rows
- Duplicate columns
- Blank column names
- Missing values
- Duplicate Primary IDs

</td>
<td valign="top" width="50%">

**Business Rule Checks**
- Duplicate Company IDs
- Duplicate Company-Year records
- Invalid years
- Missing Company IDs
- Missing Year values
- Negative Sales
- Negative Assets
- Negative Liabilities
- Negative Close Prices
- Negative Volume

</td>
</tr>
</table>

Every run produces a `reports/validation_failures.csv` audit trail of any records that fail these rules, alongside a `reports/load_audit.csv` summary of what was loaded.

---

## 📐 Analytics Modules

<details>
<summary><b>🧮 Financial Ratio Engine</b></summary>

Calculates, per company/year:
- Return on Equity (ROE)
- Profit Margin
- Debt to Equity
- Asset Turnover
- Earnings Per Share (EPS)
- Financial Quality Score

</details>

<details>
<summary><b>💯 Health Score Engine</b></summary>

Generates a **weighted score out of 100** using:
- ROE
- Profit Margin
- Debt
- Asset Turnover
- EPS

</details>

<details>
<summary><b>🏭 Sector Analytics</b></summary>

Benchmarks companies across their sector using:
- Sector Performance
- Average ROE
- Average Health Score
- Debt Analysis

</details>

<details>
<summary><b>🤝 Peer Comparison Engine</b></summary>

Compares each company against its peer group on:
- Ratio-by-ratio benchmarking
- Health Score differential
- Relative sector standing

</details>

<details>
<summary><b>🕸️ Radar Chart Engine</b></summary>

Generates a multi-metric radar chart PNG per company (92 total), plotting normalized values across ROE, margin, leverage, turnover, and health score for at-a-glance visual profiling.

</details>

<details>
<summary><b>💰 Valuation Engine</b></summary>

Produces a valuation summary and flags companies as potentially over- or under-valued based on ratio and price-based signals, exported to `valuation_summary.xlsx` and `valuation_flags.csv`.

</details>

<details>
<summary><b>🔎 Investment Screener</b></summary>

Shortlists companies using rules such as:
- Health Score ≥ 80
- Financial Quality ≥ 4

</details>

---

## 🖥 Dashboard

An interactive, **8-page Streamlit** dashboard powered by **Plotly** visualizations, KPI cards, and dynamic filters.

### Dashboard Pages

| Page | Description |
|---|---|
| 🏠 **Home** | High-level KPIs across the full NIFTY 100 universe |
| 🏢 **Company Profile** | Deep-dive financials, ratios, radar chart, and trends per company |
| 🔎 **Investment Screener** | Filterable, rules-based company shortlisting |
| 🤝 **Peer Comparison** | Side-by-side benchmarking against peer group |
| 📈 **Financial Trends** | Multi-year ratio and performance trend visualization |
| 🏭 **Sector Dashboard** | Sector-level benchmarking and comparisons |
| 💰 **Capital Allocation** | Capital structure and allocation analysis |
| 📄 **Reports** | Executive summary and downloadable analytics exports |

---

## 📸 Screenshots

<table>
  <tr>
    <td align="center" width="50%"><b>🏠 Home</b><br><img src="docs/screenshots/home.png" width="420"/></td>
    <td align="center" width="50%"><b>🏢 Company Profile</b><br><img src="docs/screenshots/company_profile.png" width="420"/></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>🔎 Investment Screener</b><br><img src="docs/screenshots/investment_screener.png" width="420"/></td>
    <td align="center" width="50%"><b>🤝 Peer Comparison</b><br><img src="docs/screenshots/peer_comparison.png" width="420"/></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>📈 Financial Trends</b><br><img src="docs/screenshots/financial_trends.png" width="420"/></td>
    <td align="center" width="50%"><b>🏭 Sector Dashboard</b><br><img src="docs/screenshots/sector_dashboard.png" width="420"/></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>💰 Capital Allocation</b><br><img src="docs/screenshots/capital_allocation.png" width="420"/></td>
    <td align="center" width="50%"><b>📄 Reports</b><br><img src="docs/screenshots/reports.png" width="420"/></td>
  </tr>
</table>

> ⚠️ Replace placeholder screenshot filenames above with your actual exported images before publishing.

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/Yashr4635/N100-financial-intelligence-platform.git

# 2. Move into the project folder
cd N100-financial-intelligence-platform

# 3. Create a virtual environment
python -m venv venv

# 4. Activate it
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 5. Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Usage

> ⚠️ **Verify before publishing:** the two commands below (`src.main` and `src.analytics.run_all`) are not backed by any file visible in the Project Structure tree above — there's no `src/main.py` or `src/analytics/run_all.py`/`__main__.py` listed. Confirm the actual entry-point filenames and swap them in below. Left as-is rather than guessed, per your own "do not invent commands" rule.

### Running the ETL Pipeline

```bash
python -m src.main
```

### Running Analytics (Ratios, Health Score, Peer Comparison, Radar Charts, Valuation)

```bash
python -m src.analytics.run_all
```

### Running the Dashboard

```bash
streamlit run dashboard/app.py
```

### Running Tests

```bash
pytest tests -v
```

<details>
<summary><b>💡 Example: querying the warehouse directly</b></summary>

```bash
sqlite3 database/nifty100.db
sqlite> SELECT company_id, roe, health_score FROM financial_ratios ORDER BY health_score DESC LIMIT 10;
```

</details>

---

## 📦 Outputs Generated

<div align="center">

| Output File | Description |
|---|---|
| `financial_ratios_calculated.csv` | Full ratio engine output per company/year |
| `company_health_scores.csv` | Weighted 0–100 health score per company |
| `sector_analysis.csv` | Sector-level benchmarking metrics |
| `investment_screener.csv` | Shortlisted companies from screener rules |
| `peer_comparison.csv` | Peer-group benchmarking results |
| `analytics_summary.xlsx` | Consolidated analytics workbook |
| `executive_summary.csv` | High-level summary export |
| `valuation_summary.xlsx` | Valuation engine output workbook |
| `valuation_flags.csv` | Over/undervaluation flags per company |
| `radar_charts/*.png` | 92 individual company radar chart profiles |

</div>

---

## 🧪 Testing

Implemented with **Pytest** across all core ETL modules.

```bash
pytest tests -v
```

```
47 Tests Passed ✅
```

| Test Module | Coverage |
|---|---|
| `test_loader.py` | Excel loading & header detection |
| `test_normalizer.py` | Schema normalization & cleaning |
| `test_validator.py` | 16-rule validation engine |
| `test_database.py` | SQLite load & schema integrity |

---

## 🧹 Code Quality

- 🖤 **Black** — enforced code formatting
- ⚡ **Ruff** — fast linting for style & correctness
- 📝 **Structured Logging** — traceable pipeline execution
- 🛡️ **Exception Handling** — resilient to malformed source data
- 🔤 **Type Hints** — improved readability & IDE support
- ⚙️ **Config-Driven** — no hardcoded paths, thresholds, or filenames

---

## ☁️ Deployment

Deployed on **Streamlit Community Cloud**.

🔗 **Live Demo:** [n100-financial-intelligence-platform](https://n100-financial-intelligence-platform-mkqsnvgduesqxum8y8jjn4.streamlit.app/)

---

## 📈 Performance Highlights

<div align="center">

| Metric | Value |
|---|---|
| Excel Datasets Ingested | 12 |
| Financial Records Processed | 1,184 |
| Companies Covered | 92 |
| Sectors Benchmarked | 10 |
| SQLite Tables | 12 |
| Validation Rules Enforced | 16 |
| Radar Charts Generated | 92 |
| Storage Engine | SQLite Data Warehouse |
| Dashboard Pages | 8 (Fully Interactive — Plotly + Streamlit) |

</div>

---

## 🚧 Roadmap & Future Improvements

### ✅ Completed

- [x] ETL Pipeline
- [x] Validation Engine
- [x] SQLite Database
- [x] Financial Ratio Engine
- [x] Health Score Engine
- [x] Sector Analytics
- [x] Peer Comparison Engine
- [x] Radar Chart Engine
- [x] Valuation Engine
- [x] Investment Screener
- [x] Reporting Engine
- [x] 8-Page Streamlit Dashboard
- [x] Unit Testing
- [x] SQL Schema
- [x] Load Audit Reporting

### 🔮 Next

- [ ] Live NSE Data Feeds
- [ ] Machine Learning Forecasting
- [ ] Portfolio Optimization
- [ ] Authentication & User Roles
- [ ] Cloud Database Migration
- [ ] REST API Integration
- [ ] Docker Deployment
- [ ] CI/CD Pipeline

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. **Fork** the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a **Pull Request**

Please run `pytest tests -v` and ensure `black`/`ruff` checks pass before submitting.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

<div align="center">

### **DS Yashaswi**

**B.Tech CSE (Data Science)**
Python Developer • Data Analyst • Financial Analytics

[![GitHub](https://img.shields.io/badge/GitHub-Yashr4635-181717?style=for-the-badge&logo=github)](https://github.com/Yashr4635)

</div>

---

<div align="center">

⭐ If you find this project useful, consider giving it a star on GitHub! ⭐

</div>
