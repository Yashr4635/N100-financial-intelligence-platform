"""
N100 Financial Intelligence Platform
Sprint 3 – Growth Metrics

Module: Growth Analysis

Implements 5-Year CAGR wrappers for:
- Revenue
- PAT (Profit After Tax)
- EPS

This module does NOT duplicate CAGR math. It reuses the
generic/specific calculators defined in src.analytics.cagr
and is responsible only for:
- Validating a 5-year (6 data point) historical series
- Extracting start/end values
- Delegating the actual CAGR computation
"""

from collections.abc import Sequence as ABCSequence
from typing import List, Optional, Sequence

from src.analytics.cagr import (
    calculate_revenue_cagr,
    calculate_pat_cagr,
    calculate_eps_cagr,
)

# 5-year CAGR requires 6 yearly data points (Year 0 ... Year 5)
REQUIRED_YEARS: int = 5
REQUIRED_DATA_POINTS: int = REQUIRED_YEARS + 1


def _validate_series(values: Sequence[float]) -> Optional[List[float]]:
    """
    Validate a historical value series for 5-year CAGR computation.

    Ensures the input is a proper sequence of numeric values with
    enough data points to cover a 5-year span, and that none of the
    values are missing or non-numeric.

    Args:
        values: Sequence of yearly financial values, ordered oldest
            to newest (e.g. [Y0, Y1, Y2, Y3, Y4, Y5]).

    Returns:
        A list of validated float values if the series is usable,
        otherwise None.
    """
    if values is None:
        return None

    if not isinstance(values, ABCSequence) or isinstance(values, (str, bytes)):
        return None

    if len(values) < REQUIRED_DATA_POINTS:
        return None

    validated: List[float] = []
    for item in values:
        if item is None:
            return None
        if isinstance(item, bool):
            return None
        if not isinstance(item, (int, float)):
            return None
        validated.append(float(item))

    return validated


def calculate_5y_revenue_cagr(
    revenue_history: Sequence[float]
) -> Optional[float]:
    """
    Calculate 5-Year Revenue CAGR from a historical revenue series.

    Args:
        revenue_history: Yearly revenue values ordered oldest to
            newest, requiring at least 6 data points (Y0 to Y5).

    Returns:
        Revenue CAGR percentage rounded to 2 decimals, or None if
        the calculation cannot be performed (missing data, invalid
        input, insufficient history, or non-positive start value).
    """
    series = _validate_series(revenue_history)
    if series is None:
        return None

    start_sales = series[0]
    end_sales = series[-1]

    return calculate_revenue_cagr(start_sales, end_sales, REQUIRED_YEARS)


def calculate_5y_pat_cagr(
    pat_history: Sequence[float]
) -> Optional[float]:
    """
    Calculate 5-Year PAT (Profit After Tax) CAGR from a historical
    PAT series.

    Args:
        pat_history: Yearly PAT values ordered oldest to newest,
            requiring at least 6 data points (Y0 to Y5).

    Returns:
        PAT CAGR percentage rounded to 2 decimals, or None if the
        calculation cannot be performed (missing data, invalid
        input, insufficient history, or non-positive start value).
    """
    series = _validate_series(pat_history)
    if series is None:
        return None

    start_pat = series[0]
    end_pat = series[-1]

    return calculate_pat_cagr(start_pat, end_pat, REQUIRED_YEARS)


def calculate_5y_eps_cagr(
    eps_history: Sequence[float]
) -> Optional[float]:
    """
    Calculate 5-Year EPS CAGR from a historical EPS series.

    Args:
        eps_history: Yearly EPS values ordered oldest to newest,
            requiring at least 6 data points (Y0 to Y5).

    Returns:
        EPS CAGR percentage rounded to 2 decimals, or None if the
        calculation cannot be performed (missing data, invalid
        input, insufficient history, or non-positive start value).
    """
    series = _validate_series(eps_history)
    if series is None:
        return None

    start_eps = series[0]
    end_eps = series[-1]

    return calculate_eps_cagr(start_eps, end_eps, REQUIRED_YEARS)