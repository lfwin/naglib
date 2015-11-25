"""
Numeric types in NAGlib.
Numbers are actually represented in NAGlib as arrays of numbers.
"""

from __future__ import division, print_function

import gmpy2
import re

from .base import NAGObject
from .core import string_types
from .tonumeric import gmpy2ify
from .printing import str_integer_type, str_rational_type, str_float_type
#from sympy import sympify, Integer, Rational, Float, I

def promotion_map(left, right):
    left = left.__class__
    right = right.__class__
    from fractions import gcd

    pmap = {Complex:1,
            Float:2,
            GaussianRational:3,
            Rational:6,
            GaussianInteger:9,
            Integer:18}
    pinv = dict([(pmap[k], k) for k in pmap.keys()])

    ltype = pmap[left]
    rtype = pmap[right]
    return pinv[gcd(ltype, rtype)]

class Numeric(NAGObject):
    """Base class for numeric types"""

    def __init__(self, *args, **kwargs):
        super(Numeric, self).__init__(*args, **kwargs)

        if isinstance(self, Integer):
            numeric_type = "Integer"
        elif isinstance(self, GaussianInteger):
            numeric_type = "GaussianInteger"
        elif isinstance(self, Rational):
            numeric_type = "Rational"
        elif isinstance(self, GaussianRational):
            numeric_type = "GaussianRational"
        elif isinstance(self, Float):
            numeric_type = "Float"
        elif isinstance(self, Complex):
            numeric_type = "Complex"
        else:
            numeric_type = None

        self._prec = -1

        # short-circuit for arithmetic operations
        kkeys = kwargs.keys()
        if "real" in kkeys:
            self._imag = {}
            reals = kwargs["real"]
            try:
                new_reals,junk = gmpy2ify(reals.values(), force_type=numeric_type)
                new_reals = new_reals.values()
            except TypeError:
                raise
            except ValueError:
                raise
            self._real = reals.copy()
            rkeys = self._real.keys()
            for i in range(len(rkeys)):
                self._real[rkeys[i]] = new_reals[i] # due to promotion
        if "imag" in kkeys:
            if not hasattr(self, "_real"):
                self._real = {}
            imags = kwargs["imag"]
            try:
                new_imags,junk = gmpy2ify(imags.values(), force_type=numeric_type)
                new_imags = new_imags.values()
            except TypeError:
                raise
            except ValueError:
                raise
            self._imag = imags.copy()
            ikeys = self._imag.keys()
            for i in range(len(ikeys)):
                self._imag[ikeys[i]] = new_imags[i]

        if not hasattr(self, "_real"):
            try:
                self._real, self._imag = gmpy2ify(*args, force_type=numeric_type)
            except TypeError:
                raise
            except ValueError:
                raise

        rkeys = self._real.keys()
        ikeys = self._imag.keys()
        # set precision if a floating-point type
        if rkeys:
            x = self._real[rkeys[0]]
            if str(type(x)) == "<type 'mpfr'>": # this is so stupid; find a fix for this
                self._prec = x.precision
        elif ikeys:
            x = self._imag[ikeys[0]]
            if str(type(x)) == "<type 'mpfr'>": # this is so stupid; find a fix for this
                self._prec = x.precision
        elif "prec" in kkeys:
            self._prec = kwargs["prec"]

        self._is_scalar = len(*args) == 1
        self._is_real = (not self._imag)
        self._is_imaginary = (not self._real)
        self._shape = len(*args)
        self._is_number = True

    def __neg__(self):
        """x.__neg__() <==> -x"""
        rkeys = self._real.keys()
        ikeys = self._imag.keys()
        reals = {}
        imags = {}
        for k in rkeys:
            reals[k] = -self._real[k]
        for k in ikeys:
            imags[k] = -self._imag[k]
        if isinstance(self, GaussianInteger):
            final_str = str_integer_type((reals, imags),from_real_imag=self._shape)
        elif isinstance(self, GaussianRational):
            final_str = str_rational_type((reals, imags),from_real_imag=self._shape)
        else:
            final_str = str_float_type((reals, imags),from_real_imag=self._shape)
        if self._shape > 1:
            final_str = final_str[1:-1]
            reps = final_str.split(", ")
        else:
            reps = [final_str]
        result = self.__class__(reps, prec=self._prec)
        return result


    def __add__(self, other):
        """x.__add__(y) <==> x + y"""
        if isinstance(other, Numeric):
            if isinstance(self, Complex) and isinstance(other, Complex): # works with Floats too
                working_precision = min(self._prec, other._prec)
            elif isinstance(self, Complex):
                working_precision = self._prec
            elif isinstance(other, Complex):
                working_precision = other._prec
            else:
                working_precision = -1

            if self._shape != other._shape:
                msg = ("incompatible operand shapes "
                       "{0} and {1}".format(self._shape, other._shape))
                raise ShapeError(msg)
            newcls = promotion_map(self, other)
            sreals = self._real.keys()
            simags = self._imag.keys()
            oreals = other._real.keys()
            oimags = other._imag.keys()
            reals = {}
            imags = {}
            for i in range(self._shape):
                # real parts
                if i in sreals and i in oreals:
                    if working_precision != -1:
                        reals[i] = gmpy2.mpfr(self._real[i] + other._real[i], working_precision)
                    else:
                        reals[i] = self._real[i] + other._real[i]
                elif i in sreals:
                    reals[i] = self._real[i]
                elif i in oreals:
                    reals[i] = other._real[i]
                # imaginary parts
                if i in simags and i in oimags:
                    if working_precision != -1:
                        imags[i] = gmpy2.mpfr(self._imag[i] + other._imag[i], working_precision)
                    else:
                        imags[i] = self._imag[i] + other._imag[i]
                elif i in simags:
                    imags[i] = self._imag[i]
                elif i in oimags:
                    imags[i] = other._imag[i]
                # clean up any zeros
                if i in reals.keys():
                    if reals[i] == 0:
                        reals.pop(i)
                if i in imags.keys():
                    if imags[i] == 0:
                        imags.pop(i)

            if isinstance(newcls, GaussianInteger):
                final_str = str_integer_type((reals, imags),from_real_imag=self._shape)
            elif isinstance(newcls, GaussianRational):
                final_str = str_rational_type((reals, imags),from_real_imag=self._shape)
            else:
                final_str = str_float_type((reals, imags),from_real_imag=self._shape)
            if self._shape > 1:
                final_str = final_str[1:-1]
                reps = final_str.split(", ")
            else:
                reps = [final_str]
            result = newcls(reps, prec=working_precision)
            return result
        elif self._shape == 1:
            if isinstance(other, complex):
                other = Complex([other])
            elif isinstance(other, float):
                other = Float([other])
            elif type(other) in (int, long):
                other = Integer([other])
            else:
                msg = ("unsupported operand type(s) for +: "
                       "'{0}' and '{1}'".format(type(self), type(other)))
                raise TypeError(msg)
            return self.__add__(other)
        else:
            msg = ("unsupported operand type(s) for +: "
                   "'{0}' and '{1}'".format(type(self), type(other)))
            raise TypeError(msg)

    def __sub__(self, other):
        """x.__sub__(y) <==> x - y"""
        try:
            minus_other = -other
            return self + minus_other
        except TypeError:
            msg = ("unsupported operand type(s) for -: "
                   "'{0}' and '{1}'".format(type(self), type(other)))
            raise TypeError(msg)
        except ShapeError:
            msg = ("incompatible operand shapes "
                   "{0} and {1}".format(self._shape, other._shape))
            raise ShapeError(msg)

    def __rsub__(self, other):
        """x.__rsub__(y) <==> y - x"""
        try:
            return -(self - other)
        except TypeError:
            msg = ("unsupported operand type(s) for -: "
                   "'{0}' and '{1}'".format(type(other), type(self)))
            raise TypeError(msg)
        except ShapeError:
            msg = ("incompatible operand shapes "
                   "{0} and {1}".format(other._shape, self._shape))
            raise ShapeError(msg)

    def __mul__(self, other):
        """x.__mul__(y) <==> x*y"""
        if isinstance(other, Numeric):
            if isinstance(self, Complex) and isinstance(other, Complex): # works with Floats too
                working_precision = min(self._prec, other._prec)
            elif isinstance(self, Complex):
                working_precision = self._prec
            elif isinstance(other, Complex):
                working_precision = other._prec
            else:
                working_precision = -1

            newcls = promotion_map(self, other)
            if self._is_scalar and other._is_scalar:
                shape = 1
                if self._real:
                    sreal = self._real[0]
                else:
                    sreal = 0
                if self._imag:
                    simag = self._imag[0]
                else:
                    simag = 0
                if other._real:
                    oreal = other._real[0]
                else:
                    oreal = 0
                if other._imag:
                    oimag = other._imag[0]
                else:
                    oimag = 0

                if working_precision != -1:
                    tmp1 = gmpy2.mpfr(sreal*oreal, working_precision)
                    tmp2 = gmpy2.mpfr(simag*oimag, working_precision)
                    real = gmpy2.mpfr(tmp1 - tmp2, working_precision)

                    tmp1 = gmpy2.mpfr(sreal*oimag, working_precision)
                    tmp2 = gmpy2.mpfr(simag*oreal, working_precision)
                    imag = gmpy2.mpfr(tmp1 + tmp2, working_precision)
                else:
                    real = sreal*oreal - simag*oimag
                    imag = sreal*oimag + simag*oreal

                if real != 0:
                    reals = {0:real}
                else:
                    reals = {}
                if imag != 0:
                    imags = {0:imag}
                else:
                    imags = {}
            elif self._is_scalar:
                shape = other._shape
                if self._real:
                    sreal = self._real[0]
                else:
                    sreal = 0
                if self._imag:
                    simag = self._imag[0]
                else:
                    simag = 0

                reals = {}
                imags = {}
                orkeys = other._real.keys()
                oikeys = other._imag.keys()
                for i in range(shape):
                    if i in orkeys:
                        oreal = other._real[i]
                    else:
                        oreal = 0
                    if i in oikeys:
                        oimag = other._imag[i]
                    else:
                        oimag = 0

                    if working_precision != -1:
                        tmp1 = gmpy2.mpfr(sreal*oreal, working_precision)
                        tmp2 = gmpy2.mpfr(simag*oimag, working_precision)
                        real = gmpy2.mpfr(tmp1 - tmp2, working_precision)

                        tmp1 = gmpy2.mpfr(sreal*oimag, working_precision)
                        tmp2 = gmpy2.mpfr(simag*oreal, working_precision)
                        imag = gmpy2.mpfr(tmp1 + tmp2, working_precision)
                    else:
                        real = sreal*oreal - simag*oimag
                        imag = sreal*oimag + simag*oreal
                    if real:
                        reals[i] = real
                    if imag:
                        imags[i] = imag

            elif other._is_scalar:
                return other*self
            else:
                msg = "operation does not make sense"
                raise ShapeError(msg)
        elif type(other) in (int, long, float, complex):
            raise NotImplementedError("not yet bud")
        else:
            msg = ("unsupported operand type(s) for *: "
                   "'{0}' and '{1}'".format(type(self), type(other)))
            raise TypeError(msg)

        if isinstance(newcls, GaussianInteger):
            final_str = str_integer_type((reals, imags),from_real_imag=shape)
        elif isinstance(newcls, GaussianRational):
            final_str = str_rational_type((reals, imags),from_real_imag=shape)
        else:
            final_str = str_float_type((reals, imags),from_real_imag=shape)
        if shape > 1:
            final_str = final_str[1:-1]
            reps = final_str.split(", ")
        else:
            reps = [final_str]
        result = newcls(reps, prec=working_precision)
        return result

    def __rmul__(self, other):
        """x.__rmul__(y) <==> y*x"""
        try:
            return other*self
        except TypeError:
            msg = ("unsupported operand type(s) for *: "
                   "'{0}' and '{1}'".format(type(other), type(self)))
            raise TypeError(msg)
        except ShapeError:
            raise
        except NotImplementedError:
            raise

    def __div__(self, other):
        """x.__div__(y) <==> x/y"""
        if isinstance(other, Numeric):
            if not other._is_scalar:
                msg = "operation doesn't make sense"
                raise ShapeError(msg)

            if isinstance(self, Complex) and isinstance(other, Complex): # works with Floats too
                working_precision = min(self._prec, other._prec)
            elif isinstance(self, Complex):
                working_precision = self._prec
            elif isinstance(other, Complex):
                working_precision = other._prec
            else:
                working_precision = -1

            newcls = promotion_map(self, other)
            if self._is_scalar:
                if self._real:
                    a = self._real[0]
                else:
                    a = 0
                if self._imag:
                    b = self._imag[0]
                else:
                    b = 0
                if other._real:
                    c = other._real[0]
                else:
                    c = 0
                if other._imag:
                    d = other._imag[0]
                else:
                    d = 0

                if c == d == 0:
                    msg = "division by zero"
                    raise ZeroDivisionError(msg)

                if working_precision != -1:
                    c2 = gmpy2.mpfr(c**2, working_precision)
                    d2 = gmpy2.mpfr(d**2, working_precision)
                    denom = gmpy2.mpfr(c2 + d2, working_precision)

                    tmp1 = gmpy2.mpfr(a*c, working_precision)
                    tmp2 = gmpy2.mpfr(b*d, working_precision)
                    real = gmpy2.mpfr((tmp1 + tmp2)/denom, working_precision)

                    tmp1 = gmpy2.mpfr(b*c, working_precision)
                    tmp2 = gmpy2.mpfr(a*d, working_precision)
                    imag = gmpy2.mpfr((tmp1 - tmp2)/denom, working_precision)
                else:
                    real = (a*c + b*d)/(c**2 + d**2)
                    imag = (b*c - a*d)/(c**2 + d**2)

                if real:
                    reals = {0:real}
                else:
                    reals = {}
                if imag:
                    imags = {0:imag}
                else:
                    imags = {}
            else:
                shape = self._shape
                reals = {}
                imags = {}
                rkeys = self._real.keys()
                ikeys = self._imag.keys()
                if other._real:
                    c = other._real[0]
                else:
                    c = 0
                if other._imag:
                    d = other._imag[0]
                else:
                    d = 0

                if working_precision != -1:
                    c2 = gmpy2.mpfr(c**2, working_precision)
                    d2 = gmpy2.mpfr(d**2, working_precision)
                    denom = gmpy2.mpfr(c2 + d2, working_precision)
                else:
                    denom = c**2 + d**2

                if c == d == 0:
                    msg = "division by zero"
                    raise ZeroDivisionError(msg)

                for i in range(shape):
                    if i in rkeys:
                        a = self._real[i]
                    else:
                        a = 0
                    if i in ikeys:
                        b = self._imag[i]
                    else:
                        b = 0

                    if working_precision != -1:
                        tmp1 = gmpy2.mpfr(a*c, working_precision)
                        tmp2 = gmpy2.mpfr(b*d, working_precision)
                        real = gmpy2.mpfr((tmp1 + tmp2)/denom, working_precision)

                        tmp1 = gmpy2.mpfr(b*c, working_precision)
                        tmp2 = gmpy2.mpfr(a*d, working_precision)
                        imag = gmpy2.mpfr((tmp1 - tmp2)/denom, working_precision)
                    else:
                        real = (a*c + b*d)/denom
                        imag = (b*c - a*d)/denom

                    if real:
                        reals[i] = real
                    if imag:
                        imags[i] = imag

        elif type(other) in (int, long, float, complex):
            raise NotImplementedError("not yet bud")
        else:
            msg = ("unsupported operand type(s) for *: "
                   "'{0}' and '{1}'".format(type(self), type(other)))
            raise TypeError(msg)

        if isinstance(newcls, GaussianInteger):
            final_str = str_integer_type((reals, imags),from_real_imag=shape)
        elif isinstance(newcls, GaussianRational):
            final_str = str_rational_type((reals, imags),from_real_imag=shape)
        else:
            final_str = str_float_type((reals, imags),from_real_imag=shape)
        if shape > 1:
            final_str = final_str[1:-1]
            reps = final_str.split(", ")
        else:
            reps = [final_str]
        result = newcls(reps, prec=working_precision)
        return result

class Complex(Numeric):
    """Complex floating-point vector type"""

    def __init__(self, *args, **kwargs):
        super(Complex, self).__init__(*args, **kwargs)

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        from naglib.envconstants import replen
        return str_float_type(self, truncate=replen)

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return str_float_type(self)

class Float(Complex):
    """Floating-point vector type"""

    def __init__(self, *args, **kwargs):
        super(Float, self).__init__(*args, **kwargs)

class GaussianRational(Numeric):
    """Gaussian rational vector type"""

    def __init__(self, *args, **kwargs):
        super(GaussianRational, self).__init__(*args, **kwargs)

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        from naglib.envconstants import replen
        return str_rational_type(self, truncate=replen)

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return str_rational_type(self)

class Rational(GaussianRational):
    """Rational vector type"""

    def __init__(self, *args, **kwargs):
        super(GaussianRational, self).__init__(*args, **kwargs)

class GaussianInteger(GaussianRational):
    """Gaussian integer vector type"""

    def __init__(self, *args, **kwargs):
        super(GaussianInteger, self).__init__(*args, **kwargs)

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        from naglib.envconstants import replen
        return str_integer_type(self, truncate=replen)

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return str_integer_type(self)

class Integer(Rational):
    """Integer vector type"""

    def __init__(self, *args, **kwargs):
        super(Integer, self).__init__(*args, **kwargs)


class ShapeError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
