import pandas as pd
from pathlib import Path


class InvestmentScreener:
    """
    Filters fundamentally strong companies based on
    health score and financial quality.
    """

    def __init__(self, health_df: pd.DataFrame):
        self.df = health_df.copy()

    def run(self):

        print("\n" + "=" * 70)
        print("INVESTMENT SCREENER")
        print("=" * 70)

        screen = self.df[
            (self.df["health_score"] >= 80)
            &
            (self.df["financial_quality_score"] >= 4)
        ].copy()

        screen = screen.sort_values(
            by="health_score",
            ascending=False
        )

        Path("data/output").mkdir(parents=True, exist_ok=True)

        output_path = "data/output/investment_screener.csv"

        screen.to_csv(
            output_path,
            index=False
        )

        print(f"Selected {len(screen)} companies")
        print(f"Saved to {output_path}")

        return screen