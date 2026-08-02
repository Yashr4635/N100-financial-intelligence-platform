"""
portfolio_summary.py

Sprint 5 – Portfolio Summary PDF for the N100 Financial Intelligence Platform.

Generates a single comprehensive PDF summarising the entire N100 universe:
  - Portfolio KPI cards (total companies, avg health score, avg ROE, etc.)
  - Health score distribution chart
  - Sector breakdown (companies per sector)
  - Top 10 companies by health score
  - Distress alert summary
  - Capital allocation pattern breakdown (pie chart)
  - Valuation flag breakdown

Inputs
------
- data/output/company_health_scores.csv
- data/output/peer_comparison.csv
- data/output/sector_analysis.csv
- data/output/valuation_flags.csv
- data/output/distress_alerts.csv
- data/output/pattern_changes.csv

Outputs
-------
- reports/portfolio/portfolio_summary.pdf
"""

from __future__ import annotations

import logging
import os
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
VALUATION_FLAGS_PATH = str(PROJECT_ROOT / "data" / "output" / "valuation_flags.csv")
DISTRESS_ALERTS_PATH = str(PROJECT_ROOT / "data" / "output" / "distress_alerts.csv")
PATTERN_CHANGES_PATH = str(PROJECT_ROOT / "data" / "output" / "pattern_changes.csv")
OUTPUT_DIR = str(PROJECT_ROOT / "reports" / "portfolio")

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
PRIMARY = "#1F4E79"
ACCENT = "#2E86AB"
POSITIVE = "#27AE60"
NEGATIVE = "#E74C3C"
NEUTRAL = "#7F8C8D"
BG = "#F8F9FA"
PALETTE = [ACCENT, POSITIVE, "#F39C12", "#8E44AD", "#16A085",
           "#E67E22", "#2980B9", "#C0392B", NEUTRAL, "#1ABC9C"]


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


class PortfolioSummaryGenerator:
    """
    Generates a multi-page portfolio summary PDF across the entire N100 universe.
    """

    def __init__(
        self,
        health_scores_path: Optional[str] = None,
        peer_comparison_path: Optional[str] = None,
        sector_analysis_path: Optional[str] = None,
        valuation_flags_path: Optional[str] = None,
        distress_alerts_path: Optional[str] = None,
        pattern_changes_path: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> None:
        self.output_dir = output_dir or OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_path = os.path.join(self.output_dir, "portfolio_summary.pdf")

        self._health_df = _load_csv(health_scores_path or HEALTH_SCORES_PATH, "health_scores")
        self._peer_df = _load_csv(peer_comparison_path or PEER_COMPARISON_PATH, "peer_comparison")
        self._sector_df = _load_csv(sector_analysis_path or SECTOR_ANALYSIS_PATH, "sector_analysis")
        self._valuation_df = _load_csv(valuation_flags_path or VALUATION_FLAGS_PATH, "valuation_flags")
        self._distress_df = _load_csv(distress_alerts_path or DISTRESS_ALERTS_PATH, "distress_alerts")
        self._pattern_df = _load_csv(pattern_changes_path or PATTERN_CHANGES_PATH, "pattern_changes")

        # Deduplicate to latest year per company
        self._latest = self._deduplicate(self._peer_df)
        if self._latest.empty:
            self._latest = self._deduplicate(self._health_df)

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
    # Page 1: Overview
    # ------------------------------------------------------------------

    def _build_overview_page(self, fig: plt.Figure) -> None:
        """Page 1: header, KPI cards, health distribution, sector breakdown."""
        df = self._latest
        health_col = next((c for c in ("health_score",) if c in df.columns), None)
        roe_col = next((c for c in ("return_on_equity_pct", "roe") if c in df.columns), None)
        margin_col = next((c for c in ("net_profit_margin_pct",) if c in df.columns), None)
        sector_col = next((c for c in ("sector", "broad_sector") if c in df.columns), None)

        if health_col:
            df[health_col] = pd.to_numeric(df[health_col], errors="coerce")
        if roe_col:
            df[roe_col] = pd.to_numeric(df[roe_col], errors="coerce")
        if margin_col:
            df[margin_col] = pd.to_numeric(df[margin_col], errors="coerce")

        # Header
        ax_hdr = fig.add_axes([0, 0.93, 1, 0.07])
        ax_hdr.set_facecolor(PRIMARY)
        ax_hdr.text(0.02, 0.55, "N100 Portfolio Summary Report",
                    ha="left", va="center", color="white",
                    fontsize=16, fontweight="bold", transform=ax_hdr.transAxes)
        ax_hdr.text(0.02, 0.15, "Overview: All Companies · All Sectors",
                    ha="left", va="center", color="#AED6F1",
                    fontsize=9, transform=ax_hdr.transAxes)
        ax_hdr.axis("off")

        # KPI Cards
        n_companies = df["company_id"].nunique() if "company_id" in df.columns else len(df)
        n_sectors = df[sector_col].nunique() if sector_col else "N/A"
        avg_health = df[health_col].mean() if health_col else None
        avg_roe = df[roe_col].mean() if roe_col else None
        avg_margin = df[margin_col].mean() if margin_col else None

        kpis = [
            ("Total Companies", str(n_companies)),
            ("Sectors Covered", str(n_sectors)),
            ("Avg Health Score", _fmt(avg_health, 1)),
            ("Avg ROE", _fmt(avg_roe, 1, "%")),
            ("Avg Net Margin", _fmt(avg_margin, 1, "%")),
        ]
        for i, (label, val) in enumerate(kpis):
            ax = fig.add_axes([0.02 + i * 0.196, 0.80, 0.18, 0.11])
            ax.set_facecolor("#EBF5FB")
            ax.text(0.5, 0.65, val, ha="center", va="center",
                    fontsize=14, fontweight="bold", color=PRIMARY, transform=ax.transAxes)
            ax.text(0.5, 0.25, label, ha="center", va="center",
                    fontsize=7, color=NEUTRAL, transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(False)

        # Health Score Distribution
        ax_hist = fig.add_axes([0.05, 0.47, 0.42, 0.29])
        if health_col and not df[health_col].dropna().empty:
            ax_hist.hist(df[health_col].dropna(), bins=10, color=ACCENT, alpha=0.85, edgecolor="white")
            ax_hist.axvline(df[health_col].mean(), color=PRIMARY, linestyle="--",
                            linewidth=2, label=f"Mean: {df[health_col].mean():.1f}")
            ax_hist.set_title("Health Score Distribution (All Companies)", fontsize=10, color=PRIMARY)
            ax_hist.set_xlabel("Health Score", fontsize=8)
            ax_hist.set_ylabel("Number of Companies", fontsize=8)
            ax_hist.legend(fontsize=8)
            ax_hist.spines["top"].set_visible(False)
            ax_hist.spines["right"].set_visible(False)
            ax_hist.tick_params(labelsize=8)
        else:
            ax_hist.text(0.5, 0.5, "No data", ha="center", va="center",
                         transform=ax_hist.transAxes, color=NEUTRAL)
            ax_hist.axis("off")

        # Sector Breakdown (horizontal bar)
        ax_sec = fig.add_axes([0.55, 0.47, 0.42, 0.29])
        if sector_col:
            sector_counts = df[sector_col].value_counts()
            colors_list = PALETTE[:len(sector_counts)]
            ax_sec.barh(sector_counts.index.tolist()[::-1],
                        sector_counts.values.tolist()[::-1],
                        color=colors_list[::-1], alpha=0.85)
            ax_sec.set_title("Companies per Sector", fontsize=10, color=PRIMARY)
            ax_sec.set_xlabel("Count", fontsize=8)
            ax_sec.tick_params(labelsize=7)
            ax_sec.spines["top"].set_visible(False)
            ax_sec.spines["right"].set_visible(False)
        else:
            ax_sec.text(0.5, 0.5, "Sector data unavailable",
                        ha="center", va="center", transform=ax_sec.transAxes, color=NEUTRAL)
            ax_sec.axis("off")

        # Rating breakdown (pie)
        rating_col = next((c for c in ("rating",) if c in df.columns), None)
        ax_pie = fig.add_axes([0.05, 0.08, 0.38, 0.35])
        if rating_col:
            rating_counts = df[rating_col].value_counts()
            pie_colors = [POSITIVE, ACCENT, "#F39C12", NEUTRAL, NEGATIVE]
            wedges, texts, autotexts = ax_pie.pie(
                rating_counts.values,
                labels=rating_counts.index,
                autopct="%1.0f%%",
                colors=pie_colors[:len(rating_counts)],
                startangle=140,
                pctdistance=0.75,
            )
            for at in autotexts:
                at.set_fontsize(8)
            for t in texts:
                t.set_fontsize(8)
            ax_pie.set_title("Rating Distribution", fontsize=10, color=PRIMARY)
        else:
            ax_pie.axis("off")
            ax_pie.text(0.5, 0.5, "Rating data unavailable",
                        ha="center", va="center", transform=ax_pie.transAxes, color=NEUTRAL)

        # Top 10 companies table
        ax_top = fig.add_axes([0.50, 0.03, 0.48, 0.40])
        ax_top.axis("off")
        ax_top.set_title("Top 10 Companies by Health Score", fontsize=10,
                          color=PRIMARY, loc="left", pad=4)
        if health_col and "company_id" in df.columns:
            top10 = df.nlargest(10, health_col)[
                [c for c in ["company_id", health_col, roe_col, margin_col] if c]
            ].copy()
            top10[health_col] = top10[health_col].round(1)
            col_labels = [c.replace("_pct", "").replace("_", " ").title()
                          for c in top10.columns]
            tbl = ax_top.table(
                cellText=[[str(v) if pd.notna(v) else "N/A" for v in row]
                          for row in top10.values.tolist()],
                colLabels=col_labels,
                loc="center",
                cellLoc="center",
            )
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(8)
            tbl.scale(1, 1.4)
            for j in range(len(col_labels)):
                cell = tbl[0, j]
                cell.set_facecolor(PRIMARY)
                cell.set_text_props(color="white", fontweight="bold")
            for r in range(1, 11):
                for j in range(len(col_labels)):
                    tbl[r, j].set_facecolor("#EBF5FB" if r % 2 == 0 else "white")

        # Footer
        ax_foot = fig.add_axes([0, 0, 1, 0.02])
        ax_foot.set_facecolor(PRIMARY)
        ax_foot.text(0.5, 0.5, "N100 Financial Intelligence Platform  |  Page 1 of 2",
                     ha="center", va="center", color="white",
                     fontsize=7, transform=ax_foot.transAxes)
        ax_foot.axis("off")

    # ------------------------------------------------------------------
    # Page 2: Intelligence signals
    # ------------------------------------------------------------------

    def _build_intelligence_page(self, fig: plt.Figure) -> None:
        """Page 2: distress alerts, pattern breakdown, valuation flags."""
        # Header
        ax_hdr = fig.add_axes([0, 0.93, 1, 0.07])
        ax_hdr.set_facecolor(PRIMARY)
        ax_hdr.text(0.02, 0.5, "N100 Portfolio  –  Intelligence Signals",
                    ha="left", va="center", color="white",
                    fontsize=16, fontweight="bold", transform=ax_hdr.transAxes)
        ax_hdr.axis("off")

        # Capital Allocation Pattern Pie
        ax_alloc = fig.add_axes([0.05, 0.57, 0.40, 0.30])
        if not self._pattern_df.empty and "allocation_pattern" in self._pattern_df.columns:
            pat_counts = self._pattern_df["allocation_pattern"].value_counts()
        elif not self._latest.empty:
            from src.analytics.cashflow_intelligence import CashFlowIntelligenceEngine
            engine = CashFlowIntelligenceEngine()
            pat_counts = self._latest.apply(
                engine._classify_capital_allocation, axis=1
            ).value_counts()
        else:
            pat_counts = pd.Series(dtype=int)

        if not pat_counts.empty:
            ax_alloc.pie(
                pat_counts.values,
                labels=pat_counts.index,
                autopct="%1.0f%%",
                colors=PALETTE[:len(pat_counts)],
                startangle=90,
                pctdistance=0.80,
            )
            ax_alloc.set_title("Capital Allocation Patterns", fontsize=10, color=PRIMARY)
        else:
            ax_alloc.text(0.5, 0.5, "No pattern data",
                          ha="center", va="center", transform=ax_alloc.transAxes, color=NEUTRAL)
            ax_alloc.axis("off")

        # Valuation Flags Bar
        ax_val = fig.add_axes([0.55, 0.57, 0.40, 0.30])
        if not self._valuation_df.empty and "valuation_flag" in self._valuation_df.columns:
            val_counts = self._valuation_df["valuation_flag"].value_counts()
            bar_colors = {
                "Undervalued": POSITIVE,
                "Fairly Valued": ACCENT,
                "Overvalued": NEGATIVE,
            }
            ax_val.bar(
                val_counts.index,
                val_counts.values,
                color=[bar_colors.get(k, NEUTRAL) for k in val_counts.index],
                alpha=0.85,
            )
            for i, (label, count) in enumerate(val_counts.items()):
                ax_val.text(i, count, str(count), ha="center", va="bottom", fontsize=9)
            ax_val.set_title("Valuation Flag Summary", fontsize=10, color=PRIMARY)
            ax_val.set_ylabel("Companies", fontsize=8)
            ax_val.tick_params(labelsize=8)
            ax_val.spines["top"].set_visible(False)
            ax_val.spines["right"].set_visible(False)
        else:
            ax_val.text(0.5, 0.5, "No valuation data",
                        ha="center", va="center", transform=ax_val.transAxes, color=NEUTRAL)
            ax_val.axis("off")

        # Distress Alerts Table
        ax_dist = fig.add_axes([0.03, 0.08, 0.94, 0.44])
        ax_dist.axis("off")
        ax_dist.set_title(
            f"Distress Alerts ({len(self._distress_df)} companies flagged)",
            fontsize=10, color=NEGATIVE, loc="left", pad=4,
        )
        if not self._distress_df.empty:
            show_cols = [c for c in ["company_id", "year", "free_cash_flow_cr",
                                      "cash_from_operations_cr", "debt_to_equity",
                                      "distress_reason"] if c in self._distress_df.columns]
            show_df = self._distress_df[show_cols].head(12)
            for col in show_df.select_dtypes(include=[float, np.number]).columns:
                show_df[col] = show_df[col].round(2)

            tbl = ax_dist.table(
                cellText=[[str(v) if pd.notna(v) else "N/A" for v in row]
                          for row in show_df.values.tolist()],
                colLabels=[c.replace("_", " ").title() for c in show_df.columns],
                loc="center",
                cellLoc="center",
            )
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(7.5)
            tbl.scale(1, 1.35)
            for j in range(len(show_df.columns)):
                cell = tbl[0, j]
                cell.set_facecolor(NEGATIVE)
                cell.set_text_props(color="white", fontweight="bold")
            for r in range(1, len(show_df) + 1):
                for j in range(len(show_df.columns)):
                    tbl[r, j].set_facecolor("#FDEDEC" if r % 2 == 0 else "white")
        else:
            ax_dist.text(0.5, 0.5,
                         "✅  No companies flagged as distressed.",
                         ha="center", va="center",
                         color=POSITIVE, fontsize=12,
                         transform=ax_dist.transAxes, fontweight="bold")

        # Footer
        ax_foot = fig.add_axes([0, 0, 1, 0.02])
        ax_foot.set_facecolor(PRIMARY)
        ax_foot.text(0.5, 0.5,
                     "N100 Financial Intelligence Platform  |  Page 2 of 2  "
                     "|  For internal use only",
                     ha="center", va="center", color="white",
                     fontsize=7, transform=ax_foot.transAxes)
        ax_foot.axis("off")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> Optional[str]:
        """
        Generate the portfolio summary PDF.

        Returns
        -------
        Path to the generated PDF, or None on failure.
        """
        print("\n" + "=" * 70)
        print("PORTFOLIO SUMMARY PDF GENERATOR")
        print("=" * 70)

        if self._latest.empty:
            logger.error("No data available for portfolio summary. Aborting.")
            return None

        try:
            with PdfPages(self.output_path) as pdf:
                fig1 = plt.figure(figsize=(11, 8.5), facecolor=BG)
                self._build_overview_page(fig1)
                pdf.savefig(fig1, bbox_inches="tight")
                plt.close(fig1)

                fig2 = plt.figure(figsize=(11, 8.5), facecolor=BG)
                self._build_intelligence_page(fig2)
                pdf.savefig(fig2, bbox_inches="tight")
                plt.close(fig2)

            print(f"  Saved: {self.output_path}")
            print("Portfolio Summary PDF complete.\n")
            return self.output_path

        except Exception as exc:
            logger.error("Failed to generate portfolio summary: %s", exc)
            return None


if __name__ == "__main__":
    gen = PortfolioSummaryGenerator()
    gen.run()
