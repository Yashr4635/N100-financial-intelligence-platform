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

from src.analytics.growth import (
    calculate_5y_revenue_cagr,
    calculate_5y_pat_cagr,
    calculate_5y_eps_cagr,
)

# 5-year CAGR needs Year0..Year5 = 6 yearly records minimum.
# Anything less means growth.py cannot compute a valid CAGR, so we
# skip the calculation entirely rather than guess with partial data.
MIN_YEARS_REQUIRED = 6


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

    def _get_company_series(self, company_df, column):
        """
        Extract a year-ordered, numeric-clean series for one company.

        Non-numeric or missing values are coerced to NaN and dropped
        so a single bad cell can't crash or silently corrupt a CAGR
        calculation. Returns None if the column is absent, or if the
        cleaned series no longer has enough points for a 5Y CAGR
        (dropping NaNs can shrink a 6-row series below the minimum
        even when the raw row count looked sufficient).

        Assumes company_df is already sorted by year (callers sort
        the full dataframe by company_id/year before grouping).
        """
        if column not in company_df.columns:
            return None

        numeric = pd.to_numeric(company_df[column], errors="coerce").dropna()

        if len(numeric) < MIN_YEARS_REQUIRED:
            return None

        return numeric.astype(float).tolist()

    def calculate_growth_metrics(self, df):
        """
        Calculate 5-Year Revenue, PAT, and EPS CAGR per company.

        Growth metrics are computed ONCE per company_id, not once
        per company-year row, because a 5-year CAGR is a single
        trailing value derived from the full history, not a
        per-year quantity. The result is merged back onto the
        per-year ratios table below (see run()) so every yearly row
        for a company carries that company's CAGR figures.
        Reuses growth.py exclusively — no CAGR math here.

        Returns
        -------
        pandas.DataFrame
            One row per company_id with revenue_cagr_5y,
            pat_cagr_5y, eps_cagr_5y.
        """
        records = []

        # Sort so groupby iterates companies in a stable, predictable
        # order and each company's rows are year-ordered going in.
        df = df.sort_values(["company_id", "year"])

        eps_col_present = "earnings_per_share" in df.columns

        for company_id, company_df in df.groupby("company_id"):
            # A 5-year CAGR needs 6 yearly records (Year0..Year5); with
            # fewer than that there is no valid start/end pair to use.
            if len(company_df) < MIN_YEARS_REQUIRED:
                records.append({
                    "company_id": company_id,
                    "revenue_cagr_5y": None,
                    "pat_cagr_5y": None,
                    "eps_cagr_5y": None,
                })
                continue

            revenue_series = self._get_company_series(company_df, "sales")
            pat_series = self._get_company_series(company_df, "net_profit")
            eps_series = (
                self._get_company_series(company_df, "earnings_per_share")
                if eps_col_present else None
            )

            records.append({
                "company_id": company_id,
                "revenue_cagr_5y": (
                    calculate_5y_revenue_cagr(revenue_series)
                    if revenue_series is not None else None
                ),
                "pat_cagr_5y": (
                    calculate_5y_pat_cagr(pat_series)
                    if pat_series is not None else None
                ),
                "eps_cagr_5y": (
                    calculate_5y_eps_cagr(eps_series)
                    if eps_series is not None else None
                ),
            })

        return pd.DataFrame(records)

    def run(self):
        df = self._load_and_merge()
        ratios = self.calculate_all_ratios(df)

        growth_metrics = self.calculate_growth_metrics(df)
        # Merge company-level CAGR values onto the per-year ratios
        # table so every yearly row for a company carries the same
        # trailing 5Y growth figures alongside that year's ratios.
        ratios = ratios.merge(growth_metrics, on="company_id", how="left")

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