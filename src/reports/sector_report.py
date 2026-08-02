"""
sector_report.py

Sprint 5 – Sector Report Generator for the N100 Financial Intelligence Platform.

Generates one PDF per broad sector containing:
  - Sector KPI summary (average ROE, Margin, D/E, Health Score)
  - Company rankings table within the sector
  - Median metric bar charts
  - Health score distribution chart

Inputs
------
- data/output/company_health_scores.csv
- data/output/peer_comparison.csv
- data/output/sector_analysis.csv

Outputs
-------
- reports/sector/<sector_name>_report.pdf  (one per sector)
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]
HEALTH_SCORES_PATH = str(PROJECT_ROOT / "data" / "output" / "company_health_scores.csv")
PEER_COMPARISON_PATH = str(PROJECT_ROOT / "data" / "output" / "peer_comparison.csv")
SECTOR_ANALYSIS_PATH = str(PROJECT_ROOT / "data" / "output" / "sector_analysis.csv")
OUTPUT_DIR = str(PROJECT_ROOT / "reports" / "sector")

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
PRIMARY = "#1F4E79"
ACCENT = "#2E86AB"
POSITIVE = "#27AE60"
NEUTRAL = "#7F8C8D"
BG = "#F8F9FA"


def _load_csv(path: str, label: str) -> pd.DataFrame:
    if not os.path.exists(path):
        logger.warning("%s not found at '%s'.", label, path)
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception as exc:
        logger.error("Failed to load %s: %s", label, exc)
        return pd.DataFrame()


def _safe_float(val) -> Optional[float]:
    if val is None:
        return None
    try:
        f = float(val)
        return None if pd.isna(f) else f
    except (ValueError, TypeError):
        return None


def _fmt(val, decimals: int = 1, suffix: str = "") -> str:
    v = _safe_float(val)
    if v is None:
        return "N/A"
    return f"{round(v, decimals)}{suffix}"


class SectorReportGenerator:
    """
    Generates one PDF sector report per broad sector, summarising
    KPIs, company rankings, median charts, and health score distribution.
    """

    def __init__(
        self,
        health_scores_path: Optional[str] = None,
        peer_comparison_path: Optional[str] = None,
        sector_analysis_path: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> None:
        self.health_scores_path = health_scores_path or HEALTH_SCORES_PATH
        self.peer_comparison_path = peer_comparison_path or PEER_COMPARISON_PATH
        self.sector_analysis_path = sector_analysis_path or SECTOR_ANALYSIS_PATH
        self.output_dir = output_dir or OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        self._health_df = _load_csv(self.health_scores_path, "health_scores")
        self._peer_df = _load_csv(self.peer_comparison_path, "peer_comparison")
        self._sector_df = _load_csv(self.sector_analysis_path, "sector_analysis")

        # Keep only the latest year per company in peer_df
        self._latest_peer = self._deduplicate(self._peer_df)

    @staticmethod
    def _deduplicate(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "company_id" not in df.columns:
            return df
        if "year" in df.columns:
            df = df.copy()
            df["year"] = pd.to_numeric(df["year"], errors="coerce")
            return df.sort_values("year", ascending=False).drop_duplicates("company_id", keep="first")
        return df.drop_duplicates("company_id", keep="last")

    # ------------------------------------------------------------------
    # Single sector report
    # ------------------------------------------------------------------

    def generate_sector_report(self, sector_name: str) -> Optional[str]:
        """Generate a PDF for one sector."""
        peer = self._latest_peer
        if peer.empty:
            logger.warning("No peer comparison data.")
            return None

        sector_col = next(
            (c for c in ("sector", "broad_sector") if c in peer.columns), None
        )
        if not sector_col:
            logger.warning("No sector column found in peer data.")
            return None

        sector_data = peer[peer[sector_col] == sector_name].copy()
        if sector_data.empty:
            logger.warning("No companies found for sector '%s'.", sector_name)
            return None

        # Resolve numeric metric columns
        def _col(candidates):
            return next((c for c in candidates if c in sector_data.columns), None)

        roe_col = _col(["return_on_equity_pct", "roe"])
        margin_col = _col(["net_profit_margin_pct", "net_profit_margin"])
        dte_col = _col(["debt_to_equity"])
        hs_col = _col(["health_score"])
        cid_col = _col(["company_id", "company", "name"])

        for col in [roe_col, margin_col, dte_col, hs_col]:
            if col:
                sector_data[col] = pd.to_numeric(sector_data[col], errors="coerce")

        safe_sector = re.sub(r"[^\w\-]", "_", sector_name)
        output_path = os.path.join(self.output_dir, f"{safe_sector}_report.pdf")

        try:
            with PdfPages(output_path) as pdf:
                fig = plt.figure(figsize=(11, 8.5), facecolor=BG)

                # -- Header --
                ax_hdr = fig.add_axes([0, 0.93, 1, 0.07])
                ax_hdr.set_facecolor(PRIMARY)
                ax_hdr.text(0.02, 0.55, f"Sector Report: {sector_name}",
                            ha="left", va="center", color="white",
                            fontsize=16, fontweight="bold", transform=ax_hdr.transAxes)
                n_companies = sector_data[cid_col].nunique() if cid_col else len(sector_data)
                ax_hdr.text(0.02, 0.15, f"{n_companies} companies",
                            ha="left", va="center", color="#AED6F1",
                            fontsize=9, transform=ax_hdr.transAxes)
                ax_hdr.axis("off")

                # -- KPI cards (top row) --
                kpis = [
                    ("Avg ROE", _fmt(sector_data[roe_col].mean() if roe_col else None, 1, "%")),
                    ("Avg Net Margin", _fmt(sector_data[margin_col].mean() if margin_col else None, 1, "%")),
                    ("Avg D/E", _fmt(sector_data[dte_col].mean() if dte_col else None, 2)),
                    ("Avg Health Score", _fmt(sector_data[hs_col].mean() if hs_col else None, 1)),
                    ("Median Health", _fmt(sector_data[hs_col].median() if hs_col else None, 1)),
                ]
                for i, (label, val) in enumerate(kpis):
                    ax = fig.add_axes([0.02 + i * 0.196, 0.80, 0.18, 0.11])
                    ax.set_facecolor("#EBF5FB")
                    ax.text(0.5, 0.65, val, ha="center", va="center",
                            fontsize=14, fontweight="bold", color=PRIMARY,
                            transform=ax.transAxes)
                    ax.text(0.5, 0.25, label, ha="center", va="center",
                            fontsize=7, color=NEUTRAL, transform=ax.transAxes)
                    ax.set_xticks([])
                    ax.set_yticks([])
                    for sp in ax.spines.values():
                        sp.set_visible(False)

                # -- Median bar chart --
                ax_med = fig.add_axes([0.05, 0.50, 0.40, 0.26])
                metrics = [c for c in [roe_col, margin_col, dte_col] if c]
                medians = [sector_data[c].median() for c in metrics]
                labels = [c.replace("_pct", "").replace("_", " ").title() for c in metrics]
                colors = [ACCENT, POSITIVE, "#E74C3C"][:len(metrics)]
                if medians:
                    bars = ax_med.bar(labels, medians, color=colors, alpha=0.85)
                    for bar, val in zip(bars, medians):
                        ax_med.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                                    f"{val:.1f}", ha="center", va="bottom", fontsize=8)
                    ax_med.set_title("Median Key Metrics", fontsize=10, color=PRIMARY)
                    ax_med.spines["top"].set_visible(False)
                    ax_med.spines["right"].set_visible(False)
                    ax_med.tick_params(labelsize=8)

                # -- Health Score Distribution --
                ax_hist = fig.add_axes([0.55, 0.50, 0.40, 0.26])
                if hs_col and not sector_data[hs_col].dropna().empty:
                    ax_hist.hist(sector_data[hs_col].dropna(), bins=8,
                                 color=ACCENT, alpha=0.8, edgecolor="white")
                    ax_hist.axvline(sector_data[hs_col].mean(), color=PRIMARY,
                                    linestyle="--", linewidth=1.5, label="Mean")
                    ax_hist.set_title("Health Score Distribution", fontsize=10, color=PRIMARY)
                    ax_hist.set_xlabel("Health Score", fontsize=8)
                    ax_hist.set_ylabel("Count", fontsize=8)
                    ax_hist.tick_params(labelsize=8)
                    ax_hist.legend(fontsize=7)
                    ax_hist.spines["top"].set_visible(False)
                    ax_hist.spines["right"].set_visible(False)
                else:
                    ax_hist.text(0.5, 0.5, "No health score data",
                                 ha="center", va="center", color=NEUTRAL,
                                 transform=ax_hist.transAxes)
                    ax_hist.axis("off")

                # -- Company Rankings table --
                ax_tbl = fig.add_axes([0.03, 0.03, 0.94, 0.43])
                ax_tbl.axis("off")
                ax_tbl.set_title("Company Rankings (by Health Score)", fontsize=10,
                                 color=PRIMARY, loc="left", pad=4)

                rank_cols = [c for c in [cid_col, roe_col, margin_col, dte_col, hs_col] if c]
                rank_df = sector_data[rank_cols].copy()
                if hs_col:
                    rank_df = rank_df.sort_values(hs_col, ascending=False)
                rank_df = rank_df.head(15)

                # Round numeric columns
                for c in [roe_col, margin_col, dte_col, hs_col]:
                    if c and c in rank_df.columns:
                        rank_df[c] = rank_df[c].round(2)

                col_labels = [c.replace("_pct", "").replace("_", " ").title() for c in rank_cols]
                table_data = rank_df.values.tolist()

                if table_data:
                    tbl = ax_tbl.table(
                        cellText=[[str(v) if pd.notna(v) else "N/A" for v in row] for row in table_data],
                        colLabels=col_labels,
                        loc="center",
                        cellLoc="center",
                    )
                    tbl.auto_set_font_size(False)
                    tbl.set_fontsize(7.5)
                    tbl.scale(1, 1.3)

                    # Header style
                    for j in range(len(col_labels)):
                        cell = tbl[0, j]
                        cell.set_facecolor(PRIMARY)
                        cell.set_text_props(color="white", fontweight="bold")

                    # Alternating row colours
                    for r in range(1, len(table_data) + 1):
                        bg = "#EBF5FB" if r % 2 == 0 else "white"
                        for j in range(len(col_labels)):
                            tbl[r, j].set_facecolor(bg)

                # Footer
                ax_foot = fig.add_axes([0, 0, 1, 0.02])
                ax_foot.set_facecolor(PRIMARY)
                ax_foot.text(0.5, 0.5,
                             "N100 Financial Intelligence Platform  |  Sector Report",
                             ha="center", va="center", color="white",
                             fontsize=7, transform=ax_foot.transAxes)
                ax_foot.axis("off")

                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)

            logger.info("Saved sector report: %s", output_path)
            return output_path

        except Exception as exc:
            logger.error("Failed to generate sector report for '%s': %s", sector_name, exc)
            return None

    def run(self) -> List[str]:
        """Generate sector reports for all sectors."""
        print("\n" + "=" * 70)
        print("SECTOR REPORT GENERATOR")
        print("=" * 70)

        peer = self._latest_peer
        if peer.empty:
            logger.error("No peer data available.")
            return []

        sector_col = next(
            (c for c in ("sector", "broad_sector") if c in peer.columns), None
        )
        if not sector_col:
            logger.error("No sector column found.")
            return []

        sectors = peer[sector_col].dropna().unique().tolist()
        logger.info("Generating reports for %d sectors.", len(sectors))

        generated: List[str] = []
        for sector in sectors:
            path = self.generate_sector_report(str(sector))
            if path:
                generated.append(path)

        print(f"  Generated {len(generated)} sector reports in '{self.output_dir}'")
        print("Sector Report Generator complete.\n")
        return generated


if __name__ == "__main__":
    gen = SectorReportGenerator()
    gen.run()
