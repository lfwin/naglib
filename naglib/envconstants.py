"""Environmental (i.e., working) constants for NAGlib"""
# set default tolerance
tol = 1e-15
# set default precision for arbitrary-precision fp numbers to double
prec = 53
# set default maximum length of numerical reprs
replen = 5

# are we debugging or not?
# code modified from sympy/__init__.py
def __naglib_debug():
    import os
    debug_str = os.getenv('NAGLIB_DEBUG', 'False')
    if debug_str in ('True', 'False'):
        return eval(debug_str)
    else:
        msg = 'unrecognized value for NAGLIB_DEBUG: {0}'.format(debug_str)
        raise RuntimeError(msg)
debug = __naglib_debug()

def __get_ground_types():
    ground_num = "base"
    ground_sym = "none"
    try:
        import libpybertini
        ground_num = "bertini"
        ground_sym = "bertini"
    except ImportError:
        pass

    try:
        import gmpy
        ground_num = "gmpy"
    except ImportError:
        pass

    try:
        import gmpy2
        ground_num = "gmpy2"
    except ImportError:
        pass

    try:
        import sympy
        ground_sym = "sympy"
    except ImportError:
        pass

    return ground_num, ground_sym

ground_num, ground_sym = __get_ground_types()
