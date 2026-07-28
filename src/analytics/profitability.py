"""
N100 Financial Intelligence Platform
Sprint 2 – Financial Ratio Engine

Module: Profitability Ratios

Implements:
- Net Profit Margin
- Operating Profit Margin
- Return on Equity (ROE)
- Return on Capital Employed (ROCE)
- Return on Assets (ROA)
"""

from typing import Optional


def calculate_net_profit_margin(
    net_profit: float,
    sales: float
) -> Optional[float]:
    """
    Calculate Net Profit Margin.

    Formula:
        (Net Profit / Sales) * 100

    Returns:
        Percentage value rounded to 2 decimals.
        Returns None if sales is missing or less than or equal to zero.
    """

    if sales is None or sales <= 0:
        return None

    if net_profit is None:
        return None

    return round((net_profit / sales) * 100, 2)


def calculate_operating_profit_margin(
    operating_profit: float,
    sales: float
) -> Optional[float]:
    """
    Calculate Operating Profit Margin.

    Formula:
        (Operating Profit / Sales) * 100

    Returns:
        Percentage value rounded to 2 decimals.
        Returns None if sales is missing or less than or equal to zero.
    """

    if sales is None or sales <= 0:
        return None

    if operating_profit is None:
        return None

    return round((operating_profit / sales) * 100, 2)


def calculate_roe(
    net_profit: float,
    equity_capital: float,
    reserves: float
) -> Optional[float]:
    """
    Calculate Return on Equity (ROE).

    Formula:
        (Net Profit / (Equity Capital + Reserves)) * 100

    Returns:
        ROE percentage rounded to 2 decimals.
        Returns None if Equity + Reserves <= 0.
    """

    if (
        net_profit is None or
        equity_capital is None or
        reserves is None
    ):
        return None

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return round((net_profit / equity) * 100, 2)


def calculate_roce(
    ebit: float,
    equity_capital: float,
    reserves: float,
    borrowings: float
) -> Optional[float]:
    """
    Calculate Return on Capital Employed (ROCE).

    Formula:
        (EBIT / (Equity + Reserves + Borrowings)) * 100

    Returns:
        ROCE percentage rounded to 2 decimals.
        Returns None if Capital Employed <= 0.
    """

    if (
        ebit is None or
        equity_capital is None or
        reserves is None or
        borrowings is None
    ):
        return None

    capital_employed = equity_capital + reserves + borrowings

    if capital_employed <= 0:
        return None

    return round((ebit / capital_employed) * 100, 2)


def calculate_roa(
    net_profit: float,
    total_assets: float
) -> Optional[float]:
    """
    Calculate Return on Assets (ROA).

    Formula:
        (Net Profit / Total Assets) * 100

    Returns:
        ROA percentage rounded to 2 decimals.
        Returns None if Total Assets <= 0.
    """

    if net_profit is None or total_assets is None:
        return None

    if total_assets <= 0:
        return None

    return round((net_profit / total_assets) * 100, 2)