CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY,
    company_name TEXT,
    sector TEXT,
    industry TEXT
);

CREATE TABLE balancesheet (
    company_id INTEGER,
    year INTEGER,
    total_assets REAL,
    total_liabilities REAL
);