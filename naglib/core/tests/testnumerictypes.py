"""Test whether numerify correctly converts varying arguments"""

from __future__ import print_function

import sys
sys.path.insert(0, "../../..")
from naglib.core.numbers import (Integer, GaussianInteger, Rational,
                                 GaussianRational, Float, Complex)

import gmpy2
import unittest

class TestIntegerOperations(unittest.TestCase):
    def setUp(self):
        self.x = gmpy2.mpz("2")
        self.y = gmpy2.mpz("-3")
        self.xI = Integer([self.x])
        self.yI = Integer([self.y])

    def test_addition(self):
        xz = self.x
        yz = self.y
        zz = Integer([xz + yz])
        xI = self.xI
        yI = self.yI
        zI = xI + yI

        self.assertEqual(zz, zI)

    def test_subtraction(self):
        xz = self.x
        yz = self.y
        zz = Integer([xz - yz])
        xI = self.xI
        yI = self.yI
        zI = xI - yI

        self.assertEqual(zz, zI)

        zz = Integer([yz - xz])
        zI = yI - xI
        self.assertEqual(zz, zI)

    def test_multiplication(self):
        xz = self.x
        yz = self.y
        zz = Integer([xz * yz])
        xI = self.xI
        yI = self.yI
        zI = xI * yI

        self.assertEqual(zz, zI)

    def test_division(self):
        xz = self.x
        yz = self.y
        zz = Rational([gmpy2.mpq(xz,yz)])
        xI = self.xI
        yI = self.yI
        zI = xI / yI

        self.assertEqual(zz, zI)

        zz = Rational([gmpy2.mpq(yz, xz)])
        zI = yI / xI
        self.assertEqual(zz, zI)

class TestGaussianIntegerOperations(unittest.TestCase):
    def setUp(self):
        self.x_real = gmpy2.mpz("2")
        self.x_imag = gmpy2.mpz("1")
        self.y_real = gmpy2.mpz("-3")
        self.y_imag = gmpy2.mpz("7")
        self.xI = GaussianInteger(["2 + I"])
        self.yI = GaussianInteger(["-3 + 7*I"])

    def test_addition(self):
        xzr = self.x_real
        xzi = self.x_imag
        yzr = self.y_real
        yzi = self.y_imag

        zz = GaussianInteger(["{0} + {1}*I".format(xzr+yzr, xzi+yzi)])
        xI = self.xI
        yI = self.yI
        zI = xI + yI
        self.assertEqual(zz, zI)

    def test_subtraction(self):
        xzr = self.x_real
        xzi = self.x_imag
        yzr = self.y_real
        yzi = self.y_imag

        zz = GaussianInteger(["{0} + {1}*I".format(xzr-yzr, xzi-yzi)])
        xI = self.xI
        yI = self.yI
        zI = xI - yI
        self.assertEqual(zz, zI)

        zz = GaussianInteger(["{0} + {1}*I".format(yzr-xzr, yzi-xzi)])
        zI = yI - xI
        self.assertEqual(zz, zI)

    def test_multiplication(self):
        xzr = self.x_real
        xzi = self.x_imag
        yzr = self.y_real
        yzi = self.y_imag

        zz = GaussianInteger(["{0} + {1}*I".format(xzr*yzr - xzi*yzi, xzr*yzi + xzi*yzr)])
        xI = self.xI
        yI = self.yI
        zI = xI*yI
        self.assertEqual(zz, zI)

    def test_division(self):
        xzr = self.x_real
        xzi = self.x_imag
        yzr = self.y_real
        yzi = self.y_imag

        zz = GaussianRational(["{0}/{1} + {2}*I/{1}".format(xzi*yzi + xzr*yzr, yzr**2 + yzi**2, xzi*yzr - xzr*yzi)])
        xI = self.xI
        yI = self.yI
        zI = xI/yI
        self.assertEqual(zz, zI)

        zz = GaussianRational(["{0}/{1} + {2}*I/{1}".format(yzi*xzi + yzr*xzr, xzr**2 + xzi**2, yzi*xzr - yzr*xzi)])
        zI = yI/xI
        self.assertEqual(zz, zI)

class TestRationalOperations(unittest.TestCase):
    def setUp(self):
        self.x = gmpy2.mpq(2,3)
        self.y = gmpy2.mpq(-3,4)
        self.xI = Rational([self.x])
        self.yI = Rational([self.y])

    def test_addition(self):
        xz = self.x
        yz = self.y
        zz = Rational([xz + yz])
        xI = self.xI
        yI = self.yI
        zI = xI + yI

        self.assertEqual(zz, zI)

    def test_subtraction(self):
        xz = self.x
        yz = self.y
        zz = Rational([xz - yz])
        xI = self.xI
        yI = self.yI
        zI = xI - yI

        self.assertEqual(zz, zI)

        zz = Rational([yz - xz])
        zI = yI - xI
        self.assertEqual(zz, zI)

    def test_multiplication(self):
        xz = self.x
        yz = self.y
        zz = Rational([xz * yz])
        xI = self.xI
        yI = self.yI
        zI = xI * yI

        self.assertEqual(zz, zI)

    def test_division(self):
        xz = self.x
        yz = self.y
        zz = Rational([xz/yz])
        xI = self.xI
        yI = self.yI
        zI = xI / yI

        self.assertEqual(zz, zI)

        zz = Rational([yz/xz])
        zI = yI / xI
        self.assertEqual(zz, zI)

class TestGaussianIntegerOperations(unittest.TestCase):
    def setUp(self):
        self.x_real = gmpy2.mpq(2,3)
        self.x_imag = gmpy2.mpq(-3,4)
        self.y_real = gmpy2.mpq(-1,5)
        self.y_imag = gmpy2.mpq(6,7)
        self.xI = GaussianRational(["{0} + {1}*I/{2}".format(self.x_real,
            self.x_imag.numerator, self.x_imag.denominator)])
        self.yI = GaussianRational(["{0} + {1}*I/{2}".format(self.y_real,
            self.y_imag.numerator, self.y_imag.denominator)])

    def test_addition(self):
        xzr = self.x_real
        xzi = self.x_imag
        yzr = self.y_real
        yzi = self.y_imag

        zz = GaussianRational(["{0} + {1}*I/{2}".format(xzr+yzr, (xzi+yzi).numerator, (xzi+yzi).denominator)])
        xI = self.xI
        yI = self.yI
        zI = xI + yI
        self.assertEqual(zz, zI)

    def test_subtraction(self):
        xzr = self.x_real
        xzi = self.x_imag
        yzr = self.y_real
        yzi = self.y_imag

        zz = GaussianRational(["{0} + {1}*I/{2}".format(xzr-yzr, (xzi-yzi).numerator, (xzi-yzi).denominator)])
        xI = self.xI
        yI = self.yI
        zI = xI - yI
        self.assertEqual(zz, zI)

        zz = GaussianRational(["{0} + {1}*I/{2}".format(yzr-xzr, (yzi-xzi).numerator, (yzi-xzi).denominator)])
        zI = yI - xI
        self.assertEqual(zz, zI)

    def test_multiplication(self):
        xzr = self.x_real
        xzi = self.x_imag
        yzr = self.y_real
        yzi = self.y_imag

        zz = GaussianRational(["{0} + {1}*I/{2}".format(xzr*yzr - xzi*yzi, (xzr*yzi + xzi*yzr).numerator, (xzr*yzi + xzi*yzr).denominator)])
        xI = self.xI
        yI = self.yI
        zI = xI*yI
        self.assertEqual(zz, zI)

    def test_division(self):
        xzr = self.x_real
        xzi = self.x_imag
        yzr = self.y_real
        yzi = self.y_imag

        denom = yzr**2 + yzi**2
        real = (xzi*yzi + xzr*yzr)/denom
        imag = (xzi*yzr - xzr*yzi)/denom

        zz = GaussianRational(["{0} + {1}*I/{2}".format(real, imag.numerator, imag.denominator)])
        xI = self.xI
        yI = self.yI
        zI = xI/yI
        self.assertEqual(zz, zI)

        denom = xzr**2 + xzi**2
        real = (yzi*xzi + yzr*xzr)/denom
        imag = (yzi*xzr - yzr*xzi)/denom

        zz = GaussianRational(["{0} + {1}*I/{2}".format(real, imag.numerator, imag.denominator)])
        zI = yI/xI
        self.assertEqual(zz, zI)

if __name__ == "__main__":
    unittest.main()
