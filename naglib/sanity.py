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

# check whether we have six
try:
    import six
except ImportError:
    msg = ("NAGlib depends on the Python compatibility library `six'. "
           "See https://pypi.python.org/pypi/six for details.")
    raise ImportError(msg)
del six

# first check whether we have gmpy2
try:
    import gmpy2
except ImportError:
    msg = ("NAGlib depends on the gmpy2 library. "
           "See https://pypi.python.org/pypi/gmpy2 for details.")
    raise ImportError(msg)

# now check whether we have at least the minimal version of gmpy2
major,minor,release = [int(n) for n in gmpy2.version().split('.')]
if major == 2 and minor == 0 and release < 5:
    msg = "NAGlib requires gmpy2 version 2.0.5 or above."
    raise ImportError(msg)
del gmpy2

# first check whether we have SymPy
try:
    import sympy
except ImportError:
    msg = ("NAGlib depends on the SymPy library. "
        "See http://docs.sympy.org/latest/install.html for details.")
    raise ImportError(msg)

# now check whether we have at least the minimal version of SymPy
major, minor, release = [int(n) for n in sympy.__version__.split('.')[:3]]
if major == 0 and minor == 7 and release < 6:
    msg = "NAGlib requires SymPy version 0.7.6 or above."
    raise ImportError(msg)
del sympy, release

del sys, major, minor
