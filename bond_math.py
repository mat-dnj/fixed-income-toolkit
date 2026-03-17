''' 
bond_math.py
module created to price bonds, compute duration, convexity, DV01.

Functions: 
bond_price
ytm_from_price
macaulay_duration
modified_duration
convexity
dv01
price_change
bond_summary
'''

import numpy as np
from scipy.optimize import brentq 

def bond_price(face, coupon, maturity, ytm, freq=2):
    """
    price a fixed coupon bond by discounting all future cash flows
    """
    n_periods = int(maturity*freq)
    c_payments = face * coupon / freq
    r = ytm / freq

    pv_coupons = sum(c_payments/(1+r)** t for t in range (1, n_periods+1))

    pv_face = face / (1+r)**n_periods
    return pv_coupons+pv_face


def ytm_from_price (market_price, face, coupon, maturity, ytm, freq=2):
    """
    calculates YTM of a bond given its market price 
    we want to find where: (bond_price - market_price) == 0
    """
    objective = lambda y: bond_price(face, coupon, maturity, y, freq) - market_price
    try:
        return brentq(objective, a= -0.1, b=1.0, xtol=1e-6)
    except ValueError:
        # prevents code from crashing if brentq fails
        return None 
    

def macaulay_duration(face, coupon, maturity, ytm, freq=2):
    """
    weigthed average time to receive all of the cash flows
    """
    n_periods = int(maturity*freq)
    c_payments = face * coupon / freq
    r = ytm / freq 
    price = bond_price(face, coupon, maturity, ytm, freq)

    weighted_cf = sum((t / freq) * (c_payments/(1+r)**t) for t in range(1, n_periods+1))
    weighted_cf += (n_periods / freq) * face / (1+r)**n_periods
    return weighted_cf / price


def modified_duration(face, coupon, maturity, ytm, freq=2):
    """
    modified duration --> % change in price for a 1% change in yield,
    Macaulqy duration adjusted for compounding frequency.
    """
    macaulay = macaulay_duration(face, coupon, maturity, ytm, freq)
    return macaulay / (1+ytm/freq)


def convexity(face, coupon, maturity, ytm, freq=2):
    """
    Curvature in the price/yield relationship
    Gives linear approximation of prices changes.
    """
    n_periods = int(maturity*freq)
    c_payments = face*coupon / freq
    r = ytm/freq
    price = bond_price(face, coupon, maturity, ytm,freq)

    cx = 0.0
    for t in range(1, n_periods+1):
        cf = c_payments if t<n_periods else c_payments+face
        cx += (t*(t+1) / freq**2) * cf / (1+r)**t 
    return cx / (price*(1+r)**2)


def dv01(face, coupon, maturity, ytm, freq=2):
    """
    Dollar Value of 1 basis point.
    """
    bp = 0.0001 #1basis point(0.01%)
    price_up = bond_price(face, coupon, maturity, ytm+bp, freq)
    price_down = bond_price(face, coupon, maturity, ytm-bp, freq)
    return (price_down-price_up) / 2   #slope at current ytm


def price_change(face, coupon, maturity, ytm, dy, freq=2):
    """
    Estimates the bond price changes given a yield shift,
    Uses the second order Taylor expansion,
    Duration--> main driver for small moves,
    Convexity --> becomes significant for larger yield moves
    """
    price = bond_price(face, coupon, maturity, ytm, freq)
    mod_duration = modified_duration(face, coupon, maturity,  ytm, freq)
    conv = convexity(face, coupon, maturity, ytm, freq)

    duration_effect = -mod_duration * price * dy
    convexity_effect = 1/2 * (conv*price) * dy**2

    approx_new_price = price + duration_effect + convexity_effect
    actual_new_price = bond_price(face, coupon, maturity, ytm + dy, freq)

    return {
        'original price': price,
        'duration_effect': duration_effect,
        'convexity_effect': convexity_effect,
        'approx_new_price': approx_new_price,
        'actual_new_price': actual_new_price,
        'residual': abs(approx_new_price-actual_new_price)
    }

def bond_summary(face, coupon, maturity, ytm, freq=2):
    """
    Print full risk metric summary for a bond
    """
    price = bond_price(face, coupon, maturity, ytm, freq)
    mac_duration = macaulay_duration(face, coupon, maturity, ytm, freq)
    mod_duration = modified_duration(face, coupon, maturity, ytm, freq)
    conv = convexity(face, coupon, maturity, ytm, freq)
    dv = dv01(face, coupon, maturity, ytm, freq)

    # shows what happens for a 100bp move
    shift_up = price_change(face, coupon, maturity, ytm, 0.01, freq)
    shift_down = price_change(face, coupon, maturity, ytm, -0.01, freq)

    print(f'Bond Summary: {coupon*100:.2f}% Coupon, {maturity}Y, {ytm*100:.2f}% YTM')
    print('-'*27)
    print(f'  Price:              {price:>10.3f}')
    print(f'  Macaulay Duration:  {mac_duration:>10.3f}')
    print(f'  Modified Duration   {mod_duration:>10.3f}')
    print(f'  Convexity:          {conv:>10.3f}')
    print(f'  DV01:               {dv:>10.3f}')
    print('-'*27)
    print(f"  +100bp move: {shift_up['actual_new_price']:.3f}"
          f"  ({shift_up['actual_new_price']-price:.3f})")
    print(f"  -100bp move: {shift_down['actual_new_price']:.3f}"
          f"  ({shift_down['actual_new_price']-price:.3f})")


# next: clean and optmize module, 
# need to figure out how to use these DV01s to size a trade
# if I want to go long 10Y and short 2Y, how much of each?