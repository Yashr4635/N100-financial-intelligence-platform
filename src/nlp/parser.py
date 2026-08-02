"""
parser.py

Sprint 5 Module 1 — NLP text parser for the N100 Financial Intelligence Platform.

Loads textual analysis from raw Excel data, extracts structured financial
entities (CAGR, percentages, ratios, currency values, years, company
identifiers), validates parsed CAGR against independently calculated CAGR
when available, and exports results to CSV.

Inputs
------
- data/raw/analysis.xlsx
- data/raw/companies.xlsx          (company identifier validation)
- database/nifty100.db             (calculated 5Y CAGR benchmarks)
- data/output/company_health_scores.csv  (ROE validation benchmark)

Outputs
-------
- data/output/analysis_parsed.csv
- data/output/parse_failures.csv
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd

from src.utils.config import DATABASE_PATH, OUTPUT_DIR, RAW_DATA_DIR

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ANALYSIS_INPUT_PATH = RAW_DATA_DIR / "analysis.xlsx"
COMPANIES_INPUT_PATH = RAW_DATA_DIR / "companies.xlsx"
HEALTH_SCORES_PATH = OUTPUT_DIR / "company_health_scores.csv"
PARSED_OUTPUT_PATH = OUTPUT_DIR / "analysis_parsed.csv"
FAILURES_OUTPUT_PATH = OUTPUT_DIR / "parse_failures.csv"

VALIDATION_TOLERANCE_PCT = 5.0

ANALYSIS_FIELD_MAP: Dict[str, str] = {
    "compounded_sales_growth": "revenue_cagr",
    "compounded_profit_growth": "pat_cagr",
    "stock_price_cagr": "stock_cagr",
    "roe": "roe_cagr",
}

# Regex patterns
_CAGR_YEAR_PATTERN = re.compile(
    r"(\d+)\s*[Yy]ear[s]?\s*:?\s*([-]?[\d.]+)\s*%",
    re.IGNORECASE,
)
_CAGR_TTM_PATTERN = re.compile(
    r"TTM\s*:?\s*([-]?[\d.]+)\s*%",
    re.IGNORECASE,
)
_CAGR_LAST_YEAR_PATTERN = re.compile(
    r"Last\s+Year\s*:?\s*([-]?[\d.]+)\s*%",
    re.IGNORECASE,
)
_CAGR_ONE_YEAR_PATTERN = re.compile(
    r"1\s+Year\s*:?\s*([-]?[\d.]+)\s*%",
    re.IGNORECASE,
)
_PERCENTAGE_PATTERN = re.compile(
    r"([-]?[\d.]+)\s*%",
)
_RATIO_PATTERN = re.compile(
    r"([-]?[\d.]+)\s*(?:times|x)\s*(?:its\s+)?(?:book\s+value|(?:debt|equity|sales|revenue|pe|p/e|price[\s-]?to[\s-]?book)?)",
    re.IGNORECASE,
)
_RATIO_COLON_PATTERN = re.compile(
    r"([-]?[\d.]+)\s*:\s*([-]?[\d.]+)",
)
_CURRENCY_PATTERN = re.compile(
    r"(?:Rs\.?|INR|₹)\s*([-]?[\d,]+(?:\.\d+)?)\s*(?:Cr|Crore|crores|Lakh|Lac|M|mn|bn)?",
    re.IGNORECASE,
)
_CURRENCY_CR_PATTERN = re.compile(
    r"([-]?[\d,]+(?:\.\d+)?)\s*(?:Cr|Crore|crores)\b",
    re.IGNORECASE,
)
_YEAR_PATTERN = re.compile(
    r"\b(19\d{2}|20\d{2})\b",
)
_COMPANY_TICKER_PATTERN = re.compile(
    r"\b([A-Z]{2,12})\b",
)


@dataclass
class ParsedMetric:
    """A single extracted metric from financial text."""

    company_id: str
    source_column: str
    field: str
    metric_type: str
    raw_value: str
    period_label: str
    period_years: Optional[int]
    parsed_value: float
    parsed_unit: str
    validation_status: str = "Pending"
    validation_note: str = ""
    calculated_benchmark: Optional[float] = None


@dataclass
class ParseFailure:
    """A record that could not be parsed or failed validation."""

    company_id: str
    source_column: str
    field: str
    raw_value: str
    failure_reason: str
    metric_type: str = "cagr"


class TextPatternExtractor:
    """
    Regex-based extractor for financial text patterns.

    Supports CAGR strings, standalone percentages, ratios, currency
    amounts, calendar years, and company ticker identifiers.
    """

    @staticmethod
    def parse_cagr_entries(text: str) -> List[Tuple[str, Optional[int], float]]:
        """
        Extract CAGR-style (period_label, period_years, percentage) tuples.

        Handles formats such as ``10 Years: 21%``, ``TTM: 43%``,
        ``Last Year: 12%``, and ``1 Year: -2%``.
        """
        if not isinstance(text, str) or not text.strip():
            return []

        results: List[Tuple[str, Optional[int], float]] = []

        for match in _CAGR_YEAR_PATTERN.finditer(text):
            years = int(match.group(1))
            pct = float(match.group(2))
            results.append((f"{years} Years", years, pct))

        for match in _CAGR_TTM_PATTERN.finditer(text):
            results.append(("TTM", 1, float(match.group(1))))

        for match in _CAGR_LAST_YEAR_PATTERN.finditer(text):
            results.append(("Last Year", 1, float(match.group(1))))

        for match in _CAGR_ONE_YEAR_PATTERN.finditer(text):
            results.append(("1 Year", 1, float(match.group(1))))

        return results

    @staticmethod
    def parse_percentages(text: str) -> List[float]:
        """Extract standalone percentage values from text."""
        if not isinstance(text, str):
            return []
        return [float(m.group(1)) for m in _PERCENTAGE_PATTERN.finditer(text)]

    @staticmethod
    def parse_ratios(text: str) -> List[float]:
        """Extract ratio values (e.g. ``2.76 times its book value``)."""
        if not isinstance(text, str):
            return []

        ratios: List[float] = []
        for match in _RATIO_PATTERN.finditer(text):
            ratios.append(float(match.group(1)))

        for match in _RATIO_COLON_PATTERN.finditer(text):
            left, right = float(match.group(1)), float(match.group(2))
            if right != 0:
                ratios.append(round(left / right, 4))

        return ratios

    @staticmethod
    def parse_currency_values(text: str) -> List[Tuple[float, str]]:
        """
        Extract currency amounts.

        Returns list of (amount, unit) where unit is ``inr`` or ``inr_cr``.
        """
        if not isinstance(text, str):
            return []

        values: List[Tuple[float, str]] = []

        for match in _CURRENCY_PATTERN.finditer(text):
            amount = float(match.group(1).replace(",", ""))
            suffix = (match.group(0) or "").lower()
            unit = "inr_cr" if "cr" in suffix or "crore" in suffix else "inr"
            values.append((amount, unit))

        for match in _CURRENCY_CR_PATTERN.finditer(text):
            amount = float(match.group(1).replace(",", ""))
            values.append((amount, "inr_cr"))

        return values

    @staticmethod
    def parse_years(text: str) -> List[int]:
        """Extract four-digit calendar years from text."""
        if not isinstance(text, str):
            return []
        return [int(m.group(1)) for m in _YEAR_PATTERN.finditer(text)]

    @staticmethod
    def parse_company_identifiers(
        text: str,
        known_companies: Optional[Sequence[str]] = None,
    ) -> List[str]:
        """
        Extract company ticker identifiers from text.

        When *known_companies* is supplied, only recognised tickers are
        returned; otherwise all uppercase tokens of 2–12 characters are
        returned.
        """
        if not isinstance(text, str):
            return []

        known = {c.upper() for c in known_companies} if known_companies else None
        found: List[str] = []

        for match in _COMPANY_TICKER_PATTERN.finditer(text):
            token = match.group(1).upper()
            if known is None or token in known:
                if token not in found:
                    found.append(token)

        return found


class CalculatedCAGRValidator:
    """
    Loads independently calculated CAGR benchmarks for validation.

    Reads 5-year revenue/PAT CAGR from the warehouse via the ratio
    calculator, and ROE from company health scores.
    """

    def __init__(
        self,
        health_scores_path: Path = HEALTH_SCORES_PATH,
        database_path: Path = DATABASE_PATH,
    ) -> None:
        self.health_scores_path = health_scores_path
        self.database_path = database_path
        self._growth_lookup: Dict[str, Dict[str, Optional[float]]] = {}
        self._roe_lookup: Dict[str, float] = {}

    def load(self) -> None:
        """Load calculated CAGR and ROE benchmarks."""
        self._load_growth_metrics()
        self._load_roe_benchmarks()

    def _load_growth_metrics(self) -> None:
        """Compute 5Y revenue and PAT CAGR per company from the warehouse."""
        if not self.database_path.exists():
            logger.warning("Database not found at '%s'.", self.database_path)
            return

        try:
            from src.analytics.ratio_calculator import RatioCalculator

            calculator = RatioCalculator()
            try:
                merged = calculator._load_and_merge()
                growth_df = calculator.calculate_growth_metrics(merged)
            finally:
                calculator.close()

            for _, row in growth_df.iterrows():
                company_id = str(row["company_id"]).strip()
                self._growth_lookup[company_id] = {
                    "revenue_cagr": _safe_float(row.get("revenue_cagr_5y")),
                    "pat_cagr": _safe_float(row.get("pat_cagr_5y")),
                }

            logger.info(
                "Loaded calculated CAGR benchmarks for %d companies.",
                len(self._growth_lookup),
            )
        except Exception as exc:
            logger.error("Failed to load growth metrics: %s", exc)

    def _load_roe_benchmarks(self) -> None:
        """Load latest ROE per company from health scores."""
        if not self.health_scores_path.exists():
            logger.warning(
                "Health scores not found at '%s'.", self.health_scores_path
            )
            return

        try:
            health_df = pd.read_csv(self.health_scores_path)
            latest = (
                health_df.sort_values("year", ascending=False)
                .drop_duplicates(subset=["company_id"], keep="first")
            )
            for _, row in latest.iterrows():
                roe = _safe_float(row.get("return_on_equity_pct"))
                if roe is not None:
                    self._roe_lookup[str(row["company_id"]).strip()] = roe

            logger.info(
                "Loaded ROE benchmarks for %d companies.", len(self._roe_lookup)
            )
        except Exception as exc:
            logger.error("Failed to load health scores: %s", exc)

    def resolve_benchmark(
        self,
        company_id: str,
        field: str,
        period_years: Optional[int],
    ) -> Optional[float]:
        """
        Return the calculated benchmark for a parsed CAGR field.

        5-year revenue and PAT CAGR are compared against ratio-engine
        outputs; ROE uses the latest health-score ROE regardless of period.
        """
        company_id = company_id.strip()

        if field == "roe_cagr":
            return self._roe_lookup.get(company_id)

        if period_years == 5 and company_id in self._growth_lookup:
            return self._growth_lookup[company_id].get(field)

        return None

    def validate(
        self,
        company_id: str,
        field: str,
        parsed_pct: float,
        period_years: Optional[int],
    ) -> Tuple[str, str, Optional[float]]:
        """
        Validate a parsed CAGR against calculated benchmarks.

        Returns
        -------
        (validation_status, validation_note, calculated_benchmark)
        """
        benchmark = self.resolve_benchmark(company_id, field, period_years)

        if benchmark is None:
            return (
                "Unverified – no calculated benchmark",
                "Calculated value not available for comparison",
                None,
            )

        diff = abs(parsed_pct - benchmark)
        if diff <= VALIDATION_TOLERANCE_PCT:
            return (
                "Validated",
                f"Parsed={parsed_pct:.1f}%, Calc={benchmark:.1f}%, diff={diff:.1f}%",
                benchmark,
            )

        return (
            "Mismatch",
            (
                f"Parsed={parsed_pct:.1f}%, Calc={benchmark:.1f}%, diff={diff:.1f}% "
                f"(tolerance={VALIDATION_TOLERANCE_PCT}%)"
            ),
            benchmark,
        )


class AnalysisTextParser:
    """
    End-to-end parser for the analysis textual dataset.

    Loads raw analysis rows, extracts structured metrics, validates CAGR
    against calculated benchmarks, and exports parsed/failure CSVs.

    Attributes
    ----------
    parsed_df : pd.DataFrame
        Successfully parsed records.
    failures_df : pd.DataFrame
        Records that failed parsing or validation.
    """

    def __init__(
        self,
        analysis_path: Optional[Path] = None,
        companies_path: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ) -> None:
        self.analysis_path = analysis_path or ANALYSIS_INPUT_PATH
        self.companies_path = companies_path or COMPANIES_INPUT_PATH
        self.output_dir = output_dir or OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.parsed_output_path = self.output_dir / "analysis_parsed.csv"
        self.failures_output_path = self.output_dir / "parse_failures.csv"

        self.extractor = TextPatternExtractor()
        self.validator = CalculatedCAGRValidator()

        self.parsed_df: pd.DataFrame = pd.DataFrame()
        self.failures_df: pd.DataFrame = pd.DataFrame()
        self._known_companies: List[str] = []

    def load_analysis(self) -> pd.DataFrame:
        """Load the raw analysis Excel file (header row 1)."""
        if not self.analysis_path.exists():
            logger.error("Analysis file not found: '%s'.", self.analysis_path)
            return pd.DataFrame()

        try:
            df = pd.read_excel(self.analysis_path, header=1)
            df.columns = [
                str(c).strip().lower().replace(" ", "_") for c in df.columns
            ]
            logger.info("Loaded analysis data: %d rows.", len(df))
            return df
        except Exception as exc:
            logger.error("Failed to load analysis.xlsx: %s", exc)
            return pd.DataFrame()

    def load_known_companies(self) -> List[str]:
        """Load valid company identifiers from companies.xlsx."""
        if not self.companies_path.exists():
            logger.warning(
                "Companies file not found at '%s'.", self.companies_path
            )
            return []

        try:
            df = pd.read_excel(self.companies_path, header=1)
            df.columns = [
                str(c).strip().lower().replace(" ", "_") for c in df.columns
            ]
            col = "company_id" if "company_id" in df.columns else df.columns[0]
            companies = [
                str(v).strip()
                for v in df[col].dropna().unique()
                if str(v).strip()
            ]
            logger.info("Loaded %d known company identifiers.", len(companies))
            return companies
        except Exception as exc:
            logger.error("Failed to load companies.xlsx: %s", exc)
            return []

    def _validate_company_id(self, company_id: str) -> bool:
        """Return True if *company_id* exists in the master company list."""
        if not self._known_companies:
            return True
        return company_id.strip().upper() in {
            c.upper() for c in self._known_companies
        }

    def _parse_row(
        self,
        row: pd.Series,
        parsed: List[ParsedMetric],
        failures: List[ParseFailure],
    ) -> None:
        """Parse all text columns in a single analysis row."""
        company_id = str(row.get("company_id", "")).strip()
        company_valid = self._validate_company_id(company_id)

        if company_id and not company_valid:
            failures.append(
                ParseFailure(
                    company_id=company_id,
                    source_column="company_id",
                    field="company_id",
                    raw_value=company_id,
                    failure_reason="Unknown company identifier",
                    metric_type="company_id",
                )
            )

        text_columns = [c for c in row.index if c in ANALYSIS_FIELD_MAP]

        for col in text_columns:
            raw_value = row.get(col, "")
            raw_text = "" if pd.isna(raw_value) else str(raw_value)
            field_name = ANALYSIS_FIELD_MAP[col]

            cagr_entries = self.extractor.parse_cagr_entries(raw_text)
            if cagr_entries:
                for period_label, period_years, pct in cagr_entries:
                    status, note, benchmark = self.validator.validate(
                        company_id, field_name, pct, period_years
                    )
                    parsed.append(
                        ParsedMetric(
                            company_id=company_id,
                            source_column=col,
                            field=field_name,
                            metric_type="cagr",
                            raw_value=raw_text,
                            period_label=period_label,
                            period_years=period_years,
                            parsed_value=pct,
                            parsed_unit="pct",
                            validation_status=status,
                            validation_note=note,
                            calculated_benchmark=benchmark,
                        )
                    )
            else:
                failures.append(
                    ParseFailure(
                        company_id=company_id,
                        source_column=col,
                        field=field_name,
                        raw_value=raw_text,
                        failure_reason="No CAGR pattern matched",
                        metric_type="cagr",
                    )
                )

            for pct in self.extractor.parse_percentages(raw_text):
                parsed.append(
                    ParsedMetric(
                        company_id=company_id,
                        source_column=col,
                        field=field_name,
                        metric_type="percentage",
                        raw_value=raw_text,
                        period_label="",
                        period_years=None,
                        parsed_value=pct,
                        parsed_unit="pct",
                        validation_status="N/A",
                        validation_note="Standalone percentage extraction",
                    )
                )

            for ratio in self.extractor.parse_ratios(raw_text):
                parsed.append(
                    ParsedMetric(
                        company_id=company_id,
                        source_column=col,
                        field=field_name,
                        metric_type="ratio",
                        raw_value=raw_text,
                        period_label="",
                        period_years=None,
                        parsed_value=ratio,
                        parsed_unit="ratio",
                        validation_status="N/A",
                        validation_note="Ratio extraction",
                    )
                )

            for amount, unit in self.extractor.parse_currency_values(raw_text):
                parsed.append(
                    ParsedMetric(
                        company_id=company_id,
                        source_column=col,
                        field=field_name,
                        metric_type="currency",
                        raw_value=raw_text,
                        period_label="",
                        period_years=None,
                        parsed_value=amount,
                        parsed_unit=unit,
                        validation_status="N/A",
                        validation_note="Currency extraction",
                    )
                )

            for year in self.extractor.parse_years(raw_text):
                parsed.append(
                    ParsedMetric(
                        company_id=company_id,
                        source_column=col,
                        field=field_name,
                        metric_type="year",
                        raw_value=raw_text,
                        period_label=str(year),
                        period_years=year,
                        parsed_value=float(year),
                        parsed_unit="year",
                        validation_status="N/A",
                        validation_note="Year extraction",
                    )
                )

            for ticker in self.extractor.parse_company_identifiers(
                raw_text, self._known_companies or None
            ):
                if ticker != company_id.upper():
                    parsed.append(
                        ParsedMetric(
                            company_id=company_id,
                            source_column=col,
                            field=field_name,
                            metric_type="company_id",
                            raw_value=raw_text,
                            period_label=ticker,
                            period_years=None,
                            parsed_value=0.0,
                            parsed_unit="ticker",
                            validation_status="Validated",
                            validation_note=f"Recognised ticker: {ticker}",
                        )
                    )

    def parse(self, analysis_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Parse all rows in the analysis dataframe.

        Returns
        -------
        (parsed_df, failures_df)
        """
        parsed_records: List[ParsedMetric] = []
        failure_records: List[ParseFailure] = []

        for _, row in analysis_df.iterrows():
            self._parse_row(row, parsed_records, failure_records)

        parsed_df = _metrics_to_dataframe(parsed_records)
        failures_df = _failures_to_dataframe(failure_records)

        if not parsed_df.empty:
            mismatch_mask = parsed_df["validation_status"] == "Mismatch"
            if mismatch_mask.any():
                mismatch_failures = _mismatch_to_failures(
                    parsed_df.loc[mismatch_mask]
                )
                if failures_df.empty:
                    failures_df = mismatch_failures
                else:
                    failures_df = pd.concat(
                        [failures_df.reset_index(drop=True),
                         mismatch_failures.reset_index(drop=True)],
                        ignore_index=True,
                    )
                parsed_df = parsed_df.loc[~mismatch_mask].reset_index(drop=True)

        return parsed_df, failures_df

    def export(
        self,
        parsed_df: pd.DataFrame,
        failures_df: pd.DataFrame,
    ) -> None:
        """Write parsed and failure records to CSV."""
        parsed_df.to_csv(self.parsed_output_path, index=False)
        failures_df.to_csv(self.failures_output_path, index=False)
        logger.info("Exported %s", self.parsed_output_path)
        logger.info("Exported %s", self.failures_output_path)

    def run(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Execute the full NLP parsing pipeline.

        Returns
        -------
        (parsed_df, failures_df)
        """
        print("\n" + "=" * 70)
        print("NLP PARSER (Sprint 5 Module 1)")
        print("=" * 70)

        self._known_companies = self.load_known_companies()
        analysis_df = self.load_analysis()

        if analysis_df.empty:
            logger.error("No analysis data to parse. Aborting.")
            self.parsed_df = pd.DataFrame()
            self.failures_df = pd.DataFrame()
            return self.parsed_df, self.failures_df

        self.validator.load()
        parsed_df, failures_df = self.parse(analysis_df)
        self.export(parsed_df, failures_df)

        self.parsed_df = parsed_df
        self.failures_df = failures_df

        print(f"  Parsed records    : {len(parsed_df)}")
        print(f"  Failures/mismatches: {len(failures_df)}")
        print(f"  Saved: {self.parsed_output_path}")
        print(f"  Saved: {self.failures_output_path}")
        print("NLP Parser complete.\n")

        return parsed_df, failures_df


# Backward-compatible alias used by existing Sprint 5 runners.
NLPParser = AnalysisTextParser


def _safe_float(value: object) -> Optional[float]:
    """Convert a value to float, returning None on failure or NaN."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        result = float(value)
        if pd.isna(result):
            return None
        return result
    except (TypeError, ValueError):
        return None


def _metrics_to_dataframe(metrics: List[ParsedMetric]) -> pd.DataFrame:
    """Convert ParsedMetric objects to a flat DataFrame."""
    if not metrics:
        return pd.DataFrame()

    records = [
        {
            "company_id": m.company_id,
            "source_column": m.source_column,
            "field": m.field,
            "metric_type": m.metric_type,
            "raw_value": m.raw_value,
            "period_label": m.period_label,
            "period_years": m.period_years,
            "parsed_value": m.parsed_value,
            "parsed_unit": m.parsed_unit,
            "validation_status": m.validation_status,
            "validation_note": m.validation_note,
            "calculated_benchmark": m.calculated_benchmark,
        }
        for m in metrics
    ]
    return pd.DataFrame(records)


def _failures_to_dataframe(failures: List[ParseFailure]) -> pd.DataFrame:
    """Convert ParseFailure objects to a flat DataFrame."""
    if not failures:
        return pd.DataFrame()

    records = [
        {
            "company_id": f.company_id,
            "source_column": f.source_column,
            "field": f.field,
            "raw_value": f.raw_value,
            "failure_reason": f.failure_reason,
            "metric_type": f.metric_type,
        }
        for f in failures
    ]
    return pd.DataFrame(records)


def _mismatch_to_failures(mismatch_df: pd.DataFrame) -> pd.DataFrame:
    """Convert validation mismatch rows to failure schema."""
    return pd.DataFrame(
        {
            "company_id": mismatch_df["company_id"].values,
            "source_column": mismatch_df["source_column"].values,
            "field": mismatch_df["field"].values,
            "raw_value": mismatch_df["raw_value"].values,
            "failure_reason": mismatch_df["validation_note"].values,
            "metric_type": mismatch_df["metric_type"].values,
        }
    )


def _configure_logging() -> None:
    """Configure module-level logging when run as a script."""
    if not logger.handlers and not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )


if __name__ == "__main__":
    _configure_logging()
    parser = AnalysisTextParser()
    parser.run()
