"""
Numeric types in NAGlib.
Numbers are actually represented in NAGlib as arrays of numbers.
"""

from __future__ import division, print_function

import re

from .base import NAGObject
from .core import string_types
from sympy import sympify, Integer, Rational, Float, I

is_int      = re.compile(r"^[-+]?\d+$")
is_rational = re.compile(r"^[-+]?\d+/\d+$")
is_float    = re.compile(r"^[-+]?\d*\.?\d+([eE][-+]?\d+)?$")

is_imag_int      = re.compile(r"^[-+]?([iI](\s*\*?\s*\d+)?|\d+(j|\s*\*?\s*[iI]))$")
is_imag_rational = re.compile(r"^[-+]?([iI](\s*\*?\s*\d+)?/\d+|\d+(j|\s*\*?\s*[iI])/\d+)$")
is_imag_float    = re.compile(r"^[-+]?([iI]\s*\*?\s*\d+\.?\d+([eE][-+]?\d+)?|\d*\.?\d+([eE][-+]?\d+)?(j|\s*\*?\s*[iI]))$")

def is_gaussian_int(val):
    # use positive lookbehind so we don't accidentally capture [+-] at The
    # beginning of a string
    # TODO: this doesn't capture the case where the imaginary part comes first!
    breakup = re.split(r"(?<=\d)\s*[-+]\s*", val)
    if len(breakup) != 2:
        return False
    else:
        a,b = breakup
        if (is_int.match(a) and is_imag_int.match(b)) or (is_imag_int.match(a) and is_int.match(b)):
            return True
        else:
            return False

def is_gaussian_rational(val):
    # use positive lookbehind so we don't accidentally capture [+-] at The
    # beginning of a string
    # TODO: this doesn't capture the case where the imaginary part comes first!
    breakup = re.split(r"(?<=\d)\s*[-+]\s*", val)
    if len(breakup) != 2:
        return False
    else:
        a,b = breakup
        if (is_rational.match(a) and is_imag_rational.match(b)) \
            or (is_imag_rational.match(a) and is_rational.match(b)) \
            or (is_int.match(a) and is_imag_rational.match(b)) \
            or (is_rational.match(a) and is_imag_int.match(b)) \
            or (is_imag_int.match(a) and is_rational.match(b)) \
            or (is_imag_rational.match(a) and is_int.match(b)):
            return True
        else:
            return False

def is_gaussian_float(val):
    # use positive lookbehind so we don't accidentally capture [+-] at The
    # beginning of a string
    # TODO: this doesn't capture the case where the imaginary part comes first!
    breakup = re.split(r"(?<=\d)\s*[-+]\s*", val)
    if len(breakup) != 2:
        return False
    else:
        a,b = breakup
        if (is_float.match(a) and is_imag_float.match(b)) \
            or (is_imag_float.match(a) and is_float.match(b)) \
            or (is_int.match(a) and is_imag_float.match(b)) \
            or (is_float.match(a) and is_imag_int.match(b)) \
            or (is_imag_int.match(a) and is_float.match(b)) \
            or (is_imag_float.match(a) and is_int.match(b)):
            return True
        else:
            return False

def get_numeric_type(vals):
    vals = [re.sub(r"^\(|\)$", "", str(val)) for val in vals]

    # keyword k is a member of class assumptions[k], i.e., a gaussian int is not a vanilla int
    assumptions = {"int": ("int", "gaussian int", "rational", "gaussian rational", "float", "gaussian float"),
                   "gaussian int": ("gaussian int", "gaussian rational"),
                   "rational": ("rational", "gaussian rational"),
                   "gaussian rational": ("gaussian rational"),
                   "float": ("float", "gaussian float"),
                   "gaussian float": ("gaussian float")}

    possibles = set(("int", "gaussian int", "rational", "gaussian rational",
                     "float", "gaussian float"))
    for val in vals:
        if is_int.match(val):
            pass
        elif is_imag_int.match(val) or is_gaussian_int(val):
            possibles.difference_update(set(("int", "rational", "float")))
        elif is_rational.match(val):
            possibles.difference_update(set(("int", "gaussian int", "float")))
        elif is_imag_rational.match(val) or is_gaussian_rational(val):
            possibles.difference_update(set(("int", "gaussian int", "rational", "float", "gaussian float")))
        elif is_float.match(val):
            possibles.difference_update(set(("int", "gaussian int","rational", "gaussian rational")))
        elif is_imag_float.match(val) or is_gaussian_float(val):
            possibles.difference_update(set(("int", "gaussian int", "rational", "gaussian rational", "float")))
        else:
            print("{0} is not a number".format(val)) # DEBUG
            return None

        print("{0}".format(val)) # DEBUG
        if not possibles:
            print("last possibility eliminated with".format(val)) # DEBUG
            return None

    for possibility in ("int", "gaussian int", "rational", "gaussian rational",
                        "float", "gaussian float"):
        if possibility in possibles:
            return possibility # lowest one

class Numeric(NAGObject):
    """Base class for numeric types"""

    def __init__(self, *args):
        super(Numeric, self).__init__(*args)

        self._prec = -1
        if len(args) == 1:
            args = args[0]

            if isinstance(args, tuple) or isinstance(args, list):
                args = [str(arg) for arg in args]
                numeric_type = get_numeric_type(args)
                if numeric_type:
                    self._type = numeric_type
                    self._entries = [sympify(arg) for arg in args] # TODO: use gmpy or mpmath if available
                else:
                    msg = ("expected iterable of strings of similar type "
                           "but got incompatible types")
                    raise ValueError(msg)
            else:
                value_type = type(args)
                if value_type not in (int, long, float, complex, str):
                    msg = ("expected str|int|long|float|complex object but got "
                           "{0} instead".format(value_type))
                    raise TypeError(msg)

            self._is_number = True
            if len(self._entries) == 1:
                self._is_scalar = True
            else:
                self._is_scalar = False
        else:
            pass

class Complex(Numeric):
    """Complex floating-point vector type"""

    def __init__(self, *args):
        super(Complex, self).__init__(*args)

class Float(Complex):
    """Floating-point vector type"""

    def __init__(self, *args):
        super(Float, self).__init__(*args)

class GaussianRational(Numeric):
    """Gaussian rational vector type"""

    def __init__(self, *args):
        super(GaussianRational, self).__init__(*args)

class Rational(GaussianRational):
    """Rational vector type"""

    def __init__(self, *args):
        super(GaussianRational, self).__init__(*args)

class Integer(Rational):
    """Integer vector type"""

    def __init__(self, *args):
        super(Integer, self).__init__(*args)

class GaussianInteger(GaussianRational):
    """Gaussian integer vector type"""

    def __init__(self, *args):
        super(GaussianInteger, self).__init__(*args)
