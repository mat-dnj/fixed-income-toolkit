# fixed-income-toolkit
Basic Bond math library and FRED integration for US Treasury data. 
This is part of a broader fixed income library I am actually building.

_Part 2 will add yield curve PCA with level, slope and curvature decomposition, relative value signals and DV01 neutral trade construction._

## Part I

### 1. Modules

* `fred_client.py` --> Pull live treasury yields from FRED API 
* `bond_math.py` --> Price bonds, compute duration, convexity, DV01
* `test_bond_math.py` --> tests covering every function

### 2. Setup 
```bash
pip install -r requirements.txt
```
Get your FRED API key at https://fred.stlouisfed.org/docs/api/api_key.html

```bash
export fred_api_key="your key here"
```

### 3. Quick start
Use the bond_sumary function to get the breakdown of a bond price, sensitivity and scenario analysis.
```python
from bond_math import bond_summary
# 10Y bond, 4.5% coupon, 5% YTM
bond_summary(face=1000, coupon=0.045, maturity=10, ytm=0.05)
```

```
Bond Summary: 4.50% Coupon, 10Y, 5.00% YTM
---------------------------
  Price:                 961.027
  Macaulay Duration:       8.117
  Modified Duration        7.919
  Convexity:              75.300
  DV01:                    0.761
---------------------------
  +100bp move: 888.419  (-72.608)
  -100bp move: 1040.879  (79.851)
```

## Part II - work in progress
* PCA on yield curve --> level / slope / curvature
* Z-score to find when 2 tenirs are mispriced vs each other
* DV01-neutral trade construction (how to size the long and the short legs)
* backtesting the strategy on historical data