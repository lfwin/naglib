"""
NAGlib is a Python library for numerical algebraic geometry.
"""

# OS sanity checking; do this before anything else!
try:
    import sanity
except ImportError as e:
    raise ImportError(e.message)
del sanity

from .envconstants import tol, dps, DEBUG
from .release import __version__, __authors__

from .core import *
