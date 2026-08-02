"""
nlp_parser.py

Sprint 5 – NLP Parser for the N100 Financial Intelligence Platform.

Parses structured financial text (e.g. "10 Years: 21%") from the
``analysis`` dataset using regex, extracts CAGR figures, and validates
them against the independently calculated CAGR values from the ETL
pipeline.

Inputs
------
- data/raw/analysis.xlsx          (raw text fields with CAGR strings)
- data/output/company_health_scores.csv  (calculated ratios for validation)

Outputs
-------
- data/output/analysis_parsed.csv    – successfully parsed & validated rows
- data/output/parse_failures.csv     – rows that failed parsing or validation

Design
------
Each cell in the analysis table looks like:
    "10 Years: 21%"  /  "5 Years:       24%"  /  "3 Years: 18%"
The regex extracts (period_label, years, percentage) tuples.
Validation compares the parsed CAGR against the calculated CAGR from the
ratio engine (±3 % tolerance), flagging large discrepancies.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ANALYSIS_INPUT_PATH = os.path.join("data", "raw", "analysis.xlsx")
HEALTH_SCORES_PATH = os.path.join("data", "output", "company_health_scores.csv")
OUTPUT_DIR = os.path.join("data", "output")
PARSED_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "analysis_parsed.csv")
FAILURES_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "parse_failures.csv")

# Regex: captures "10 Years: 21%" / "5 Years :  6%" / "3 Years:18%"
_CAGR_PATTERN = re.compile(
    r"(\d+)\s*[Yy]ear[s]?\s*:?\s*([\d.]+)\s*%",
    re.IGNORECASE,
)

# Validation tolerance in percentage points
VALIDATION_TOLERANCE_PCT = 5.0

# Column name -> canonical field name mapping
ANALYSIS_FIELD_MAP: Dict[str, str] = {
    "compounded_sales_growth": "revenue_cagr",
    "compounded_profit_growth": "pat_cagr",
    "stock_price_cagr": "stock_cagr",
    "roe": "roe_cagr",
}


class NLPParser:
    """
    Parses structured financial text from the analysis dataset and
    validates the extracted CAGR values against calculated ratios.

    Attributes
    ----------
    parsed_df : pd.DataFrame
        Successfully parsed records after validation.
    failures_df : pd.DataFrame
        Records that failed parsing or validation.
    """

    def __init__(
        self,
        analysis_path: Optional[str] = None,
        health_scores_path: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> None:
        self.analysis_path = analysis_path or ANALYSIS_INPUT_PATH
        self.health_scores_path = health_scores_path or HEALTH_SCORES_PATH
        self.output_dir = output_dir or OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        self.parsed_output_path = os.path.join(self.output_dir, "analysis_parsed.csv")
        self.failures_output_path = os.path.join(self.output_dir, "parse_failures.csv")

        self.parsed_df: pd.DataFrame = pd.DataFrame()
        self.failures_df: pd.DataFrame = pd.DataFrame()

    # ------------------------------------------------------------------
    # Loading helpers
    # ------------------------------------------------------------------

    def _load_analysis(self) -> pd.DataFrame:
        """Load the raw analysis Excel file (header row 1)."""
        if not os.path.exists(self.analysis_path):
            logger.warning("analysis.xlsx not found at '%s'.", self.analysis_path)
            return pd.DataFrame()
        try:
            df = pd.read_excel(self.analysis_path, header=1)
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            logger.info("Loaded analysis data: %d rows.", len(df))
            return df
        except Exception as exc:
            logger.error("Failed to load analysis.xlsx: %s", exc)
            return pd.DataFrame()

    def _load_health_scores(self) -> pd.DataFrame:
        """Load company health scores (already calculated CAGR values)."""
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

    # ------------------------------------------------------------------
    # Parsing logic
    # ------------------------------------------------------------------

    @staticmethod
    def parse_cagr_text(text: str) -> List[Tuple[int, float]]:
        """
        Extract all (years, percentage) pairs from a CAGR text string.

        Parameters
        ----------
        text : str
            Raw cell value such as "10 Years: 21%" or "5 Years: 24%".

        Returns
        -------
        List of (years: int, pct: float) tuples. Empty list on no match.
        """
        if not isinstance(text, str):
            return []
        matches = _CAGR_PATTERN.findall(text)
        result = []
        for years_str, pct_str in matches:
            try:
                result.append((int(years_str), float(pct_str)))
            except ValueError:
                continue
        return result

    def _parse_analysis_df(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Iterate over each row/field, parse CAGR text, and collect
        successful parses and failures.

        Returns
        -------
        (parsed_records_df, failures_df)
        """
        parsed_records: List[dict] = []
        failure_records: List[dict] = []

        text_cols = [c for c in df.columns if c in ANALYSIS_FIELD_MAP]

        for _, row in df.iterrows():
            company_id = str(row.get("company_id", "")).strip()
            row_parsed_any = False

            for col in text_cols:
                raw_value = row.get(col, "")
                field_name = ANALYSIS_FIELD_MAP[col]
                pairs = self.parse_cagr_text(str(raw_value))

                if not pairs:
                    failure_records.append({
                        "company_id": company_id,
                        "field": field_name,
                        "raw_value": raw_value,
                        "failure_reason": "No CAGR pattern matched",
                    })
                    continue

                for years, pct in pairs:
                    parsed_records.append({
                        "company_id": company_id,
                        "field": field_name,
                        "raw_value": raw_value,
                        "period_years": years,
                        "parsed_cagr_pct": pct,
                        "validation_status": "Pending",
                        "validation_note": "",
                    })
                    row_parsed_any = True

            if not row_parsed_any and not text_cols:
                failure_records.append({
                    "company_id": company_id,
                    "field": "ALL",
                    "raw_value": "",
                    "failure_reason": "No text columns found",
                })

        parsed_df = pd.DataFrame(parsed_records)
        failures_df = pd.DataFrame(failure_records)
        return parsed_df, failures_df

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_against_calculated(
        self,
        parsed_df: pd.DataFrame,
        health_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Validate parsed CAGR values against the calculated ones from the
        health scores / ratio engine. Uses a ±VALIDATION_TOLERANCE_PCT
        tolerance. Updates 'validation_status' and 'validation_note'.

        Parameters
        ----------
        parsed_df : pd.DataFrame
            Records with 'parsed_cagr_pct' columns.
        health_df : pd.DataFrame
            company_health_scores.csv with calculated metrics.

        Returns
        -------
        parsed_df with validation columns populated.
        """
        if parsed_df.empty or health_df.empty:
            if not parsed_df.empty:
                parsed_df["validation_status"] = "Skipped – no calculated data"
            return parsed_df

        # Build a lookup: company_id -> latest row
        health_latest = (
            health_df
            .sort_values("year", ascending=False)
            .drop_duplicates(subset=["company_id"], keep="first")
            .set_index("company_id")
        )

        # Candidate calculated columns for each field
        field_to_calc_cols: Dict[str, List[str]] = {
            "revenue_cagr": ["revenue_cagr_5y", "revenue_cagr"],
            "pat_cagr": ["pat_cagr_5y", "pat_cagr"],
            "stock_cagr": ["stock_price_cagr"],
            "roe_cagr": ["return_on_equity_pct", "roe_percentile"],
        }

        def _resolve_calc_val(company: str, field: str) -> Optional[float]:
            if company not in health_latest.index:
                return None
            row = health_latest.loc[company]
            for col in field_to_calc_cols.get(field, []):
                val = row.get(col) if isinstance(row, pd.Series) else None
                if val is not None and not (isinstance(val, float) and pd.isna(val)):
                    try:
                        return float(val)
                    except (ValueError, TypeError):
                        continue
            return None

        statuses, notes = [], []
        for _, rec in parsed_df.iterrows():
            calc = _resolve_calc_val(rec["company_id"], rec["field"])
            parsed = rec["parsed_cagr_pct"]

            if calc is None:
                statuses.append("Unverified – no calculated benchmark")
                notes.append("Calculated value not available for comparison")
            else:
                diff = abs(parsed - calc)
                if diff <= VALIDATION_TOLERANCE_PCT:
                    statuses.append("Validated")
                    notes.append(f"Parsed={parsed:.1f}%, Calc={calc:.1f}%, diff={diff:.1f}%")
                else:
                    statuses.append("Mismatch")
                    notes.append(
                        f"Parsed={parsed:.1f}%, Calc={calc:.1f}%, diff={diff:.1f}% "
                        f"(tolerance={VALIDATION_TOLERANCE_PCT}%)"
                    )

        parsed_df = parsed_df.copy()
        parsed_df["validation_status"] = statuses
        parsed_df["validation_note"] = notes
        return parsed_df

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Execute the full NLP parsing pipeline:
        1. Load raw analysis text data.
        2. Parse CAGR values using regex.
        3. Validate against calculated benchmarks.
        4. Save parsed and failure CSVs.

        Returns
        -------
        (parsed_df, failures_df)
        """
        print("\n" + "=" * 70)
        print("NLP PARSER")
        print("=" * 70)

        analysis_df = self._load_analysis()
        if analysis_df.empty:
            logger.error("No analysis data to parse. Aborting.")
            self.parsed_df = pd.DataFrame()
            self.failures_df = pd.DataFrame()
            return self.parsed_df, self.failures_df

        health_df = self._load_health_scores()

        parsed_df, failures_df = self._parse_analysis_df(analysis_df)
        logger.info("Parsed %d records; %d failures before validation.", len(parsed_df), len(failures_df))

        if not parsed_df.empty:
            parsed_df = self._validate_against_calculated(parsed_df, health_df)

            # Move Mismatch rows to failures
            mismatch_mask = parsed_df["validation_status"] == "Mismatch"
            if mismatch_mask.any():
                mismatch_rows = parsed_df[mismatch_mask].rename(
                    columns={"validation_note": "failure_reason"}
                ).drop(columns=["validation_status"], errors="ignore")
                failures_df = pd.concat([failures_df, mismatch_rows], ignore_index=True)
                parsed_df = parsed_df[~mismatch_mask].reset_index(drop=True)

        # Save outputs
        parsed_df.to_csv(self.parsed_output_path, index=False)
        failures_df.to_csv(self.failures_output_path, index=False)

        self.parsed_df = parsed_df
        self.failures_df = failures_df

        print(f"  Parsed records   : {len(parsed_df)}")
        print(f"  Failures/mismatches: {len(failures_df)}")
        print(f"  Saved: {self.parsed_output_path}")
        print(f"  Saved: {self.failures_output_path}")
        print("NLP Parser complete.\n")

        return parsed_df, failures_df


if __name__ == "__main__":
    parser = NLPParser()
    parser.run()
