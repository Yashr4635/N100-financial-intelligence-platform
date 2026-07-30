"""
peer_comparison_engine.py

Peer Comparison Engine for the N100 Financial Intelligence Platform.

Consumes the DataFrame produced after RatioEngine and HealthScoreEngine
(joined with sector information), groups companies by sector, computes
sector-relative percentile rankings for a defined set of financial
metrics, flags sector leaders per metric, derives an overall_peer_rank,
persists the result to CSV, and returns the enriched DataFrame.

Dependencies: pandas only.
"""

from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


class PeerComparisonEngine:
    """
    Computes sector-relative peer comparison metrics for companies.

    Expected input
    ---------------
    A pandas DataFrame with a sector column (accepts 'sector' or a known
    alias such as 'broad_sector' — see SECTOR_COL_ALIASES) and, ideally,
    a company identifier column (e.g. 'company', 'company_id', 'ticker').

    Each output metric (e.g. 'roe') is resolved against a list of
    candidate source column names (see METRIC_CONFIG) so the engine works
    whether the upstream data calls it 'roe' or 'return_on_equity_pct'.
    Metrics with no matching source column are skipped gracefully.

    Output
    ------
    The same DataFrame enriched with:
      - '<metric>_percentile'       sector-relative percentile (0-100, higher = better)
      - '<metric>_sector_leader'    boolean flag for the best-in-sector company
      - 'overall_peer_score'        mean of all available percentile columns
      - 'overall_peer_rank'         sector-relative rank derived from overall_peer_score

    The result is also written to `data/output/peer_comparison.csv` by default.
    """

    # canonical metric name -> config. 'candidates' lists possible source
    # column names in priority order; the first one found in the input
    # DataFrame is used. 'percentile_col' is always the clean output name.
    METRIC_CONFIG: Dict[str, Dict[str, object]] = {
        "roe": {
            "candidates": ["roe", "return_on_equity_pct", "return_on_equity"],
            "percentile_col": "roe_percentile",
            "higher_is_better": True,
        },
        "roa": {
            "candidates": ["roa", "return_on_assets_pct", "return_on_assets"],
            "percentile_col": "roa_percentile",
            "higher_is_better": True,
        },
        "net_profit_margin": {
            "candidates": ["net_profit_margin", "net_profit_margin_pct"],
            "percentile_col": "net_margin_percentile",
            "higher_is_better": True,
        },
        "operating_margin": {
            "candidates": ["operating_margin", "operating_profit_margin_pct", "operating_margin_pct"],
            "percentile_col": "operating_margin_percentile",
            "higher_is_better": True,
        },
        "asset_turnover": {
            "candidates": ["asset_turnover"],
            "percentile_col": "asset_turnover_percentile",
            "higher_is_better": True,
        },
        "interest_coverage": {
            "candidates": ["interest_coverage"],
            "percentile_col": "interest_coverage_percentile",
            "higher_is_better": True,
        },
        "debt_to_equity": {
            "candidates": ["debt_to_equity"],
            "percentile_col": "debt_to_equity_percentile",
            "higher_is_better": False,
        },
        "revenue_growth": {
            "candidates": ["revenue_growth", "revenue_growth_pct"],
            "percentile_col": "revenue_growth_percentile",
            "higher_is_better": True,
        },
        "eps_growth": {
            "candidates": ["eps_growth", "eps_growth_pct"],
            "percentile_col": "eps_growth_percentile",
            "higher_is_better": True,
        },
        "health_score": {
            "candidates": ["health_score"],
            "percentile_col": "health_score_percentile",
            "higher_is_better": True,
        },
    }

    SECTOR_COL = "sector"
    # Known alternative names for the sector column seen across upstream
    # modules (e.g. SectorAnalysis uses 'broad_sector').
    SECTOR_COL_ALIASES = ["sector", "broad_sector", "Sector", "Broad_Sector", "sector_name"]
    DEFAULT_OUTPUT_PATH = os.path.join("data", "output", "peer_comparison.csv")

    def __init__(self, df: pd.DataFrame, output_path: Optional[str] = None):
        if df is None or df.empty:
            raise ValueError("Input DataFrame is empty or None.")

        df = df.copy()

        # Normalize the sector column name if it exists under a known alias.
        if self.SECTOR_COL not in df.columns:
            for alias in self.SECTOR_COL_ALIASES:
                if alias in df.columns:
                    df = df.rename(columns={alias: self.SECTOR_COL})
                    logger.info(
                        "Using '%s' as the sector column (renamed to '%s').",
                        alias, self.SECTOR_COL,
                    )
                    break

        if self.SECTOR_COL not in df.columns:
            raise ValueError(
                f"Input DataFrame must contain a '{self.SECTOR_COL}' column "
                f"(also checked aliases: {self.SECTOR_COL_ALIASES}). "
                f"Available columns: {list(df.columns)}"
            )

        self.df: pd.DataFrame = df
        self.output_path: str = output_path or self.DEFAULT_OUTPUT_PATH

        # Resolve each canonical metric to an actual source column, if any
        # candidate is present in the input DataFrame.
        self._metric_source: Dict[str, str] = {}
        missing_metrics: List[str] = []

        for metric, config in self.METRIC_CONFIG.items():
            source_col = self._resolve_source_column(df, config["candidates"])  # type: ignore[arg-type]
            if source_col is not None:
                self._metric_source[metric] = source_col
            else:
                missing_metrics.append(metric)

        self.available_metrics: List[str] = list(self._metric_source.keys())
        self.missing_metrics: List[str] = missing_metrics

        if self.missing_metrics:
            logger.warning(
                "Skipping metrics with no matching source column in input DataFrame: %s",
                ", ".join(self.missing_metrics),
            )
        if not self.available_metrics:
            logger.warning("No recognized metric columns found in input DataFrame.")
        else:
            logger.info(
                "Resolved metric source columns: %s",
                {m: self._metric_source[m] for m in self.available_metrics},
            )

    @staticmethod
    def _resolve_source_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
        """Return the first candidate column name present in df, else None."""
        for candidate in candidates:
            if candidate in df.columns:
                return candidate
        return None

    # ------------------------------------------------------------------ #
    # Core computation steps
    # ------------------------------------------------------------------ #

    def _compute_percentiles(self) -> None:
        """
        Compute sector-relative percentile ranks for each available metric.

        Percentiles are on a 0-100 scale where 100 = best within the sector,
        accounting for reversed metrics (e.g. lower Debt/Equity is better).
        Missing/non-numeric values are coerced to NaN and receive a NaN
        percentile rather than being dropped from the DataFrame.
        """
        for metric in self.available_metrics:
            config = self.METRIC_CONFIG[metric]
            source_col = self._metric_source[metric]
            percentile_col = str(config["percentile_col"])
            higher_is_better = bool(config["higher_is_better"])

            # Coerce to numeric; invalid entries become NaN and are handled safely.
            self.df[source_col] = pd.to_numeric(self.df[source_col], errors="coerce")

            def _rank_within_sector(group: pd.Series) -> pd.Series:
                valid = group.dropna()
                if valid.empty:
                    return pd.Series(index=group.index, dtype=float)
                ranks = valid.rank(pct=True, ascending=higher_is_better) * 100.0
                return ranks.reindex(group.index)

            percentiles = (
                self.df.groupby(self.SECTOR_COL, group_keys=False)[source_col]
                .apply(_rank_within_sector)
            )
            self.df[percentile_col] = percentiles.round(2)

    def _identify_sector_leaders(self) -> None:
        """
        Flag the sector leader (best-in-sector) for every available metric
        via a boolean column '<metric>_sector_leader'. Ties are all flagged.
        """
        for metric in self.available_metrics:
            percentile_col = str(self.METRIC_CONFIG[metric]["percentile_col"])
            leader_col = f"{metric}_sector_leader"

            sector_max = self.df.groupby(self.SECTOR_COL)[percentile_col].transform("max")
            self.df[leader_col] = (
                self.df[percentile_col].notna()
                & sector_max.notna()
                & (self.df[percentile_col] == sector_max)
            )

    def _compute_overall_rank(self) -> None:
        """
        Derive 'overall_peer_score' (row-wise mean of available percentile
        columns, NaNs skipped) and 'overall_peer_rank' (sector-relative rank
        of that score, 1 = best). Companies with no valid percentiles at all
        get NaN score/rank.
        """
        percentile_cols = [
            str(self.METRIC_CONFIG[m]["percentile_col"]) for m in self.available_metrics
        ]

        if not percentile_cols:
            self.df["overall_peer_score"] = pd.NA
            self.df["overall_peer_rank"] = pd.NA
            return

        self.df["overall_peer_score"] = (
            self.df[percentile_cols].mean(axis=1, skipna=True).round(2)
        )

        self.df["overall_peer_rank"] = (
            self.df.groupby(self.SECTOR_COL)["overall_peer_score"]
            .rank(method="min", ascending=False)
        )
        self.df["overall_peer_rank"] = self.df["overall_peer_rank"].astype("Int64")

    def _save_output(self) -> None:
        output_dir = os.path.dirname(self.output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        self.df.to_csv(self.output_path, index=False)
        logger.info("Saved peer comparison output to '%s'.", self.output_path)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def run(self) -> pd.DataFrame:
        """
        Executes the full peer comparison pipeline:
          1. Compute sector-relative percentiles for each available metric.
          2. Flag sector leaders per metric.
          3. Compute overall_peer_score / overall_peer_rank.
          4. Persist to CSV.
        Returns the enriched DataFrame.
        """
        logger.info(
            "Starting peer comparison for %d companies across %d sectors.",
            len(self.df),
            self.df[self.SECTOR_COL].nunique(dropna=True),
        )

        self._compute_percentiles()
        self._identify_sector_leaders()
        self._compute_overall_rank()
        self._save_output()

        logger.info("Peer comparison complete.")
        return self.df


if __name__ == "__main__":
    # Manual smoke test / usage example, using real-world-style column names
    # (as returned by HealthScoreEngine) to mirror production data.
    sample_data = pd.DataFrame({
        "company_id": [1, 2, 3, 4, 5],
        "broad_sector": ["Tech", "Tech", "Tech", "Finance", "Finance"],
        "return_on_equity_pct": [15.0, 22.5, None, 9.0, 11.0],
        "net_profit_margin_pct": [12.0, 18.0, 9.0, 20.0, 15.0],
        "operating_profit_margin_pct": [14.0, 19.0, 10.0, 21.0, 16.0],
        "asset_turnover": [1.2, 0.9, 1.0, 0.5, 0.6],
        "interest_coverage": [5.0, 8.0, 4.0, 3.0, 2.5],
        "debt_to_equity": [0.5, 0.3, 0.8, 1.2, 0.9],
        "health_score": [80, 90, 75, 70, 65],
    })

    engine = PeerComparisonEngine(sample_data, output_path="data/output/peer_comparison.csv")
    result = engine.run()
    print(result.to_string())