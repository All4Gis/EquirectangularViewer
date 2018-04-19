# -*- coding: utf-8 -*-
import sys


try:
    sys.path.append(
        "D:\eclipse\plugins\org.python.pydev_5.9.2.201708151115\pysrc")
except ImportError:
    None


def classFactory(iface):
    from Geo360 import Geo360
    return Geo360(iface)
