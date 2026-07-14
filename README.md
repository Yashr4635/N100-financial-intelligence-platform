# 📈 N100 Financial Intelligence Platform

## Overview

The N100 Financial Intelligence Platform is an end-to-end financial analytics system built using Python, SQLite, Pandas, and Streamlit.

It automates:

- ETL Pipeline
- Data Validation
- Financial Ratio Calculation
- Company Health Score
- Sector Analytics
- Investment Screening
- Interactive Dashboard

---

## Features

- Automated ETL Pipeline
- SQLite Data Warehouse
- Financial Ratio Engine
- Health Score Engine
- Sector Analytics
- Investment Screener
- Interactive Streamlit Dashboard
- Unit Testing
- Error Handling
- Logging
- Config Driven Architecture

---

## Tech Stack

- Python
- Pandas
- SQLite
- Streamlit
- Plotly
- OpenPyXL
- Pytest

---

## Folder Structure

```text
N100-Financial-Intelligence-Platform/
│
├── dashboard/
│   └── app.py
│
├── src/
│   ├── etl/
│   ├── database/
│   ├── analytics/
│   ├── dashboard/
│   └── utils/
│
├── database/
│   └── nifty100.db
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── output/
│
├── reports/
│   ├── validation_failures.csv
│   └── load_audit.csv
│
├── sql/
│   ├── schema.sql
│   └── exploratory_queries.sql
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

---

## ETL Workflow

```
Excel Files
     │
     ▼
Excel Loader
     │
     ▼
Normalizer
     │
     ▼
Validator
     │
     ▼
SQLite Database
     │
     ▼
Analytics Engine
     │
     ▼
Dashboard
```

---

## Datasets Processed

- Companies
- Balance Sheet
- Cash Flow
- Profit & Loss
- Financial Ratios
- Market Capitalization
- Stock Prices
- Sectors
- Peer Groups
- Analysis
- Documents
- Pros & Cons

---

## Database

SQLite database:

```
database/nifty100.db
```

Main tables include:

- companies
- balancesheet
- cashflow
- profitandloss
- financial_ratios
- market_cap
- stock_prices
- sectors
- peer_groups
- analysis
- documents
- prosandcons

---

## Data Quality Validation

Current validation checks include:

- Empty dataset detection
- Duplicate rows
- Duplicate columns
- Blank column names
- Missing values
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
- Duplicate Primary IDs

---

## Analytics Modules

### Financial Ratio Engine

Calculates:

- ROE
- Profit Margin
- Debt to Equity
- Asset Turnover
- EPS
- Financial Quality Score

---

### Health Score Engine

Generates a score out of 100 using:

- ROE
- Profit Margin
- Debt
- Asset Turnover
- EPS

---

### Sector Analytics

Provides:

- Sector Performance
- Average ROE
- Average Health Score
- Debt Analysis

---

### Investment Screener

Filters companies using:

- Health Score ≥ 80
- Financial Quality ≥ 4

---

## Dashboard

Pages:

- Overview
- Company Analysis
- Sector Analysis
- Investment Screener

<table>
  <tr>
    <td><b>Overview</b><br><img src="docs/screenshots/overview.png" width="400"/></td>
    <td><b>Company Analysis</b><br><img src="docs/screenshots/company_analysis.png" width="400"/></td>
  </tr>
  <tr>
    <td><b>Sector Analysis</b><br><img src="docs/screenshots/sector_analysis.png" width="400"/></td>
    <td><b>Investment Screener</b><br><img src="docs/screenshots/investment_screener.png" width="400"/></td>
  </tr>
</table>

---

## Generated Reports

After execution, the pipeline automatically generates:

```
reports/
├── validation_failures.csv
└── load_audit.csv
```

---

## Testing

Implemented using **Pytest**.

Current status:

```
8 Tests Passed
```

Test modules:

- test_loader.py
- test_normalizer.py
- test_validator.py
- test_database.py

Run tests:

```bash
pytest tests -v
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Yashr4635/N100-financial-intelligence-platform.git
```

Move into the project folder:

```bash
cd N100-financial-intelligence-platform
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

macOS/Linux

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Run

Run the ETL pipeline:

```bash
python -m src.main
```

Run the dashboard:

```bash
streamlit run dashboard/app.py
```

Run unit tests:

```bash
pytest tests -v
```

---

## Roadmap

### Completed

- ETL Pipeline
- Validation Engine
- SQLite Database
- Financial Ratio Engine
- Health Score Engine
- Sector Analytics
- Investment Screener
- Streamlit Dashboard
- Testing
- SQL Schema
- Load Audit

### Next

- Live NSE Data
- Machine Learning Forecasting
- Portfolio Optimization
- API Integration
- Docker Deployment

---

## Author

**Yashaswi R**

B.Tech CSE (Data Science)

Data Analytics • AI/ML • Financial Intelligence

GitHub: [https://github.com/Yashr4635](https://github.com/Yashr4635)