"""
capital_allocation.py

Sprint 5 – Capital Allocation Analytics for the N100 Financial
Intelligence Platform.

Detects and classifies the capital allocation pattern for each company
over time, identifies historical pattern changes, and writes a CSV with
the pattern history.

This module is a thin coordinator: it imports CashFlowIntelligenceEngine
to reuse its classification logic and focuses on the allocation analytics
output required by Sprint 5.

Inputs
------
- data/output/company_health_scores.csv

Outputs
-------
- data/output/pattern_changes.csv   (already produced by
  CashFlowIntelligenceEngine; this module re-exports + enriches it)
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import pandas as pd

from src.analytics.cashflow_intelligence import CashFlowIntelligenceEngine, _safe_float

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

HEALTH_SCORES_PATH = os.path.join("data", "output", "company_health_scores.csv")
OUTPUT_DIR = os.path.join("data", "output")
PATTERN_CHANGES_PATH = os.path.join(OUTPUT_DIR, "pattern_changes.csv")


class CapitalAllocationAnalytics:
    """
    Standalone Capital Allocation Analytics module.

    Re-uses CashFlowIntelligenceEngine's classification logic and
    enriches the output with transition type labels and severity scores.
    """

    TRANSITION_SEVERITY: dict = {
        "Balanced → Growth Investor": ("Positive", "Increased investment"),
        "Balanced → Distressed": ("Negative", "Deterioration signal"),
        "Growth Investor → Cash Accumulator": ("Positive", "Investment payoff"),
        "Distressed → Balanced": ("Positive", "Recovery signal"),
        "Distressed → Growth Investor": ("Positive", "Strong recovery"),
        "Cash Accumulator → Distressed": ("Negative", "Rapid deterioration"),
        "Dividend Focus → Distressed": ("Negative", "Dividend cut risk"),
        "Debt Reducer → Growth Investor": ("Positive", "Balance sheet leverage for growth"),
    }

    def __init__(
        self,
        health_scores_path: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> None:
        self.health_scores_path = health_scores_path or HEALTH_SCORES_PATH
        self.output_dir = output_dir or OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_path = os.path.join(self.output_dir, "pattern_changes.csv")

    def _load_health_scores(self) -> pd.DataFrame:
        if not os.path.exists(self.health_scores_path):
            logger.warning("Health scores not found at '%s'.", self.health_scores_path)
            return pd.DataFrame()
        try:
            df = pd.read_csv(self.health_scores_path)
            logger.info("Loaded health scores: %d rows.", len(df))
            return df
        except Exception as exc:
            logger.error("Failed to load health scores: %s", exc)
            return pd.DataFrame()

    def _classify_and_track(self, health_df: pd.DataFrame) -> pd.DataFrame:
        """
        Classify each company-year and build the full allocation history,
        then detect changes and enrich with severity labels.
        """
        if health_df.empty:
            return pd.DataFrame()

        engine = CashFlowIntelligenceEngine()

        df = health_df.copy()
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df = df.dropna(subset=["year"]).sort_values(["company_id", "year"])
        df["allocation_pattern"] = df.apply(engine._classify_capital_allocation, axis=1)
        df["prev_pattern"] = df.groupby("company_id")["allocation_pattern"].shift(1)

        changes = df[
            df["prev_pattern"].notna() & (df["allocation_pattern"] != df["prev_pattern"])
        ].copy()

        if changes.empty:
            logger.info("No pattern changes detected.")
            return pd.DataFrame()

        changes["change_description"] = (
            changes["prev_pattern"] + " → " + changes["allocation_pattern"]
        )

        def _severity(desc: str):
            entry = self.TRANSITION_SEVERITY.get(desc, ("Neutral", "Pattern shift"))
            return entry[0]

        def _note(desc: str):
            entry = self.TRANSITION_SEVERITY.get(desc, ("Neutral", "Pattern shift"))
            return entry[1]

        changes["transition_type"] = changes["change_description"].apply(_severity)
        changes["transition_note"] = changes["change_description"].apply(_note)

        keep = [
            "company_id", "year",
            "prev_pattern", "allocation_pattern",
            "change_description", "transition_type", "transition_note",
        ]
        return changes[[c for c in keep if c in changes.columns]].reset_index(drop=True)

    def run(self) -> pd.DataFrame:
        """
        Run the Capital Allocation Analytics pipeline.

        Returns
        -------
        pattern_changes DataFrame.
        """
        print("\n" + "=" * 70)
        print("CAPITAL ALLOCATION ANALYTICS")
        print("=" * 70)

        health_df = self._load_health_scores()
        pattern_df = self._classify_and_track(health_df)

        pattern_df.to_csv(self.output_path, index=False)

        print(f"  Pattern changes detected: {len(pattern_df)}")
        print(f"  Saved: {self.output_path}")
        print("Capital Allocation Analytics complete.\n")

        return pattern_df


if __name__ == "__main__":
    analytics = CapitalAllocationAnalytics()
    analytics.run()
