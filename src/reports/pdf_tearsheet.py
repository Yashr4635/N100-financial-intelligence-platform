"""
pdf_tearsheet.py

Sprint 5 – PDF Tearsheet Generator for the N100 Financial Intelligence Platform.

Generates a professional two-page PDF tearsheet for every company using
matplotlib's PdfPages backend (no external PDF library required).

Each tearsheet includes:
  Page 1:
    - Header: Company name, sector, rating badge
    - KPI cards: ROE, Net Margin, D/E, Health Score, EPS
    - Revenue trend (bar chart)
    - PAT trend (bar chart)
    - ROE / ROCE line chart
    - Radar chart (embedded from pre-generated PNG)

  Page 2:
    - Balance Sheet summary (bar chart)
    - Cash Flow summary (bar chart)
    - Pros (top 5)
    - Cons (top 5)
    - Capital Allocation Badge

Inputs
------
- data/output/company_health_scores.csv
- data/output/peer_comparison.csv
- data/output/pros_cons_generated.csv
- data/output/pattern_changes.csv
- data/raw/profitandloss.xlsx
- data/raw/balancesheet.xlsx
- data/raw/cashflow.xlsx
- reports/radar_charts/<TICKER>_radar.png

Outputs
-------
- reports/tearsheets/<TICKER>_tearsheet.pdf  (one per company)
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

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
PROS_CONS_PATH = str(PROJECT_ROOT / "data" / "output" / "pros_cons_generated.csv")
PATTERN_CHANGES_PATH = str(PROJECT_ROOT / "data" / "output" / "pattern_changes.csv")
PNL_RAW_PATH = str(PROJECT_ROOT / "data" / "raw" / "profitandloss.xlsx")
BS_RAW_PATH = str(PROJECT_ROOT / "data" / "raw" / "balancesheet.xlsx")
CF_RAW_PATH = str(PROJECT_ROOT / "data" / "raw" / "cashflow.xlsx")
RADAR_CHARTS_DIR = str(PROJECT_ROOT / "reports" / "radar_charts")
OUTPUT_DIR = str(PROJECT_ROOT / "reports" / "tearsheets")

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
PRIMARY = "#1F4E79"
ACCENT = "#2E86AB"
POSITIVE = "#27AE60"
NEGATIVE = "#E74C3C"
NEUTRAL = "#7F8C8D"
BG = "#F8F9FA"
CARD_BG = "#EBF5FB"


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _safe_float(val) -> Optional[float]:
    if val is None:
        return None
    try:
        f = float(val)
        return None if pd.isna(f) else f
    except (ValueError, TypeError):
        return None


def _fmt(val, decimals: int = 1, suffix: str = "") -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "N/A"
    return f"{round(float(val), decimals):,}{suffix}"


def _normalise_year(val) -> Optional[int]:
    """Convert "Mar-13", "Dec 2012", 2023, etc. to integer year."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).strip()
    m = re.match(r"[A-Za-z]+-(\d{2})$", s)
    if m:
        yy = int(m.group(1))
        return 2000 + yy if yy < 50 else 1900 + yy
    m2 = re.match(r"[A-Za-z]+\s+(\d{4})$", s)
    if m2:
        return int(m2.group(1))
    try:
        return int(float(s))
    except ValueError:
        return None


def _load_csv(path: str, label: str) -> pd.DataFrame:
    if not os.path.exists(path):
        logger.warning("%s not found at '%s'.", label, path)
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception as exc:
        logger.error("Failed to load %s: %s", label, exc)
        return pd.DataFrame()


def _load_excel(path: str, label: str, header: int = 1) -> pd.DataFrame:
    if not os.path.exists(path):
        logger.warning("%s not found at '%s'.", label, path)
        return pd.DataFrame()
    try:
        df = pd.read_excel(path, header=header)
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
        return df
    except Exception as exc:
        logger.error("Failed to load %s: %s", label, exc)
        return pd.DataFrame()


# ---------------------------------------------------------------------------
# Drawing primitives
# ---------------------------------------------------------------------------

def _draw_kpi_card(ax: plt.Axes, label: str, value: str, color: str = PRIMARY) -> None:
    """Draw a KPI card with a coloured top border inside the given axes."""
    ax.set_facecolor(CARD_BG)
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.05, 0.05), 0.9, 0.9, boxstyle="round,pad=0.02",
        facecolor=CARD_BG, edgecolor=color, linewidth=2,
        transform=ax.transAxes, clip_on=False
    ))
    ax.text(0.5, 0.65, value, ha="center", va="center",
            fontsize=14, fontweight="bold", color=color, transform=ax.transAxes)
    ax.text(0.5, 0.28, label, ha="center", va="center",
            fontsize=7, color=NEUTRAL, transform=ax.transAxes, wrap=True)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def _header_page1(fig: plt.Figure, company: str, sector: str, rating: str) -> None:
    """Draw the page 1 header band."""
    ax_hdr = fig.add_axes([0, 0.93, 1, 0.07])
    ax_hdr.set_facecolor(PRIMARY)
    ax_hdr.text(0.02, 0.55, company, ha="left", va="center",
                color="white", fontsize=16, fontweight="bold",
                transform=ax_hdr.transAxes)
    ax_hdr.text(0.02, 0.15, f"Sector: {sector}", ha="left", va="center",
                color="#AED6F1", fontsize=9, transform=ax_hdr.transAxes)
    # Rating badge
    badge_color = {
        "Excellent": POSITIVE, "Very Good": ACCENT,
        "Good": "#F39C12", "Average": NEUTRAL, "Poor": NEGATIVE,
    }.get(str(rating), NEUTRAL)
    ax_hdr.text(0.98, 0.5, f"  {rating}  ", ha="right", va="center",
                color="white", fontsize=10, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=badge_color, edgecolor="white"),
                transform=ax_hdr.transAxes)
    ax_hdr.set_xticks([])
    ax_hdr.set_yticks([])
    for spine in ax_hdr.spines.values():
        spine.set_visible(False)


def _bar_chart(ax: plt.Axes, years: list, values: list,
               title: str, ylabel: str, color: str = ACCENT) -> None:
    """Simple bar chart with year labels."""
    if not years or not values:
        ax.text(0.5, 0.5, "No data", ha="center", va="center",
                transform=ax.transAxes, color=NEUTRAL)
        ax.set_title(title, fontsize=9, color=PRIMARY, pad=4)
        return
    bars = ax.bar(years, values, color=color, alpha=0.85, width=0.6)
    ax.set_title(title, fontsize=9, color=PRIMARY, pad=4)
    ax.set_ylabel(ylabel, fontsize=7)
    ax.tick_params(axis="both", labelsize=7)
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels([str(y) for y in years], rotation=45, ha="right", fontsize=6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # Value labels on top of bars
    for bar, val in zip(bars, values):
        if val is not None and not pd.isna(val):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f"{val:,.0f}", ha="center", va="bottom", fontsize=5)


def _line_chart(ax: plt.Axes, years: list, series_dict: Dict[str, list],
                title: str, ylabel: str) -> None:
    """Multi-line chart."""
    colors = [ACCENT, POSITIVE, "#E67E22", NEGATIVE]
    ax.set_title(title, fontsize=9, color=PRIMARY, pad=4)
    ax.set_ylabel(ylabel, fontsize=7)
    ax.tick_params(axis="both", labelsize=7)

    has_data = False
    for i, (label, values) in enumerate(series_dict.items()):
        clean = [(y, v) for y, v in zip(years, values)
                 if v is not None and not (isinstance(v, float) and pd.isna(v))]
        if not clean:
            continue
        ys, vs = zip(*clean)
        ax.plot(ys, vs, marker="o", markersize=3, linewidth=1.5,
                color=colors[i % len(colors)], label=label)
        has_data = True

    if not has_data:
        ax.text(0.5, 0.5, "No data", ha="center", va="center",
                transform=ax.transAxes, color=NEUTRAL)
    else:
        ax.legend(fontsize=6, loc="best")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class PDFTearsheetGenerator:
    """
    Generates a two-page PDF tearsheet per company using matplotlib.

    Usage
    -----
    gen = PDFTearsheetGenerator()
    gen.run()                   # all companies
    gen.generate_one("TCS")     # single company
    """

    def __init__(
        self,
        health_scores_path: Optional[str] = None,
        peer_comparison_path: Optional[str] = None,
        pros_cons_path: Optional[str] = None,
        pattern_changes_path: Optional[str] = None,
        pnl_path: Optional[str] = None,
        bs_path: Optional[str] = None,
        cf_path: Optional[str] = None,
        radar_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> None:
        self.health_scores_path = health_scores_path or HEALTH_SCORES_PATH
        self.peer_comparison_path = peer_comparison_path or PEER_COMPARISON_PATH
        self.pros_cons_path = pros_cons_path or PROS_CONS_PATH
        self.pattern_changes_path = pattern_changes_path or PATTERN_CHANGES_PATH
        self.pnl_path = pnl_path or PNL_RAW_PATH
        self.bs_path = bs_path or BS_RAW_PATH
        self.cf_path = cf_path or CF_RAW_PATH
        self.radar_dir = radar_dir or RADAR_CHARTS_DIR
        self.output_dir = output_dir or OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        # Pre-load all datasets once
        self._health_df = _load_csv(self.health_scores_path, "health_scores")
        self._peer_df = _load_csv(self.peer_comparison_path, "peer_comparison")
        self._pros_cons_df = _load_csv(self.pros_cons_path, "pros_cons")
        self._pattern_df = _load_csv(self.pattern_changes_path, "pattern_changes")
        self._pnl_df = _load_excel(self.pnl_path, "profitandloss", header=1)
        self._bs_df = _load_excel(self.bs_path, "balancesheet", header=1)
        self._cf_df = _load_excel(self.cf_path, "cashflow", header=1)

        # Normalise years in raw files
        for df in [self._pnl_df, self._bs_df, self._cf_df]:
            if not df.empty and "year" in df.columns:
                df["year"] = df["year"].apply(_normalise_year)

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------

    def _company_latest_row(self, company_id: str) -> Optional[pd.Series]:
        """Return the latest-year health score row for a company."""
        df = self._health_df
        if df.empty or "company_id" not in df.columns:
            return None
        subset = df[df["company_id"] == company_id].copy()
        if subset.empty:
            return None
        if "year" in subset.columns:
            subset["year"] = pd.to_numeric(subset["year"], errors="coerce")
            subset = subset.sort_values("year", ascending=False)
        return subset.iloc[0]

    def _peer_latest_row(self, company_id: str) -> Optional[pd.Series]:
        df = self._peer_df
        if df.empty or "company_id" not in df.columns:
            return None
        subset = df[df["company_id"] == company_id].copy()
        if subset.empty:
            return None
        if "year" in subset.columns:
            subset["year"] = pd.to_numeric(subset["year"], errors="coerce")
            subset = subset.sort_values("year", ascending=False)
        return subset.iloc[0]

    def _get_sector(self, company_id: str) -> str:
        row = self._peer_latest_row(company_id)
        if row is None:
            return "Unknown"
        for col in ("sector", "broad_sector"):
            if col in row.index and pd.notna(row[col]):
                return str(row[col])
        return "Unknown"

    def _get_trend(self, df: pd.DataFrame, company_id: str,
                   col: str, n_years: int = 8) -> tuple:
        """Return (years_list, values_list) for a company from a raw df."""
        if df.empty or "company_id" not in df.columns or col not in df.columns:
            return [], []
        subset = df[df["company_id"] == company_id].dropna(subset=["year", col])
        if subset.empty:
            return [], []
        subset = subset.sort_values("year").tail(n_years)
        years = [int(y) for y in subset["year"].tolist()]
        vals = pd.to_numeric(subset[col], errors="coerce").tolist()
        return years, vals

    def _get_pros_cons(self, company_id: str, top_n: int = 5) -> tuple:
        """Return (pros list, cons list)."""
        df = self._pros_cons_df
        if df.empty or "company_id" not in df.columns:
            return [], []
        subset = df[df["company_id"] == company_id]
        pros = (
            subset[subset["type"] == "Pro"]
            .sort_values("confidence", ascending=False)
            .head(top_n)["insight"].tolist()
        ) if "type" in subset.columns else []
        cons = (
            subset[subset["type"] == "Con"]
            .sort_values("confidence", ascending=False)
            .head(top_n)["insight"].tolist()
        ) if "type" in subset.columns else []
        return pros, cons

    def _get_latest_alloc_pattern(self, company_id: str) -> str:
        """Return the most recent allocation pattern for a company."""
        df = self._pattern_df
        if df.empty or "company_id" not in df.columns:
            # Fall back to health_scores classification
            row = self._company_latest_row(company_id)
            if row is None:
                return "N/A"
            from src.analytics.cashflow_intelligence import CashFlowIntelligenceEngine
            engine = CashFlowIntelligenceEngine()
            return engine._classify_capital_allocation(row)

        subset = df[df["company_id"] == company_id]
        if subset.empty:
            return "N/A"
        if "year" in subset.columns:
            subset = subset.sort_values("year", ascending=False)
        val = subset.iloc[0].get("allocation_pattern", "N/A")
        return str(val) if pd.notna(val) else "N/A"

    def _radar_path(self, company_id: str) -> Optional[str]:
        """Find the radar chart PNG for a company, case-insensitive."""
        candidates = [
            os.path.join(self.radar_dir, f"{company_id}_radar.png"),
            os.path.join(self.radar_dir, f"{company_id.upper()}_radar.png"),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        # Search directory
        if os.path.isdir(self.radar_dir):
            for fname in os.listdir(self.radar_dir):
                if fname.lower() == f"{company_id.lower()}_radar.png":
                    return os.path.join(self.radar_dir, fname)
        return None

    # ------------------------------------------------------------------
    # Page building
    # ------------------------------------------------------------------

    def _build_page1(
        self,
        fig: plt.Figure,
        company_id: str,
        latest_row: pd.Series,
        sector: str,
    ) -> None:
        """Build page 1: header, KPIs, revenue, PAT, ROE/ROCE, radar."""
        rating = str(latest_row.get("rating", "N/A"))
        _header_page1(fig, company_id, sector, rating)

        # KPI cards (5 across, in a thin row)
        kpi_specs = [
            ("ROE", _fmt(_safe_float(latest_row.get("return_on_equity_pct")), 1, "%")),
            ("Net Margin", _fmt(_safe_float(latest_row.get("net_profit_margin_pct")), 1, "%")),
            ("D/E Ratio", _fmt(_safe_float(latest_row.get("debt_to_equity")), 2)),
            ("Health Score", _fmt(_safe_float(latest_row.get("health_score")), 0)),
            ("EPS", _fmt(_safe_float(latest_row.get("earnings_per_share")), 1)),
        ]

        for i, (label, value) in enumerate(kpi_specs):
            ax = fig.add_axes([0.02 + i * 0.196, 0.80, 0.18, 0.11])
            color = POSITIVE if i == 3 and _safe_float(latest_row.get("health_score", 0) or 0) >= 80 else PRIMARY
            _draw_kpi_card(ax, label, value, color)

        # Revenue trend
        rev_years, rev_vals = self._get_trend(self._pnl_df, company_id, "sales")
        ax_rev = fig.add_axes([0.05, 0.54, 0.42, 0.23])
        _bar_chart(ax_rev, rev_years, rev_vals, "Revenue Trend (₹ Cr)", "₹ Cr", ACCENT)

        # PAT trend
        pat_years, pat_vals = self._get_trend(self._pnl_df, company_id, "net_profit")
        ax_pat = fig.add_axes([0.55, 0.54, 0.42, 0.23])
        _bar_chart(ax_pat, pat_years, pat_vals, "PAT Trend (₹ Cr)", "₹ Cr", POSITIVE)

        # ROE line chart
        peer_row = self._peer_latest_row(company_id)
        peer_df_sub = self._peer_df[self._peer_df["company_id"] == company_id].copy() \
            if not self._peer_df.empty else pd.DataFrame()

        roe_years, roe_vals = self._get_trend(self._health_df, company_id, "return_on_equity_pct")
        ax_roe = fig.add_axes([0.05, 0.29, 0.42, 0.21])
        _line_chart(ax_roe, roe_years, {"ROE (%)": roe_vals}, "ROE Trend", "ROE %")

        # Radar chart
        radar_path = self._radar_path(company_id)
        ax_radar = fig.add_axes([0.52, 0.27, 0.45, 0.25])
        if radar_path:
            try:
                img = plt.imread(radar_path)
                ax_radar.imshow(img)
                ax_radar.axis("off")
                ax_radar.set_title("Peer-Relative Radar", fontsize=8, color=PRIMARY)
            except Exception:
                ax_radar.text(0.5, 0.5, "Radar chart\nunavailable",
                              ha="center", va="center", color=NEUTRAL,
                              transform=ax_radar.transAxes, fontsize=8)
                ax_radar.axis("off")
        else:
            ax_radar.text(0.5, 0.5, "Radar chart\nnot generated",
                          ha="center", va="center", color=NEUTRAL,
                          transform=ax_radar.transAxes, fontsize=8)
            ax_radar.axis("off")

        # Footer
        ax_foot = fig.add_axes([0, 0, 1, 0.03])
        ax_foot.set_facecolor(PRIMARY)
        ax_foot.text(0.5, 0.5, "N100 Financial Intelligence Platform  |  Page 1 of 2",
                     ha="center", va="center", color="white", fontsize=7,
                     transform=ax_foot.transAxes)
        ax_foot.set_xticks([])
        ax_foot.set_yticks([])
        for s in ax_foot.spines.values():
            s.set_visible(False)

    def _build_page2(
        self,
        fig: plt.Figure,
        company_id: str,
        pros: List[str],
        cons: List[str],
        alloc_pattern: str,
    ) -> None:
        """Build page 2: BS summary, CF summary, pros, cons, allocation badge."""
        # Page 2 header
        ax_hdr2 = fig.add_axes([0, 0.93, 1, 0.07])
        ax_hdr2.set_facecolor(PRIMARY)
        ax_hdr2.text(0.02, 0.5, f"{company_id}  –  Financial Deep Dive",
                     ha="left", va="center", color="white",
                     fontsize=14, fontweight="bold", transform=ax_hdr2.transAxes)
        ax_hdr2.set_xticks([])
        ax_hdr2.set_yticks([])
        for s in ax_hdr2.spines.values():
            s.set_visible(False)

        # Balance Sheet trend
        bs_years, bs_total_assets = self._get_trend(self._bs_df, company_id, "total_assets")
        _, bs_borrowings = self._get_trend(self._bs_df, company_id, "borrowings")
        ax_bs = fig.add_axes([0.05, 0.67, 0.42, 0.22])
        _bar_chart(ax_bs, bs_years, bs_total_assets,
                   "Balance Sheet – Total Assets (₹ Cr)", "₹ Cr", ACCENT)

        # Cash Flow trend
        cf_years, cf_ops = self._get_trend(self._cf_df, company_id, "operating_activity")
        ax_cf = fig.add_axes([0.55, 0.67, 0.42, 0.22])
        _bar_chart(ax_cf, cf_years, cf_ops,
                   "Cash from Operations (₹ Cr)", "₹ Cr", POSITIVE)

        # Capital Allocation Badge
        badge_colors = {
            "Growth Investor": ACCENT,
            "Dividend Focus": POSITIVE,
            "Cash Accumulator": "#8E44AD",
            "Debt Reducer": "#16A085",
            "Balanced": NEUTRAL,
            "Distressed": NEGATIVE,
        }
        alloc_color = badge_colors.get(alloc_pattern, NEUTRAL)

        ax_badge = fig.add_axes([0.05, 0.54, 0.9, 0.10])
        ax_badge.set_facecolor(alloc_color)
        ax_badge.text(0.5, 0.55, f"Capital Allocation: {alloc_pattern}",
                      ha="center", va="center", color="white",
                      fontsize=13, fontweight="bold", transform=ax_badge.transAxes)
        ax_badge.set_xticks([])
        ax_badge.set_yticks([])
        for s in ax_badge.spines.values():
            s.set_visible(False)

        # Pros section
        ax_pros = fig.add_axes([0.05, 0.10, 0.42, 0.41])
        ax_pros.set_facecolor("#EAFAF1")
        ax_pros.set_title("✅  Pros", fontsize=11, color=POSITIVE, pad=6, loc="left")
        ax_pros.axis("off")
        if pros:
            for i, text in enumerate(pros[:5]):
                wrapped = text[:80] + ("…" if len(text) > 80 else "")
                ax_pros.text(0.03, 0.88 - i * 0.17, f"• {wrapped}",
                             ha="left", va="top", fontsize=8, color="#1E8449",
                             transform=ax_pros.transAxes, wrap=True)
        else:
            ax_pros.text(0.5, 0.5, "No pros generated", ha="center", va="center",
                         color=NEUTRAL, transform=ax_pros.transAxes, fontsize=9)

        # Cons section
        ax_cons = fig.add_axes([0.55, 0.10, 0.42, 0.41])
        ax_cons.set_facecolor("#FDEDEC")
        ax_cons.set_title("⚠️  Cons", fontsize=11, color=NEGATIVE, pad=6, loc="left")
        ax_cons.axis("off")
        if cons:
            for i, text in enumerate(cons[:5]):
                wrapped = text[:80] + ("…" if len(text) > 80 else "")
                ax_cons.text(0.03, 0.88 - i * 0.17, f"• {wrapped}",
                             ha="left", va="top", fontsize=8, color="#922B21",
                             transform=ax_cons.transAxes, wrap=True)
        else:
            ax_cons.text(0.5, 0.5, "No cons generated", ha="center", va="center",
                         color=NEUTRAL, transform=ax_cons.transAxes, fontsize=9)

        # Footer
        ax_foot = fig.add_axes([0, 0, 1, 0.03])
        ax_foot.set_facecolor(PRIMARY)
        ax_foot.text(0.5, 0.5,
                     "N100 Financial Intelligence Platform  |  Page 2 of 2  "
                     "|  For internal use only",
                     ha="center", va="center", color="white", fontsize=7,
                     transform=ax_foot.transAxes)
        ax_foot.set_xticks([])
        ax_foot.set_yticks([])
        for s in ax_foot.spines.values():
            s.set_visible(False)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_one(self, company_id: str) -> Optional[str]:
        """
        Generate a two-page tearsheet PDF for a single company.

        Parameters
        ----------
        company_id : str
            Company ticker / identifier matching 'company_id' in the data.

        Returns
        -------
        Output PDF path, or None on failure.
        """
        latest_row = self._company_latest_row(company_id)
        if latest_row is None:
            logger.warning("No data for company '%s'. Skipping.", company_id)
            return None

        sector = self._get_sector(company_id)
        pros, cons = self._get_pros_cons(company_id)
        alloc = self._get_latest_alloc_pattern(company_id)

        safe_name = re.sub(r"[^\w\-]", "_", company_id)
        output_path = os.path.join(self.output_dir, f"{safe_name}_tearsheet.pdf")

        try:
            with PdfPages(output_path) as pdf:
                # Page 1
                fig1 = plt.figure(figsize=(11, 8.5), facecolor=BG)
                self._build_page1(fig1, company_id, latest_row, sector)
                pdf.savefig(fig1, bbox_inches="tight")
                plt.close(fig1)

                # Page 2
                fig2 = plt.figure(figsize=(11, 8.5), facecolor=BG)
                self._build_page2(fig2, company_id, pros, cons, alloc)
                pdf.savefig(fig2, bbox_inches="tight")
                plt.close(fig2)

            logger.info("Generated tearsheet: %s", output_path)
            return output_path

        except Exception as exc:
            logger.error("Failed to generate tearsheet for '%s': %s", company_id, exc)
            return None

    def run(self) -> List[str]:
        """
        Generate tearsheets for all companies in the health scores data.

        Returns
        -------
        List of generated PDF paths.
        """
        print("\n" + "=" * 70)
        print("PDF TEARSHEET GENERATOR")
        print("=" * 70)

        if self._health_df.empty or "company_id" not in self._health_df.columns:
            logger.error("No health score data. Cannot generate tearsheets.")
            return []

        companies = self._health_df["company_id"].dropna().unique().tolist()
        logger.info("Generating tearsheets for %d companies.", len(companies))

        generated: List[str] = []
        for company_id in companies:
            path = self.generate_one(str(company_id))
            if path:
                generated.append(path)

        print(f"  Generated {len(generated)} tearsheets in '{self.output_dir}'")
        print("PDF Tearsheet Generator complete.\n")
        return generated


if __name__ == "__main__":
    gen = PDFTearsheetGenerator()
    gen.run()
