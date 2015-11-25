"""Test whether gmpy2ify correctly converts varying arguments"""

from __future__ import print_function

import sys
sys.path.insert(0, "../../..")
from numbers import (Integer, GaussianInteger, Rational, GaussianRational,
                     Float, Complex)

import gmpy2
import unittest



if __name__ == "__main__":
    unittest.main()
