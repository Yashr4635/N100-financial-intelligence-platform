import pandas as pd
from pathlib import Path
from src.utils.logger import logger

class HealthScoreEngine:

    def __init__(self):
        self.df = pd.read_csv(
            "data/output/financial_ratios_calculated.csv"
        )

    def calculate_score(self):

        print("\n" + "=" * 70)
        print("COMPANY HEALTH SCORE ENGINE")
        print("=" * 70)

        score = pd.Series(0, index=self.df.index)

        # ROE (25)
        score += (self.df["return_on_equity_pct"] >= 20) * 25

        # Net Profit Margin (20)
        score += (self.df["net_profit_margin_pct"] >= 10) * 20

        # Debt to Equity (20)
        score += (self.df["debt_to_equity"] <= 1) * 20

        # Asset Turnover (15)
        score += (self.df["asset_turnover"] >= 1) * 15

        # EPS (20)
        score += (self.df["earnings_per_share"] > 0) * 20

        self.df["health_score"] = score

        self.df["rating"] = pd.cut(
            self.df["health_score"],
            bins=[-1, 39, 59, 74, 89, 100],
            labels=[
                "Poor",
                "Average",
                "Good",
                "Very Good",
                "Excellent"
            ]
        )

        Path("data/output").mkdir(parents=True, exist_ok=True)

        self.df.to_csv(
            "data/output/company_health_scores.csv",
            index=False
        )

        print(
            f"Saved {len(self.df)} health scores."
        )

        return self.df