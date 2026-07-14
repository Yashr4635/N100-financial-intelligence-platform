<div align="center">

# 📈 N100 Financial Intelligence Platform

### Enterprise-Grade Financial Analytics System for NIFTY 100 Companies

**ETL Automation • Data Validation • Financial Ratio Engine • Health Scoring • Sector Analytics • Investment Screening • Interactive Dashboard**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Engine-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Data%20Warehouse-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Visualizations-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![Pytest](https://img.shields.io/badge/Pytest-Tested-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Build](https://img.shields.io/badge/Build-Passing-brightgreen?style=flat-square)](#-testing)
[![Tests](https://img.shields.io/badge/Tests-8%20Passed-success?style=flat-square)](#-testing)
[![Maintenance](https://img.shields.io/badge/Maintained-Yes-blue?style=flat-square)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-ff69b4.svg?style=flat-square)](#-contributing)

[**🚀 Live Demo**](https://n100-financial-intelligence-platform-mkqsnvgduesqxum8y8jjn4.streamlit.app/) · [**📖 Documentation**](#-table-of-contents) · [**🐛 Report Bug**](https://github.com/Yashr4635/N100-financial-intelligence-platform/issues) · [**✨ Request Feature**](https://github.com/Yashr4635/N100-financial-intelligence-platform/issues)

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

The **N100 Financial Intelligence Platform** is an end-to-end financial analytics system built with **Python, SQLite, Pandas, and Streamlit**. It transforms raw, messy Excel exports of NIFTY 100 company financials into a clean, validated, queryable data warehouse — then layers on a full analytics stack: financial ratios, company health scoring, sector benchmarking, an investment screener, and a live interactive dashboard.

It automates:

| Stage | Capability |
|---|---|
| 🔄 | ETL Pipeline |
| 🧪 | Data Validation |
| 📊 | Financial Ratio Calculation |
| 💯 | Company Health Score |
| 🏭 | Sector Analytics |
| 🔎 | Investment Screening |
| 🖥️ | Interactive Dashboard |

---

## 🌟 Key Highlights

<div align="center">

| 📁 12 Datasets | 🏢 92 Companies | 🏭 10 Sectors | 📈 1,000+ Records | ✅ 16 Validation Rules |
|:---:|:---:|:---:|:---:|:---:|
| Excel sources ingested | NIFTY 100 coverage | Fully benchmarked | Loaded & validated | Data quality gates |

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
- ✅ **Investment Screener** — rules-based company shortlisting
- ✅ **Interactive Streamlit Dashboard** — Plotly-powered, multi-page, filterable
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
                │   SQLite Database   │  ← nifty100.db
                └──────────┬─────────┘
                           │
                           ▼
                ┌────────────────────┐
                │   Analytics Engine  │  ← ratios, health score, sectors
                └──────────┬─────────┘
                           │
                           ▼
                ┌────────────────────┐
                │   Streamlit         │
                │   Dashboard         │
                └────────────────────┘
```

---

## 📂 Project Structure

```text
N100-Financial-Intelligence-Platform/
│
├── dashboard/
│   └── app.py                     # Streamlit entry point
│
├── src/
│   ├── etl/                       # Loading, normalization, validation
│   ├── database/                  # SQLite connection & schema logic
│   ├── analytics/                 # Ratio engine, health score, screener
│   ├── dashboard/                 # Dashboard page components
│   └── utils/                     # Shared helpers, config, logging
│
├── database/
│   └── nifty100.db                # Generated SQLite warehouse
│
├── data/
│   ├── raw/                       # Original Excel exports
│   ├── processed/                 # Cleaned intermediate data
│   └── output/                    # Final load-ready datasets
│
├── reports/
│   ├── validation_failures.csv    # Data quality failure log
│   └── load_audit.csv             # ETL load audit trail
│
├── sql/
│   ├── schema.sql                 # Table definitions
│   └── exploratory_queries.sql    # Analyst SQL queries
│
├── tests/
│   ├── test_loader.py
│   ├── test_normalizer.py
│   ├── test_validator.py
│   └── test_database.py
│
├── docs/
│   └── screenshots/
│       ├── overview.png
│       ├── company_analysis.png
│       ├── sector_analysis.png
│       └── investment_screener.png
│
├── requirements.txt
└── README.md
```

| Folder | Purpose |
|---|---|
| `dashboard/` | Streamlit application entry point |
| `src/etl/` | Excel loading, normalization, and validation logic |
| `src/database/` | Database connection, schema creation, and load routines |
| `src/analytics/` | Financial ratio engine, health scoring, sector analytics, screener |
| `src/dashboard/` | Reusable UI components for dashboard pages |
| `src/utils/` | Configuration, logging, and shared utility functions |
| `database/` | Generated SQLite data warehouse |
| `data/` | Raw, processed, and output-stage datasets |
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
| **`src/analytics/`** | Houses the Financial Ratio Engine, Health Score Engine, Sector Analytics, and Investment Screener logic. |
| **`src/utils/`** | Centralizes configuration, path management, and structured logging used across all modules. |
| **`src/dashboard/`** | Provides the page-level components (Overview, Company Analysis, Sector Analysis, Investment Screener) consumed by `dashboard/app.py`. |

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

### 🧮 Financial Ratio Engine

Calculates, per company/year:

- Return on Equity (ROE)
- Profit Margin
- Debt to Equity
- Asset Turnover
- Earnings Per Share (EPS)
- Financial Quality Score

### 💯 Health Score Engine

Generates a **weighted score out of 100** using:

- ROE
- Profit Margin
- Debt
- Asset Turnover
- EPS

### 🏭 Sector Analytics

Benchmarks companies across their sector using:

- Sector Performance
- Average ROE
- Average Health Score
- Debt Analysis

### 🔎 Investment Screener

Shortlists companies using rules such as:

- Health Score ≥ 80
- Financial Quality ≥ 4

---

## 🖥 Dashboard

An interactive, multi-page **Streamlit** dashboard powered by **Plotly** visualizations, KPI cards, and dynamic filters.

| Page | Description |
|---|---|
| 🏠 **Overview** | High-level KPIs across the full NIFTY 100 universe |
| 🏢 **Company Analysis** | Deep-dive financials, ratios, and trends per company |
| 🏭 **Sector Analysis** | Sector-level benchmarking and comparisons |
| 🔎 **Investment Screener** | Filterable, rules-based company shortlisting |

---

## 📸 Screenshots

<table>
  <tr>
    <td align="center" width="50%"><b>🏠 Overview</b><br><img src="docs/screenshots/overview.png" width="420"/></td>
    <td align="center" width="50%"><b>🏢 Company Analysis</b><br><img src="docs/screenshots/company_analysis.png" width="420"/></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>🏭 Sector Analysis</b><br><img src="docs/screenshots/sector_analysis.png" width="420"/></td>
    <td align="center" width="50%"><b>🔎 Investment Screener</b><br><img src="docs/screenshots/investment_screener.png" width="420"/></td>
  </tr>
</table>

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

```bash
# Run the full ETL pipeline (load, normalize, validate, warehouse)
python -m src.main

# Launch the interactive dashboard
streamlit run dashboard/app.py

# Run the full test suite
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

## 🧪 Testing

Implemented with **Pytest** across all core ETL modules.

```bash
pytest tests -v
```

```
8 Tests Passed ✅
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
| Financial Records Processed | 1,000+ |
| Companies Covered | 92 |
| Sectors Benchmarked | 10 |
| Validation Rules Enforced | 16 |
| Storage Engine | SQLite Data Warehouse |
| Dashboard | Fully Interactive (Plotly + Streamlit) |

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
- [x] Investment Screener
- [x] Streamlit Dashboard
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

### **Yashaswi R**

**B.Tech CSE (Data Science)**
Python Developer • Data Analyst • Financial Analytics

[![GitHub](https://img.shields.io/badge/GitHub-Yashr4635-181717?style=for-the-badge&logo=github)](https://github.com/Yashr4635)

</div>

---

<div align="center">

⭐ If you find this project useful, consider giving it a star on GitHub! ⭐

</div>
