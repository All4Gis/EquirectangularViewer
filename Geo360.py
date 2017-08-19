# -*- coding: utf-8 -*-
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
import os.path
from qgis.core import *
from qgis.gui import QgsMapToolIdentify, QgsMessageBar
import qgis.utils

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Geo360Dialog import Geo360Dialog 
import config
import gui.generated.resources_rc
from server.local_server import *
from utils.log import log
from utils.qgsutils import qgsutils


try:
    import sys
    from pydevd import *
except:
    None
    
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    import ctypes
    from cefpython3 import cefpython
except:
    None
       
    
class Geo360:
    timer = None
    
    """QGIS Plugin Implementation."""
     
    def __init__(self, iface):
        
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        
        self.plugin_path = os.path.dirname(os.path.realpath(__file__))

    def createTimer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.onTimer)
        self.timer.start(10)

    def onTimer(self):
        try:
            cefpython.MessageLoopWork()
        except:
            None
        

    def stopTimer(self):
        self.timer.stop()
  
  
    def StartCefPython(self):
        qgsutils.showUserAndLogMessage(self, u"Information: ", u"Create Viewer.", QgsMessageBar.INFO, onlyLog=True)   
        settings = {}
        settings["browser_subprocess_path"] = "%s/%s" % (
            cefpython.GetModuleDirectory(), "subprocess")
        settings["log_severity"] = cefpython.LOGSEVERITY_DISABLE  # LOGSEVERITY_DISABLE - will not create "debug.log" file.
        settings["context_menu"] = {
            "enabled": False,
            "navigation": False,  # Back, Forward, Reload
            "print": False,
            "view_source": False,
            "external_browser": False,  # Open in external browser
            "devtools": False,  # Developer Tools
        }
    
        cefpython.Initialize(settings)
        
    # Add Geo360 tool
    def initGui(self):
        log.initLogging()
        self.action = QAction(QIcon(":/EquirectangularViewer/images/icon.png"), u"Equirectangular Viewer", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Equirectangular Viewer", self.action)
 

    # Unload Geo360 tool
    def unload(self):
        self.iface.removePluginMenu(u"&Equirectangular Viewer", self.action)
        self.iface.removeToolBarIcon(self.action)
 
    # Run click feature
    def run(self):
        self.encontrado = False       
        
        # Check if mapa foto is loaded
        lys = self.canvas.layers()
        if len(lys) == 0:
            qgsutils.showUserAndLogMessage(self, u"Information: ", u"You need to upload the photo layer.", level=QgsMessageBar.INFO)
            return
        
        # Folder viewer for local server
        folder = self.plugin_path + "\\viewer"        
       
        # Start local server in plugin folder
        openWebApp(folder)
        QtGui.qApp.processEvents()  
        
        self.StartCefPython()  
        QtGui.qApp.processEvents()    
 
        # Create Timer is necessary for cefpython
        self.createTimer()
        QtGui.qApp.processEvents() 
        
        for layer in lys:
            if layer.name() == config.layer_name:
                self.encontrado = True
                self.mapTool = SelectTool(self.iface, parent=self, layer=layer)
                self.iface.mapCanvas().setMapTool(self.mapTool)
                
        if self.encontrado == False:
            qgsutils.showUserAndLogMessage(self, u"Information: ", u"You need to upload the photo layer.", level=QgsMessageBar.INFO)   
    
        return
 
    # Run dialog Geo360
    def ShowDialog(self, featuresId=None, layer=None): 
        
        self.featuresId = featuresId
        self.layer = layer
 
        Geo360 = qgis.utils.plugins["EquirectangularViewer"] 
        try:
            if (Geo360.dlg):                
                qgsutils.removeAllHighlightFeaturesFromCanvasScene(self.canvas)
                self.dlg.ReloadView(self.featuresId) 
                
                if(Geo360.dlg.isVisible() == False):
                    self.dlg.show()                     
                return
        except: 
            self.dlg = Geo360Dialog(self.iface, parent=self.iface.mainWindow(), featuresId=featuresId, layer=self.layer)
            self.dlg.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
            self.dlg.show()        
            None          
                          
# Select Photo on map
class SelectTool(QgsMapToolIdentify):
    def __init__(self, iface, parent=None, layer=None):
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())   
        self.canvas = iface.mapCanvas()
        self.iface = iface
        self.layer = layer
        self.parent = parent

        self.cursor = QCursor(QPixmap(["16 16 3 1",
                    "      c None",
                    ".     c #FF0000",
                    "+     c #FFFFFF",
                    "                ",
                    "       +.+      ",
                    "      ++.++     ",
                    "     +.....+    ",
                    "    +.     .+   ",
                    "   +.   .   .+  ",
                    "  +.    .    .+ ",
                    " ++.    .    .++",
                    " ... ...+... ...",
                    " ++.    .    .++",
                    "  +.    .    .+ ",
                    "   +.   .   .+  ",
                    "   ++.     .+   ",
                    "    ++.....+    ",
                    "      ++.++     ",
                    "       +.+      "]))

    def activate(self):
        self.canvas.setCursor(self.cursor)
    
    def canvasReleaseEvent(self, event):
        found_features = self.identify(event.x(), event.y(), [self.layer], self.TopDownAll)
        
        if len(found_features) > 0:

            layer = found_features[0].mLayer
            feature = found_features[0].mFeature

            qgsutils.zoomToFeature(self.canvas, layer, feature.id())         
            self.parent.ShowDialog(featuresId=feature.id(), layer=layer)
