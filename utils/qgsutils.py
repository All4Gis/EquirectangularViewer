"""
/***************************************************************************
 Geo360 viewer Plugin    
 ***************************************************************************/
"""
import os

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt, QCoreApplication

from qgis.gui import QgsRubberBand, QgsMessageBar

from EquirectangularViewer.utils.log import log

try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	def _fromUtf8(s):
		return s
	
try:
	import sys
	from pydevd import *
except:
	None;

class qgsutils(object):
 
	@staticmethod
	def getAttributeFromFeature(feature, columnName):
		return feature.attribute(columnName)

	@staticmethod	
	def zoomToFeature(canvas, layer, id):
		if layer:
			for feature in layer.getFeatures():
				if feature.id()== id:
					canvas.setExtent(feature.geometry().boundingBox())
					canvas.refresh()
					return True
		return False

	@staticmethod
	def removeAllHighlightFeaturesFromCanvasScene(canvas):
		vertex_items = [ i for i in canvas.scene().items() if issubclass(type(i), QgsRubberBand)]
		for ver in vertex_items:
			if ver in canvas.scene().items():
				canvas.scene().removeItem(ver)

	#Show user & log info/warning/error messages
	@staticmethod
	def showUserAndLogMessage(parent, before, text, level, duration = 3, onlyLog = False):
		if not onlyLog:	 
			parent.iface.messageBar().popWidget()
			parent.iface.messageBar().pushMessage(_fromUtf8(before), _fromUtf8(text), level = level, duration = duration) 
			QtGui.qApp.processEvents()
		if level == QgsMessageBar.INFO:
			log.info(text)
		elif level == QgsMessageBar.WARNING:
			log.warning(text)
		elif level == QgsMessageBar.CRITICAL:
			log.error(text)
		#QgsMessageLog.logMessage(text, level = level)
		return

	@staticmethod	
	def getToFeature(canvas, layer, id):
		if layer:
			for feature in layer.getFeatures():
				if feature.id()== id:
					return feature
		return False
 