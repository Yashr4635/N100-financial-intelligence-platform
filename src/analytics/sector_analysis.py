import sqlite3
import pandas as pd
from pathlib import Path


class SectorAnalysis:

    def __init__(self):
        self.conn = sqlite3.connect("database/nifty100.db")

    def run(self):

        print("\n" + "=" * 70)
        print("SECTOR ANALYTICS")
        print("=" * 70)

        health = pd.read_csv(
            "data/output/company_health_scores.csv"
        )

        sectors = pd.read_sql(
            "SELECT * FROM sectors",
            self.conn
        )

        df = health.merge(
            sectors,
            on="company_id",
            how="left"
        )

        summary = (
            df.groupby("broad_sector")
            .agg(
                companies=("company_id", "nunique"),
                avg_health_score=("health_score", "mean"),
                avg_roe=("return_on_equity_pct", "mean"),
                avg_profit_margin=("net_profit_margin_pct", "mean"),
                avg_debt_to_equity=("debt_to_equity", "mean")
            )
            .reset_index()
        )

        summary = summary.round(2)

        Path("data/output").mkdir(
            parents=True,
            exist_ok=True
        )

        summary.to_csv(
            "data/output/sector_analysis.csv",
            index=False
        )

        print(summary)
        print("\nSector analysis saved.")

        self.conn.close()