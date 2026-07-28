"""
N100 Financial Intelligence Platform
Sprint 2 – Financial Ratio Engine

Module: Leverage & Efficiency Ratios

Implements:
- Debt to Equity Ratio
- Interest Coverage Ratio
- Debt Free Label
- High Leverage Flag
- Net Debt
- Asset Turnover
"""

from typing import Optional


def calculate_debt_to_equity(
    borrowings: float,
    equity_capital: float,
    reserves: float
) -> Optional[float]:
    """
    Debt to Equity Ratio

    Formula:
        Borrowings / (Equity + Reserves)
    """

    if (
        borrowings is None or
        equity_capital is None or
        reserves is None
    ):
        return None

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round(borrowings / equity, 2)


def calculate_interest_coverage(
    operating_profit: float,
    other_income: float,
    interest: float
) -> Optional[float]:
    """
    Interest Coverage Ratio

    Formula:
        (Operating Profit + Other Income) / Interest
    """

    if (
        operating_profit is None or
        other_income is None or
        interest is None
    ):
        return None

    if interest <= 0:
        return None

    return round((operating_profit + other_income) / interest, 2)


def calculate_net_debt(
    borrowings: float,
    investments: float
) -> Optional[float]:
    """
    Net Debt

    Formula:
        Borrowings - Investments
    """

    if borrowings is None or investments is None:
        return None

    return round(borrowings - investments, 2)


def calculate_asset_turnover(
    sales: float,
    total_assets: float
) -> Optional[float]:
    """
    Asset Turnover

    Formula:
        Sales / Total Assets
    """

    if sales is None or total_assets is None:
        return None

    if total_assets <= 0:
        return None

    return round(sales / total_assets, 2)


def is_debt_free(
    borrowings: float
) -> bool:
    """
    Returns True if company has no debt.
    """

    if borrowings is None:
        return False

    return borrowings == 0


def is_high_leverage(
    debt_equity_ratio: float,
    sector: str
) -> bool:
    """
    High leverage flag.

    Sprint Requirement:
    Ignore Financial sector.
    High leverage if D/E > 5.
    """

    if debt_equity_ratio is None:
        return False

    if sector is None:
        return False

    if sector.strip().lower() == "financials":
        return False

    return debt_equity_ratio > 5