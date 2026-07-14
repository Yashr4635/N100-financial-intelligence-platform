import sqlite3
import pandas as pd
from pathlib import Path
from src.utils.logger import logger
from src.utils.config import DATABASE_PATH


class SectorAnalysis:

    def __init__(self):
        try:
            self.conn = sqlite3.connect(DATABASE_PATH)
        except sqlite3.Error as e:
            raise RuntimeError(f"Database connection failed: {e}")

    def run(self):

        print("\n" + "=" * 70)
        print("SECTOR ANALYTICS")
        print("=" * 70)

        try:
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

        except Exception as e:
            raise RuntimeError(f"Sector analysis failed: {e}")

        finally:
            self.conn.close()

        return summary