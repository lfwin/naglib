"""Environmental (i.e., working) constants for NAGlib"""
# set default tolerance
tol = 1e-15
# set default dps for arbitrary-precision fp numbers
dps = 50

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
DEBUG = __naglib_debug()
