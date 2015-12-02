"""Test whether numerify correctly converts varying arguments"""

from __future__ import print_function

import sys
sys.path.insert(0, "../../..")
from naglib.core.numerify import numerify

from fractions import Fraction

import gmpy2
import unittest

class TestStringEdgeCases(unittest.TestCase):
    def setUp(self):
        self.one = "1"
        self.minus_one = "-1"
        self.I = "I"
        self.halfI = "I/2"
        self.minushalfI = "-I/2"
        self.oneI = "1*I"
        self.minusoneI = "-1*I"
        self.zeroI = "0*I"
        self.zero_plus_zeroI = "0 + 0*I"
        self.no_spaces = "1+3*I"
        self.lots_of_spaces = "1                             +                                  3             *                I"
        self.float_with_exponent = "314.159E-2*I"
    
    def test_one(self):
        one = self.one
        real,imag = numerify(one)
        self.assertEqual(real[0], 1)
        self.assertEqual(imag, {})
    def test_minus_one(self):
        minus_one = self.minus_one
        real,imag = numerify(minus_one)
        self.assertEqual(real[0], -1)
        self.assertEqual(imag, {})
    def test_I(self):
        I = self.I
        real,imag = numerify(I)
        self.assertEqual(real, {})
        self.assertEqual(imag[0], 1)
    def test_halfI(self):
        halfI = self.halfI
        real,imag = numerify(halfI)
        self.assertEqual(real, {})
        self.assertEqual(imag[0], 0.5)
    def test_minushalfI(self):
        minushalfI = self.minushalfI
        real,imag = numerify(minushalfI)
        self.assertEqual(real, {})
        self.assertEqual(imag[0], -0.5)
    def test_oneI(self):
        oneI = self.oneI
        real,imag = numerify(oneI)
        self.assertEqual(real, {})
        self.assertEqual(imag[0], 1)
    def test_minusoneI(self):
        minusoneI = self.minusoneI
        real,imag = numerify(minusoneI)
        self.assertEqual(real, {})
        self.assertEqual(imag[0], -1)
    def test_zeroI(self):
        zeroI = self.zeroI
        real,imag = numerify(zeroI)
        self.assertEqual(real, {})
        self.assertEqual(imag, {})
    def test_zero_plus_zeroI(self):
        zeroI = self.zero_plus_zeroI
        real,imag = numerify(zeroI)
        self.assertEqual(real, {})
        self.assertEqual(imag, {})
    def test_no_spaces(self):
        spaces = self.no_spaces
        real,imag = numerify(spaces)
        self.assertEqual(real.keys(), imag.keys())
        self.assertEqual(real.keys(), [0])
        self.assertEqual(real[0], 1)
        self.assertEqual(imag[0], 3)
    def test_lots_of_spaces(self):
        spaces = self.lots_of_spaces
        real,imag = numerify(spaces)
        self.assertEqual(real.keys(), imag.keys())
        self.assertEqual(real.keys(), [0])
        self.assertEqual(real[0], 1)
        self.assertEqual(imag[0], 3)
    def test_float_with_exponent(self):
        with_exp = self.float_with_exponent
        real,imag = numerify(with_exp)
        self.assertEqual(real, {})
        self.assertAlmostEqual(imag[0], 3.14159)

class TestIntegerSingleton(unittest.TestCase):
    def setUp(self):
        self.int_literal = 3
        self.long_literal = 3L
        self.int_str = "-3"
    def test_from_int_literal(self):
        n = self.int_literal
        real,imag = numerify(n)
        self.assertEqual(real.keys(), [0])
        self.assertEqual(real[0], 3)
        self.assertEqual(imag, {})
    def test_from_long_literal(self):
        n = self.long_literal
        real,imag = numerify(n)
        self.assertEqual(real.keys(), [0])
        self.assertEqual(real[0], 3)
        self.assertEqual(imag, {})
    def test_from_int_string(self):
        n = self.int_str
        real,imag = numerify(n)
        self.assertEqual(real.keys(), [0])
        self.assertEqual(real[0], -3)
        self.assertEqual(imag, {})

class TestImaginaryIntegerSingleton(unittest.TestCase):
    def setUp(self):
        self.threeI = "3*I"
        self.minus_threeI = "-3*I"
    def test_threeI(self):
        threeI = self.threeI
        real,imag = numerify(threeI)
        self.assertEqual(real, {})
        self.assertEqual(imag[0], 3)
    def test_minus_threeI(self):
        minus_threeI = self.minus_threeI
        real,imag = numerify(minus_threeI)
        self.assertEqual(imag.keys(), [0])
        self.assertEqual(real, {})
        self.assertEqual(imag[0], -3)

class TestGaussianIntegerSingleton(unittest.TestCase):
    def setUp(self):
        self.gauss = "-1 - 4*I"
    def test_gauss(self):
        gauss = self.gauss
        real,imag = numerify(gauss)
        self.assertEqual(real.keys(), [0])
        self.assertEqual(imag.keys(), [0])
        self.assertEqual(real[0], -1)
        self.assertEqual(imag[0], -4)

class TestRationalSingleton(unittest.TestCase):
    def setUp(self):
        self.rat_literal = Fraction(1,2)
        self.rat_str = "-1/2"
    def test_rat_literal(self):
        q = self.rat_literal
        real,imag = numerify(q)
        self.assertEqual(real.keys(), [0])
        self.assertEqual(real[0], Fraction(1,2))
        self.assertEqual(imag, {})
    def test_rat_str(self):
        q = self.rat_str
        real,imag = numerify(q)
        self.assertEqual(real.keys(), [0])
        self.assertEqual(real[0], Fraction(-1,2))
        self.assertEqual(imag, {})

class TestImaginaryRationalSingleton(unittest.TestCase):
    def setUp(self):
        self.minus_thirdI = "-I/3"
    def test_minus_thirdI(self):
        q = self.minus_thirdI
        real,imag = numerify(q)
        self.assertEqual(imag.keys(), [0])
        self.assertEqual(real, {})
        self.assertEqual(imag[0], Fraction(-1,3))

class TestGaussianRationalSingleton(unittest.TestCase):
    def setUp(self):
        self.pure_rational = "-1/2 - 3*I/4"
        self.int_first     = "-3 + 4*I/5"
        self.int_last      = "4/5 - 3*I"
    def test_pure_rational(self):
        q = self.pure_rational
        real,imag = numerify(q)
        self.assertEqual(real.keys(), [0])
        self.assertEqual(imag.keys(), [0])
        self.assertEqual(real[0], Fraction(-1,2))
        self.assertEqual(imag[0], Fraction(-3,4))
    def test_int_first(self):
        q = self.int_first
        real,imag = numerify(q)
        self.assertEqual(real.keys(), [0])
        self.assertEqual(imag.keys(), [0])
        self.assertEqual(real[0], -3)
        self.assertEqual(imag[0], Fraction(4,5))
    def test_int_last(self):
        q = self.int_last
        real,imag = numerify(q)
        self.assertEqual(real.keys(), [0])
        self.assertEqual(imag.keys(), [0])
        self.assertEqual(real[0], Fraction(4,5))
        self.assertEqual(imag[0], -3)

class TestFloatSingleton(unittest.TestCase):
    def setUp(self):
        self.float_literal = 314.159E-2
        self.complex_literal_no_imag = 314.159E-2 + 0j
        self.float_str = "314.159e-2"
    def test_float_literal(self):
        x = self.float_literal
        real,imag = numerify(x)
        self.assertEqual(real.keys(), [0])
        self.assertAlmostEqual(real[0], 3.14159)
        self.assertEqual(imag, {})
    def test_complex_literal_no_imag(self):
        x = self.complex_literal_no_imag
        real,imag = numerify(x)
        self.assertEqual(real.keys(), [0])
        self.assertAlmostEqual(real[0], 3.14159)
        self.assertEqual(imag, {})
    def test_float_str(self):
        x = self.float_str
        real,imag = numerify(x)
        self.assertEqual(real.keys(), [0])
        self.assertAlmostEqual(real[0], 3.14159)
        self.assertEqual(imag, {})

class TestComplexSingleton(unittest.TestCase):
    def setUp(self):
        self.complex_literal = 314.159E-2 - 271828e-5j
        self.complex_string = "314.159E-2 - 271828e-5*I"
    def test_complex_literal(self):
        z = self.complex_literal
        real,imag = numerify(z)
        self.assertEqual(real.keys(), [0])
        self.assertEqual(imag.keys(), [0])
        self.assertAlmostEqual(real[0], 3.14159)
        self.assertAlmostEqual(imag[0], -2.71828)
    def test_complex_str(self):
        z = self.complex_string
        real,imag = numerify(z)
        self.assertEqual(real.keys(), [0])
        self.assertEqual(imag.keys(), [0])
        self.assertAlmostEqual(real[0], 3.14159)
        self.assertAlmostEqual(imag[0], -2.71828)

if __name__ == "__main__":
    unittest.main()
