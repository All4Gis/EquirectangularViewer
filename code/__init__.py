# -*- coding: utf-8 -*-
import sys

try:
    sys.path.append(
        "D:\eclipse\plugins\org.python.pydev.core_7.0.3.201811082356\pysrc")
    from pydevd import *
except ImportError:
    None


def classFactory(iface):
    from .Geo360 import Geo360
    return Geo360(iface)
