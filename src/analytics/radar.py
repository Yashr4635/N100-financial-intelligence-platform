"""
radar.py

Radar Chart Engine for the N100 Financial Intelligence Platform.

Reads the Peer Comparison Engine output and generates one normalized
(0-100) radar/spider chart per company across a defined set of financial
metrics. Companies with fewer than three available metrics are skipped.

Charting is done with matplotlib only. pandas is used solely for reading
and manipulating the tabular input data (consistent with the rest of the
platform's analytics engines).
"""

from __future__ import annotations

import logging
import os
import re
from typing import Dict, List, Optional

import matplotlib
matplotlib.use("Agg")  # headless-safe backend, no display required
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


class RadarChartEngine:
    """
    Generates one radar (spider) chart per company from the Peer
    Comparison Engine output, plotting up to eight financial metrics
    normalized to a common 0-100 scale.

    Input
    -----
    data/output/peer_comparison.csv

    Output
    ------
    One PNG per eligible company (>= MIN_METRICS_REQUIRED metrics
    available) at:
        reports/radar_charts/<company_name>_radar.png

    Notes
    -----
    Each canonical metric (e.g. 'ROE') is resolved against a list of
    candidate source column names, so the engine tolerates upstream
    naming differences (e.g. 'roe' vs 'return_on_equity_pct'). Metrics
    with no matching column anywhere in the dataset are skipped globally;
    metrics missing for a specific company are skipped for that company
    only.
    """

    INPUT_PATH = os.path.join("data", "output", "peer_comparison.csv")
    OUTPUT_DIR = os.path.join("reports", "radar_charts")
    MIN_METRICS_REQUIRED = 3

    # canonical metric label -> {candidate source columns, higher_is_better}
    METRIC_CONFIG: Dict[str, Dict[str, object]] = {
        "ROE": {
            "candidates": ["roe", "return_on_equity_pct", "return_on_equity", "roe_percentile"],
            "higher_is_better": True,
        },
        "ROCE": {
            "candidates": [
                "roce", "return_on_capital_employed_pct", "return_on_capital_employed", "roce_pct",
            ],
            "higher_is_better": True,
        },
        "Net Profit Margin": {
            "candidates": ["net_profit_margin", "net_profit_margin_pct", "net_margin_percentile"],
            "higher_is_better": True,
        },
        "Debt to Equity": {
            "candidates": ["debt_to_equity"],
            "higher_is_better": False,
        },
        "FCF Score": {
            "candidates": ["fcf_score", "fcf_to_debt", "free_cash_flow_score"],
            "higher_is_better": True,
        },
        "PAT CAGR 5Y": {
            "candidates": ["pat_cagr_5y", "pat_cagr_5yr", "profit_cagr_5y", "pat_cagr"],
            "higher_is_better": True,
        },
        "Revenue CAGR 5Y": {
            "candidates": ["revenue_cagr_5y", "revenue_cagr_5yr", "revenue_growth_5y", "revenue_cagr"],
            "higher_is_better": True,
        },
        "Composite Quality Score": {
            "candidates": [
                "composite_quality_score", "financial_quality_score", "quality_score", "health_score",
            ],
            "higher_is_better": True,
        },
    }

    # Candidate columns for the company label used in chart titles/filenames.
    COMPANY_NAME_CANDIDATES = ["company_name", "company", "name", "ticker", "symbol", "company_id"]
    # Candidate columns identifying the reporting period, used to pick the
    # most recent row per company when the input has one row per company
    # per year (as produced by RatioEngine / HealthScoreEngine).
    YEAR_COL_CANDIDATES = ["year", "fiscal_year", "report_year"]

    def __init__(self, input_path: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Load the Peer Comparison Engine output, collapse it to one row per
        company (keeping the most recent year available, if a year column
        is present), resolve which metrics and company-identifier column
        are available, and pre-compute normalized (0-100) metric values
        for every company.

        Parameters
        ----------
        input_path : optional override for the peer comparison CSV path.
        output_dir : optional override for the radar chart output directory.
        """
        self.input_path = input_path or self.INPUT_PATH
        self.output_dir = output_dir or self.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        raw_df: pd.DataFrame = self._load_csv(self.input_path)

        self.company_col: Optional[str] = self._resolve_column(raw_df, self.COMPANY_NAME_CANDIDATES)
        if not self.company_col and not raw_df.empty:
            logger.warning("No company identifier column found; falling back to row index as label.")

        self.df: pd.DataFrame = self._collapse_to_one_row_per_company(raw_df)

        # Resolve each canonical metric to an actual source column, if any
        # candidate is present in the input DataFrame.
        self._metric_source: Dict[str, str] = {}
        for metric, config in self.METRIC_CONFIG.items():
            col = self._resolve_column(self.df, config["candidates"])  # type: ignore[arg-type]
            if col:
                self._metric_source[metric] = col

        self.available_metrics: List[str] = list(self._metric_source.keys())
        missing = [m for m in self.METRIC_CONFIG if m not in self._metric_source]
        if missing:
            logger.warning(
                "Metrics with no matching source column (skipped for all companies): %s",
                ", ".join(missing),
            )

        self._normalized_df: Optional[pd.DataFrame] = None
        if not self.df.empty and self.available_metrics:
            self._normalized_df = self._normalize_metrics()

    def _collapse_to_one_row_per_company(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reduce a DataFrame that may contain multiple rows per company
        (e.g. one row per fiscal year) down to a single row per company.

        If a year-like column is present, the row with the latest year is
        kept for each company. Otherwise the last occurrence per company
        is kept, and a warning is logged since recency cannot be verified.
        If no company identifier column is found at all, the DataFrame is
        returned unchanged (each row is treated as its own 'company').
        """
        if df.empty or not self.company_col:
            return df

        if not df[self.company_col].duplicated().any():
            return df

        year_col = self._resolve_column(df, self.YEAR_COL_CANDIDATES)

        if year_col:
            df_sorted = df.sort_values(by=[self.company_col, year_col])
            deduped = df_sorted.drop_duplicates(subset=self.company_col, keep="last")
            logger.info(
                "Collapsed %d rows to %d companies using latest '%s' per '%s'.",
                len(df), len(deduped), year_col, self.company_col,
            )
        else:
            deduped = df.drop_duplicates(subset=self.company_col, keep="last")
            logger.warning(
                "Multiple rows per company found but no year column to determine recency; "
                "keeping the last row per '%s' (%d rows -> %d companies).",
                self.company_col, len(df), len(deduped),
            )

        return deduped.reset_index(drop=True)

    # ------------------------------------------------------------------ #
    # Loading & helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _load_csv(path: str) -> pd.DataFrame:
        """Load the peer comparison CSV safely, returning an empty DataFrame on failure."""
        if not os.path.exists(path):
            logger.warning(
                "Peer comparison input not found at '%s'. No radar charts will be generated.", path
            )
            return pd.DataFrame()
        try:
            df = pd.read_csv(path)
            logger.info(
                "Loaded peer comparison data: %d rows, %d columns from '%s'.",
                len(df), len(df.columns), path,
            )
            return df
        except Exception as exc:  # noqa: BLE001 - defensive load, must not crash the pipeline
            logger.warning("Failed to read peer comparison data from '%s': %s.", path, exc)
            return pd.DataFrame()

    @staticmethod
    def _resolve_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
        """Return the first candidate column name present in df, else None."""
        for candidate in candidates:
            if candidate in df.columns:
                return candidate
        return None

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Make a string safe to use as a filename component."""
        name = str(name).strip()
        name = re.sub(r"[^\w\-]+", "_", name)
        name = re.sub(r"_+", "_", name).strip("_")
        return name or "unknown_company"

    # ------------------------------------------------------------------ #
    # Normalization
    # ------------------------------------------------------------------ #

    def _normalize_metrics(self) -> pd.DataFrame:
        """
        Min-max normalize each available metric to a 0-100 scale across
        all companies in the dataset.

        Metrics where a lower raw value is better (e.g. Debt to Equity)
        are inverted after scaling so that 100 always means 'best' on the
        chart. Missing/non-numeric values remain NaN after normalization
        and are excluded per-company at chart-generation time.
        """
        normalized = pd.DataFrame(index=self.df.index)

        for metric in self.available_metrics:
            source_col = self._metric_source[metric]
            higher_is_better = bool(self.METRIC_CONFIG[metric]["higher_is_better"])

            values = pd.to_numeric(self.df[source_col], errors="coerce")
            valid = values.dropna()

            if valid.empty:
                normalized[metric] = np.nan
                continue

            min_val, max_val = valid.min(), valid.max()

            if min_val == max_val:
                # No spread across companies: treat every valid value as
                # equal (mid-scale) rather than dividing by zero.
                scaled = values.where(values.isna(), 50.0)
            else:
                scaled = (values - min_val) / (max_val - min_val) * 100.0
                if not higher_is_better:
                    scaled = 100.0 - scaled

            normalized[metric] = scaled.round(2)

        return normalized

    # ------------------------------------------------------------------ #
    # Chart generation
    # ------------------------------------------------------------------ #

    def _company_label(self, row_idx) -> str:
        """Return a human-readable label for the company at the given row index."""
        if self.company_col:
            return str(self.df.loc[row_idx, self.company_col])
        return f"company_{row_idx}"

    def generate_chart(self, row_idx) -> Optional[str]:
        """
        Generate a single radar chart for one company, identified by its
        row index in the loaded DataFrame.

        Parameters
        ----------
        row_idx : the DataFrame index label of the company's row.

        Returns
        -------
        The output PNG file path, or None if the company was skipped
        (fewer than MIN_METRICS_REQUIRED metrics available, or no data
        loaded at all).
        """
        if self._normalized_df is None or row_idx not in self._normalized_df.index:
            logger.warning("No normalized data available for row %s; skipping.", row_idx)
            return None

        company_label = self._company_label(row_idx)
        company_values = self._normalized_df.loc[row_idx]

        available = company_values.dropna()
        if len(available) < self.MIN_METRICS_REQUIRED:
            logger.info(
                "Skipping '%s': only %d/%d metric(s) available (minimum %d required).",
                company_label, len(available), len(self.available_metrics), self.MIN_METRICS_REQUIRED,
            )
            return None

        labels = list(available.index)
        values = list(available.values)

        # Close the polygon loop for the radar plot.
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        plot_values = values + values[:1]
        plot_angles = angles + angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(plot_angles, plot_values, linewidth=2, color="#1f77b4")
        ax.fill(plot_angles, plot_values, color="#1f77b4", alpha=0.25)

        ax.set_xticks(angles)
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=7)
        ax.set_title(f"{company_label}\nPeer-Relative Financial Profile", fontsize=11, pad=20)

        fig.tight_layout()

        filename = f"{self._sanitize_filename(company_label)}_radar.png"
        output_path = os.path.join(self.output_dir, filename)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        logger.info("Saved radar chart for '%s' to '%s'.", company_label, output_path)
        return output_path

    def generate_all(self) -> List[str]:
        """
        Generate radar charts for every company in the dataset that has
        at least MIN_METRICS_REQUIRED available metrics.

        Returns
        -------
        The list of output file paths actually created.
        """
        if self.df.empty:
            logger.warning("No input data loaded; no radar charts will be generated.")
            return []

        if not self.available_metrics:
            logger.warning("No recognized metric columns found; no radar charts will be generated.")
            return []

        generated: List[str] = []
        skipped = 0

        for row_idx in self.df.index:
            path = self.generate_chart(row_idx)
            if path:
                generated.append(path)
            else:
                skipped += 1

        logger.info(
            "Radar chart generation complete: %d chart(s) generated, %d compan%s skipped.",
            len(generated), skipped, "y" if skipped == 1 else "ies",
        )
        return generated

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def run(self) -> bool:
        """
        Execute the full radar chart pipeline: load data, normalize
        metrics, and generate one chart per eligible company.

        Returns
        -------
        True on successful completion (even if zero charts were generated
        due to missing or insufficient data).
        """
        print("\n" + "=" * 70)
        print("RADAR CHART ENGINE")
        print("=" * 70)

        generated = self.generate_all()

        print(f"Generated {len(generated)} radar chart(s) in '{self.output_dir}'.")
        print("\nRadar chart generation complete.")

        return True


if __name__ == "__main__":
    # Manual smoke test / usage example using sample data mirroring the
    # real Peer Comparison Engine output.
    os.makedirs("data/output", exist_ok=True)

    sample_peer = pd.DataFrame(
        {
            "company_id": [1, 2, 3, 4],
            "company_name": ["Alpha Corp", "Beta Ltd", "Gamma Inc", "Delta LLC"],
            "sector": ["Tech", "Tech", "Finance", "Finance"],
            "return_on_equity_pct": [15.0, 22.5, 9.0, 11.0],
            "net_profit_margin_pct": [12.0, 18.0, 20.0, None],
            "debt_to_equity": [0.5, 0.3, 1.2, 0.9],
            "financial_quality_score": [70, 85, 60, 55],
        }
    )
    sample_peer.to_csv("data/output/peer_comparison.csv", index=False)

    engine = RadarChartEngine()
    engine.run()