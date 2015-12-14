"""Polynomials"""

from __future__ import division, print_function

from fractions import Fraction

from naglib.core.base import NAGObject
from naglib.core.groundtypes import SYMBOLS
from naglib.core.numbers import Numeric, Integer, Rational, Float

class Monomial(NAGObject):
    """Monomial class; for internal use only"""
    def __init__(self, *args, **kwargs):
        super(Monomial, self).__init__(*args, **kwargs)
        kkeys = kwargs.keys()

        try:
            degrees = args[0]
        except IndexError: # nothing in args
            if "degrees" in kkeys:
                degrees = kkeys["degrees"]
            else:
                degrees = {}
        try:
            assert(hasattr(degrees, "keys"))
        except AssertionError:
            msg = "give us a dict"
            raise TypeError(msg)

        try:
            sum(degrees.values())
        except TypeError:
            msg = "give us a dict with numerical values"
            raise ValueError(msg)

        self._degrees = degrees.copy()
        for k in self._degrees.keys():
            if self._degrees[k] == 0:
                self._degrees.pop(k)

        self._is_symbol = True
        self._is_scalar = True
        self._ground_type = SYMBOLS

    def __repr__(self):
        """x.__repr__ <==> repr(x)"""
        return self.__str__()

    def __str__(self):
        """x.__str__ <==> str(x)"""
        degrees = self._degrees
        variables = sorted(degrees.keys(), reverse=True)

        if self.total_degree == 0:
            return '1'
        else:
            return '*'.join(["{0}**{1}".format(v, degrees[v]) if degrees[v] != 1 else str(v) for v in variables])

    def __pow__(self, other):
        cls = self.__class__
        degrees = self._degrees.copy()

        try:
            degrees = dict([(v,degrees[v]*other) for v in degrees.keys()])
        except TypeError:
            msg = "invalid exponent"
            raise TypeError(msg)

        return cls(degrees)

    def copy(self):
        """returns a copy of self"""
        cls = self.__class__
        degrees = self._degrees.copy()
        return cls(degrees)

    def degree(self, arg):
        """returns the degree of the argument"""
        try:
            return self._degrees[arg]
        except KeyError:
            return 0

    def total_degree(self):
        """returns the total degree of the monomial"""
        degrees = self._degrees
        return sum(degrees.values())

class Term(NAGObject):
    """Term (monomial with a coefficient) class; for internal use only"""
    def __init__(self, *args, **kwargs):
        super(Term, self).__init__(*args, **kwargs)
        kkeys = kwargs.keys()

        try:
            monomial = args[0]
        except IndexError: # nothing in args
            if "monomial" in kkeys:
                monomial = kkeys["monomial"]
            else:
                monomial = Monomial({})
        try:
            assert(isinstance(monomial, Monomial))
        except AssertionError:
            msg = "give us a Monomial"
            raise TypeError(msg)

        try:
            coefficient = args[1]
        except IndexError:
            if "coefficient" in kkeys:
                coefficient = kkeys["coefficient"]
            else:
                coefficient = Integer(0)
        try:
            assert(isinstance(coefficient, Numeric))
        except AssertionError:
            if not hasattr(coefficient, real) and hasattr(coefficient, imag):
                msg = "coefficient needs to be a number, guy"
                raise TypeError(msg)
            if isinstance(coefficient, int) or isinstance(coefficient, long):
                coefficient = Integer(coefficient)
            elif isinstance(coefficient, Fraction):
                coefficient = Rational(coefficient)
            else:
                coefficient = Float(coefficient)

        if coefficient == 0: # no need to store degrees if we don't have to
            monomial = Monomial({})

        self._monomial = monomial.copy()
        self._coefficient = coefficient.copy()

        self._is_symbol = True
        self._is_scalar = True

        self._ground_type = SYMBOLS

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return self.__str__()

    def __str__(self):
        """x.__str__() <==> str(x)"""
        mon, coeff = self._monomial, self._coefficient

        if mon.total_degree() == 0:
            return str(coeff)
        elif abs(coeff) == 1 and (isinstance(coeff, Integer) or isinstance(coeff, Rational)):
            if coeff == 1:
                return str(mon)
            else:
                return '-' + str(mon)
        else:
            return '*'.join([str(coeff), str(mon)])

    def __neg__(self):
        """x.__neg__() <==> -x"""
        cls = self.__class__
        mon, coeff = self._monomial, self._coefficient
        return cls(mon, -coeff)

class Polynomial(NAGObject):
    """Polynomial class"""
    def __init__(self, *args, **kwargs):
        super(Polynomial, self).__init__(*args, **kwargs)
        kkeys = kwargs.keys()

        self._ground_type = SYMBOLS
