from src.analytics.leverage import (
    calculate_debt_to_equity,
    calculate_interest_coverage,
    calculate_net_debt,
    calculate_asset_turnover,
    is_debt_free,
    is_high_leverage,
)


# ----------------------------
# Debt to Equity
# ----------------------------

def test_debt_to_equity_normal():
    assert calculate_debt_to_equity(200, 300, 200) == 0.4


def test_debt_to_equity_negative_equity():
    assert calculate_debt_to_equity(200, -300, 100) is None


# ----------------------------
# Interest Coverage Ratio
# ----------------------------

def test_interest_coverage_normal():
    assert calculate_interest_coverage(100, 20, 20) == 6.0


def test_interest_coverage_zero_interest():
    assert calculate_interest_coverage(100, 20, 0) is None


# ----------------------------
# Net Debt
# ----------------------------

def test_net_debt():
    assert calculate_net_debt(500, 200) == 300


# ----------------------------
# Asset Turnover
# ----------------------------

def test_asset_turnover_normal():
    assert calculate_asset_turnover(1000, 500) == 2.0


def test_asset_turnover_zero_assets():
    assert calculate_asset_turnover(1000, 0) is None


# ----------------------------
# Debt Free
# ----------------------------

def test_debt_free():
    assert is_debt_free(0) is True


def test_not_debt_free():
    assert is_debt_free(100) is False


# ----------------------------
# High Leverage
# ----------------------------

def test_high_leverage():
    assert is_high_leverage(6, "Technology") is True


def test_financial_sector():
    assert is_high_leverage(10, "Financials") is False