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

from qgis.gui import QgsMapToolIdentify
from qgis.PyQt.QtCore import Qt, QSettings, QThread
from qgis.PyQt.QtGui import QIcon, QCursor, QPixmap
from qgis.PyQt.QtWidgets import QAction

from EquirectangularViewer.Geo360Dialog import Geo360Dialog
import EquirectangularViewer.config as config
from EquirectangularViewer.utils.log import log
from EquirectangularViewer.utils.qgsutils import qgsutils
from qgis.core import QgsApplication
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import time

try:
    from pydevd import *
except ImportError:
    None


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class Geo360:

    """QGIS Plugin Implementation."""

    def __init__(self, iface):

        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        threadcount = QThread.idealThreadCount()
        # use all available cores and parallel rendering
        QgsApplication.setMaxThreads(threadcount)
        QSettings().setValue("/qgis/parallel_rendering", True)
        # OpenCL acceleration
        QSettings().setValue("/core/OpenClEnabled", True)
        self.dlg = None
        self.server = None
        self.make_server()

    def initGui(self):
        """Add Geo360 tool"""
        log.initLogging()
        self.action = QAction(
            QIcon(":/EquirectangularViewer/images/icon.png"),
            u"Equirectangular Viewer",
            self.iface.mainWindow(),
        )
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Equirectangular Viewer", self.action)

    def unload(self):
        """Unload Geo360 tool"""
        self.iface.removePluginMenu(u"&Equirectangular Viewer", self.action)
        self.iface.removeToolBarIcon(self.action)
        # Close server
        self.close_server()

    def is_running(self):
        return self.server_thread and self.server_thread.is_alive()

    def close_server(self):
        # Close server
        if self.server is not None:
            self.server.shutdown()
            time.sleep(1)
            self.server.server_close()
            while self.server_thread.is_alive():
                self.server_thread.join()
            self.server = None

    def make_server(self):
        # Close server
        self.close_server()
        # Create Server
        directory = (
            QgsApplication.qgisSettingsDirPath().replace("\\", "/")
            + "python/plugins/EquirectangularViewer/viewer"
        )
        try:
            self.server = ThreadingHTTPServer(
                (config.IP, config.PORT),
                partial(QuietHandler, directory=directory),
            )
            self.server_thread = Thread(
                target=self.server.serve_forever, name="http_server"
            )
            self.server_thread.daemon = True
            print("Serving at port: %s" % self.server.server_address[1])
            time.sleep(1)
            self.server_thread.start()
            # while self.server_thread.is_alive():
            #     print ("isRunning")
        except Exception:
            print("Server Error")

    def run(self):
        """Run click feature"""
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
                u"Information: ", u"You need to upload the photo layer."
            )
            return

    def ShowDialog(self, featuresId=None, layer=None):
        """Run dialog Geo360"""
        self.featuresId = featuresId
        self.layer = layer

        if self.dlg is None:
            self.dlg = Geo360Dialog(
                self.iface, parent=self, featuresId=featuresId, layer=self.layer
            )
            self.dlg.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
            self.dlg.show()
        else:
            self.dlg.ReloadView(self.featuresId)


class SelectTool(QgsMapToolIdentify):
    """Select Photo on map"""

    def __init__(self, iface, parent=None, layer=None):
        QgsMapToolIdentify.__init__(self, iface.mapCanvas())
        self.canvas = iface.mapCanvas()
        self.iface = iface
        self.layer = layer
        self.parent = parent

        self.cursor = QCursor(
            QPixmap(
                [
                    "16 16 3 1",
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
                    "       +.+      ",
                ]
            )
        )

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def canvasReleaseEvent(self, event):
        found_features = self.identify(
            event.x(), event.y(), [self.layer], self.TopDownAll
        )

        if len(found_features) > 0:

            layer = found_features[0].mLayer
            feature = found_features[0].mFeature

            qgsutils.zoomToFeature(self.canvas, layer, feature.id())
            self.parent.ShowDialog(featuresId=feature.id(), layer=layer)
