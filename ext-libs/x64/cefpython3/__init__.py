__all__ = ["cefpython", "wx"]
__version__ = "31.2"
__author__ = "The CEF Python authors"

import sys

if 0x02070000 <= sys.hexversion < 0x03000000:
    from . import cefpython_py27 as cefpython
elif 0x03000000 <= sys.hexversion < 0x04000000:
    from . import cefpython_py32 as cefpython
else:
    raise Exception("Unsupported python version: " + sys.version)
