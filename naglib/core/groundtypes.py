"""Check for libraries for symbolic/numeric types and decide which to use"""

from __future__ import division, print_function

# check for libpybertini
def __has_libpybertini():
    try:
        import libpybertini
    except ImportError:
        return False
    return True

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

syms = []
nums = []
if __has_libpybertini():
    syms.append("libpybertini")
    nums.append("libpybertini")
if __has_sympy():
    syms.append("sympy")
    nums.append("sympy")
if __has_gmpy2():
    nums.append("gmpy2")

# these should be nonempty or something has failed in naglib/sanity.py
NUMBERS = nums[-1]
SYMBOLS = syms[-1]
