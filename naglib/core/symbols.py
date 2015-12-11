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
		if not issubclass(other, cls):
			return False
		return self._name == other._name


class Monomial(NAGObject):
	"""Monomial class; for internal use only"""
	def __init__(self, *args, **kwargs):
		super(Monomial, self).__init__(*args, **kwargs)
        kkeys = kwargs.keys()

		try:
			variables = args[0]
			degrees = args[1]
		except IndexError:
			if "variables" in kkeys:
				variables = kkeys["variables"]
			else:
				variables = ()
			if "degrees" in kkeys:
				degrees = kkeys["variables"]
			else:
				degrees = tuple([0 for i in range(len(variables))])

        self._ground_type = SYMBOLS
