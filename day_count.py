"""
day_count.py
day count convention defines the rules for calculating the amounr of interest that is accrued between any two given dates or any interest rate produt.
    clean price = quoted price
    dirty price = clean price + accrued interest
"""

from datetime import date 
from dateutil.relativedelta import relativedelta


def act_act(prev_coupon: date, settlement: date, period_end: date):
    actual_days = (settlement-prev_coupon).days
    period_days = (period_end-prev_coupon).days

    if period_days <=0:
        return 0.0
    return actual_days/period_days


def act_360(start: date, end: date):
    actual_days = (end - start).days
    return actual_days/360


def accrued_interest(face, coupon, prev_coupon: date, settlement: date, next_coupon: date, 
                     freq: int=2, convention : str='ACT/ACT') -> float:
    coupon_payment = face * (coupon/freq)
    if convention.upper().replace(' ','')=="ACT/ACT":
        DCF = act_act(prev_coupon, settlement, next_coupon)
    
    else :
        DCF = act_360(prev_coupon, settlement)
    
    return DCF *coupon_payment


def clean_to_dirty(clean_price: float, face: float, coupon: float, settlement: date, prev_coupon: date, 
                   next_coupon: date, freq: int = 2, convention: str = "ACT/ACT") -> float:
    
    ai = accrued_interest(face, coupon, settlement, prev_coupon,
                         next_coupon, freq, convention)
    return clean_price + ai


def dirty_to_clean(dirty_price: float, face: float, coupon: float, settlement: date, prev_coupon: date, 
                   next_coupon: date, freq: int = 2, convention: str = "ACT/ACT") -> float:
    
    ai = accrued_interest(face, coupon, settlement, prev_coupon,
                         next_coupon, freq, convention)
    return dirty_price - ai
