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

        if self.is_constant:
            return '1'
        else:
            dstr = []
            for v in degrees.keys():
                d = degrees[v]
                if d == 1:
                    dstr.append(str(v))
                elif d < 0:
                    dstr.append("{0}**({1})".format(v, d))
                else:
                    dstr.append("{0}**{1}".format(v, d))
            return '*'.join(dstr)

    def __neg__(self):
        """x.__neg__() <==> -x"""
        degrees = self._degrees
        return Term(degrees, -1)

    def __eq__(self, other):
        """x.__eq__(y) <==> x==y"""
        sdegrees = self._degrees

        from naglib.core.symbols import Symbol

        if isinstance(other, Symbol):
            dkeys = sdegrees.keys()
            return (len(dkeys) == 1 and other in dkeys and sdegrees[other] == 1)
        elif isinstance(other, Term):
            odegrees = other._degrees
            return (odegrees == sdegrees and other.coefficient == 1)
        elif isinstance(other, Monomial):
            odegrees = other._degrees
            return odegrees == sdegrees
        elif isinstance(other, Polynomial):
            return NotImplementedError
        else:
            return False

    def __add__(self, other):
        """x.__add__(y) <==> x + y"""
        as_term = Term(self._degrees, 1)
        try:
            return as_term + other
        except TypeError:
            raise
        except NotImplementedError:
            raise

    def __radd__(self, other):
        """x.__radd__(y) <==> y + x"""
        as_term = Term(self._degrees, 1)
        try:
            return other + as_term
        except TypeError:
            raise
        except NotImplementedError:
            raise

    def __sub__(self, other):
        """x.__sub__(y) <==> x - y"""
        as_term = Term(self._degrees, 1)
        try:
            return as_term - other
        except TypeError:
            raise
        except NotImplementedError:
            raise

    def __rsub__(self, other):
        """x.__rsub__(y) <==> y - x"""
        as_term = Term(self._degrees, 1)
        try:
            return other - as_term
        except TypeError:
            raise
        except NotImplementedError:
            raise

    def __mul__(self, other):
        """x.__mul__(y) <==> x*y"""
        cls = self.__class__

        from naglib.core.symbols import Symbol

        if isinstance(other, Term):
            as_term = Term(self._degrees, 1)
            return as_term*other
        elif isinstance(other, cls):
            sdegrees = self._degrees
            odegrees = other._degrees
            svars = set(sdegrees.keys())
            ovars = set(odegrees.keys())

            degrees = {}
            for v in svars.intersection(ovars):
                degrees[v] = sdegrees[v] + odegrees[v]
            for v in svars.symmetric_difference(ovars):
                if v in svars:
                    degrees[v] = sdegrees[v]
                else:
                    degrees[v] = odegrees[v]
            return cls(degrees)
        elif isinstance(other, Symbol):
            other = Monomial({other:1})
            return self*other
        elif isinstance(other, Polynomial):
            raise NotImplementedError
        elif hasattr(other, "real") and hasattr(other, "imag"):
            return Term(self._degrees, other)
        else:
            msg = "unsupported operand type(s) for *: {0} and {1}".format(type(self), type(other))
            raise TypeError(msg)

    def __rmul__(self, other):
        """x.__rmul__(y) <==> y*x"""
        cls = self.__class__

        from naglib.core.symbols import Symbol

        if isinstance(other, Term):
            as_term = Term(self._degrees, 1)
            return other*as_term
        elif isinstance(other, cls):
            sdegrees = self._degrees
            odegrees = other._degrees
            svars = set(sdegrees.keys())
            ovars = set(odegrees.keys())

            degrees = {}
            for v in svars.intersection(ovars):
                degrees[v] = sdegrees[v] + odegrees[v]
            for v in svars.symmetric_difference(ovars):
                if v in svars:
                    degrees[v] = sdegrees[v]
                else:
                    degrees[v] = odegrees[v]
            return cls(degrees)
        elif isinstance(other, Symbol):
            other = Monomial({other:1})
            return other*self
        elif isinstance(other, Polynomial):
            raise NotImplementedError
        elif hasattr(other, "real") and hasattr(other, "imag"):
            return Term(self._degrees, other)
        else:
            msg = "unsupported operand type(s) for *: {0} and {1}".format(type(other), type(self))
            raise TypeError(msg)

    def __div__(self, other):
        """x.__div__(y) <==> x/y"""
        cls = self.__class__

        from naglib.core.symbols import Symbol

        if isinstance(other, Term):
            as_term = Term(self._degrees, 1)
            return as_term/other
        elif isinstance(other, cls):
            sdegrees = self._degrees
            odegrees = other._degrees
            svars = set(sdegrees.keys())
            ovars = set(odegrees.keys())

            degrees = {}
            for v in svars.intersection(ovars):
                degrees[v] = sdegrees[v] - odegrees[v]
            for v in svars.symmetric_difference(ovars):
                if v in svars:
                    degrees[v] = sdegrees[v]
                else:
                    degrees[v] = -odegrees[v]
            return cls(degrees)
        elif isinstance(other, Symbol):
            other = Monomial({other:1})
            return self/other
        elif isinstance(other, Polynomial):
            raise NotImplementedError
        elif hasattr(other, "real") and hasattr(other, "imag"):
            try:
                return Term(self._degrees, 1/other)
            except ZeroDivisionError:
                raise
        else:
            msg = "unsupported operand type(s) for /: {0} and {1}".format(type(self), type(other))
            raise TypeError(msg)

    def __rdiv__(self, other):
        """x.__rdiv__(y) <==> y/x"""
        cls = self.__class__

        from naglib.core.symbols import Symbol

        if isinstance(other, Term):
            as_term = Term(self._degrees, 1)
            return other/as_term
        elif isinstance(other, cls):
            sdegrees = self._degrees
            odegrees = other._degrees
            svars = set(sdegrees.keys())
            ovars = set(odegrees.keys())

            degrees = {}
            for v in svars.intersection(ovars):
                degrees[v] = odegrees[v] - sdegrees[v]
            for v in svars.symmetric_difference(ovars):
                if v in svars:
                    degrees[v] = -sdegrees[v]
                else:
                    degrees[v] = odegrees[v]
            return cls(degrees)
        elif isinstance(other, Symbol):
            other = Monomial({other:1})
            return other/self
        elif isinstance(other, Polynomial):
            raise NotImplementedError
        elif hasattr(other, "real") and hasattr(other, "imag"):
            degrees = {v:-self._degrees[v] for v in degrees.keys()}
            return Term(degrees, other)
        else:
            msg = "unsupported operand type(s) for /: {0} and {1}".format(type(other), type(self))
            raise TypeError(msg)

    def __pow__(self, other):
        """x.__pow__(y) <==> x**y"""
        cls = self.__class__
        degrees = self._degrees

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

    def degree(self, arg=None):
        """returns the degree of the argument"""
        degrees = self._degrees

        if arg is None:
            return degrees.values()
        try:
            return degrees[arg]
        except KeyError:
            return 0

    def total_degree(self):
        """returns the total degree of the monomial"""
        degrees = self._degrees
        return sum(degrees.values())

    @property
    def is_constant(self):
        return self.total_degree() == 0

class Term(Monomial):
    """Term (monomial with a coefficient) class; for internal use only"""
    def __init__(self, *args, **kwargs):
        super(Term, self).__init__(*args, **kwargs)
        kkeys = kwargs.keys()

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
            if not (hasattr(coefficient, "real") and hasattr(coefficient, "imag")):
                msg = "coefficient needs to be a number, guy"
                raise TypeError(msg)
            if isinstance(coefficient, int) or isinstance(coefficient, long):
                coefficient = Integer(coefficient)
            elif isinstance(coefficient, Fraction):
                coefficient = Rational(coefficient)
            else:
                coefficient = Float(coefficient)

        if coefficient == 0: # no need to store degrees if we don't have to
            self._degrees = {}

        self._coefficient = coefficient.copy()

        self._is_symbol = True
        self._is_scalar = True

        self._ground_type = SYMBOLS

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return self.__str__()

    def __str__(self):
        """x.__str__() <==> str(x)"""
        degrees = self._degrees
        coefficient = self._coefficient

        if self.is_constant:
            return str(coefficient)
        else:
            monstr = super(Term, self).__str__()
            if coefficient == 1:
                return monstr
            elif coefficient == -1:
                return '-' + monstr
            elif coefficient.imag != 0:
                return "({0})*{1}".format(coefficient, monstr)
            else:
                return "{0}*{1}".format(coefficient, monstr)

    def __neg__(self):
        """x.__neg__() <==> -x"""
        cls = self.__class__
        degrees, coefficient = self._degrees.copy(), self._coefficient
        return cls(degrees, -coefficient)

    def __eq__(self, other):
        """x.__eq__(y) <==> x==y"""
        sdegrees = self._degrees

        from naglib.core.symbols import Symbol

        if isinstance(other, Symbol):
            dkeys = sdegrees.keys()
            return (len(dkeys) == 1 and self._coefficient == 1 and other in dkeys and sdegrees[other] == 1)
        elif isinstance(other, Term):
            odegrees = other._degrees
            return (odegrees == sdegrees and other.coefficient == self._coefficient)
        elif isinstance(other, Monomial):
            odegrees = other._degrees
            return (odegrees == sdegrees and self._coefficient == 1)
        elif isinstance(other, Polynomial):
            return NotImplementedError
        elif hasattr(other, "real") and hasattr(other, "imag"):
            return (self.is_constant and self._coefficient == other)
        else:
            return False

    def __add__(self, other):
        """x.__add__(y) <==> x + y"""
        cls = self.__class__

        from naglib.core.symbols import Symbol

        if isinstance(other, cls):
            if self._degrees == other._degrees:
                return cls(self._degrees, self._coefficient + other.coefficient)
            else:
                return Polynomial(summands=[self, other])

        elif isinstance(other, Symbol):
            other = Term({other:1}, 1)
            return self + other
        elif isinstance(other, Monomial):
            degrees = other._degrees
            coeff = 1
            other = Term(degrees, coeff)
            return self + other
        elif isinstance(other, Polynomial):
            raise NotImplementedError
        elif hasattr(other, "real") and hasattr(other, "imag"):
            other = Term({}, other)
            return self + other
        else:
            msg = "unsupported operand type(s) for +: {0} and {1}".format(type(self), type(other))
            raise TypeError(msg)

    def __radd__(self, other):
        """x.__radd__(y) <==> y + x"""
        cls = self.__class__

        from naglib.core.symbols import Symbol

        if isinstance(other, cls):
            if self._degrees == other._degrees:
                return cls(self._degrees, other.coefficient + self._coefficient)
            else:
                return Polynomial(summands=[other, self])

        elif isinstance(other, Symbol):
            other = Term({other:1}, 1)
            return other + self
        elif isinstance(other, Monomial):
            degrees = other._degrees
            coeff = 1
            other = Term(degrees, coeff)
            return other + self
        elif isinstance(other, Polynomial):
            raise NotImplementedError
        elif hasattr(other, "real") and hasattr(other, "imag"):
            other = Term({}, other)
            return other + self
        else:
            msg = "unsupported operand type(s) for +: {0} and {1}".format(type(other), type(self))
            raise TypeError(msg)

    def __sub__(self, other):
        """x.__sub__(y) <==> x - y"""
        cls = self.__class__

        from naglib.core.symbols import Symbol

        if isinstance(other, cls):
            if self._degrees == other._degrees:
                return cls(self._degrees, self._coefficient - other.coefficient)
            else:
                return Polynomial(summands=[self, -other])

        elif isinstance(other, Symbol):
            other = Term({other:1}, 1)
            return self - other
        elif isinstance(other, Monomial):
            degrees = other._degrees
            coeff = 1
            other = Term(degrees, coeff)
            return self - other
        elif isinstance(other, Polynomial):
            raise NotImplementedError
        elif hasattr(other, "real") and hasattr(other, "imag"):
            other = Term({}, other)
            return self - other
        else:
            msg = "unsupported operand type(s) for -: {0} and {1}".format(type(self), type(other))
            raise TypeError(msg)

    def __rsub__(self, other):
        """x.__rsub__(y) <==> y - x"""
        cls = self.__class__

        from naglib.core.symbols import Symbol

        if isinstance(other, cls):
            if self._degrees == other._degrees:
                return cls(self._degrees, other.coefficient - self._coefficient)
            else:
                return Polynomial(summands=[self, -other])

        elif isinstance(other, Symbol):
            other = Term({other:1}, 1)
            return other - self
        elif isinstance(other, Monomial):
            degrees = other._degrees
            coeff = 1
            other = Term(degrees, coeff)
            return other - self
        elif isinstance(other, Polynomial):
            raise NotImplementedError
        elif hasattr(other, "real") and hasattr(other, "imag"):
            other = Term({}, other)
            return other - self
        else:
            msg = "unsupported operand type(s) for -: {0} and {1}".format(type(other), type(self))
            raise TypeError(msg)

    def __mul__(self, other):
        """x.__mul__(y) <==> x*y"""
        cls = self.__class__

        from naglib.core.symbols import Symbol

        if isinstance(other, cls):
            scoeff = self._coefficient
            ocoeff = other.coefficient
            sdegrees = self._degrees
            odegrees = other._degrees
            svars = set(sdegrees.keys())
            ovars = set(odegrees.keys())

            degrees = {}
            for v in svars.intersection(ovars):
                degrees[v] = sdegrees[v] + odegrees[v]
            for v in svars.symmetric_difference(ovars):
                if v in svars:
                    degrees[v] = sdegrees[v]
                else:
                    degrees[v] = odegrees[v]
            coeff = scoeff*ocoeff

            return cls(degrees, coeff)

        elif isinstance(other, Symbol):
            other = Term({other:1}, 1)
            return self*other
        elif isinstance(other, Monomial):
            degrees = other._degrees
            other = Term(degrees, 1)
            return self*other
        elif isinstance(other, Polynomial):
            raise NotImplementedError
        elif hasattr(other, "real") and hasattr(other, "imag"):
            other = Term({}, other)
            return self*other
        else:
            msg = "unsupported operand type(s) for *: {0} and {1}".format(type(self), type(other))
            raise TypeError(msg)

    def __rmul__(self, other):
        """x.__rmul__(y) <==> y*x"""
        cls = self.__class__

        from naglib.core.symbols import Symbol

        if isinstance(other, cls):
            scoeff = self._coefficient
            ocoeff = other.coefficient
            sdegrees = self._degrees
            odegrees = other._degrees
            svars = set(sdegrees.keys())
            ovars = set(odegrees.keys())

            degrees = {}
            for v in svars.intersection(ovars):
                degrees[v] = sdegrees[v] + odegrees[v]
            for v in svars.symmetric_difference(ovars):
                if v in svars:
                    degrees[v] = sdegrees[v]
                else:
                    degrees[v] = odegrees[v]
            coeff = ocoeff*scoeff

            return cls(degrees, coeff)

        elif isinstance(other, Symbol):
            other = Term({other:1}, 1)
            return other*self
        elif isinstance(other, Monomial):
            degrees = other._degrees
            other = Term(degrees, 1)
            return other*self
        elif isinstance(other, Polynomial):
            raise NotImplementedError
        elif hasattr(other, "real") and hasattr(other, "imag"):
            other = Term({}, other)
            return other*self
        else:
            msg = "unsupported operand type(s) for *: {0} and {1}".format(type(other), type(self))
            raise TypeError(msg)

    def __div__(self, other):
        """x.__div__(y) <==> x/y"""
        cls = self.__class__

        from naglib.core.symbols import Symbol

        if isinstance(other, cls):
            scoeff = self._coefficient
            ocoeff = other.coefficient
            sdegrees = self._degrees
            odegrees = other._degrees
            svars = set(sdegrees.keys())
            ovars = set(odegrees.keys())

            degrees = {}
            for v in svars.intersection(ovars):
                degrees[v] = sdegrees[v] - odegrees[v]
            for v in svars.symmetric_difference(ovars):
                if v in svars:
                    degrees[v] = sdegrees[v]
                else:
                    degrees[v] = -odegrees[v]
            coeff = scoeff/(ocoeff)

            return cls(degrees, coeff)

        elif isinstance(other, Symbol):
            other = Term({other:1}, 1)
            return self/other
        elif isinstance(other, Monomial):
            degrees = other._degrees
            other = Term(degrees, 1)
            return self/other
        elif isinstance(other, Polynomial):
            raise NotImplementedError
        elif hasattr(other, "real") and hasattr(other, "imag"):
            other = Term({}, other)
            try:
                return self/other
            except ZeroDivisionError:
                raise
        else:
            msg = "unsupported operand type(s) for /: {0} and {1}".format(type(self), type(other))
            raise TypeError(msg)

    def __truediv__(self, other):
        return self.__div__(other)

    def __rdiv__(self, other):
        """x.__rdiv__(y) <==> y/x"""
        cls = self.__class__

        from naglib.core.symbols import Symbol

        if isinstance(other, cls):
            scoeff = self._coefficient
            ocoeff = other.coefficient
            sdegrees = self._degrees
            odegrees = other._degrees
            svars = set(sdegrees.keys())
            ovars = set(odegrees.keys())

            degrees = {}
            for v in svars.intersection(ovars):
                degrees[v] = -sdegrees[v] + odegrees[v]
            for v in svars.symmetric_difference(ovars):
                if v in svars:
                    degrees[v] = -sdegrees[v]
                else:
                    degrees[v] = odegrees[v]
            try:
                coeff = ocoeff/scoeff
            except ZeroDivisionError:
                raise

            return cls(degrees, coeff)

        elif isinstance(other, Symbol):
            other = Term({other:1}, 1)
            return other/self
        elif isinstance(other, Monomial):
            degrees = other._degrees
            other = Term(degrees, 1)
            return other/self
        elif isinstance(other, Polynomial):
            raise NotImplementedError
        elif hasattr(other, "real") and hasattr(other, "imag"):
            other = Term({}, other)
            return other/self
        else:
            msg = "unsupported operand type(s) for /: {0} and {1}".format(type(other), type(self))
            raise TypeError(msg)

    def __rtruediv__(self, other):
        return self.__rdiv__(other)

    def __pow__(self, other):
        """x.__pow__(y) <==> x**y"""
        cls = self.__class__

        coeff = self._coefficient
        degrees = self._degrees

        try:
            degrees = dict([(v,degrees[v]*other) for v in degrees.keys()])
            coeff = coeff**other
        except TypeError:
            msg = "invalid exponent"
            raise TypeError(msg)

        return cls(degrees, coeff)

    def as_coeff_monomial(self):
        """returns a tuple of the coefficient and monomial"""
        coefficient = self._coefficient
        monomial = Monomial(self._degrees)

        return (coefficient, monomial)

    def copy(self):
        """returns a copy of self"""
        cls = self.__class__
        degrees = self._degrees.copy()
        coefficient = self._coefficient
        return cls(degrees, coefficient)

    @property
    def coefficient(self):
        return self._coefficient

class Polynomial(NAGObject):
    """Polynomial class"""
    def __init__(self, *args, **kwargs):
        super(Polynomial, self).__init__(*args, **kwargs)
        kkeys = kwargs.keys()

        try:
            from naglib.core.core import string_types
            assert(type(args[0]) in string_types)
        except IndexError:
            if "summands" in kkeys:
                self._summands = kwargs["summands"]
        except AssertionError:
            # check for Symbol, Monomial/Term
            pass

        self._ground_type = SYMBOLS

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return self.__str__()

    def __str__(self):
        """x.__str__() <==> str(x)"""
        summands = self._summands
        return " + ".join([str(s) for s in summands])
