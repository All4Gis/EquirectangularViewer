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
import os
from qgis.gui import QgsMapToolIdentify
from PyQt5.QtCore import QTimer, Qt, QSettings, QThread
from PyQt5.QtGui import QIcon, QCursor, QPixmap
from PyQt5.QtWidgets import QAction

from EquirectangularViewer.Geo360Dialog import Geo360Dialog
import EquirectangularViewer.config as config
from EquirectangularViewer.server.local_server import serverInFolder, serverShutdown
from EquirectangularViewer.utils.log import log
from EquirectangularViewer.utils.qgsutils import qgsutils
from qgis.core import QgsApplication
import platform

try:
    from pydevd import *
except ImportError:
    None

# libs_path = os.path.join(os.path.dirname(__file__), "libs")
# sys.path.append(libs_path)

try:
    from cefpython3 import cefpython as cef
    import ctypes
except ImportError:
    None

WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")

class Geo360:

    """QGIS Plugin Implementation."""

    def __init__(self, iface):

        if not cef.GetAppSetting("external_message_pump"):
            self.timer = self.createTimer()
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        threadcount = QThread.idealThreadCount()
        # use all available cores and parallel rendering
        QgsApplication.setMaxThreads(threadcount)
        QSettings().setValue("/qgis/parallel_rendering", True)
        # OpenCL acceleration
        QSettings().setValue("/core/OpenClEnabled", True)
        self.dlg = None

    def createTimer(self):
        timer = QTimer()
        timer.timeout.connect(self.onTimer)
        timer.start(10)
        return timer

    def onTimer(self):
        try:
            cef.MessageLoopWork()
        except Exception:
            None

    def stopTimer(self):
        self.timer.stop()

    def StartCefPython(self):
        ''' Start CefPython '''
        settings = {}
        settings["browser_subprocess_path"] = "%s/%s" % (
            cef.GetModuleDirectory(), "subprocess")
        settings["log_severity"] = cef.LOGSEVERITY_DISABLE
        settings["context_menu"] = {
            "enabled": True,
            "navigation": False,  # Back, Forward, Reload
            "print": True,
            "view_source": True,
            "external_browser": False,  # Open in external browser
            "devtools": True,  # Developer Tools
        }
        
        if MAC:
        # requires enabling message pump on Mac
        # in Qt example. Calling cef.DoMessageLoopWork in a timer
        # doesn't work anymore.
            settings["external_message_pump"] = True

        cef.Initialize(settings)

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
        #ShutDown server
        serverShutdown()
        #ShutDown Cef
        cef.Shutdown()

    def run(self):
        ''' Run click feature '''
        #Trick fix AttributeError: module 'sys' has no attribute 'argv'
        # We need fedback about this
        sys.argv = []

        self.found = False

        # Check if mapa foto is loaded
        lys = self.canvas.layers()
        for layer in lys:
            if layer.name() == config.layer_name:
                self.found = True
                self.mapTool = SelectTool(self.iface, parent=self, layer=layer)
                self.iface.mapCanvas().setMapTool(self.mapTool)

        if self.found is False:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"You need to upload the photo layer.")
            return

        # Folder viewer for local server
        folder = QgsApplication.qgisSettingsDirPath() + 'python/plugins/EquirectangularViewer/viewer'
        # Start local server in plugin folder
        serverInFolder(folder)
        self.StartCefPython()


    def ShowDialog(self, featuresId=None, layer=None):
        ''' Run dialog Geo360 '''
        self.featuresId = featuresId
        self.layer = layer

        if self.dlg is None:
            self.dlg = Geo360Dialog(self.iface, parent=self, featuresId=featuresId, layer=self.layer)
            self.dlg.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
            self.dlg.show()
        else:
            self.dlg.ReloadView(self.featuresId)


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
