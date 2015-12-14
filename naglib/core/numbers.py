"""
Numeric types in NAGlib.
Complex numbers are first-class objects in NAGlib
"""

from __future__ import division, print_function

from .base import NAGObject
from .core import string_types
from .groundtypes import NUMBERS

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
    else:
        try:
            val = float(val)
        except ValueError:
            raise

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
            elif isinstance(args[0], Numeric):
                self._real = args[0].real
                self._imag = args[0].imag
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

    def __str__(self):
        """x.__str__() <==> str(x)"""
        real, imag = self._real, self._imag

        if imag == 0:
            return "{0}".format(real)
        if imag < 0:
            return "{0} - {1}*I".format(real, abs(imag))
        else:
            return "{0} + {1}*I".format(real, imag)

    def __copy__(self):
        """x.__copy__ <==> copy(x)"""
        cls = self.__class__
        real, imag = self._real, self._imag
        if hasattr(self, "prec"):
            prec = self.prec
            return cls((real, imag), prec)
        else:
            return cls((real, imag))

    def __coerce__(self, other, try_float=False):
        left = self.__class__
        right = other.__class__
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

        if try_float:
            return Float
        else:
            return pinv[gcd(ltype, rtype)]

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
        else:
            from math import sqrt

        return float(sqrt(self._real**2 + self._imag**2))

    def __neg__(self):
        cls = self.__class__
        return cls((-self._real, -self._imag))

    def __add__(self, other):
        """x.__add__(y) <==> x + y"""
        try:
            cls = self.__coerce__(other)
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

    def __radd__(self, other):
        """x.__radd__(y) <==> y + x"""
        try:
            cls = self.__coerce__(other)
        except TypeError:
            msg = "unsupported operand type(s) for +: '{0}' and '{1}'".format(type(other), type(self))
            raise TypeError(msg)

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        try:
            real = oreal + sreal
            imag = oimag + simag
        except:
            nclass = real.__class__
            oreal = nclass(str(oreal)) # hacky
            oimag = nclass(str(oimag))
            real = oreal + sreal
            imag = oimag + simag

        return cls((real, imag))

    def __sub__(self, other):
        """x.__sub__(y) <==> x - y"""
        try:
            cls = self.__coerce__(other)
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
            cls = self.__coerce__(other)
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
            cls = self.__coerce__(other)
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

    def __rmul__(self, other):
        """x.__rmul__(y) <==> y*x"""
        try:
            cls = self.__coerce__(other)
        except TypeError:
            msg = "unsupported operand type(s) for *: '{0}' and '{1}'".format(type(other), type(self))
            raise TypeError(msg)

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        try:
            real = oreal*sreal - oimag*simag
            imag = oreal*simag + oimag*sreal
        except:
            nclass = real.__class__
            oreal = nclass(str(oreal)) # hacky
            oimag = nclass(str(oimag))
            real = oreal*sreal - oimag*simag
            imag = oreal*simag + oimag*sreal

        return cls((real, imag))

    def __div__(self, other):
        """x.__div__(y) <==> x/y"""
        try:
            cls = self.__coerce__(other)
        except TypeError:
            msg = "unsupported operand type(s) for /: '{0}' and '{1}'".format(type(self), type(other))
            raise TypeError(msg)

        if other == 0 or (hasattr(other, "is_zero") and other.is_zero()):
            msg = "division by zero"
            raise ZeroDivisionError(msg)

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        try:
            denom = oreal**2 + oimag**2
            real = (sreal*oreal + simag*oimag)/denom
            imag = (simag*oreal - sreal*oimag)/denom
        except:
            nclass = real.__class__
            oreal = nclass(str(oreal)) # hacky
            oimag = nclass(str(oimag))
            denom = oreal**2 + oimag**2
            real = (sreal*oreal + simag*oimag)/denom
            imag = (simag*oreal - sreal*oimag)/denom

        return cls((real, imag))

    def __rdiv__(self, other):
        """x.__rdiv__(y) <==> y/x"""
        try:
            cls = self.__coerce__(other)
        except TypeError:
            msg = "unsupported operand type(s) for /: '{0}' and '{1}'".format(type(other), type(self))
            raise TypeError(msg)

        if self == 0 or self.is_zero():
            msg = "division by zero"
            raise ZeroDivisionError(msg)

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        try:
            denom = sreal**2 + simag**2
            real = (sreal*oreal + simag*oimag)/denom
            imag = (sreal*oimag - simag*oreal)/denom
        except:
            nclass = real.__class__
            oreal = nclass(str(oreal)) # hacky
            oimag = nclass(str(oimag))
            denom = sreal**2 + simag**2
            real = (sreal*oreal + simag*oimag)/denom
            imag = (sreal*oimag - simag*oreal)/denom

        return cls((real, imag))

    def __pow__(self, other):
        """x.__pow__(y) <==> x**y"""
        try:
            cls = self.__coerce__(other, try_float=True)
        except TypeError:
            msg = "unsupported operand type(s) for **: '{0}' and '{1}'".format(type(self), type(other))
            raise TypeError(msg)

        if other == 1:
            return self.__copy__()
        elif other == 0:
            return cls(1)

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        # use polar coordinates and return a Float
        if hasattr(self, "prec"):
            sprec = self.prec
        else:
            sprec = -1
        if hasattr(other, "prec"):
            oprec = other.prec
        else:
            oprec = -1
        if sprec != -1 and oprec != -1:
            prec = min(sprec, oprec)
        elif sprec != -1:
            prec = sprec
        elif oprec != -1:
            prec = oprec
        else:
            prec = 53

        if self._ground_type == "gmpy2":
            from gmpy2 import context, local_context, sqrt, atan2, exp, log, cos, sin
            with local_context(context(), precision=prec):
                mod = sqrt(sreal**2 + simag**2)
                arg = atan2(simag, sreal)
                pmod = mod**oreal*exp(-arg*oimag)
                real = pmod*cos(oimag*log(mod) + oreal*arg)
                imag = pmod*sin(oimag*log(mod) + oreal*arg)
        elif self._ground_type == "sympy":
            from sympy import sqrt, atan2, exp, log, cos, sin
            mod = sqrt(sreal**2 + simag**2)
            if mod == 0:
                arg = 0
            else:
                arg = atan2(simag, sreal)
            pmod = mod**oreal*exp(-arg*oimag)
            real = pmod*cos(oimag*log(mod) + oreal*arg)
            imag = pmod*sin(oimag*log(mod) + oreal*arg)
        else:
            from math import sqrt, atan2, exp, log, cos, sin
            mod = sqrt(sreal**2 + simag**2)
            arg = atan2(simag, sreal)
            pmod = mod**oreal*exp(-arg*oimag)
            real = pmod*cos(oimag*log(mod) + oreal*arg)
            imag = pmod*sin(oimag*log(mod) + oreal*arg)

        return cls((real, imag), prec=prec)

    def __rpow__(self, other):
        """x.__pow__(y) <==> x**y"""
        try:
            cls = self.__coerce__(other, try_float=True)
        except TypeError:
            msg = "unsupported operand type(s) for **: '{0}' and '{1}'".format(type(other), type(self))
            raise TypeError(msg)

        if self == 1:
            if hasattr(other, "copy"):
                return other.__copy__()
            else:
                return other
        elif self == 0:
            return cls(1)

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        # use polar coordinates and return a Float
        if hasattr(self, "prec"):
            sprec = self.prec
        else:
            sprec = -1
        if hasattr(other, "prec"):
            oprec = other.prec
        else:
            oprec = -1
        if sprec != -1 and oprec != -1:
            prec = min(sprec, oprec)
        elif sprec != -1:
            prec = sprec
        elif oprec != -1:
            prec = oprec
        else:
            prec = 53

        if self._ground_type == "gmpy2":
            from gmpy2 import context, local_context, sqrt, atan2, exp, log, cos, sin
            with local_context(context(), precision=prec):
                mod = sqrt(oreal**2 + oimag**2)
                arg = atan2(oimag, oreal)
                pmod = mod**sreal*exp(-arg*simag)
                real = pmod*cos(simag*log(mod) + sreal*arg)
                imag = pmod*sin(simag*log(mod) + sreal*arg)
        elif self._ground_type == "sympy":
            from sympy import sqrt, atan2, exp, log, cos, sin
            mod = sqrt(oreal**2 + oimag**2)
            if mod == 0:
                arg = 0
            else:
                arg = atan2(oimag, oreal)
            pmod = mod**sreal*exp(-arg*simag)
            real = pmod*cos(simag*log(mod) + sreal*arg)
            imag = pmod*sin(simag*log(mod) + sreal*arg)
        else:
            from math import sqrt, atan2, exp, log, cos, sin
            mod = sqrt(oreal**2 + oimag**2)
            arg = atan2(oimag, oreal)
            pmod = mod**sreal*exp(-arg*simag)
            real = pmod*cos(simag*log(mod) + sreal*arg)
            imag = pmod*sin(simag*log(mod) + sreal*arg)

        return cls((real, imag), prec=prec)

    def arg(self):
        """the argument; returns a double-precision floating point number"""
        real, imag = self._real, self._imag
        if hasattr(self, "prec"):
            prec = self.prec
        else:
            prec = 53

        if self._ground_type == "gmpy2":
            from gmpy2 import atan2, context, local_context
            with local_context(context(), precision=prec):
                theta = atan2(imag, real)
                theta = float(theta)
        elif self._ground_type == "sympy":
            if real == imag == 0:
                theta = 0.0
            else:
                from sympy import atan2
                theta = float(atan2(imag, real))
        else:
            from math import atan2
            theta = atan2(imag, real)

        return theta

    def conjugate(self):
        """the complex conjugate"""
        cls = self.__class__
        real, imag = self._real, self._imag
        return cls((real, -imag))

    def copy(self):
        """returns a copy of self"""
        cls = self.__class__
        real, imag = self._real, self._imag
        if hasattr(self, "prec"):
            return cls((real, imag), self._prec)
        else:
            return cls((real, imag))

    def is_real(self):
        return abs(self._imag) == 0

    def is_zero(self):
        return self._real == self._imag == 0

    def polar(self):
        """polar coordinates"""
        return (self.__abs__(), self.arg())

    @property
    def real(self):
        return self._real
    @property
    def imag(self):
        return self._imag

class Float(Numeric):
    """Adaptive-multiprecision complex floating-point number"""
    def __init__(self, *args, **kwargs):
        super(Float, self).__init__(*args, **kwargs)
        kkeys = kwargs.keys()

        # this is meaningless if ground_type is "native"
        # TODO: account for this
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
        from math import ceil
        real,imag = self._real,self._imag

        rdps = idps = int(ceil(self._prec/3.33))
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
        prec = self._prec

        if self._ground_type == "gmpy2":
            from gmpy2 import context, local_context
            with local_context(context(), precision=prec):
                real, imag = -self._real, -self._imag
        else:
            real, imag = -self._real, -self._imag

        return cls((real, imag), prec=prec)

    def __add__(self, other):
        """x.__add__(y) <==> x + y"""
        try:
            cls = self.__coerce__(other)
        except TypeError:
            msg = "unsupported operand type(s) for +: '{0}' and '{1}'".format(type(self), type(other))
            raise TypeError(msg)

        if isinstance(other, Numeric) and hasattr(other, "prec"): # Float or derived
            prec = min(self._prec, other.prec)
        elif isinstance(other, Numeric) or hasattr(other, "numerator"): # Rational or Integer; exact
            # ints, longs, and Fractions have the "numerator" attribute
            prec = self._prec
        else:
            from naglib.envconstants import prec

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        if self._ground_type == "gmpy2":
            from gmpy2 import context, local_context
            with local_context(context(), precision=prec):
                try:
                    real = sreal + oreal
                    imag = simag + oimag
                except:
                    nclass = real.__class__
                    oreal = nclass(str(oreal), prec) # hacky
                    oimag = nclass(str(oimag), prec)
                    real = sreal + oreal
                    imag = simag + oimag
        else:
            try:
                real = sreal + oreal
                imag = simag + oimag
            except:
                nclass = real.__class__
                oreal = nclass(str(oreal), prec) # hacky
                oimag = nclass(str(oimag), prec)
                real = sreal + oreal
                imag = simag + oimag

        return cls((real, imag), prec=prec)

    def __radd__(self, other):
        """x.__radd__(y) <==> y + x"""
        try:
            cls = self.__coerce__(other)
        except TypeError:
            msg = "unsupported operand type(s) for +: '{0}' and '{1}'".format(type(other), type(self))
            raise TypeError(msg)

        if isinstance(other, Numeric) and hasattr(other, "prec"): # Float or derived
            prec = min(self._prec, other.prec)
        elif isinstance(other, Numeric) or hasattr(other, "numerator"): # Rational or Integer; exact
            # ints, longs, and Fractions have the "numerator" attribute
            prec = self._prec
        else:
            from naglib.envconstants import prec

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        if self._ground_type == "gmpy2":
            from gmpy2 import context, local_context
            with local_context(context(), precision=prec):
                try:
                    real = oreal + sreal
                    imag = oimag + simag
                except:
                    nclass = real.__class__
                    oreal = nclass(str(oreal), prec) # hacky
                    oimag = nclass(str(oimag), prec)
                    real = oreal + sreal
                    imag = oimag + simag
        else:
            try:
                real = oreal + sreal
                imag = oimag + simag
            except:
                nclass = real.__class__
                oreal = nclass(str(oreal), prec) # hacky
                oimag = nclass(str(oimag), prec)
                real = oreal + sreal
                imag = oimag + simag

        return cls((real, imag), prec=prec)

    def __sub__(self, other):
        """x.__sub__(y) <==> x - y"""
        try:
            cls = self.__coerce__(other)
        except TypeError:
            msg = "unsupported operand type(s) for -: '{0}' and '{1}'".format(type(self), type(other))
            raise TypeError(msg)

        if isinstance(other, Numeric) and hasattr(other, "prec"): # Float or derived
            prec = min(self._prec, other.prec)
        elif isinstance(other, Numeric) or hasattr(other, "numerator"): # Rational or Integer; exact
            # ints, longs, and Fractions have the "numerator" attribute
            prec = self._prec
        else:
            from naglib.envconstants import prec

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        if self._ground_type == "gmpy2":
            from gmpy2 import context, local_context
            with local_context(context(), precision=prec):
                try:
                    real = sreal - oreal
                    imag = simag - oimag
                except:
                    nclass = real.__class__
                    oreal = nclass(str(oreal), prec) # hacky
                    oimag = nclass(str(oimag), prec)
                    real = sreal - oreal
                    imag = simag - oimag
        else:
            try:
                real = sreal - oreal
                imag = simag - oimag
            except:
                nclass = real.__class__
                oreal = nclass(str(oreal), prec) # hacky
                oimag = nclass(str(oimag), prec)
                real = sreal - oreal
                imag = simag - oimag

        return cls((real, imag), prec=prec)

    def __rsub__(self, other):
        """x.__rsub__(y) <==> y - x"""
        try:
            cls = self.__coerce__(other)
        except TypeError:
            msg = "unsupported operand type(s) for -: '{0}' and '{1}'".format(type(other), type(self))
            raise TypeError(msg)

        if isinstance(other, Numeric) and hasattr(other, "prec"): # Float or derived
            prec = min(self._prec, other.prec)
        elif isinstance(other, Numeric) or hasattr(other, "numerator"): # Rational or Integer; exact
            # ints, longs, and Fractions have the "numerator" attribute
            prec = self._prec
        else:
            from naglib.envconstants import prec

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        if self._ground_type == "gmpy2":
            from gmpy2 import context, local_context
            with local_context(context(), precision=prec):
                try:
                    real = oreal - sreal
                    imag = oimag - simag
                except:
                    nclass = real.__class__
                    oreal = nclass(str(oreal), prec) # hacky
                    oimag = nclass(str(oimag), prec)
                    real = oreal - sreal
                    imag = oimag - simag
        else:
            try:
                real = oreal - sreal
                imag = oimag - simag
            except:
                nclass = real.__class__
                oreal = nclass(str(oreal), prec) # hacky
                oimag = nclass(str(oimag), prec)
                real = oreal - sreal
                imag = oimag - simag

        return cls((real, imag), prec=prec)

    def __mul__(self, other):
        """x.__mul__(y) <==> x*y"""
        try:
            cls = self.__coerce__(other)
        except TypeError:
            msg = "unsupported operand type(s) for *: '{0}' and '{1}'".format(type(self), type(other))
            raise TypeError(msg)

        if isinstance(other, Numeric) and hasattr(other, "prec"): # Float or derived
            prec = min(self._prec, other.prec)
        elif isinstance(other, Numeric) or hasattr(other, "numerator"): # Rational or Integer; exact
            # ints, longs, and Fractions have the "numerator" attribute
            prec = self._prec
        else:
            from naglib.envconstants import prec

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        if self._ground_type == "gmpy2":
            from gmpy2 import context, local_context
            with local_context(context(), precision=prec):
                try:
                    real = sreal*oreal - simag*oimag
                    imag = sreal*oimag + simag*oreal
                except:
                    nclass = real.__class__
                    oreal = nclass(str(oreal), prec) # hacky
                    oimag = nclass(str(oimag), prec)
                    real = sreal*oreal - simag*oimag
                    imag = sreal*oimag + simag*oreal
        else:
            try:
                real = sreal*oreal - simag*oimag
                imag = sreal*oimag + simag*oreal
            except:
                nclass = real.__class__
                oreal = nclass(str(oreal), prec) # hacky
                oimag = nclass(str(oimag), prec)
                real = sreal*oreal - simag*oimag
                imag = sreal*oimag + simag*oreal

        return cls((real, imag), prec=prec)

    def __rmul__(self, other):
        """x.__rmul__(y) <==> y*x"""
        try:
            cls = self.__coerce__(other)
        except TypeError:
            msg = "unsupported operand type(s) for *: '{0}' and '{1}'".format(type(other), type(self))
            raise TypeError(msg)

        if isinstance(other, Numeric) and hasattr(other, "prec"): # Float or derived
            prec = min(self._prec, other.prec)
        elif isinstance(other, Numeric) or hasattr(other, "numerator"): # Rational or Integer; exact
            # ints, longs, and Fractions have the "numerator" attribute
            prec = self._prec
        else:
            from naglib.envconstants import prec

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        if self._ground_type == "gmpy2":
            from gmpy2 import context, local_context
            with local_context(context(), precision=prec):
                try:
                    real = oreal*sreal - oimag*simag
                    imag = oreal*simag + oimag*sreal
                except:
                    nclass = real.__class__
                    oreal = nclass(str(oreal), prec) # hacky
                    oimag = nclass(str(oimag), prec)
                    real = oreal*sreal - oimag*simag
                    imag = oreal*simag + oimag*sreal
        else:
            try:
                real = oreal*sreal - oimag*simag
                imag = oreal*simag + oimag*sreal
            except:
                nclass = real.__class__
                oreal = nclass(str(oreal), prec) # hacky
                oimag = nclass(str(oimag), prec)
                real = oreal*sreal - oimag*simag
                imag = oreal*simag + oimag*sreal

        return cls((real, imag), prec=prec)

    def __div__(self, other):
        """x.__div__(y) <==> x/y"""
        try:
            cls = self.__coerce__(other)
        except TypeError:
            msg = "unsupported operand type(s) for /: '{0}' and '{1}'".format(type(self), type(other))
            raise TypeError(msg)

        if isinstance(other, Numeric) and hasattr(other, "prec"): # Float or derived
            prec = min(self._prec, other.prec)
        elif isinstance(other, Numeric) or hasattr(other, "numerator"): # Rational or Integer; exact
            # ints, longs, and Fractions have the "numerator" attribute
            prec = self._prec
        else:
            from naglib.envconstants import prec

        if other == 0 or (hasattr(other, "is_zero") and other.is_zero()):
            msg = "division by zero"
            raise ZeroDivisionError(msg)

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        if self._ground_type == "gmpy2":
            from gmpy2 import context, local_context
            with local_context(context(), precision=prec):
                try:
                    denom = oreal**2 + oimag**2
                    real = (sreal*oreal + simag*oimag)/denom
                    imag = (simag*oreal - sreal*oimag)/denom
                except:
                    nclass = real.__class__
                    oreal = nclass(str(oreal), prec) # hacky
                    oimag = nclass(str(oimag), prec)
                    denom = oreal**2 + oimag**2
                    real = (sreal*oreal + simag*oimag)/denom
                    imag = (simag*oreal - sreal*oimag)/denom
        else:
            try:
                denom = oreal**2 + oimag**2
                real = (sreal*oreal + simag*oimag)/denom
                imag = (simag*oreal - sreal*oimag)/denom
            except:
                nclass = real.__class__
                oreal = nclass(str(oreal), prec) # hacky
                oimag = nclass(str(oimag), prec)
                denom = oreal**2 + oimag**2
                real = (sreal*oreal + simag*oimag)/denom
                imag = (simag*oreal - sreal*oimag)/denom

        return cls((real, imag), prec=prec)

    def __rdiv__(self, other):
        """x.__rdiv__(y) <==> y/x"""
        try:
            cls = self.__coerce__(other)
        except TypeError:
            msg = "unsupported operand type(s) for /: '{0}' and '{1}'".format(type(other), type(self))
            raise TypeError(msg)

        if isinstance(other, Numeric) and hasattr(other, "prec"): # Float or derived
            prec = min(self._prec, other.prec)
        elif isinstance(other, Numeric) or hasattr(other, "numerator"): # Rational or Integer; exact
            # ints, longs, and Fractions have the "numerator" attribute
            prec = self._prec
        else:
            from naglib.envconstants import prec

        if self == 0 or self.is_zero():
            msg = "division by zero"
            raise ZeroDivisionError(msg)

        sreal = self._real
        oreal = other.real
        simag = self._imag
        oimag = other.imag

        if self._ground_type == "gmpy2":
            from gmpy2 import context, local_context, get_context
            with local_context(context(), precision=prec):
                try:
                    denom = sreal**2 + simag**2
                    real = (sreal*oreal + simag*oimag)/denom
                    imag = (sreal*oimag - simag*oreal)/denom
                except:
                    nclass = real.__class__
                    oreal = nclass(str(oreal), prec) # hacky
                    oimag = nclass(str(oimag), prec)
                    denom = sreal**2 + simag**2
                    real = (sreal*oreal + simag*oimag)/denom
                    imag = (sreal*oimag - simag*oreal)/denom
        else:
            try:
                denom = sreal**2 + simag**2
                real = (sreal*oreal + simag*oimag)/denom
                imag = (sreal*oimag - simag*oreal)/denom
            except:
                nclass = real.__class__
                oreal = nclass(str(oreal), prec) # hacky
                oimag = nclass(str(oimag), prec)
                denom = sreal**2 + simag**2
                real = (sreal*oreal + simag*oimag)/denom
                imag = (sreal*oimag - simag*oreal)/denom

        return cls((real, imag), prec=prec)

    def conjugate(self):
        """the complex conjugate"""
        cls = self.__class__
        prec = self._prec
        if self._ground_type == "gmpy2":
            from gmpy2 import context, local_context
            with local_context(context(), precision=prec):
                real, imag = self._real, -self._imag
        else:
            real, imag = self._real, -self._imag

        return cls((real, imag), prec=prec)

    def almost_equal(self, other, tol=None):
        """1-norm of difference is less than tolerance"""
        if not tol:
            from naglib.envconstants import tol
        try:
            return abs(self - other) < tol
        except TypeError:
            raise

    def is_zero(self, tol=None):
        if not tol:
            from naglib.envconstants import tol
        return abs(self) < tol

    def is_real(self, tol=None):
        if not tol:
            from naglib.envconstants import tol
        return abs(self._imag) < tol

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
