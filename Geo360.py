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

from Geo360Dialog import Geo360Dialog
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QTimer, Qt
from PyQt4.QtGui import QAction, QIcon, QCursor, QPixmap
import config
import gui.generated.resources_rc
from qgis.core import *
from qgis.gui import QgsMapToolIdentify, QgsMessageBar
import qgis.utils
from server.local_server import *
from utils.log import log
from utils.qgsutils import qgsutils


try:
    from pydevd import *
except ImportError:
    None

try:
    from cefpython3 import cefpython
except ImportError:
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
        ''' Start CefPython '''
        qgsutils.showUserAndLogMessage(
            self, u"Information: ", u"Create Viewer.", QgsMessageBar.INFO,
            onlyLog=True)
        settings = {}
        settings["browser_subprocess_path"] = "%s/%s" % (
            cefpython.GetModuleDirectory(), "subprocess")
        settings["log_severity"] = cefpython.LOGSEVERITY_DISABLE
        settings["context_menu"] = {
            "enabled": False,
            "navigation": False,  # Back, Forward, Reload
            "print": False,
            "view_source": False,
            "external_browser": False,  # Open in external browser
            "devtools": False,  # Developer Tools
        }

        cefpython.Initialize(settings)

    def initGui(self):
        ''' Add Geo360 tool '''
        log.initLogging()
        self.action = QAction(QIcon(":/EquirectangularViewer/images/icon.png"),
                              u"Equirectangular Viewer",
                              self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Equirectangular Viewer", self.action)

    def unload(self):
        ''' Unload Geo360 tool '''
        self.iface.removePluginMenu(u"&Equirectangular Viewer", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        ''' Run click feature '''
        self.encontrado = False

        # Check if mapa foto is loaded
        lys = self.canvas.layers()
        if len(lys) == 0:
            qgsutils.showUserAndLogMessage(
                self, u"Information: ", u"You need to upload the photo layer.",
                QgsMessageBar.INFO)
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

        if self.encontrado is False:
            qgsutils.showUserAndLogMessage(
                self, u"Information: ", u"You need to upload the photo layer.",
                level=QgsMessageBar.INFO)

        return

    def ShowDialog(self, featuresId=None, layer=None):
        ''' Run dialog Geo360 '''
        self.featuresId = featuresId
        self.layer = layer

        Geo360 = qgis.utils.plugins["EquirectangularViewer"]
        try:
            if (Geo360.dlg):
                qgsutils.removeAllHighlightFeaturesFromCanvasScene(self.canvas)
                self.dlg.ReloadView(self.featuresId)

                if(Geo360.dlg.isVisible() is False):
                    self.dlg.show()
                return
        except:
            self.dlg = Geo360Dialog(self.iface, parent=self.iface.mainWindow(
            ), featuresId=featuresId, layer=self.layer)
            self.dlg.setWindowFlags(
                Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
            self.dlg.show()
            None


class SelectTool(QgsMapToolIdentify):
    ''' Select Photo on map '''

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
        found_features = self.identify(
            event.x(), event.y(), [self.layer], self.TopDownAll)

        if len(found_features) > 0:

            layer = found_features[0].mLayer
            feature = found_features[0].mFeature

            qgsutils.zoomToFeature(self.canvas, layer, feature.id())
            self.parent.ShowDialog(featuresId=feature.id(), layer=layer)
