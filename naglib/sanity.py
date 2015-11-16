"""
NAGlib depends on external libraries and a minimum version of Python.
Ensure we have these.
"""

# check whether we have at least the minimal version of Python
import sys
major, minor = sys.version_info[0], sys.version_info[1]
if major == 2 and minor < 7:
    msg = "NAGlib requires Python version 2.7 or above."
    raise ImportError(msg)
elif major == 3:
    pass # check for Py3 version as necessary

# check whether we have SymPy at all
try:
    import sympy
except ImportError:
    msg = ("NAGlib depends on the external library SymPy. "
           "See http://docs.sympy.org/latest/install.html for installation.")
    raise ImportError(msg)

# now check whether we have at least the minimal version of SymPy
major, minor, release = [int(n) for n in sympy.__version__.split('.')[:3]]
if major == 0 and minor == 7 and release < 6:
    msg = "NAGlib requires SymPy version 0.7.6 or above."
    raise ImportError(msg)
del sympy, release

del sys, major, minor
