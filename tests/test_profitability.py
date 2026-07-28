import pytest

from src.analytics.profitability import (
    calculate_net_profit_margin,
    calculate_operating_profit_margin,
    calculate_roe,
    calculate_roce,
    calculate_roa,
)


# ----------------------------
# Net Profit Margin
# ----------------------------

def test_net_profit_margin_normal():
    assert calculate_net_profit_margin(200, 1000) == 20.0


def test_net_profit_margin_zero_sales():
    assert calculate_net_profit_margin(200, 0) is None


def test_net_profit_margin_negative_sales():
    assert calculate_net_profit_margin(200, -1000) is None


# ----------------------------
# Operating Profit Margin
# ----------------------------

def test_operating_profit_margin_normal():
    assert calculate_operating_profit_margin(250, 1000) == 25.0


def test_operating_profit_margin_zero_sales():
    assert calculate_operating_profit_margin(250, 0) is None


# ----------------------------
# Return on Equity (ROE)
# ----------------------------

def test_roe_normal():
    assert calculate_roe(100, 300, 200) == 20.0


def test_roe_negative_equity():
    assert calculate_roe(100, -300, 100) is None


# ----------------------------
# Return on Capital Employed (ROCE)
# ----------------------------

def test_roce_normal():
    assert calculate_roce(150, 400, 200, 400) == 15.0


def test_roce_zero_capital():
    assert calculate_roce(150, 0, 0, 0) is None


# ----------------------------
# Return on Assets (ROA)
# ----------------------------

def test_roa_normal():
    assert calculate_roa(120, 1200) == 10.0


def test_roa_zero_assets():
    assert calculate_roa(120, 0) is None