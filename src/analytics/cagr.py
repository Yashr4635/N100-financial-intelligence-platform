"""
N100 Financial Intelligence Platform
Sprint 2 – Financial Ratio Engine

Module: CAGR Metrics

Implements:
- Generic CAGR Calculator
- Revenue CAGR
- PAT CAGR
- EPS CAGR
"""

from typing import Optional


def calculate_cagr(
    start_value: float,
    end_value: float,
    years: int
) -> Optional[float]:
    """
    Generic CAGR calculator.

    Formula:
        ((End / Start) ** (1 / Years) - 1) * 100

    Returns
    -------
    float
        CAGR percentage rounded to 2 decimals.

    Returns None for all edge cases.
    """

    if (
        start_value is None or
        end_value is None or
        years is None
    ):
        return None

    if years <= 0:
        return None

    # Sprint edge cases
    if start_value <= 0:
        return None

    if end_value < 0:
        return None

    try:
        cagr = ((end_value / start_value) ** (1 / years) - 1) * 100
        return round(cagr, 2)

    except Exception:
        return None


def calculate_revenue_cagr(
    start_sales: float,
    end_sales: float,
    years: int
) -> Optional[float]:
    """
    Revenue CAGR.
    """
    return calculate_cagr(
        start_sales,
        end_sales,
        years
    )


def calculate_pat_cagr(
    start_pat: float,
    end_pat: float,
    years: int
) -> Optional[float]:
    """
    Profit After Tax CAGR.
    """
    return calculate_cagr(
        start_pat,
        end_pat,
        years
    )


def calculate_eps_cagr(
    start_eps: float,
    end_eps: float,
    years: int
) -> Optional[float]:
    """
    EPS CAGR.
    """
    return calculate_cagr(
        start_eps,
        end_eps,
        years
    )