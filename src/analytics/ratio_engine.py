import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = "database/nifty100.db"
OUTPUT = "data/output/financial_ratios_calculated.csv"


class RatioEngine:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)

    def run(self):

        print("\n" + "=" * 70)
        print("FINANCIAL RATIO ENGINE")
        print("=" * 70)

        df = pd.read_sql(
            "SELECT * FROM financial_ratios",
            self.conn
        )

        # Convert numeric columns
        numeric_cols = [
            "return_on_equity_pct",
            "net_profit_margin_pct",
            "operating_profit_margin_pct",
            "debt_to_equity",
            "asset_turnover",
            "earnings_per_share",
            "book_value_per_share",
            "free_cash_flow_cr",
            "cash_from_operations_cr",
            "total_debt_cr"
        ]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Derived metric
        df["fcf_to_debt"] = (
            df["free_cash_flow_cr"] /
            df["total_debt_cr"].replace(0, pd.NA)
        )

        # Quality score
        score = 0

        score += (df["return_on_equity_pct"] > 15).astype(int)
        score += (df["net_profit_margin_pct"] > 10).astype(int)
        score += (df["debt_to_equity"] < 1).astype(int)
        score += (df["asset_turnover"] > 1).astype(int)
        score += (df["earnings_per_share"] > 0).astype(int)

        df["financial_quality_score"] = score

        Path("data/output").mkdir(parents=True, exist_ok=True)

        df.to_csv(
            OUTPUT,
            index=False
        )

        print(f"\nSaved {len(df)} records")
        print(OUTPUT)

        self.conn.close()