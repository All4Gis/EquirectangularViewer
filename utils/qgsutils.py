"""
/***************************************************************************
 Geo360 viewer Plugin    
 ***************************************************************************/
"""

from EquirectangularViewer.utils.log import log
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt, QCoreApplication
from qgis.gui import QgsRubberBand, QgsMessageBar


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

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
    def removeAllHighlightFeaturesFromCanvasScene(canvas):
        ''' Remove Highlight from canvas '''
        vertex_items = [i for i in canvas.scene().items(
        ) if issubclass(type(i), QgsRubberBand)]
        for ver in vertex_items:
            if ver in canvas.scene().items():
                canvas.scene().removeItem(ver)

    @staticmethod
    def showUserAndLogMessage(parent, before, text, level, duration=3, onlyLog=False):
        ''' Show user & log info/warning/error messages '''
        if not onlyLog:
            parent.iface.messageBar().popWidget()
            parent.iface.messageBar().pushMessage(
                _fromUtf8(before), _fromUtf8(text), level=level, duration=duration)
            QtGui.qApp.processEvents()
        if level == QgsMessageBar.INFO:
            log.info(text)
        elif level == QgsMessageBar.WARNING:
            log.warning(text)
        elif level == QgsMessageBar.CRITICAL:
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
