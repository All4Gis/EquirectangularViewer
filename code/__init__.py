"""
/***************************************************************************
 Equirectangular Viewer
                                 A QGIS plugin
 Show local equirectangular images.
                             -------------------
        begin                : 2017-02-17
        copyright            : (C) 2016 All4Gis.
        email                : franka1986@gmail.com
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 #   any later version.                                                    *
 *                                                                         *
 ***************************************************************************/
"""
import sys

try:
    sys.path.append("C:\eclipse\plugins\org.python.pydev.core_8.3.0.202104101217\pysrc")
    sys.path.append(
        "/home/fragalop/eclipse/plugins/org.python.pydev.core_8.3.0.202104101217/pysrc"
    )
    from pydevd import *
except ImportError:
    None


def classFactory(iface):
    from .Geo360 import Geo360

    return Geo360(iface)
