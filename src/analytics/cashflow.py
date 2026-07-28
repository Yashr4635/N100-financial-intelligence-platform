"""
N100 Financial Intelligence Platform
Sprint 2 – Financial Ratio Engine

Module: Cash Flow KPIs

Implements:
- Free Cash Flow
- Operating Cash Flow Ratio
- Cash Conversion Ratio
"""

from typing import Optional


def calculate_free_cash_flow(
    operating_cash_flow: float,
    capital_expenditure: float
) -> Optional[float]:
    """
    Free Cash Flow

    Formula:
        Operating Cash Flow - Capital Expenditure
    """

    if operating_cash_flow is None or capital_expenditure is None:
        return None

    return round(
        operating_cash_flow - capital_expenditure,
        2
    )


def calculate_operating_cash_flow_ratio(
    operating_cash_flow: float,
    current_liabilities: float
) -> Optional[float]:
    """
    Operating Cash Flow Ratio

    Formula:
        Operating Cash Flow / Current Liabilities
    """

    if (
        operating_cash_flow is None or
        current_liabilities is None
    ):
        return None

    if current_liabilities <= 0:
        return None

    return round(
        operating_cash_flow / current_liabilities,
        2
    )


def calculate_cash_conversion_ratio(
    operating_cash_flow: float,
    net_profit: float
) -> Optional[float]:
    """
    Cash Conversion Ratio

    Formula:
        Operating Cash Flow / Net Profit
    """

    if (
        operating_cash_flow is None or
        net_profit is None
    ):
        return None

    if net_profit <= 0:
        return None

    return round(
        operating_cash_flow / net_profit,
        2
    )