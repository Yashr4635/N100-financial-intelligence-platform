# 📊 N100 Financial Intelligence Platform

A production-oriented Financial Intelligence Platform that performs ETL (Extract, Transform, Load), data quality validation, SQLite database creation, and financial data processing for NIFTY 100 companies.

---

# 🚀 Project Overview

The N100 Financial Intelligence Platform is designed to build a clean, validated, and queryable financial database from multiple Excel datasets.

The project processes company financial statements, stock prices, market capitalization, cash flow, balance sheet, profit & loss statements, and sector information through an automated ETL pipeline.

---

# ✨ Features

- ✅ Smart Excel Loader
- ✅ Automatic Header Detection
- ✅ Dataset Normalization
- ✅ 16 Data Quality Validation Rules
- ✅ SQLite Database Generation
- ✅ ETL Load Audit Report
- ✅ Validation Failure Report
- ✅ SQL Exploratory Queries
- ✅ Unit Testing with Pytest

---

# 📂 Project Structure

```text
N100-FINANCIAL-INTELLIGENCE-PLATFORM/

├── data/
│   ├── raw/
│   ├── processed/
│   └── output/
│
├── database/
│   └── nifty100.db
│
├── docs/
│
├── reports/
│   ├── validation_failures.csv
│   └── load_audit.csv
│
├── sql/
│   ├── schema.sql
│   └── exploratory_queries.sql
│
├── src/
│   ├── etl/
│   ├── database/
│   ├── analytics/
│   ├── dashboard/
│   └── utils/
│
├── tests/
│
└── README.md
```

---

# ⚙️ ETL Pipeline

```
Excel Files
      │
      ▼
Excel Loader
      │
      ▼
Normalization
      │
      ▼
Validation
      │
      ▼
SQLite Database
      │
      ▼
Reports
```

---

# 📊 Datasets Processed

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

# 🗄 Database

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

# ✅ Data Quality Validation

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

# 📑 Generated Reports

After execution, the pipeline automatically generates:

```
reports/
├── validation_failures.csv
└── load_audit.csv
```

---

# 🧪 Testing

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

# 🛠 Tech Stack

- Python
- Pandas
- NumPy
- SQLite
- SQLAlchemy
- OpenPyXL
- Streamlit
- Plotly
- Pytest
- Git
- GitHub

---

# ▶️ Run the Project

Clone the repository:

```bash
git clone https://github.com/Yashr4635/N100-financial-intelligence-platform.git
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

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the ETL pipeline:

```bash
python -m src.main
```

Run unit tests:

```bash
pytest tests -v
```

---

# 🚧 Roadmap

## Completed

- ETL Pipeline
- Validation Engine
- SQLite Database
- Testing
- SQL Schema
- Load Audit

## Next

- Financial Ratio Engine
- Company Health Score
- Investment Screener
- Streamlit Dashboard
- Analytics Module
- Reporting Dashboard

---

# 👨‍💻 Author

**Yashaswi R**

B.Tech CSE (Data Science)

Data Analytics • AI/ML • Financial Intelligence

GitHub:
https://github.com/Yashr4635