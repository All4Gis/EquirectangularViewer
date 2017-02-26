# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtCore
  
# try:
#     sys.path.append("C:/eclipse/plugins/org.python.pydev_5.5.0.201701191708/pysrc")
# except:
#     None

def classFactory(iface):
    from Geo360 import Geo360
    return Geo360(iface)
