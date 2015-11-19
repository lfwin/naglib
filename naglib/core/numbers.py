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
#from sympy import sympify, Integer, Rational, Float, I

class Numeric(NAGObject):
    """Base class for numeric types"""

    def __init__(self, *args):
        super(Numeric, self).__init__(*args)
        self._is_number = True
        self._is_scalar = len(*args) == 1

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        entries = self._entries
        if self._is_scalar:
            return str(entries[0])
        else:
            # TODO: truncate this if the string is too long
            return "({0})".format(", ".join([str(e) for e in entries]))

class Complex(Numeric):
    """Complex floating-point vector type"""

    def __init__(self, *args):
        super(Complex, self).__init__(*args)

        self._real = {} # sparsity
        self._imag = {}

        if self._numeric_type == "rational":
            from fractions import Fraction
            args = [Fraction(a) for a in self._args]
            nums = [mpmath.mpf(a.numerator) for a in args]
            denoms = [mpmath.mpf(a.denominator) for a in args]
            try:
                self._args = [nums[i]/denoms[i] for i in range(len(args))]
            except ZeroDivisionError:
                msg = "division by zero"
                raise ZeroDivisionError(msg)
            for i in range(self._length):
                if self._args[i] != 0:
                    self._real[i] = self._args[i]

        elif self._numeric_type == "Gaussian rational":
            pass

        #print("args: {0}".format(self._args))
        for i in range(self._length):
            arg = self._args[i]
            #print("arg: {0}".format(arg))
            val = re.sub(r' ', '', arg)
            breakup = re.split(r"(?<=[iI\d])([-+])", val)
            if len(breakup) == 1: # pure real or pure imag
                if 'i' in val or 'I' in val or 'j' in val:
                    val = re.sub(r"[ijI]", '', val)
                    if val == '':
                        val = '1'
                    elif val == '-':
                        val = "-1"
                    val = long(val)
                    if val != 0:
                        self._imag[i] = val
                else:
                    val = long(val)
                    if val != 0:
                        self._real[i] = long(val)
            elif len(breakup) != 3:
                raise ValueError(arg)
            else:
                left, right = breakup[0], breakup[1] + breakup[2]
                if 'i' in left or 'I' in left:
                    imag = re.sub(r"([iI]|\*)", '', left)
                    real = right
                else:
                    imag = re.sub(r"([iIj]|\*)", '', right)
                    if imag == '-':
                        imag = '-1'
                    elif imag == '+':
                        imag = '1'
                    real = left
                real, imag = long(real), long(imag)
                if real != 0:
                    self._real[i] = real
                if imag != 0:
                    self._imag[i] = imag

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

        try:
            self._real, self._imag = gmpy2ify(*args, force_type="Gaussian int")
        except TypeError:
            raise
        except ValueError:
            raise
        self._length = len(*args)
        #print("args: {0}".format(self._args))

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        if self._is_scalar:
            if self._real:
                rep = str(self._real[0])
            else:
                rep = ''
            if self._imag:
                if rep and self._imag[0] > 0:
                    rep += '+' + str(self._imag[0]) + "*I"
                else:
                    rep += str(self._imag[0]) + "*I"
            if not rep: # zero
                return '0'
        else:
            reals = self._real.keys()
            imags = self._imag.keys()
            entries = []
            for i in range(self._length):
                entry = ''
                if i in reals:
                    entry += str(self._real[i])
                if i in imags:
                    if entry and self._imag[i] == 1:
                        entry += "+I"
                    elif entry and self._imag[i] == -1:
                        entry += "-I"
                    elif entry and self._imag[i] > 1:
                        entry += '+' + str(self._imag[i]) + "*I"
                    elif not entry and self._imag[i] == 1:
                        entry += 'I'
                    elif not entry and self._imag[i] == -1:
                        entry += "-I"
                    else:
                        entry += str(self._imag[i]) + "*I"
                if entry:
                    entries.append(entry)
                else:
                    entries.append('0')
            rep = '(' + ", ".join(entries) + ')'
        return rep
