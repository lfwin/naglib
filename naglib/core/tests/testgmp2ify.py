"""Test whether gmp2ify correctly converts varying arguments"""

from __future__ import print_function

import sys
sys.path.insert(0, "..")
from tonumeric import gmpy2ify

import gmpy2
import unittest

class TestSingleton(unittest.TestCase):
    def setUp(self):
        self.int_literal = 3
        self.int_str = '3'
        self.imag_int_str1 = "2*I"
        self.imag_int_str2 = "2I"
        self.imag_int_str3 = "2*i"
        self.imag_int_str4 = "2i"
        self.gauss_int_str1 = "3 + " + self.imag_int_str1
        self.gauss_int_str2 = "3 + " + self.imag_int_str2
        self.gauss_int_str3 = "3 + " + self.imag_int_str3
        self.gauss_int_str4 = "3 + " + self.imag_int_str4
        self.gauss_int_zero = "0 + 2*I" # this should succeed as well
        self.rat_str = "-2/3"
        self.imag_rat_str1 = "-2*I/3"
        self.imag_rat_str2 = "-2I/3"
        self.imag_rat_str3 = "-2*i/3"
        self.imag_rat_str4 = "-2i/3"
        self.gauss_rat_str1 = "-1 " + self.imag_rat_str1
        self.gauss_rat_str2 = "-1 " + self.imag_rat_str2
        self.gauss_rat_str3 = "-1 " + self.imag_rat_str3
        self.gauss_rat_str4 = "-1 " + self.imag_rat_str4
        self.gauss_rat_zero = "0 - 2*I/3" # this should succeed
        self.float_literal = 314.159e-2
        self.float_str = "314.159e-2"
        self.imag_float_literal = 314.159e-2j
        self.imag_float_str1 = "314.159e-2*I"
        self.imag_float_str2 = "314.159e-2I"
        self.imag_float_str3 = "314.159e-2*i"
        self.imag_float_str4 = "314.159e-2i"
        self.imag_float_str5 = "314.159e-2*j" # this should fail
        self.imag_float_str6 = "314.159e-2j" # this should succeed
        self.complex_str1 = "2.71828E1 + " + self.imag_float_str1
        self.complex_str2 = "2.71828E1 + " + self.imag_float_str2
        self.complex_str3 = "2.71828E1 + " + self.imag_float_str3
        self.complex_str4 = "2.71828E1 + " + self.imag_float_str4
        self.complex_str5 = "2.71828E1 + " + self.imag_float_str5 # this should fail
        self.complex_str6 = "2.71828E1 + " + self.imag_float_str6 # this should succeed
        self.complex_zero = "0 + 314.159e-2j" # this should succeed

    def test_takes_no_singletons(self):
        lit = self.int_literal
        self.assertRaises(TypeError, gmpy2ify, lit)

    def test_int_construction(self):
        lit  = self.int_literal
        str1 = self.int_str

        from_lit = gmpy2ify([lit])
        from_str = gmpy2ify([str1])
        self.assertEqual(from_lit, from_str)
        self.assertEqual(from_lit[0][0], 3)
        self.assertEqual(from_lit[1], {})

    def test_gauss_int_construction(self):
        str1 = self.imag_int_str1
        str2 = self.imag_int_str2
        str3 = self.imag_int_str3
        str4 = self.imag_int_str4
        str5 = self.gauss_int_str1
        str6 = self.gauss_int_str2
        str7 = self.gauss_int_str3
        str8 = self.gauss_int_str4
        str9 = self.gauss_int_zero

        from_str1 = gmpy2ify([str1])
        from_str2 = gmpy2ify([str2])
        from_str3 = gmpy2ify([str3])
        from_str4 = gmpy2ify([str4])

        from_str5 = gmpy2ify([str5])
        from_str6 = gmpy2ify([str6])
        from_str7 = gmpy2ify([str7])
        from_str8 = gmpy2ify([str8])

        from_str9 = gmpy2ify([str9])

        self.assertEqual(from_str1, from_str2)
        self.assertEqual(from_str2, from_str3)
        self.assertEqual(from_str3, from_str4)
        self.assertEqual(from_str4, from_str1)
        self.assertEqual(from_str1[0], {})
        self.assertEqual(from_str1[1][0], 2)

        self.assertEqual(from_str5, from_str6)
        self.assertEqual(from_str6, from_str7)
        self.assertEqual(from_str7, from_str8)
        self.assertEqual(from_str8, from_str5)
        self.assertEqual(from_str5[0][0], 3)
        self.assertEqual(from_str5[1][0], 2)

        self.assertEqual(from_str9[0], {})
        self.assertEqual(from_str9[1][0], 2)

    def test_rational_construction(self):
        str1 = self.rat_str #= "-2/3"

        from_str = gmpy2ify([str1])
        self.assertEqual(from_str[0][0], gmpy2.mpq(-2,3))
        self.assertEqual(from_str[1], {})

    def test_gauss_rat_construction(self):
        str1 = self.imag_rat_str1
        str2 = self.imag_rat_str2
        str3 = self.imag_rat_str3
        str4 = self.imag_rat_str4
        str5 = self.gauss_rat_str1
        str6 = self.gauss_rat_str2
        str7 = self.gauss_rat_str3
        str8 = self.gauss_rat_str4

        str9 = self.gauss_rat_zero

        from_str1 = gmpy2ify([str1])
        from_str2 = gmpy2ify([str2])
        from_str3 = gmpy2ify([str3])
        from_str4 = gmpy2ify([str4])

        from_str5 = gmpy2ify([str5])
        from_str6 = gmpy2ify([str6])
        from_str7 = gmpy2ify([str7])
        from_str8 = gmpy2ify([str8])

        from_str9 = gmpy2ify([str9])

        self.assertEqual(from_str1, from_str2)
        self.assertEqual(from_str2, from_str3)
        self.assertEqual(from_str3, from_str4)
        self.assertEqual(from_str4, from_str1)
        self.assertEqual(from_str1[0], {})
        self.assertEqual(from_str1[1][0], gmpy2.mpq(-2,3))

        self.assertEqual(from_str5, from_str6)
        self.assertEqual(from_str6, from_str7)
        self.assertEqual(from_str7, from_str8)
        self.assertEqual(from_str8, from_str5)
        self.assertEqual(from_str5[0][0], -1)
        self.assertEqual(from_str5[1][0], gmpy2.mpq(-2,3))

        self.assertEqual(from_str9[0], {})
        self.assertEqual(from_str9[1][0], gmpy2.mpq(-2,3))

    def test_float_construction(self):
        lit  = self.float_literal
        str1 = self.float_str

        from_lit = gmpy2ify([lit])
        from_str = gmpy2ify([str1])
        self.assertEqual(from_lit, from_str)
        self.assertEqual(from_lit[0][0], 3.14159)
        self.assertEqual(from_lit[1], {})

    def test_complex_construction(self):
        str1 = self.imag_float_str1
        str2 = self.imag_float_str2
        str3 = self.imag_float_str3
        str4 = self.imag_float_str4
        str5 = self.imag_float_str5
        str6 = self.imag_float_str6
        str7 = self.complex_str1
        str8 = self.complex_str2
        str9 = self.complex_str3
        str10 = self.complex_str4
        str11 = self.complex_str5
        str12 = self.complex_str6
        str13 = self.complex_zero

        from_str1 = gmpy2ify([str1])
        from_str2 = gmpy2ify([str2])
        from_str3 = gmpy2ify([str3])
        from_str4 = gmpy2ify([str4])
        self.assertRaises(TypeError, gmpy2ify, str5)
        from_str6 = gmpy2ify([str6])

        from_str7 = gmpy2ify([str7])
        from_str8 = gmpy2ify([str8])
        from_str9 = gmpy2ify([str9])
        from_str10 = gmpy2ify([str10])
        self.assertRaises(TypeError, gmpy2ify, str11)
        from_str12 = gmpy2ify([str12])

        from_str13 = gmpy2ify([str13])

        self.assertEqual(from_str1, from_str2)
        self.assertEqual(from_str2, from_str3)
        self.assertEqual(from_str3, from_str4)
        self.assertEqual(from_str4, from_str6)
        self.assertEqual(from_str6, from_str1)
        self.assertEqual(from_str1[0], {})
        self.assertEqual(from_str1[1][0], 3.14159)

        self.assertEqual(from_str7, from_str8)
        self.assertEqual(from_str8, from_str9)
        self.assertEqual(from_str9, from_str10)
        self.assertEqual(from_str10, from_str12)
        self.assertEqual(from_str12, from_str7)
        self.assertAlmostEqual(from_str7[0][0], 27.1828)
        self.assertAlmostEqual(from_str7[1][0], 3.14159)

        self.assertEqual(from_str13[0], {})
        self.assertAlmostEqual(from_str13[1][0], 3.14159)

if __name__ == "__main__":
    unittest.main()
