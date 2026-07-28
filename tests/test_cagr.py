import pytest

from src.analytics.cagr import (
    calculate_cagr,
    calculate_revenue_cagr,
    calculate_pat_cagr,
    calculate_eps_cagr,
)


def test_calculate_cagr_normal():
    assert calculate_cagr(100, 200, 5) == 14.87


def test_calculate_cagr_zero_years():
    assert calculate_cagr(100, 200, 0) is None


def test_calculate_cagr_negative_start():
    assert calculate_cagr(-100, 200, 5) is None


def test_calculate_cagr_zero_start():
    assert calculate_cagr(0, 200, 5) is None


def test_calculate_cagr_negative_end():
    assert calculate_cagr(100, -200, 5) is None


def test_calculate_cagr_none():
    assert calculate_cagr(None, 200, 5) is None
    assert calculate_cagr(100, None, 5) is None


def test_revenue_cagr():
    assert calculate_revenue_cagr(100, 200, 5) == 14.87


def test_pat_cagr():
    assert calculate_pat_cagr(100, 200, 5) == 14.87


def test_eps_cagr():
    assert calculate_eps_cagr(10, 20, 5) == 14.87