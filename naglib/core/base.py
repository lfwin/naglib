"""Base classes for all NAGlib objects"""

from __future__ import division, print_function

from naglib.core.core import with_metaclass, BaseMeta

class NAGObject(with_metaclass(BaseMeta)):
    """Base class for all NAGlib objects"""

    def __new__(cls, *args):
        obj = object.__new__(cls)
        obj._args = args
        return obj

    def __init__(self, *args):
        self._is_number = False
        self._is_scalar = False

    # TODO: add pickle support
