"""
Symbolic types in NAGlib
"""

from __future__ import division, print_function

import gmpy2
import re

from .base import NAGObject
from .core import string_types
from .groundtypes import SYMBOLS

valid_sym = re.compile(r"^[A-z][A-z0-9_]*$")

class Symbol(NAGObject):
	def __init__(self, *args, **kwargs):
		super(Symbol, self).__init__(*args, **kwargs)
		kkeys = kwargs.keys()

		try:
			self._name = args[0]
		except IndexError:
			if "name" in kkeys:
				self._name = kwargs["name"]

		if not type(self._name) in string_types:
			msg = "can't understand data type"
			raise TypeError(msg)

		if not valid_sym.match(self._name):
			msg = "valid symbols begin with ascii letters and contain only letters, numbers, and underscores"
			raise ValueError(msg)

		self._is_symbol = True
		self._is_scalar = True

	def __repr__(self):
		"""x.__repr__ <==> repr(x)"""
		return self.__str__()

	def __str__(self):
		"""x.__str__ <==> str(x)"""
		return self._name

	def __copy__(self):
		"""x.__copy__ <==> copy(x)"""
		cls = self.__class__
		name = self._name
		return cls(name)

	def __eq__(self, other):
		"""x.__eq__(y) <==> x == y"""
		cls = self.__class__
		if not isinstance(other, cls):
			return False
		return self._name == other._name

	def __ne__(self, other):
		"""x.__ne__(y) <==> x != y"""
		cls = self.__class__
		if not isinstance(other, cls):
			return True
		return self._name != other._name

	def __lt__(self, other):
		"""x.__lt__(y) <==> x < y"""
		cls = self.__class__
		if not isinstance(other, cls):
			return False
		return self._name > other._name # x > y under this scheme

	def __gt__(self, other):
		"""x.__gt__(y) <==> x > y"""
		cls = self.__class__
		if not isinstance(other, cls):
			return False
		return self._name < other._name # x > y under this scheme

	def __neg__(self):
		"""x.__neg__() <==> -x"""
		from naglib.core.numbers import Integer
		from naglib.algebra.polynomial import Monomial, Term

		coeff = Integer(-1)
		smon = Monomial({self:1})
		return Term(smon, coeff)

	def __add__(self, other):
		"""x.__add__(y) <==> x + y"""
		from naglib.core.numbers import Numeric, Integer, Rational, Float
		from naglib.algebra.polynomial import Monomial
		from fractions import Fraction

		smon = Monomial({self:1})

		if isinstance(other, Symbol):
			omon = Monomial({other:1})
			return smon + omon
		elif isinstance(other, Monomial):
			return smon + other
		elif isinstance(other, Numeric):
			return smon + other
		elif isinstance(other, complex) or isinstance(other, float):
			num = Float(other)
			return smon + num
		elif isinstance(other, Fraction):
			num = Rational(other)
			return smon + num
		elif isinstance(other, int) or isinstance(other, long):
			num = Integer(other)
			return smon + num
		else:
			msg = "unsupported operand type(s) for +: {0} and {1}".format(type(self), type(other))
			raise TypeError(msg)

	def __radd__(self, other):
		"""x.__radd__(y) <==> y + x"""
		from naglib.core.numbers import Numeric, Integer, Rational, Float
		from naglib.algebra.polynomial import Monomial
		from fractions import Fraction

		smon = Monomial({self:1})

		if isinstance(other, Symbol):
			omon = Monomial({other:1})
			return omon + smon
		elif isinstance(other, Monomial):
			return other + smon
		elif isinstance(other, Numeric):
			return other + smon
		elif isinstance(other, complex) or isinstance(other, float):
			num = Float(other)
			return num + smon
		elif isinstance(other, Fraction):
			num = Rational(other)
			return num + smon
		elif isinstance(other, int) or isinstance(other, long):
			num = Integer(other)
			return num + smon
		else:
			msg = "unsupported operand type(s) for +: {0} and {1}".format(type(other), type(self))
			raise TypeError(msg)

	def __sub__(self, other):
		"""x.__sub__(y) <==> x - y"""
		from naglib.core.numbers import Numeric, Integer, Rational, Float
		from naglib.algebra.polynomial import Monomial
		from fractions import Fraction

		smon = Monomial({self:1})

		if isinstance(other, Symbol):
			omon = Monomial({other:1})
			return smon - omon
		elif isinstance(other, Monomial):
			return smon - other
		elif isinstance(other, Numeric):
			return smon - other
		elif isinstance(other, complex) or isinstance(other, float):
			num = Float(other)
			return smon - num
		elif isinstance(other, Fraction):
			num = Rational(other)
			return smon - num
		elif isinstance(other, int) or isinstance(other, long):
			num = Integer(other)
			return smon - num
		else:
			msg = "unsupported operand type(s) for -: {0} and {1}".format(type(self), type(other))
			raise TypeError(msg)

	def __rsub__(self, other):
		"""x.__rsub__(y) <==> y - x"""
		from naglib.core.numbers import Numeric, Integer, Rational, Float
		from naglib.algebra.polynomial import Monomial
		from fractions import Fraction

		smon = Monomial({self:1})

		if isinstance(other, Symbol):
			omon = Monomial({other:1})
			return omon - smon
		elif isinstance(other, Monomial):
			return other - smon
		elif isinstance(other, Numeric):
			return other - smon
		elif isinstance(other, complex) or isinstance(other, float):
			num = Float(other)
			return num - smon
		elif isinstance(other, Fraction):
			num = Rational(other)
			return num - smon
		elif isinstance(other, int) or isinstance(other, long):
			num = Integer(other)
			return num - smon
		else:
			msg = "unsupported operand type(s) for -: {0} and {1}".format(type(other), type(self))
			raise TypeError(msg)

	def __mul__(self, other):
		"""x.__mul__(y) <==> x*y"""
		from naglib.core.numbers import Numeric, Integer, Rational, Float
		from naglib.algebra.polynomial import Monomial
		from fractions import Fraction

		smon = Monomial({self:1})

		if isinstance(other, Symbol):
			omon = Monomial({other:1})
			return smon*omon
		elif isinstance(other, Monomial):
			return smon*other
		elif isinstance(other, Numeric):
			return other*smon
		elif isinstance(other, complex) or isinstance(other, float):
			coeff = Float(other)
			return smon*coeff
		elif isinstance(other, Fraction):
			coeff = Rational(other)
			return smon*coeff
		elif isinstance(other, int) or isinstance(other, long):
			coeff = Integer(other)
			return smon*coeff
		else:
			msg = "unsupported operand type(s) for *: {0} and {1}".format(type(self), type(other))
			raise TypeError(msg)

	def __rmul__(self, other):
		"""x.__rmul__(y) <==> y*x"""
		from naglib.core.numbers import Numeric, Integer, Rational, Float
		from naglib.algebra.polynomial import Monomial
		from fractions import Fraction

		smon = Monomial({self:1})

		if isinstance(other, Symbol):
			omon = Monomial({other:1})
			return omon*smon
		elif isinstance(other, Monomial):
			return other*smon
		elif isinstance(other, Numeric):
			return other*smon
		elif isinstance(other, complex) or isinstance(other, float):
			coeff = Float(other)
			return coeff*smon
		elif isinstance(other, Fraction):
			coeff = Rational(other)
			return coeff*smon
		elif isinstance(other, int) or isinstance(other, long):
			coeff = Integer(other)
			return coeff*smon
		else:
			msg = "unsupported operand type(s) for *: {0} and {1}".format(type(other), type(self))
			raise TypeError(msg)

	def __pow__(self, other):
		"""x.__pow__(y) <==> x**y"""
		from naglib.algebra.polynomial import Monomial
		try:
			return Monomial({self:other})
		except TypeError:
			raise
