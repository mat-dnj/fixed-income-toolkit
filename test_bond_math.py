"""
tests for bond_math.py
"""
import pytest
from bond_math import (bond_price, ytm_from_price, macaulay_duration, modified_duration, convexity, dv01)


def test_par_bond():
    # Coupon = ytm, price should be exactly face value
    price = bond_price(1000, 0.05, 10, 0.05, freq=2)
    assert price == pytest.approx(1000.0)


def test_frequency_impact():
    # Annual vs Semi annual compounding give diferent prices.
    annual = bond_price(1000, 0.05, 10, 0.05, freq=1)
    semi_ann = bond_price(1000, 0.05, 10, 0.05, freq=2)
    assert annual!= semi_ann


def test_discount_and_premium():
    assert bond_price(1000, 0.04, 10, 0.05, freq=2) < 1000 #discount
    assert bond_price(1000, 0.06, 10, 0.05, freq=2) > 1000 #premium


def test_price_yield_inverse():
    # high ytm = lower price
    low_yield_price = bond_price(1000, 0.045, 10, 0.03, freq=2)
    high_yield_price = bond_price(1000, 0.045, 10, 0.07, freq=2)
    assert low_yield_price > high_yield_price


def test_ytm_consistency():
    # verify that the YTM solver correctly inverts the bond pricing function.
    target_yield = 0.0489
    computed_price = bond_price(1000, 0.045, 10, target_yield, freq=2)
    solved = bond_price(1000, 0.045, 10, computed_price, freq=2)
    assert solved == pytest.approx(target_yield, rel=1e-8)


def test_zero_coupon_duration():
    # zero coupon bond--> no cash flows so duration = maturity exactly
    d = macaulay_duration(1000, 0 ,7 , 0.05, freq=2)
    assert d == pytest.approx(7)


def test_modified_lthan_macaulay():
    mac = macaulay_duration(1000, 0.045, 10, 0.05, freq=2)
    mod = modified_duration(1000, 0.045, 10, 0.05, freq=2)
    assert mod<mac


def test_longer_bond_more_risk():
    # longer maturity = higher duration and higher dv01
    assert modified_duration(1000, 0.045, 30, 0.05, freq=2) > modified_duration(1000, 0.045, 2, 0.05, freq=2)
    assert dv01(1000, 0.045, 30, 0.05, freq=2) > dv01(1000, 0.045, 2, 0.05, freq=2)


# TODO: come back and better test convexity, not sure I fully understand the formula yet, just know the output should be positive
# also have to figure out how to handle accrued interest, cause all prices assume we're on a coupon date which is never true in real life