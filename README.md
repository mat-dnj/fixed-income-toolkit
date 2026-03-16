# fixed-income-toolkit
Bond pricing and live US Treasury data from scratch. 
_Part of a broader fixed income library being built incrementally._

** Part 2 will add yield curve PCA with level, slope and curvature decomposition, relative value signals and DV01 neutral trade construction.**

---

## what's in Part 1

`fred_client.py` -> Pull live treasury yields from FRED API
`bond_math` --> Price bonds, compute duration, convexity, DV01
`test/test_bond_math.py` --> tests covering every function
