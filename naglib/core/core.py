"""
The creamy center of NAGlib.
Includes meta stuff and compatibility stuff.
"""

from __future__ import division, print_function
from six import with_metaclass

import sys
three = sys.version_info[0] == 3 # Python 3
del sys

if three:
    string_types = (str,)
else:
    string_types = (str, unicode)

class BaseMeta(type):
    def __init__(cls, *args, **kwargs):
        pass

    def __eq__(cls, other):
        if not isinstance(other, BaseMeta):
            return False
        else:
            cn = cls.__name__
            on = other.__name__
            if cn == on:
                return 0

    def __lt__(cls, other):
        if cls.__cmp__(other) == -1:
            return True
        return False

    def __gt__(cls, other):
        if cls.__cmp__(other) == 1:
            return True
        return False
