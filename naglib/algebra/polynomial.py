"""Polynomials"""

from __future__ import division, print_function

from naglib.base import NAGObject
from naglib.groundtypes import SYMBOLS

class Polynomial(NAGObject):
    """Polynomial class"""
    def __init__(self, *args, **kwargs):
        super(Polynomial, self).__init__(*args, **kwargs)
        kkeys = kwargs.keys()

        self._ground_type = SYMBOLS
