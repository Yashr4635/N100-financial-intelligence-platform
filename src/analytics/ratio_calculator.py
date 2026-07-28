import os
import sqlite3
import pandas as pd

from src.utils.config import DATABASE_PATH

from src.analytics.profitability import (
    calculate_net_profit_margin,
    calculate_operating_profit_margin,
    calculate_roe,
    calculate_roce,
)

from src.analytics.leverage import (
    calculate_debt_to_equity,
    calculate_interest_coverage,
    calculate_asset_turnover,
)


class RatioCalculator:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)

    def _load_and_merge(self):
        pnl = pd.read_sql("SELECT * FROM profitandloss", self.conn)
        bs = pd.read_sql("SELECT * FROM balancesheet", self.conn)
        cf = pd.read_sql("SELECT * FROM cashflow", self.conn)

        # BAND-AID: this hides an ETL bug, it doesn't fix it.
        # keep='first' means you are silently choosing an arbitrary
        # duplicate row with no guarantee it's the correct one.
        for name, table in (("pnl", pnl), ("bs", bs), ("cf", cf)):
            before = len(table)
            table.drop_duplicates(subset=["company_id", "year"], inplace=True)
            after = len(table)
            if before != after:
                print(f"[WARN] {name}: dropped {before - after} duplicate rows")

        df = pnl.merge(bs, on=["company_id", "year"], suffixes=("_pnl", "_bs"))
        df = df.merge(cf, on=["company_id", "year"])

        expected = df[["company_id", "year"]].drop_duplicates().shape[0]
        if len(df) != expected:
            raise ValueError("Duplicate company/year rows exist after merge.")

        return df

    def calculate_all_ratios(self, df):
        ratios = pd.DataFrame()
        ratios["company_id"] = df["company_id"]
        ratios["year"] = df["year"]

        ratios["net_profit_margin_pct"] = df.apply(
            lambda row: calculate_net_profit_margin(row["net_profit"], row["sales"]),
            axis=1,
        )

        ratios["operating_profit_margin_pct"] = df.apply(
            lambda row: calculate_operating_profit_margin(row["operating_profit"], row["sales"]),
            axis=1,
        )

        ratios["return_on_equity_pct"] = df.apply(
            lambda row: calculate_roe(row["net_profit"], row["equity_capital"], row["reserves"]),
            axis=1,
        )

        ratios["return_on_capital_employed_pct"] = df.apply(
            lambda row: calculate_roce(
                row["operating_profit"], row["equity_capital"], row["reserves"], row["borrowings"]
            ),
            axis=1,
        )

        ratios["debt_to_equity"] = df.apply(
            lambda row: calculate_debt_to_equity(
                row["borrowings"], row["equity_capital"], row["reserves"]
            ),
            axis=1,
        )

        ratios["interest_coverage"] = df.apply(
            lambda row: calculate_interest_coverage(
                row["operating_profit"], row["other_income"], row["interest"]
            ),
            axis=1,
        )

        ratios["asset_turnover"] = df.apply(
            lambda row: calculate_asset_turnover(row["sales"], row["total_assets"]),
            axis=1,
        )

        return ratios

    def run(self):
        df = self._load_and_merge()
        ratios = self.calculate_all_ratios(df)  # <-- this call was missing

        ratios.to_sql(
            "financial_ratios",
            self.conn,
            if_exists="replace",
            index=False,
        )

        print("financial_ratios table updated.")
        print("\nCalculated Ratios\n")
        print(ratios.head())

        return ratios

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    calc = RatioCalculator()
    try:
        calc.run()
    finally:
        calc.close()