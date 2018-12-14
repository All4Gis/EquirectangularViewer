"""
/***************************************************************************
 Geo360 viewer Plugin
 ***************************************************************************/
"""

from qgis.core import Qgis as QGis
from qgis.gui import QgsRubberBand
from qgis.utils import iface

from EquirectangularViewer.utils.log import log

try:
    from pydevd import *
except ImportError:
    None


class qgsutils(object):

    @staticmethod
    def getAttributeFromFeature(feature, columnName):
        ''' Get Attribute from feature '''
        return feature.attribute(columnName)

    @staticmethod
    def zoomToFeature(canvas, layer, ide):
        ''' Zoom to feature by Id '''
        if layer:
            for feature in layer.getFeatures():
                if feature.id() == ide:
                    canvas.setExtent(feature.geometry().boundingBox())
                    canvas.refresh()
                    return True
        return False

    @staticmethod
    def showUserAndLogMessage(before, text="", level=QGis.Info, duration=3, onlyLog=False):
        ''' Show user & log info/warning/error messages '''
        if not onlyLog:
            iface.messageBar().popWidget()
            iface.messageBar().pushMessage(
                before, text, level=level, duration=duration)
        if level == QGis.Info:
            log.info(text)
        elif level == QGis.Warning:
            log.warning(text)
        elif level == QGis.Critical:
            log.error(text)
        return

    @staticmethod
    def getToFeature(layer, ide):
        ''' Get To feature by ID '''
        if layer:
            for feature in layer.getFeatures():
                if feature.id() == ide:
                    return feature
        return False
