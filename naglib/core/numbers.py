"""
Numeric types in NAGlib.
Complex numbers are first-class objects in NAGlib
"""

from __future__ import division, print_function

from .base import NAGObject
from .core import string_types
from .groundtypes import NUMBERS

import re

def coercion_map(left, right):
    left = left.__class__
    right = right.__class__
    from fractions import gcd, Fraction

    pmap = {Float:1,
            Rational:2,
            Integer:4}
    pinv = dict([(pmap[k], k) for k in pmap.keys()])
    pmap.update({complex:1,
                 float:1,
                 Fraction:2,
                 int:4,
                 long:4})

    try:
        ltype = pmap[left]
        rtype = pmap[right]
    except KeyError:
        msg = "can't coerce {0} and {1} to a common type"
        raise TypeError(msg)

    return pinv[gcd(ltype, rtype)]

def init_nan():
    if NUMBERS == "gmpy2":
        from gmpy2 import nan
    elif NUMBERS == "sympy":
        from sympy import nan
    else:
        nan = float("nan")
    return nan

def init_float(val, prec=0):
    val = str(val)
    if NUMBERS == "gmpy2":
        from gmpy2 import mpfr
        try:
            val = mpfr(val, prec)
        except ValueError: # invalid digits
            raise
        except TypeError: # invalid precision
            raise
    elif NUMBERS == "sympy":
        from sympy import Float
        prec = '' if prec == 0 else prec
        try:
            val = Float(val, prec)
        except ValueError: # invalid number
            raise
    elif NUMBERS == "libpybertini":
        from libpybertini import default_precision, mpfr_float as mpfr
        if prec > 0:
            try:
                default_precision(prec) # this is clunky and should be fixed
            except: # ArgumentError, but I'll be damned if I know where to import it from
                raise TypeError
        try:
            val = mpfr(val)
        except RuntimeError:
            raise ValueError

    return val

def init_rational(val):
    val = str(val)
    if NUMBERS == "gmpy2":
        from gmpy2 import mpq
        try:
            val = mpq(val)
        except ValueError: # invalid digits
            raise
    elif NUMBERS == "sympy":
        from sympy import Rational
        try:
            val = Rational(val)
        except TypeError: # invalid number
            raise ValueError
    else:
        from fractions import Fraction
        try:
            val = Fraction(val)
        except ValueError:
            raise

    return val

def init_integer(val):
    val = str(val)
    if NUMBERS == "gmpy2":
        from gmpy2 import mpz
        try:
            val = mpz(val)
        except ValueError: # invalid digits
            raise
    elif NUMBERS == "sympy":
        from sympy import Integer
        try:
            val = Integer(val)
        except TypeError: # invalid number
            raise ValueError
    else:
        try:
            val = long(val)
        except ValueError:
            raise

    return val

class Numeric(NAGObject):
    """Base class for numeric types"""
    def __init__(self, *args, **kwargs):
        super(Numeric, self).__init__(*args, **kwargs)
        kkeys = kwargs.keys()

        # defaults
        self._real = self._imag = 0

        try:
            self._real, self._imag = args[0]
        except IndexError: # args is empty; check kwargs
            if "real" in kkeys:
                self._real = kwargs["real"]
            else:
                real = 0
            if "imag" in kkeys:
                self._imag = kwargs["imag"]
            else:
                self._imag = 0
        except TypeError: # not iterable
            if isinstance(args[0], complex):
                self._real, self._imag = args[0].real, args[0].imag
            else:
                self._real = args[0]
                self._imag = 0
        except ValueError: # too many values to unpack
            self._real = args[0]
            self._imag = 0

        self._is_number = True
        self._is_scalar = True
        self._ground_type = NUMBERS

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return self.__str__()

    def __eq__(self, other):
        """x.__eq__(y) <==> x == y"""
        try:
            return self._real == other.real and self._imag == other.imag
        except AttributeError:
            return False

    def __ne__(self, other):
        """x.__ne__(y) <==> x != y"""
        try:
            return self._real != other.real or self._imag != other.imag
        except AttributeError:
            return True

    def __lt__(self, other):
        """x.__lt__y() <==> x < y"""
        try:
            return (self._imag == 0 and other.imag == 0) and self._real < other.real
        except AttributeError:
            return False

    def __gt__(self, other):
        """x.__gt__(y) <==> x > y"""
        try:
            return (self._imag == 0 and other.imag == 0) and self._real > other.real
        except AttributeError:
            return False

    def __abs__(self):
        """x.__abs__() <==> abs(x)"""
        if self._ground_type == "gmpy2":
            from gmpy2 import sqrt
        elif self._ground_type == "sympy":
            from sympy import sqrt
        elif self._ground_type == "libpybertini":
            from libpybertini import sqrt
        else:
            from math import sqrt

        return float(sqrt(self._real**2 + self._imag**2))

    def __neg__(self):
        cls = self.__class__
        return cls((-self._real, -self._imag))

    def __add__(self, other):
        """x.__add__(y) <==> x + y"""
        try:
            cls = coercion_map(self, other)
        except TypeError:
            msg = "unsupported operand type(s) for +: '{0}' and '{1}'".format(type(self), type(other))
            raise TypeError(msg)

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        try:
            real = sreal + oreal
            imag = simag + oimag
        except:
            nclass = real.__class__
            oreal = nclass(str(oreal)) # hacky
            oimag = nclass(str(oimag))
            real = sreal + oreal
            imag = simag + oimag

        return cls((real, imag))

    def __sub__(self, other):
        """x.__sub__(y) <==> x - y"""
        try:
            cls = coercion_map(self, other)
        except TypeError:
            msg = "unsupported operand type(s) for -: '{0}' and '{1}'".format(type(self), type(other))
            raise TypeError(msg)

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        try:
            real = sreal - oreal
            imag = simag - oimag
        except:
            nclass = real.__class__
            oreal = nclass(str(oreal)) # hacky
            oimag = nclass(str(oimag))
            real = sreal - oreal
            imag = simag - oimag

        return cls((real, imag))

    def __rsub__(self, other):
        """x.__rsub__(y) <==> y - x"""
        try:
            cls = coercion_map(self, other)
        except TypeError:
            msg = "unsupported operand type(s) for -: '{0}' and '{1}'".format(type(other), type(self))
            raise TypeError(msg)

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        try:
            real = oreal - sreal
            imag = oimag - simag
        except:
            nclass = real.__class__
            oreal = nclass(str(oreal)) # hacky
            oimag = nclass(str(oimag))
            real = oreal - sreal
            imag = oimag - simag

        return cls((real, imag))

    def __mul__(self, other):
        """x.__mul__(y) <==> x*y"""
        try:
            cls = coercion_map(self, other)
        except TypeError:
            msg = "unsupported operand type(s) for *: '{0}' and '{1}'".format(type(self), type(other))
            raise TypeError(msg)

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        try:
            real = sreal*oreal - simag*oimag
            imag = sreal*oimag + simag*oreal
        except:
            nclass = real.__class__
            oreal = nclass(str(oreal)) # hacky
            oimag = nclass(str(oimag))
            real = sreal*oreal - simag*oimag
            imag = sreal*oimag + simag*oreal

        return cls((real, imag))

    def __div__(self, other):
        """x.__div__(y) <==> x/y"""
        try:
            cls = coercion_map(self, other)
        except TypeError:
            msg = "unsupported operand type(s) for /: '{0}' and '{1}'".format(type(self), type(other))
            raise TypeError(msg)

        if other == 0 or (hasattr(other, "is_zero") and other.is_zero):
            msg = "division by zero"
            raise ZeroDivisionError(msg)

        oreal = other.real
        oimag = other.imag
        denom = oreal**2 + oimag**2
        oinv = other.__class__((oreal/denom, -oimag/denom))

        return self*oinv

    def conjugate(self):
        """the complex conjugate"""
        cls = self.__class__
        real, imag = self._real, self._imag
        return cls((real, -imag))

    @property
    def real(self):
        return self._real
    @property
    def imag(self):
        return self._imag
    @property
    def is_real(self):
        from naglib.envconstants import tol
        return abs(self._imag) < tol
    @property
    def is_zero(self):
        from naglib.envconstants import tol
        return abs(self) < tol

class Float(Numeric):
    """Adaptive-multiprecision complex floating-point number"""
    def __init__(self, *args, **kwargs):
        super(Float, self).__init__(*args, **kwargs)
        kkeys = kwargs.keys()

        try:
            prec = args[1]
        except IndexError:
            if "prec" in kkeys:
                prec = kwargs["prec"]
            else:
                from naglib.envconstants import prec

        try:
            self._real = init_float(self._real, prec)
        except ValueError: # invalid number
            msg = "can't create Float from argument: '{0}'".format(self._real)
            raise ValueError(msg)
        except TypeError: # invalid precision
            msg = "can't create Float with precision: '{0}'".format(prec)
            raise TypeError(msg)

        try:
            self._imag = init_float(self._imag, prec)
        except ValueError: # invalid number
            msg = "can't create Float from argument: '{0}'".format(self._imag)
            raise ValueError(msg)
        except TypeError: # invalid precision
            msg = "can't create Float with precision: '{0}'".format(prec)
            raise TypeError(msg)

        self._prec = prec

    def __str__(self):
        """x.__str__() <==> str(x)"""
        from math import floor
        real,imag = self._real,self._imag

        rdps = idps = int(floor(self._prec/3.33))
        if real == int(real):
            rdps = 1
        if imag == int(imag):
            idps = 1

        if imag == 0:
            return "{1:.{0}f}".format(rdps,real)
        elif imag < 0:
            return "{2:.{0}f} - {3:.{1}f}*I".format(rdps,idps,real,abs(imag))
        else:
            return "{2:.{0}f} + {3:.{1}f}*I".format(rdps,idps,real,imag)

    def __neg__(self):
        cls = self.__class__
        return cls((-self._real, -self._imag),prec=self._prec)

    def almost_equal(self,other,tol=None):
        """1-norm of difference is less than tolerance"""
        if not tol:
            from naglib.envconstants import tol
        try:
            return abs(self - other) < tol
        except TypeError:
            raise

    @property
    def prec(self):
        return self._prec
    @prec.setter
    def prec(self, p):
        if p <= 1:
            msg = "invalid precision"
            raise ValueError(msg)

        try:
            self._real = init_float(self._real, p)
        except ValueError: # invalid number; shouldn't happen here
            msg = "can't create Float from argument: '{0}'".format(self._real)
            raise ValueError(msg)
        except TypeError: # invalid precision
            msg = "can't create Float with precision: '{0}'".format(p)
            raise TypeError(msg)

        try:
            self._imag = init_float(self._imag, p)
        except ValueError: # invalid number
            msg = "can't create Float from argument: '{0}'".format(self._imag)
            raise ValueError(msg)
        except TypeError: # invalid precision
            msg = "can't create Float with precision: '{0}'".format(p)
            raise TypeError(msg)

        self._prec = p

class Rational(Numeric):
    def __init__(self, *args, **kwargs):
        super(Rational, self).__init__(*args, **kwargs)

        try:
            self._real = init_rational(self._real)
        except ValueError: # invalid number
            msg = "can't create Rational from argument: '{0}'".format(self._real)
            raise ValueError(msg)

        try:
            self._imag = init_rational(self._imag)
        except ValueError: # invalid number
            msg = "can't create Rational from argument: '{0}'".format(self._imag)
            raise ValueError(msg)

    def __str__(self):
        """x.__str__() <==> str(x)"""
        real, imag = self._real, self._imag

        inum = imag.numerator
        iden = imag.denominator

        if imag == 0:
            return "{0}".format(real)
        if iden == 1 and imag < 0:
            return "{0} - {1}*I".format(real, abs(inum))
        elif iden == 1:
            return "{0} + {1}*I".format(real, inum)
        elif imag < 0:
            return "{0} - {1}*I/{2}".format(real, abs(inum), iden)
        else:
            return "{0} + {1}*I/{2}".format(real, inum, iden)

class Integer(Numeric):
    def __init__(self, *args, **kwargs):
        super(Integer, self).__init__(*args, **kwargs)

        try:
            self._real = init_integer(self._real)
        except ValueError: # invalid number
            msg = "can't create Integer from argument: '{0}'".format(self._real)
            raise ValueError(msg)

        try:
            self._imag = init_integer(self._imag)
        except ValueError: # invalid number
            msg = "can't create Integer from argument: '{0}'".format(self._imag)
            raise ValueError(msg)

    def __str__(self):
        """x.__str__() <==> str(x)"""
        real, imag = self._real, self._imag

        if imag == 0:
            return "{0}".format(real)
        if imag < 0:
            return "{0} - {1}*I".format(real, abs(imag))
        else:
            return "{0} + {1}*I".format(real, imag)

# from .numerify import numerify
# from .printing import str_integer_type, str_rational_type, str_float_type, str_numeric_type
# #from sympy import sympify, Integer, Rational, Float, I
#

#
# class Numeric(NAGObject):
#     """Base class for numeric types"""
#
#     def __init__(self, *args, **kwargs):
#         super(Numeric, self).__init__(*args, **kwargs)
#
#         if isinstance(self, Integer):
#             numeric_type = "Integer"
#         elif isinstance(self, GaussianInteger):
#             numeric_type = "GaussianInteger"
#         elif isinstance(self, Rational):
#             numeric_type = "Rational"
#         elif isinstance(self, GaussianRational):
#             numeric_type = "GaussianRational"
#         elif isinstance(self, Float):
#             numeric_type = "Float"
#         elif isinstance(self, Complex):
#             numeric_type = "Complex"
#         else:
#             numeric_type = None
#
#         try:
#             self._real, self._imag = numerify(*args, force_type=numeric_type)
#         except TypeError:
#             raise
#         except ValueError:
#             raise
#
#         self._prec = -1
#         rkeys = self._real.keys()
#         ikeys = self._imag.keys()
#         # set precision if a floating-point type
#         if rkeys:
#             x = self._real[rkeys[0]]
#             if str(type(x)) == "<type 'mpfr'>": # find a fix for this
#                 self._prec = x.precision
#         elif ikeys:
#             x = self._imag[ikeys[0]]
#             if str(type(x)) == "<type 'mpfr'>":
#                 self._prec = x.precision
#         self._shape = len(*args)
#
#     def __neg__(self):
#         """x.__neg__() <==> -x"""
#         rkeys = self._real.keys()
#         ikeys = self._imag.keys()
#         reals = {}
#         imags = {}
#         for k in rkeys:
#             reals[k] = -self._real[k]
#         for k in ikeys:
#             imags[k] = -self._imag[k]
#
#         final_str = str_numeric_type((reals, imags), ntype=self.__class__,
#                                      shape=self._shape)
#         if self._shape > 1:
#             final_str = final_str[1:-1]
#             reps = final_str.split(", ")
#         else:
#             reps = [final_str]
#         result = self.__class__(reps, prec=self._prec)
#         return result
#
#     def __eq__(self, other):
#         """x.__eq__(y) <==> x == y"""
#         # TODO: check for equality with Python builtins
#         if not isinstance(other, Numeric):
#             return False
#         elif self._shape != other._shape:
#             return False
#         else:
#             srkeys = self._real.keys()
#             sikeys = self._imag.keys()
#             orkeys = other._real.keys()
#             oikeys = other._imag.keys()
#
#             if srkeys != orkeys or sikeys != oikeys:
#                 return False
#             shape = self._shape
#             isequal = True
#             for i in range(shape):
#                 if i in srkeys:
#                     isequal = (self._real[i] == other._real[i])
#                 if i in sikeys:
#                     isequal = (self._imag[i] == other._imag[i])
#                 if not isequal:
#                     return False
#             return True
#
#     def __abs__(self):
#         """
#         x.__abs__() <==> abs(x)
#         returns the 2-norm of self, to double precision
#         """
#         from math import sqrt
#
#         reals = self._real
#         imags = self._imag
#         rkeys = reals.keys()
#         ikeys = imags.keys()
#         shape = self._shape
#
#         absval = 0.0
#         for i in range(shape):
#             if i in ikeys and i in okeys:
#                 absval += reals[i]**2 + imags[i]**2
#             elif i in rkeys:
#                 absval += reals[i]**2
#             elif i in ikeys:
#                 absval += imags[i]**2
#         return sqrt(absval)
#
#     def __add__(self, other):
#         """x.__add__(y) <==> x + y"""
#         # try:
#         #     newcls = promotion_map(self, other)
#         # except TypeError:
#         #     msg = ("unsupported operand type(s) for +: "
#         #            "'{0}' and '{1}'".format(type(self), type(other)))
#         #     raise TypeError(msg)
#
#         if isinstance(other, Numeric):
#             if isinstance(self, Complex) and isinstance(other, Complex): # works with Floats too
#                 working_precision = min(self._prec, other._prec)
#             elif isinstance(self, Complex):
#                 working_precision = self._prec
#             elif isinstance(other, Complex):
#                 working_precision = other._prec
#             else:
#                 working_precision = -1
#
#             if self._shape != other._shape:
#                 msg = ("incompatible operand shapes "
#                        "{0} and {1}".format(self._shape, other._shape))
#                 raise ShapeError(msg)
#             newcls = promotion_map(self, other)
#             sreals = self._real.keys()
#             simags = self._imag.keys()
#             oreals = other._real.keys()
#             oimags = other._imag.keys()
#             reals = {}
#             imags = {}
#             for i in range(self._shape):
#                 # real parts
#                 if i in sreals and i in oreals:
#                     if working_precision != -1:
#                         reals[i] = gmpy2.mpfr(self._real[i] + other._real[i], working_precision)
#                     else:
#                         reals[i] = self._real[i] + other._real[i]
#                 elif i in sreals:
#                     reals[i] = self._real[i]
#                 elif i in oreals:
#                     reals[i] = other._real[i]
#                 # imaginary parts
#                 if i in simags and i in oimags:
#                     if working_precision != -1:
#                         imags[i] = gmpy2.mpfr(self._imag[i] + other._imag[i], working_precision)
#                     else:
#                         imags[i] = self._imag[i] + other._imag[i]
#                 elif i in simags:
#                     imags[i] = self._imag[i]
#                 elif i in oimags:
#                     imags[i] = other._imag[i]
#                 # clean up any zeros
#                 if i in reals.keys():
#                     if reals[i] == 0:
#                         reals.pop(i)
#                 if i in imags.keys():
#                     if imags[i] == 0:
#                         imags.pop(i)
#
#             final_str = str_numeric_type((reals, imags), ntype=newcls,
#                                          shape=self._shape)
#             if self._shape > 1:
#                 final_str = final_str[1:-1]
#                 reps = final_str.split(", ")
#             else:
#                 reps = [final_str]
#             result = newcls(reps, prec=working_precision)
#             return result
#         elif self._shape == 1:
#             if isinstance(other, complex):
#                 other = Complex([other])
#             elif isinstance(other, float):
#                 other = Float([other])
#             elif type(other) in (int, long):
#                 other = Integer([other])
#             else:
#                 msg = ("unsupported operand type(s) for +: "
#                        "'{0}' and '{1}'".format(type(self), type(other)))
#                 raise TypeError(msg)
#             return self.__add__(other)
#         else:
#             msg = ("unsupported operand type(s) for +: "
#                    "'{0}' and '{1}'".format(type(self), type(other)))
#             raise TypeError(msg)
#
#     def __sub__(self, other):
#         """x.__sub__(y) <==> x - y"""
#         try:
#             minus_other = -other
#             return self + minus_other
#         except TypeError:
#             msg = ("unsupported operand type(s) for -: "
#                    "'{0}' and '{1}'".format(type(self), type(other)))
#             raise TypeError(msg)
#         except ShapeError:
#             msg = ("incompatible operand shapes "
#                    "{0} and {1}".format(self._shape, other._shape))
#             raise ShapeError(msg)
#
#     def __rsub__(self, other):
#         """x.__rsub__(y) <==> y - x"""
#         try:
#             return -(self - other)
#         except TypeError:
#             msg = ("unsupported operand type(s) for -: "
#                    "'{0}' and '{1}'".format(type(other), type(self)))
#             raise TypeError(msg)
#         except ShapeError:
#             msg = ("incompatible operand shapes "
#                    "{0} and {1}".format(other._shape, self._shape))
#             raise ShapeError(msg)
#
#     def __mul__(self, other):
#         """x.__mul__(y) <==> x*y"""
#         if isinstance(other, Numeric):
#             if isinstance(self, Complex) and isinstance(other, Complex): # works with Floats too
#                 working_precision = min(self._prec, other._prec)
#             elif isinstance(self, Complex):
#                 working_precision = self._prec
#             elif isinstance(other, Complex):
#                 working_precision = other._prec
#             else:
#                 working_precision = -1
#
#             newcls = promotion_map(self, other)
#             if self.is_scalar and other.is_scalar:
#                 shape = 1
#                 if self._real:
#                     sreal = self._real[0]
#                 else:
#                     sreal = 0
#                 if self._imag:
#                     simag = self._imag[0]
#                 else:
#                     simag = 0
#                 if other._real:
#                     oreal = other._real[0]
#                 else:
#                     oreal = 0
#                 if other._imag:
#                     oimag = other._imag[0]
#                 else:
#                     oimag = 0
#
#                 if working_precision != -1:
#                     tmp1 = gmpy2.mpfr(sreal*oreal, working_precision)
#                     tmp2 = gmpy2.mpfr(simag*oimag, working_precision)
#                     real = gmpy2.mpfr(tmp1 - tmp2, working_precision)
#
#                     tmp1 = gmpy2.mpfr(sreal*oimag, working_precision)
#                     tmp2 = gmpy2.mpfr(simag*oreal, working_precision)
#                     imag = gmpy2.mpfr(tmp1 + tmp2, working_precision)
#                 else:
#                     real = sreal*oreal - simag*oimag
#                     imag = sreal*oimag + simag*oreal
#
#                 if real != 0:
#                     reals = {0:real}
#                 else:
#                     reals = {}
#                 if imag != 0:
#                     imags = {0:imag}
#                 else:
#                     imags = {}
#             elif self.is_scalar:
#                 shape = other._shape
#                 if self._real:
#                     sreal = self._real[0]
#                 else:
#                     sreal = 0
#                 if self._imag:
#                     simag = self._imag[0]
#                 else:
#                     simag = 0
#
#                 reals = {}
#                 imags = {}
#                 orkeys = other._real.keys()
#                 oikeys = other._imag.keys()
#                 for i in range(shape):
#                     if i in orkeys:
#                         oreal = other._real[i]
#                     else:
#                         oreal = 0
#                     if i in oikeys:
#                         oimag = other._imag[i]
#                     else:
#                         oimag = 0
#
#                     if working_precision != -1:
#                         tmp1 = gmpy2.mpfr(sreal*oreal, working_precision)
#                         tmp2 = gmpy2.mpfr(simag*oimag, working_precision)
#                         real = gmpy2.mpfr(tmp1 - tmp2, working_precision)
#
#                         tmp1 = gmpy2.mpfr(sreal*oimag, working_precision)
#                         tmp2 = gmpy2.mpfr(simag*oreal, working_precision)
#                         imag = gmpy2.mpfr(tmp1 + tmp2, working_precision)
#                     else:
#                         real = sreal*oreal - simag*oimag
#                         imag = sreal*oimag + simag*oreal
#                     if real:
#                         reals[i] = real
#                     if imag:
#                         imags[i] = imag
#
#             elif other.is_scalar:
#                 return other*self
#             else:
#                 msg = "operation does not make sense"
#                 raise ShapeError(msg)
#         elif type(other) in (int, long, float, complex):
#             raise NotImplementedError("not yet bud")
#         else:
#             msg = ("unsupported operand type(s) for *: "
#                    "'{0}' and '{1}'".format(type(self), type(other)))
#             raise TypeError(msg)
#
#         final_str = str_numeric_type((reals, imags), ntype=newcls,
#                                      shape=shape)
#         if shape > 1:
#             final_str = final_str[1:-1]
#             reps = final_str.split(", ")
#         else:
#             reps = [final_str]
#         result = newcls(reps, prec=working_precision)
#         return result
#
#     def __rmul__(self, other):
#         """x.__rmul__(y) <==> y*x"""
#         try:
#             return other*self
#         except TypeError:
#             msg = ("unsupported operand type(s) for *: "
#                    "'{0}' and '{1}'".format(type(other), type(self)))
#             raise TypeError(msg)
#         except ShapeError:
#             raise
#         except NotImplementedError:
#             raise
#
#     def __div__(self, other):
#         """x.__div__(y) <==> x/y"""
#         if isinstance(other, Numeric):
#             if not other.is_scalar:
#                 msg = "operation doesn't make sense"
#                 raise ShapeError(msg)
#
#             if isinstance(self, Complex) and isinstance(other, Complex): # works with Floats too
#                 working_precision = min(self._prec, other._prec)
#             elif isinstance(self, Complex):
#                 working_precision = self._prec
#             elif isinstance(other, Complex):
#                 working_precision = other._prec
#             else:
#                 working_precision = -1
#
#             newcls = promotion_map(self, other)
#             if issubclass(newcls, Integer) and not (self % other).is_zero:
#                 newcls = Rational
#             elif issubclass(newcls, GaussianInteger):
#                 newcls = GaussianRational
#             shape = self._shape
#             if self.is_scalar:
#                 if self._real:
#                     a = self._real[0]
#                 else:
#                     a = 0
#                 if self._imag:
#                     b = self._imag[0]
#                 else:
#                     b = 0
#                 if other._real:
#                     c = other._real[0]
#                 else:
#                     c = 0
#                 if other._imag:
#                     d = other._imag[0]
#                 else:
#                     d = 0
#
#                 if c == d == 0:
#                     msg = "division by zero"
#                     raise ZeroDivisionError(msg)
#
#                 if working_precision != -1:
#                     c2 = gmpy2.mpfr(c**2, working_precision)
#                     d2 = gmpy2.mpfr(d**2, working_precision)
#                     denom = gmpy2.mpfr(c2 + d2, working_precision)
#
#                     tmp1 = gmpy2.mpfr(a*c, working_precision)
#                     tmp2 = gmpy2.mpfr(b*d, working_precision)
#                     real = gmpy2.mpfr((tmp1 + tmp2)/denom, working_precision)
#
#                     tmp1 = gmpy2.mpfr(b*c, working_precision)
#                     tmp2 = gmpy2.mpfr(a*d, working_precision)
#                     imag = gmpy2.mpfr((tmp1 - tmp2)/denom, working_precision)
#                 else:
#                     real = gmpy2.mpq(a*c + b*d, c**2 + d**2)
#                     imag = gmpy2.mpq(b*c - a*d, c**2 + d**2)
#
#                 if real:
#                     reals = {0:real}
#                 else:
#                     reals = {}
#                 if imag:
#                     imags = {0:imag}
#                 else:
#                     imags = {}
#             else:
#                 reals = {}
#                 imags = {}
#                 rkeys = self._real.keys()
#                 ikeys = self._imag.keys()
#                 if other._real:
#                     c = other._real[0]
#                 else:
#                     c = 0
#                 if other._imag:
#                     d = other._imag[0]
#                 else:
#                     d = 0
#
#                 if working_precision != -1:
#                     c2 = gmpy2.mpfr(c**2, working_precision)
#                     d2 = gmpy2.mpfr(d**2, working_precision)
#                     denom = gmpy2.mpfr(c2 + d2, working_precision)
#                 else:
#                     denom = c**2 + d**2
#
#                 if c == d == 0:
#                     msg = "division by zero"
#                     raise ZeroDivisionError(msg)
#
#                 for i in range(shape):
#                     if i in rkeys:
#                         a = self._real[i]
#                     else:
#                         a = 0
#                     if i in ikeys:
#                         b = self._imag[i]
#                     else:
#                         b = 0
#
#                     if working_precision != -1:
#                         tmp1 = gmpy2.mpfr(a*c, working_precision)
#                         tmp2 = gmpy2.mpfr(b*d, working_precision)
#                         real = gmpy2.mpfr((tmp1 + tmp2)/denom, working_precision)
#
#                         tmp1 = gmpy2.mpfr(b*c, working_precision)
#                         tmp2 = gmpy2.mpfr(a*d, working_precision)
#                         imag = gmpy2.mpfr((tmp1 - tmp2)/denom, working_precision)
#                     else:
#                         real = gmpy2.mpq(a*c + b*d, denom)
#                         imag = gmpy2.mpq(b*c - a*d, denom)
#
#                     if real:
#                         reals[i] = real
#                     if imag:
#                         imags[i] = imag
#
#         elif type(other) in (int, long, float, complex):
#             raise NotImplementedError("not yet bud")
#         else:
#             msg = ("unsupported operand type(s) for *: "
#                    "'{0}' and '{1}'".format(type(self), type(other)))
#             raise TypeError(msg)
#
#         final_str = str_numeric_type((reals, imags), ntype=newcls,
#                                      shape=shape)
#         if shape > 1:
#             final_str = final_str[1:-1]
#             reps = final_str.split(", ")
#         else:
#             reps = [final_str]
#         result = newcls(reps, prec=working_precision)
#         return result
#
#     @property
#     def is_number(self):
#         return True
#     @property
#     def shape(self):
#         return self._shape
#     @property
#     def is_scalar(self):
#         return self._shape == 1
#     @property
#     def is_real(self):
#         return not self._imag
#     @property
#     def is_imag(self):
#         return not self._real and not not self._real
#     @property
#     def is_zero(self):
#         return not self._real and not self._imag
#
# class Complex(Numeric):
#     """Complex floating-point vector type"""
#
#     def __init__(self, *args, **kwargs):
#         super(Complex, self).__init__(*args, **kwargs)
#
#     def __repr__(self):
#         """x.__repr__() <==> repr(x)"""
#         from naglib.envconstants import replen
#         return str_float_type(self, truncate=replen)
#
#     def __str__(self):
#         """x.__str__() <==> str(x)"""
#         return str_float_type(self)
#
# class Float(Complex):
#     """Floating-point vector type"""
#
#     def __init__(self, *args, **kwargs):
#         super(Float, self).__init__(*args, **kwargs)
#
# class GaussianRational(Numeric):
#     """Gaussian rational vector type"""
#
#     def __init__(self, *args, **kwargs):
#         super(GaussianRational, self).__init__(*args, **kwargs)
#
#     def __repr__(self):
#         """x.__repr__() <==> repr(x)"""
#         from naglib.envconstants import replen
#         return str_rational_type(self, truncate=replen)
#
#     def __str__(self):
#         """x.__str__() <==> str(x)"""
#         return str_rational_type(self)
#
# class Rational(GaussianRational):
#     """Rational vector type"""
#
#     def __init__(self, *args, **kwargs):
#         super(GaussianRational, self).__init__(*args, **kwargs)
#
# class GaussianInteger(GaussianRational):
#     """Gaussian integer vector type"""
#
#     def __init__(self, *args, **kwargs):
#         super(GaussianInteger, self).__init__(*args, **kwargs)
#
#     def __repr__(self):
#         """x.__repr__() <==> repr(x)"""
#         from naglib.envconstants import replen
#         return str_integer_type(self, truncate=replen)
#
#     def __str__(self):
#         """x.__str__() <==> str(x)"""
#         return str_integer_type(self)
#
#     def __mod__(self, other):
#         """x.__mod__(y) <==> x % y"""
#         if isinstance(other, Integer) or type(other) in (int, long):
#             if isinstance(other, Integer):
#                 if not other.is_scalar:
#                     msg = ("incompatible operand shapes "
#                            "{0} and {1}".format(self._shape, other._shape))
#                     raise ShapeError(msg)
#                 other = other._real[0]
#
#             reals = self._real
#             imags = self._imag
#             rkeys = reals.keys()
#             ikeys = imags.keys()
#             shape = self._shape
#
#             nreals = {}
#             nimags = {}
#
#             for i in range(shape):
#                 if i in rkeys:
#                     nreals[i] = reals[i] % other
#                     if nreals[i] == 0:
#                         nreals.pop(i)
#                 if i in ikeys:
#                     nimags[i] = imags[i] % other
#                     if nimags[i] == 0:
#                         nimags.pop(i)
#             final_str = str_integer_type((nreals, nimags),shape=shape)
#             if shape > 1:
#                 final_str = final_str[1:-1]
#                 reps = final_str.split(", ")
#             else:
#                 reps = [final_str]
#             result = self.__class__(reps)
#             return result
#         else:
#             msg = ""
#             raise TypeError(msg)
#
# class Integer(GaussianInteger):
#     """Integer vector type"""
#
#     def __init__(self, *args, **kwargs):
#         super(Integer, self).__init__(*args, **kwargs)
#
# class ShapeError(Exception):
#     def __init__(self, message):
#         self.message = message
#
#     def __str__(self):
#         return self.message
