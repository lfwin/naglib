"""Define constants and register exit functions"""
TOL = 1e-15
DPS = 50
TEMPDIR = '/tmp/naglib/'

import sys
if sys.version_info[0] == 2 and sys.version_info[1] < 6:
    msg = 'Python version 2.7 or above is required for NAGlib.'
    raise ImportError(msg)
else:  # Python 3
    pass
    # Here we can also check for specific Python 3 versions, if needed
del sys

# create a temporary directory in which to work
def settempdir(dirname=TEMPDIR):
    import naglib as nl
    
    import os
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        
    if 'TEMPDIR' in dir(nl):
        nl.TEMPDIR = dirname
    
    return dirname

from sympy import __version__ as spver
spver = [int(n) for n in spver.split('.')[:3]]
if spver[0] == 0 and spver[1] == 7 and spver[2] < 6:
    msg = 'SymPy version 0.7.6 or above is required for NAGlib'
    raise ImportError(msg)
del spver

# determine whether we are testing/debugging or not
def __naglib_debug():
    # helper function so we don't import os globally
    import os
    debug_str = os.getenv('NAGLIB_DEBUG', 'False')
    if debug_str in ('True', 'False'):
        return eval(debug_str)
    else:
        msg = 'unrecognized value for NAGLIB_DEBUG: {0}'.format(debug_str)
        raise RuntimeError(msg)
NAGLIB_DEBUG = __naglib_debug()
TEMPDIR = settempdir(TEMPDIR)

# register a cleanup function on exit
import atexit
@atexit.register
def cleanup():
    if NAGLIB_DEBUG:
        pass
    # bug here
    #else:
        #import os
        #import shutil
        #if os.path.exists(TEMPDIR):
            #shutil.rmtree(TEMPDIR)
del atexit
