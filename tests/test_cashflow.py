from src.analytics.cashflow import (
    calculate_free_cash_flow,
    calculate_operating_cash_flow_ratio,
    calculate_cash_conversion_ratio,
)


def test_free_cash_flow():
    assert calculate_free_cash_flow(1000, 250) == 750


def test_free_cash_flow_none():
    assert calculate_free_cash_flow(None, 250) is None
    assert calculate_free_cash_flow(1000, None) is None


def test_operating_cash_flow_ratio():
    assert calculate_operating_cash_flow_ratio(1000, 500) == 2.0


def test_operating_cash_flow_ratio_zero():
    assert calculate_operating_cash_flow_ratio(1000, 0) is None


def test_operating_cash_flow_ratio_none():
    assert calculate_operating_cash_flow_ratio(None, 500) is None
    assert calculate_operating_cash_flow_ratio(1000, None) is None


def test_cash_conversion_ratio():
    assert calculate_cash_conversion_ratio(1000, 500) == 2.0


def test_cash_conversion_ratio_zero():
    assert calculate_cash_conversion_ratio(1000, 0) is None


def test_cash_conversion_ratio_none():
    assert calculate_cash_conversion_ratio(None, 500) is None
    assert calculate_cash_conversion_ratio(1000, None) is None