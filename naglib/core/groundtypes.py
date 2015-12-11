"""Check for libraries for symbolic/numeric types and decide which to use"""

from __future__ import division, print_function

# check for SymPy
def __has_sympy():
    try:
        import sympy
    except ImportError:
        return False
    return True

# check for gmpy2
def __has_gmpy2():
    try:
        import gmpy2
    except ImportError:
        return False
    return True

syms = ["native"]
nums = ["native"]
if __has_sympy():
    syms.append("sympy")
    nums.append("sympy")
if __has_gmpy2():
    nums.append("gmpy2")

NUMBERS = nums[-1]
SYMBOLS = syms[-1]
