"""
pros_cons_generator.py

Sprint 5 – Pros & Cons Generator for the N100 Financial Intelligence Platform.

Implements all business rules to derive qualitative pros and cons for
each company from quantitative financial data (health scores, ratios,
peer rankings). Augments these with text parsed from the raw
``prosandcons`` dataset. Each insight carries a confidence score.

Inputs
------
- data/raw/prosandcons.xlsx              (raw qualitative text)
- data/output/company_health_scores.csv  (ratios + health score)
- data/output/peer_comparison.csv        (peer percentiles)
- data/output/sector_analysis.csv        (sector benchmarks)

Outputs
-------
- data/output/pros_cons_generated.csv

Business Rules
--------------
Pros generated when:
  ROE >= 15%                  → "Strong return on equity"
  Net Profit Margin >= 10%    → "Healthy profit margins"
  Debt/Equity <= 0.5          → "Low leverage / strong balance sheet"
  FCF > 0                     → "Positive free cash flow"
  Health Score >= 80          → "High overall financial health"
  Peer rank <= 3              → "Sector leader in peer comparison"
  Dividend payout >= 25%      → "Consistent dividend payer"
  Asset Turnover >= 1.2       → "Efficient asset utilisation"

Cons generated when:
  ROE < 5%                    → "Weak return on equity"
  Net Profit Margin < 5%      → "Thin profit margins"
  Debt/Equity > 2             → "High leverage / debt risk"
  FCF < 0                     → "Negative free cash flow"
  Health Score < 50           → "Weak financial health overall"
  Interest Coverage < 2       → "Low interest coverage – debt stress"
  Dividend payout == 0        → "No dividend distribution"
  Debt/Equity > 1 & ROE < 10% → "Leveraged with weak returns"
"""

from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PROSANDCONS_PATH = os.path.join("data", "raw", "prosandcons.xlsx")
HEALTH_SCORES_PATH = os.path.join("data", "output", "company_health_scores.csv")
PEER_COMPARISON_PATH = os.path.join("data", "output", "peer_comparison.csv")
SECTOR_ANALYSIS_PATH = os.path.join("data", "output", "sector_analysis.csv")
OUTPUT_DIR = os.path.join("data", "output")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "pros_cons_generated.csv")


# ---------------------------------------------------------------------------
# Business Rule Definitions
# ---------------------------------------------------------------------------

def _safe_float(val) -> Optional[float]:
    """Convert a value to float safely; return None on failure."""
    if val is None:
        return None
    try:
        f = float(val)
        return None if pd.isna(f) else f
    except (ValueError, TypeError):
        return None


def _roe_pro(row: pd.Series) -> Optional[Tuple[str, float]]:
    roe = _safe_float(row.get("return_on_equity_pct"))
    if roe is None:
        return None
    if roe >= 20:
        return ("Strong return on equity (ROE {:.1f}%)".format(roe), 0.95)
    if roe >= 15:
        return ("Healthy return on equity (ROE {:.1f}%)".format(roe), 0.80)
    return None


def _roe_con(row: pd.Series) -> Optional[Tuple[str, float]]:
    roe = _safe_float(row.get("return_on_equity_pct"))
    if roe is None:
        return None
    if roe < 5:
        return ("Weak return on equity (ROE {:.1f}%)".format(roe), 0.90)
    if roe < 10:
        return ("Below-average return on equity (ROE {:.1f}%)".format(roe), 0.70)
    return None


def _margin_pro(row: pd.Series) -> Optional[Tuple[str, float]]:
    npm = _safe_float(row.get("net_profit_margin_pct"))
    if npm is None:
        return None
    if npm >= 20:
        return ("Excellent net profit margin ({:.1f}%)".format(npm), 0.95)
    if npm >= 10:
        return ("Healthy net profit margin ({:.1f}%)".format(npm), 0.80)
    return None


def _margin_con(row: pd.Series) -> Optional[Tuple[str, float]]:
    npm = _safe_float(row.get("net_profit_margin_pct"))
    if npm is None:
        return None
    if npm < 3:
        return ("Very thin profit margin ({:.1f}%)".format(npm), 0.90)
    if npm < 7:
        return ("Below-average profit margin ({:.1f}%)".format(npm), 0.70)
    return None


def _leverage_pro(row: pd.Series) -> Optional[Tuple[str, float]]:
    dte = _safe_float(row.get("debt_to_equity"))
    if dte is None:
        return None
    if dte == 0:
        return ("Debt-free company", 0.95)
    if dte <= 0.5:
        return ("Low financial leverage (D/E {:.2f})".format(dte), 0.85)
    return None


def _leverage_con(row: pd.Series) -> Optional[Tuple[str, float]]:
    dte = _safe_float(row.get("debt_to_equity"))
    roe = _safe_float(row.get("return_on_equity_pct"))
    if dte is None:
        return None
    if dte > 3:
        return ("Very high debt burden (D/E {:.2f})".format(dte), 0.92)
    if dte > 2:
        return ("High financial leverage (D/E {:.2f})".format(dte), 0.82)
    if dte > 1 and roe is not None and roe < 10:
        return ("Leveraged balance sheet with weak returns (D/E {:.2f}, ROE {:.1f}%)".format(dte, roe), 0.75)
    return None


def _fcf_pro(row: pd.Series) -> Optional[Tuple[str, float]]:
    fcf = _safe_float(row.get("free_cash_flow_cr"))
    if fcf is None:
        return None
    if fcf > 1000:
        return ("Strong free cash flow generation (₹{:,.0f} Cr)".format(fcf), 0.90)
    if fcf > 0:
        return ("Positive free cash flow (₹{:,.0f} Cr)".format(fcf), 0.80)
    return None


def _fcf_con(row: pd.Series) -> Optional[Tuple[str, float]]:
    fcf = _safe_float(row.get("free_cash_flow_cr"))
    if fcf is None:
        return None
    if fcf < 0:
        return ("Negative free cash flow (₹{:,.0f} Cr)".format(fcf), 0.85)
    return None


def _health_pro(row: pd.Series) -> Optional[Tuple[str, float]]:
    hs = _safe_float(row.get("health_score"))
    if hs is None:
        return None
    if hs >= 90:
        return ("Excellent overall financial health (score {:.0f}/100)".format(hs), 0.95)
    if hs >= 80:
        return ("Strong overall financial health (score {:.0f}/100)".format(hs), 0.85)
    return None


def _health_con(row: pd.Series) -> Optional[Tuple[str, float]]:
    hs = _safe_float(row.get("health_score"))
    if hs is None:
        return None
    if hs < 40:
        return ("Poor overall financial health (score {:.0f}/100)".format(hs), 0.90)
    if hs < 60:
        return ("Below-average financial health (score {:.0f}/100)".format(hs), 0.75)
    return None


def _peer_pro(row: pd.Series) -> Optional[Tuple[str, float]]:
    rank = _safe_float(row.get("overall_peer_rank"))
    if rank is None:
        return None
    if rank <= 2:
        return ("Top sector performer (peer rank #{:.0f})".format(rank), 0.90)
    if rank <= 5:
        return ("Strong peer comparison position (rank #{:.0f})".format(rank), 0.75)
    return None


def _dividend_pro(row: pd.Series) -> Optional[Tuple[str, float]]:
    div = _safe_float(row.get("dividend_payout_ratio_pct"))
    if div is None:
        return None
    if div >= 30:
        return ("Consistent and generous dividend payer (payout {:.1f}%)".format(div), 0.85)
    if div >= 20:
        return ("Regular dividend distribution (payout {:.1f}%)".format(div), 0.75)
    return None


def _dividend_con(row: pd.Series) -> Optional[Tuple[str, float]]:
    div = _safe_float(row.get("dividend_payout_ratio_pct"))
    if div is None:
        return None
    if div == 0:
        return ("No dividend distributed to shareholders", 0.70)
    return None


def _asset_turnover_pro(row: pd.Series) -> Optional[Tuple[str, float]]:
    at_ = _safe_float(row.get("asset_turnover"))
    if at_ is None:
        return None
    if at_ >= 1.5:
        return ("Highly efficient asset utilisation (turnover {:.2f}x)".format(at_), 0.85)
    if at_ >= 1.0:
        return ("Efficient asset utilisation (turnover {:.2f}x)".format(at_), 0.75)
    return None


def _interest_coverage_con(row: pd.Series) -> Optional[Tuple[str, float]]:
    ic = _safe_float(row.get("interest_coverage"))
    if ic is None:
        return None
    if ic < 1.5:
        return ("Critically low interest coverage ratio ({:.1f}x) – debt stress".format(ic), 0.92)
    if ic < 2.5:
        return ("Low interest coverage ({:.1f}x)".format(ic), 0.78)
    return None


# Ordered list of rule functions: (rule_fn, type)
PRO_RULES = [
    _roe_pro,
    _margin_pro,
    _leverage_pro,
    _fcf_pro,
    _health_pro,
    _peer_pro,
    _dividend_pro,
    _asset_turnover_pro,
]

CON_RULES = [
    _roe_con,
    _margin_con,
    _leverage_con,
    _fcf_con,
    _health_con,
    _dividend_con,
    _interest_coverage_con,
]


class ProsConsGenerator:
    """
    Generates qualitative pros & cons for every company using
    a rule-based engine over quantitative financial data, enriched
    with raw text insights from prosandcons.xlsx.

    Each record in the output carries a confidence score (0-1) that
    reflects how strong the underlying data signal is.
    """

    def __init__(
        self,
        prosandcons_path: Optional[str] = None,
        health_scores_path: Optional[str] = None,
        peer_comparison_path: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> None:
        self.prosandcons_path = prosandcons_path or PROSANDCONS_PATH
        self.health_scores_path = health_scores_path or HEALTH_SCORES_PATH
        self.peer_comparison_path = peer_comparison_path or PEER_COMPARISON_PATH
        self.output_dir = output_dir or OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_path = os.path.join(self.output_dir, "pros_cons_generated.csv")

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    @staticmethod
    def _load_csv(path: str, label: str) -> pd.DataFrame:
        if not os.path.exists(path):
            logger.warning("%s not found at '%s'.", label, path)
            return pd.DataFrame()
        try:
            df = pd.read_csv(path)
            logger.info("Loaded %s: %d rows.", label, len(df))
            return df
        except Exception as exc:
            logger.error("Failed to load %s: %s", label, exc)
            return pd.DataFrame()

    def _load_raw_prosandcons(self) -> pd.DataFrame:
        if not os.path.exists(self.prosandcons_path):
            logger.warning("prosandcons.xlsx not found.")
            return pd.DataFrame()
        try:
            df = pd.read_excel(self.prosandcons_path, header=1)
            df.columns = [c.strip().lower() for c in df.columns]
            logger.info("Loaded prosandcons.xlsx: %d rows.", len(df))
            return df
        except Exception as exc:
            logger.error("Failed to load prosandcons.xlsx: %s", exc)
            return pd.DataFrame()

    # ------------------------------------------------------------------
    # Rule engine
    # ------------------------------------------------------------------

    def _apply_rules(self, row: pd.Series) -> Tuple[List[dict], List[dict]]:
        """
        Apply all business rules to a single company row.

        Returns
        -------
        (pro_records, con_records)
        """
        pros, cons = [], []

        company_id = str(row.get("company_id", "")).strip()

        for rule_fn in PRO_RULES:
            try:
                result = rule_fn(row)
                if result:
                    text, confidence = result
                    pros.append({
                        "company_id": company_id,
                        "type": "Pro",
                        "insight": text,
                        "confidence": round(confidence, 2),
                        "source": "Rule-Based",
                    })
            except Exception as exc:
                logger.debug("Rule %s failed for %s: %s", rule_fn.__name__, company_id, exc)

        for rule_fn in CON_RULES:
            try:
                result = rule_fn(row)
                if result:
                    text, confidence = result
                    cons.append({
                        "company_id": company_id,
                        "type": "Con",
                        "insight": text,
                        "confidence": round(confidence, 2),
                        "source": "Rule-Based",
                    })
            except Exception as exc:
                logger.debug("Rule %s failed for %s: %s", rule_fn.__name__, company_id, exc)

        return pros, cons

    # ------------------------------------------------------------------
    # Raw text integration
    # ------------------------------------------------------------------

    def _build_raw_lookup(self, raw_df: pd.DataFrame) -> Dict[str, Dict[str, List[str]]]:
        """
        Build a lookup: company_id -> {"pros": [...], "cons": [...]}
        from the raw prosandcons.xlsx.
        """
        lookup: Dict[str, Dict[str, List[str]]] = {}
        if raw_df.empty:
            return lookup

        for _, row in raw_df.iterrows():
            cid = str(row.get("company_id", "")).strip()
            if not cid:
                continue
            if cid not in lookup:
                lookup[cid] = {"pros": [], "cons": []}

            pro_text = str(row.get("pros", "")).strip()
            con_text = str(row.get("cons", "")).strip()
            if pro_text and pro_text.lower() != "nan":
                lookup[cid]["pros"].append(pro_text)
            if con_text and con_text.lower() != "nan":
                lookup[cid]["cons"].append(con_text)

        return lookup

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> pd.DataFrame:
        """
        Execute the full pros & cons generation pipeline.

        Returns
        -------
        Generated pros/cons DataFrame.
        """
        print("\n" + "=" * 70)
        print("PROS & CONS GENERATOR")
        print("=" * 70)

        # Load quantitative data (use peer_comparison for richest column set)
        peer_df = self._load_csv(self.peer_comparison_path, "peer_comparison.csv")
        health_df = self._load_csv(self.health_scores_path, "company_health_scores.csv")
        raw_df = self._load_raw_prosandcons()

        # Use peer_comparison as base (richest), fall back to health_scores
        if not peer_df.empty:
            base_df = peer_df.copy()
        elif not health_df.empty:
            base_df = health_df.copy()
        else:
            logger.error("No quantitative data available. Aborting.")
            return pd.DataFrame()

        # Deduplicate to one row per company (latest year)
        if "year" in base_df.columns and "company_id" in base_df.columns:
            base_df["year"] = pd.to_numeric(base_df["year"], errors="coerce")
            base_df = (
                base_df.sort_values("year", ascending=False)
                .drop_duplicates(subset=["company_id"], keep="first")
                .reset_index(drop=True)
            )

        raw_lookup = self._build_raw_lookup(raw_df)

        all_records: List[dict] = []

        for _, row in base_df.iterrows():
            pros, cons = self._apply_rules(row)
            all_records.extend(pros)
            all_records.extend(cons)

            # Append raw text insights
            cid = str(row.get("company_id", "")).strip()
            if cid in raw_lookup:
                for pro_text in raw_lookup[cid]["pros"]:
                    all_records.append({
                        "company_id": cid,
                        "type": "Pro",
                        "insight": pro_text,
                        "confidence": 0.65,  # human-written, moderate confidence
                        "source": "Raw-Text",
                    })
                for con_text in raw_lookup[cid]["cons"]:
                    all_records.append({
                        "company_id": cid,
                        "type": "Con",
                        "insight": con_text,
                        "confidence": 0.65,
                        "source": "Raw-Text",
                    })

        result_df = pd.DataFrame(all_records)
        result_df.to_csv(self.output_path, index=False)

        pros_count = (result_df["type"] == "Pro").sum() if not result_df.empty else 0
        cons_count = (result_df["type"] == "Con").sum() if not result_df.empty else 0

        print(f"  Companies processed: {base_df['company_id'].nunique()}")
        print(f"  Pros generated     : {pros_count}")
        print(f"  Cons generated     : {cons_count}")
        print(f"  Saved: {self.output_path}")
        print("Pros & Cons Generator complete.\n")

        return result_df


if __name__ == "__main__":
    gen = ProsConsGenerator()
    gen.run()
