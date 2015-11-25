"""Outsourcing printing of NAGlib types"""

# TODO: add support for gmpy2 and sympy types

import numbers

def str_integer_type(printme, from_real_imag=False, truncate=None):
    """
    Printing for Integer and GaussianInteger types

    Optional arguments
    ==================
    truncate: if None, attempt to intelligently determine whether
              we should truncate the length of the number
    """
    if isinstance(printme, numbers.GaussianInteger) or from_real_imag:
        if from_real_imag:
            reals, imags = printme
            shape = from_real_imag
        else:
            reals, imags = printme._real, printme._imag
            shape = printme._shape
        if hasattr(printme, "_is_scalar") and printme._is_scalar:
            if reals and imags:
                real, imag = reals[0], imags[0]
                if imag == 1:
                    rep = "{0} + I".format(real)
                elif imag == -1:
                    rep = "{0} - I".format(real)
                elif imag > 0:
                    rep = "{0} + {1}*I".format(real, imag)
                else:
                    rep = "{0} - {1}*I".format(real, -imag)
            elif reals:
                real = reals[0]
                rep = str(real)
            elif imags:
                imag = imags[0]
                if imag == 1:
                    rep = "I"
                elif imag == -1:
                    rep = "-I"
                else:
                    rep = "{0}*I".format(imag)
            else: # zero
                rep = '0'
            return rep
        else:
            rkeys = reals.keys()
            ikeys = imags.keys()
            entries = []
            for i in range(shape):
                if i in rkeys and i in ikeys:
                    real, imag = reals[i], imags[i]
                    if imag == 1:
                        rep = "{0} + I".format(real)
                    elif imag == -1:
                        rep = "{0} - I".format(real)
                    elif imag > 0:
                        rep = "{0} + {1}*I".format(real, imag)
                    else:
                        rep = "{0} - {1}*I".format(real, -imag)
                elif i in rkeys:
                    real = reals[i]
                    rep = str(real)
                elif i in ikeys:
                    imag = imags[i]
                    if imag == 1:
                        rep = 'I'
                    elif imag == -1:
                        rep = "-I"
                    else:
                        rep = str(imag) + "*I"
                else: # zero
                    rep = '0'
                entries.append(rep)

        return '(' + ", ".join(entries) + ')'
    elif type(printme) in (int, long):
        return str(printme)
    else:
        msg = "can't understand data type"
        raise TypeError(msg)

def str_rational_type(printme, from_real_imag=False, truncate=None):
    """
    Printing for Rational and GaussianRational types

    Optional arguments
    ==================
    truncate: if None, attempt to intelligently determine whether
              we should truncate the length of the number
    """
    from fractions import Fraction
    if isinstance(printme, numbers.GaussianRational) or from_real_imag:
        if from_real_imag:
            reals, imags = printme
            shape = from_real_imag
        else:
            reals, imags = printme._real, printme._imag
            shape = printme._shape
        if hasattr(printme, "_is_scalar") and printme._is_scalar:
            if imags:
                num,denom = imags[0].numerator, imags[0].denominator

            if reals and imags:
                real, imag = reals[0], imags[0]
                if imag == 1:
                    rep = "{0} + I".format(real)
                elif imag == -1:
                    rep = "{0} - I".format(real)
                elif denom == 1 and num > 0:
                    rep = "{0} + {1}*I".format(real, num)
                elif denom == 1 and num < 0:
                    rep = "{0} - {1}*I".format(real, -num)
                elif num == 1:
                    rep = "{0} + I/{1}".format(real, denom)
                elif num > 1:
                    rep = "{0} + {1}*I/{2}".format(real, num, denom)
                elif num == -1:
                    rep = "{0} - I/{1}".format(real, denom)
                else:
                    rep = "{0} - {1}*I/{2}".format(real, -num, denom)
            elif reals:
                real = reals[0]
                rep = str(real)
            elif imags:
                imag = imags[0]
                if imag == 1:
                    rep = 'I'
                elif imag == -1:
                    rep = "-I"
                elif denom == 1:
                    rep = "{0}*I".format(num)
                elif num == 1:
                    rep = "I/{0}".format(denom)
                elif num == -1:
                    rep = "-I/{0}".format(denom)
                else:
                    rep = "{0}*I/{1}".format(num, denom)
            else: # zero
                rep = '0'
            return rep
        else:
            rkeys = real.keys()
            ikeys = imag.keys()
            entries = []
            for i in range(shape):
                if i in ikeys:
                    num, denom = imag[i].numerator, imag[i].denominator

                if i in rkeys and i in ikeys:
                    real, imag = reals[i], imags[i]
                    if imag == 1:
                        rep = "{0} + I".format(real)
                    elif imag == -1:
                        rep = "{0} - I".format(real)
                    elif denom == 1 and num > 0:
                        rep = "{0} + {1}*I".format(real, num)
                    elif denom == 1 and num < 0:
                        rep = "{0} - {1}*I".format(real, -num)
                    elif num == 1:
                        rep = "{0} + I/{1}".format(real, denom)
                    elif num > 1:
                        rep = "{0} + {1}*I/{2}".format(real, num, denom)
                    elif num == -1:
                        rep = "{0} - I/{1}".format(real, denom)
                    else:
                        rep = "{0} - {1}*I/{2}".format(real, -num, denom)
                elif i in rkeys:
                    real = reals[i]
                    rep = str(real)
                elif i in ikeys:
                    imag = imags[i]
                    if imag == 1:
                        rep = 'I'
                    elif imag == -1:
                        rep = "-I"
                    elif denom == 1:
                        rep = "{0}*I".format(num)
                    elif num == 1:
                        rep = "I/{0}".format(denom)
                    elif num == -1:
                        rep = "-I/{0}".format(denom)
                    else:
                        rep = "{0}*I/{1}".format(num, denom)
                else:
                    rep = '0'
                entries.append(rep)

        return '(' + ", ".join(entries) + ')'
    elif isinstance(printme, Fraction):
        return str(printme)
    else:
        msg = "can't understand data type"
        raise TypeError(msg)

def str_float_type(printme, from_real_imag=False, truncate=None):
    """
    Printing for Float and Complex types

    Optional arguments
    ==================
    truncate: if None, attempt to intelligently determine whether
              we should truncate the length of the number
    """
    if isinstance(printme, numbers.Complex) or from_real_imag:
        if from_real_imag:
            reals, imags = printme
            shape = from_real_imag
        else:
            reals, imags = printme._real, printme._imag
            shape = printme._shape
        if hasattr(printme, "_is_scalar") and printme._is_scalar:
            if reals and imags:
                real, imag = reals[0], imags[0]
                # if real == int(real):
                #     str_real = "{0:.1}".format(real)
                # else:
                str_real = str(real)
                # if imag == int(imag):
                #     str_imag = "{0:.1}".format(abs(imag))
                # else:
                str_imag = str(abs(imag))

                if imag > 0:
                    rep = "{0} + {1}*I".format(str_real, str_imag)
                else:
                    rep = "{0} - {1}*I".format(str_real, str_imag)
            elif reals:
                real = reals[0]
                # if real == int(real):
                #     rep = "{0:.1}".format(real)
                # else:
                rep = str(real)
            elif imags:
                imag = imags[0]
                # if imag == int(imag):
                #     str_imag = "{0:.1}".format(imag)
                # else:
                str_imag = str(imag)
                rep = "{0}*I".format(str_imag)
            else: # zero
                rep = '0'
            return rep
        else:
            rkeys = reals.keys()
            ikeys = imags.keys()
            entries = []
            for i in range(shape):
                if i in rkeys and i in ikeys:
                    real, imag = reals[i], imags[i]
                    # if real == int(real):
                    #     str_real = "{0:.1}".format(real)
                    # else:
                    str_real = str(real)
                    # if imag == int(imag):
                    #     str_imag = "{0:.1}".format(abs(imag))
                    # else:
                    str_imag = str(abs(imag))

                    if imag > 0:
                        rep = "{0} + {1}*I".format(str_real, str_imag)
                    else:
                        rep = "{0} - {1}*I".format(str_real, str_imag)
                elif i in rkeys:
                    real = reals[i]
                    # if real == int(real):
                    #     rep = "{0:.1}".format(real)
                    # else:
                    rep = str(real)
                elif i in ikeys:
                    imag = imags[i]
                    # if imag == int(imag):
                    #     str_imag = "{0:.1}".format(imag)
                    # else:
                    str_imag = str(imag)
                    rep = "{0}*I".format(str_imag)
                else: # zero
                    rep = '0'
                entries.append(rep)

        return '(' + ", ".join(entries) + ')'
    elif type(printme) in (float, complex):
        return str(printme)
    else:
        msg = "can't understand data type"
        raise TypeError(msg)
