# -*- coding: utf-8 -*-
import sys

from PyQt4 import QtCore


try:
    sys.path.append("D:\eclipse\plugins\org.python.pydev_5.7.0.201704111357\pysrc")
except:
    None
    
def classFactory(iface):
    from Geo360 import Geo360
    return Geo360(iface)
