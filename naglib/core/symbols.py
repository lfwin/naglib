"""
Symbolic types in NAGlib
"""

from __future__ import division, print_function

import gmpy2
import re

from .base import NAGObject
from .core import string_types

from sympy import sympify, SympifyError

valid_sym = re.compile(r"^[A-z][A-z0-9_]*$")

class Symbol(NAGObject):
	def __init__(self, *args, **kwargs):
		super(Symbol, self).__init__(*args, **kwargs)

		if not type(args[0]) in string_types:
			msg = "can't understand data type"
			raise TypeError(msg)

		if not valid_sym.match(args[0]):
			msg = "valid symbols begin with ascii letters and contain only letters, numbers, and underscores"
			raise ValueError(msg)
		self._name = args[0]

	def __repr__(self):
		"""x.__repr__ <==> repr(x)"""
		return self.__str__()

	def __str__(self):
		"""x.__str__ <==> str(x)"""
		return self._name

	def __neg__(self):
		"""x.__neg__() <==> -x"""
		return Monomial()

	def __eq__(self, other):
		"""x.__eq__(y) <==> x == y"""
		cls = self.__class__
		if not issubclass(other, cls):
			return False
		return self._name == other._name

	def __add__(self, other):
		"""x.__add__(y) <==> x + y"""
		repstr = self.__str__() + " + " + str(other)
		try:
			rep = sympify(repstr)
		except SympifyError as e:
			message = e.message
			raise ValueError(message)

class Polynomial(Symbol):
	def __init__(self, *args, **kwargs):
		super(self, Polynomial).__init__(*args, **kwargs)

class Monomial(Polynomial):
	def __init__(self, *args, **kwargs):
		super(self, Monomial).__init__(*args, **kwargs)

class Term(Polynomial):
	def __init__(self, *args, **kwargs):
		super(self, Term).__init__(*args, **kwargs)

class PolynomialSystem(Symbol):
	def __init__(self, *args, **kwargs):
		super(self, PolynomialSystem).__init__(*args, **kwargs)
