"""Assist conversion of user input to NAGlib-style data objects"""

from .core import string_types

import re
import gmpy2

is_int = re.compile(r"^[-+]?\d+$")
is_rational = re.compile(r"^[-+]?\d+/\d+$")
is_float = re.compile(r"^[-+]?\d*\.?\d+([eE][-+]?\d+)?$")

is_imag_int = re.compile(r"^[-+]?([iI](\s*\*?\s*\d+)?|\d+\s*\*?\s*[iI])$")
is_imag_rational = re.compile(r"^[-+]?([iI](\s*\*?\s*\d+)?/\d+|\d+\s*\*?\s*[iI]/\d+)$")
is_imag_float = re.compile(r"^[-+]?([iI]\s*\*?\s*\d+\.?\d+([eE][-+]?\d+)?|\d*\.?\d+([eE][-+]?\d+)?(j|\s*\*?\s*[iI]))$")

def is_gaussian_int(val):
    # use positive lookbehind so we don't accidentally capture [+-] at the
    # beginning of a string
    val = re.sub(r' ', '', val)
    breakup = re.split(r"(?<=[iI\d])[-+]", val)
    if len(breakup) != 2:
        return False
    else:
        a,b = breakup
        if (is_int.match(a) and is_imag_int.match(b)) or (is_imag_int.match(a) and is_int.match(b)):
            return True
        else:
            return False

def is_gaussian_rational(val):
    # use positive lookbehind so we don't accidentally capture [+-] at the
    # beginning of a string
    val = re.sub(r' ', '', val)
    breakup = re.split(r"(?<=[iI\d])[-+]", val)
    if len(breakup) != 2:
        return False
    else:
        a,b = breakup
        if (is_rational.match(a) and is_imag_rational.match(b)) \
            or (is_imag_rational.match(a) and is_rational.match(b)) \
            or (is_int.match(a) and is_imag_rational.match(b)) \
            or (is_rational.match(a) and is_imag_int.match(b)) \
            or (is_imag_int.match(a) and is_rational.match(b)) \
            or (is_imag_rational.match(a) and is_int.match(b)):
            return True
        else:
            return False

def is_complex(val):
    # use positive lookbehind so we don't accidentally capture [+-] at the
    # beginning of a string
    val = re.sub(r' ', '', val)
    breakup = re.split(r"(?<=[iI\d])[-+]", val) # should cover the case of exps
    if len(breakup) != 2:
        return False
    else:
        a,b = breakup
        if (is_float.match(a) and is_imag_float.match(b)) \
            or (is_imag_float.match(a) and is_float.match(b)) \
            or (is_int.match(a) and is_imag_float.match(b)) \
            or (is_float.match(a) and is_imag_int.match(b)) \
            or (is_imag_int.match(a) and is_float.match(b)) \
            or (is_imag_float.match(a) and is_int.match(b)):
            return True
        else:
            return False

def get_numeric_type(vals, all_possibilities=False):
    """
    Return the common numeric type which the iterable `vals' of strings is
    meant to represent.

    Rules
    =====
    * An int can be promoted to a Gaussian int, a rational, a Gaussian rational,
      a float, or a complex float.
    * A Gaussian int can be promoted to a Gaussian rational or a complex float.
    * A rational can be promoted to a Gaussian rational, a float, or a complex
      float.
    * A Gaussian rational can be promoted to a complex float.
    * A float can be promoted to a complex float.
    * The complex float is the apex data type and cannot be promoted.
    """
    from functools import reduce

    pmap = {"Complex":1,
            "Float":2,
            "GaussianRational":3,
            "Rational":6,
            "GaussianInteger":9,
            "Integer":18}
    pinv = dict([(pmap[k], k) for k in pmap.keys()])

    def gnt_promotion_map(left, right):
        from fractions import gcd
        ltype = pmap[left]
        rtype = pmap[right]
        return pinv[gcd(ltype, rtype)]

    datatypes = ["Integer", "GaussianInteger", "Rational", "GaussianRational",
                 "Float", "Complex"]
    dtlist = []

    for val in vals:
        if is_int.match(val):
            dtlist.append("Integer")
        elif is_imag_int.match(val) or is_gaussian_int(val):
            dtlist.append("GaussianInteger")
        elif is_rational.match(val):
            dtlist.append("Rational")
        elif is_imag_rational.match(val) or is_gaussian_rational(val):
            dtlist.append("GaussianRational")
        elif is_float.match(val):
            dtlist.append("Float")
        elif is_imag_float.match(val) or is_complex(val):
            dtlist.append("Complex")
        else:
            print("{0} is not a number".format(val)) # DEBUGGING
            return None

    try:
        min_possibility = reduce(gnt_promotion_map, dtlist)
    except TypeError: # dtlist is empty
        min_possibility = "Integer"
    if all_possibilities:
        possibilities = [pinv[k] for k in pinv.keys() if pmap[min_possibility] % k == 0]
        return possibilities
    else:
        return min_possibility

def gmpy2ify(vals, force_type=None, use_precision=None):
    """
    Return an iterable of gmpy2-format numerical values

    Optional arguments
    ==================
    force_type: require the given type, from among:
                "Integer", "GaussianInteger", "Rational",
                "GaussianRational", "Float", "Complex"
    use_precision: require the given precision (defaults to adaptive).
                   This argument will be ignored unless used with Float or
                   Complex types.
    """

    if force_type:
        if type(force_type) not in string_types:
            msg = "force_type requires a string argument"
            raise TypeError(msg)
        if force_type not in ("Integer", "GaussianInteger", "Rational",
                              "GaussianRational", "Float", "Complex"):
            msg = ("force_type requires one of the following arguments: "
                    '"Integer", "GaussianInteger", "Rational", '
                    '"GaussianRational", "Float", "Complex"')
            raise ValueError(msg)

    if type(vals) not in (tuple, list):
        msg = "can't make sense of data type"
        raise TypeError(msg)
    # strip () from Python complex types
    vals = [re.sub(r"^\(|\)$", "", str(val)) for val in vals]

    if force_type:
        all_types = get_numeric_type(vals, all_possibilities=True)
        if force_type in all_types:
            numeric_type = force_type
        else:
            msg = "can't create {0} from given values".format(force_type)
            raise ValueError(msg)
    else:
        numeric_type = get_numeric_type(vals, all_possibilities=False)

    shape = len(vals)
    rdict = {}
    idict = {}

    if numeric_type is None:
        msg = "can't make sense of input"
        raise ValueError(msg)

    if numeric_type == "Integer":
        for i in range(shape):
            val = gmpy2.mpz(vals[i])
            if val != 0:
                rdict[i] = val
        return rdict, idict
    elif numeric_type == "GaussianInteger":
        for i in range(shape):
            val = re.sub(r'\s', '', vals[i]) # remove whitespace
            breakup = re.split(r"(?<=[iI\d])([-+])", val)
            if len(breakup) == 1: # pure real or pure imag
                if 'i' in val or 'I' in val or 'j' in val:
                    val = re.sub(r"[iI\*]", '', val)
                    if val == '':
                        val = '1'
                    elif val == '-':
                        val = "-1"
                    val = gmpy2.mpz(val)
                    if val != 0:
                        idict[i] = val
                else:
                    val = gmpy2.mpz(val)
                    if val != 0:
                        rdict[i] = gmpy2.mpz(val)
            elif len(breakup) != 3:
                raise ValueError(val) # for debugging the regex
            else:
                left, right = breakup[0], breakup[1] + breakup[2]
                if 'i' in left or 'I' in left:
                    imag = re.sub(r"[iI\*]", '', left)
                    real = right
                else:
                    imag = re.sub(r"[iI\*]", '', right)
                    if imag == '-':
                        imag = '-1'
                    elif imag == '+':
                        imag = '1'
                    # TODO: do this better
                    elif imag[0] == '+': # stopgap
                        imag = imag[1:]
                    real = left
                real, imag = gmpy2.mpz(real), gmpy2.mpz(imag)
                if real != 0:
                    rdict[i] = real
                if imag != 0:
                    idict[i] = imag
        return rdict, idict
    elif numeric_type == "Rational":
        for i in range(shape):
            val = gmpy2.mpq(vals[i])
            if val != 0:
                rdict[i] = val
        return rdict, idict
    elif numeric_type == "GaussianRational":
        for i in range(shape):
            val = re.sub(r'\s', '', vals[i]) # remove whitespace
            breakup = re.split(r"(?<=[iI\d])([-+])", val)
            if len(breakup) == 1: # pure real or pure imag
                if 'i' in val or 'I' in val or 'j' in val:
                    val = re.sub(r"[iI\*]", '', val)
                    if val[0] == '/' or val == '':
                        val = '1' + val
                    elif val[:2] == "-/":
                        val = "-1" + val[1:]
                    elif val == '-':
                        val = "-1"
                    val = gmpy2.mpq(val)
                    if val != 0:
                        idict[i] = val
                else:
                    val = gmpy2.mpq(val)
                    if val != 0:
                        rdict[i] = val
            elif len(breakup) != 3:
                raise ValueError(val) # for debugging the regex
            else:
                left, right = breakup[0], breakup[1] + breakup[2]
                if 'i' in left or 'I' in left:
                    imag = re.sub(r"[iI\*]", '', left)
                    real = right
                else:
                    imag = re.sub(r"[iI\*]", '', right)
                    if imag == '-':
                        imag = '-1'
                    elif imag == '+':
                        imag = '1'
                    # TODO: do this better
                    elif imag[0] == '+': # stopgap
                        imag = imag[1:]
                    real = left
                real, imag = gmpy2.mpq(real), gmpy2.mpq(imag)
                if real != 0:
                    rdict[i] = real
                if imag != 0:
                    idict[i] = imag
        return rdict, idict
    elif numeric_type == "Float":
        from math import ceil
        if use_precision:
            max_prec = use_precision
        else:
            max_prec = 53 # start with default (i.e., double) precision
            ratio = 3.333 # rough ratio of precision to mantissa length
            # first determine the maximum precision
            for i in range(shape):
                val = vals[i]
                if is_rational.match(val):
                    continue
                val = re.sub(r"[-+\.]", '', vals[i]) # remove signs, decimal points
                val = re.split(r"[eE]", val)[0] # ignore exponent, if any, for now
                prec = int(ceil(len(val)*ratio))
                if max_prec < prec:
                    max_prec = prec
        # now create the mpfr types
        for i in range(shape):
            if is_rational.match(vals[i]):
                vals[i] = gmpy2.mpq(vals[i])
            val = gmpy2.mpfr(vals[i], max_prec)
            if val != 0:
                rdict[i] = val
        return rdict, idict
    elif numeric_type == "Complex":
        from math import ceil
        max_prec = 53 # start with default (i.e., double) precision
        ratio = 3.333 # rough ratio of precision to mantissa length
        # first determine the maximum precision
        rvals, ivals = [0 for i in range(shape)], [0 for i in range(shape)]
        for i in range(shape):
            val = re.sub(r'\s', '', vals[i]) # remove whitespace
            breakup = re.split(r"(?<=[iI\d])([-+])", val)
            if len(breakup) == 1: # pure real or pure imag
                if 'i' in val or 'I' in val or 'j' in val:
                    val = re.sub(r"[ijI\*]", '', val)
                    if val == '':
                        val = '1'
                    elif val == '-':
                        val = "-1"
                    rvals[i] = '0'
                    ivals[i] = val
                else:
                    rvals[i] = val
                    ivals[i] = '0'
            elif len(breakup) != 3:
                raise ValueError(val) # for debugging the regex
            else:
                left, right = breakup[0], breakup[1] + breakup[2]
                if 'i' in left or 'I' in left:
                    ivals[i] = re.sub(r"[iI\*]", '', left)
                    rvals[i] = right
                else:
                    imag = re.sub(r"[ijI\*]", '', right)
                    if imag == '-':
                        imag = '-1'
                    elif imag == '+':
                        imag = '1'
                    rvals[i] = left
                    ivals[i] = imag

            if use_precision:
                max_prec = use_precision
            else:
                if is_rational.match(rvals[i]):
                    continue
                rval = re.sub(r'.', '', rvals[i]) # remove decimal point, if any
                ival = re.sub(r'.', '', ivals[i])
                rval = re.split(r"[eE]", rval)[0] # ignore exponent, if any, for now
                ival = re.split(r"[eE]", ival)[0]
                prec = int(ceil(max(len(rval)*ratio, len(ival)*ratio)))
                if max_prec < prec:
                    max_prec = prec
        # now create the mpfr types
        for i in range(shape):
            if is_rational.match(rvals[i]):
                rvals[i] = gmpy2.mpq(rvals[i])
                ivals[i] = gmpy2.mpq(ivals[i])
            rval = gmpy2.mpfr(rvals[i], max_prec)
            ival = gmpy2.mpfr(ivals[i], max_prec)
            if rval != 0:
                rdict[i] = rval
            if ival != 0:
                idict[i] = ival
        return rdict, idict
