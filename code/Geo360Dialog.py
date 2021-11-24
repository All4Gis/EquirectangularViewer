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

import math
import os
from qgis.core import (
    QgsPointXY,
    QgsProject,
    QgsFeatureRequest,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.gui import QgsRubberBand

from qgis.PyQt.QtCore import (
    QObject,
    QUrl,
    Qt,
    pyqtSignal,
)
from qgis.PyQt.QtWidgets import QDialog, QWidget, QDockWidget
from qgis.PyQt.QtGui import QWindow
import EquirectangularViewer.config as config
from EquirectangularViewer.geom.transformgeom import transformGeometry
from EquirectangularViewer.gui.ui_orbitalDialog import Ui_orbitalDialog
from EquirectangularViewer.utils.qgsutils import qgsutils
from qgis.PyQt.QtWebKitWidgets import QWebView, QWebPage
from qgis.PyQt.QtWebKit import QWebSettings

try:
    from pydevd import *
except ImportError:
    None

try:
    from PIL import Image
except ImportError:
    None


class _ViewerPage(QWebPage):
    obj = []  # synchronous
    newData = pyqtSignal(list)  # asynchronous

    def javaScriptConsoleMessage(self, msg, line, source):
        l = msg.split(",")
        self.obj = l
        self.newData.emit(l)


class Geo360Dialog(QDockWidget, Ui_orbitalDialog):

    """Geo360 Dialog Class"""

    def __init__(self, iface, parent=None, featuresId=None, layer=None):

        QDockWidget.__init__(self)

        self.setupUi(self)

        self.DEFAULT_URL = (
            "http://" + config.IP + ":" + str(config.PORT) + "/viewer.html"
        )
        self.DEFAULT_EMPTY = (
            "http://" + config.IP + ":" + str(config.PORT) + "/none.html"
        )
        self.DEFAULT_BLANK = (
            "http://" + config.IP + ":" + str(config.PORT) + "/blank.html"
        )

        # Create Viewer
        self.CreateViewer()

        self.plugin_path = os.path.dirname(os.path.realpath(__file__))
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.parent = parent

        # Orientation from image
        self.yaw = math.pi
        self.bearing = None

        self.layer = layer
        self.featuresId = featuresId

        self.actualPointDx = None
        self.actualPointSx = None
        self.actualPointOrientation = None

        self.selected_features = qgsutils.getToFeature(self.layer, self.featuresId)

        # Get image path
        self.current_image = self.GetImage()

        # Check if image exist
        if os.path.exists(self.current_image) is False:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"There is no associated image."
            )
            self.resetQgsRubberBand()
            self.ChangeUrlViewer(self.DEFAULT_EMPTY)
            return

        # Copy file to local server
        self.CopyFile(self.current_image)

        # Set RubberBand
        self.resetQgsRubberBand()
        self.setOrientation()
        self.setPosition()

    """Update data from Marzipano Viewer"""
    def onNewData(self, data):
        try:
            newYaw = float(data[0])
            self.UpdateOrientation(yaw=newYaw)
        except:
            None

    def CreateViewer(self):
        """Create Viewer"""
        qgsutils.showUserAndLogMessage(u"Information: ", u"Create viewer", onlyLog=True)

        self.cef_widget = QWebView()
        self.cef_widget.setContextMenuPolicy(Qt.NoContextMenu)

        self.cef_widget.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        pano_view_settings = self.cef_widget.settings()
        pano_view_settings.setAttribute(QWebSettings.WebGLEnabled, True)
        # pano_view_settings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        pano_view_settings.setAttribute(QWebSettings.Accelerated2dCanvasEnabled, True)
        pano_view_settings.setAttribute(QWebSettings.JavascriptEnabled, True)

        self.page = _ViewerPage()
        self.page.newData.connect(self.onNewData)
        self.cef_widget.setPage(self.page)

        self.cef_widget.load(QUrl(self.DEFAULT_URL))
        self.ViewerLayout.addWidget(self.cef_widget, 1, 0)

    # def SetInitialYaw(self):
    #     """Set Initial Viewer Yaw"""
    #     self.bearing = self.selected_features.attribute(config.column_yaw)
    #     # self.view.browser.GetMainFrame().ExecuteFunction("InitialYaw",
    #     #                                                  self.bearing)
    #     return

    def RemoveImage(self):
        """Remove Image"""
        try:
            os.remove(self.plugin_path + "/viewer/image.jpg")
        except OSError:
            pass

    def CopyFile(self, src):
        """Copy Image File in Local Server"""
        qgsutils.showUserAndLogMessage(u"Information: ", u"Copying image", onlyLog=True)

        src_dir = src
        dst_dir = self.plugin_path + "/viewer"

        # Copy image in local folder
        img = Image.open(src_dir)
        rgb_im = img.convert("RGB")
        dst_dir = dst_dir + "/image.jpg"

        try:
            os.remove(dst_dir)
        except OSError:
            pass

        rgb_im.save(dst_dir)

    def GetImage(self):
        """Get Selected Image"""
        try:
            path = qgsutils.getAttributeFromFeature(
                self.selected_features, config.column_name
            )
            if not os.path.isabs(path):  # Relative Path to Project
                path_project = QgsProject.instance().readPath("./")
                path = os.path.normpath(os.path.join(path_project, path))
        except Exception:
            qgsutils.showUserAndLogMessage(u"Information: ", u"Column not found.")
            return

        qgsutils.showUserAndLogMessage(u"Information: ", str(path), onlyLog=True)
        return path

    def ChangeUrlViewer(self, new_url):
        """Change Url Viewer"""
        self.cef_widget.load(QUrl(new_url))

    def ReloadView(self, newId):
        """Reaload Image viewer"""
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        # this will activate the window
        self.activateWindow()
        self.selected_features = qgsutils.getToFeature(self.layer, newId)

        self.current_image = self.GetImage()

        # Check if image exist
        if os.path.exists(self.current_image) is False:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"There is no associated image."
            )
            self.ChangeUrlViewer(self.DEFAULT_EMPTY)
            self.resetQgsRubberBand()
            return

        # Set RubberBand
        self.resetQgsRubberBand()
        self.setOrientation()
        self.setPosition()

        # Copy file to local server
        self.CopyFile(self.current_image)

        self.ChangeUrlViewer(self.DEFAULT_URL)

    def GetBackNextImage(self):
        """Get to Back Image"""
        sender = QObject.sender(self)

        lys = self.canvas.layers()  # Check if mapa foto is loaded
        if len(lys) == 0:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"You need load the photo layer."
            )
            return

        for layer in lys:
            if layer.name() == config.layer_name:
                self.encontrado = True
                self.iface.setActiveLayer(layer)

                f = self.selected_features

                ac_lordem = f.attribute(config.column_order)

                if sender.objectName() == "btn_back":
                    new_lordem = int(ac_lordem) - 1
                else:
                    new_lordem = int(ac_lordem) + 1

                # Filter mapa foto layer
                ids = [
                    feat.id()
                    for feat in layer.getFeatures(
                        QgsFeatureRequest().setFilterExpression(
                            config.column_order + " ='" + str(new_lordem) + "'"
                        )
                    )
                ]

                if len(ids) == 0:
                    qgsutils.showUserAndLogMessage(
                        u"Information: ", u"There is no superiority that follows."
                    )
                    # Filter mapa foto layer
                    ids = [
                        feat.id()
                        for feat in layer.getFeatures(
                            QgsFeatureRequest().setFilterExpression(
                                config.column_order + " ='" + str(ac_lordem) + "'"
                            )
                        )
                    ]
                # Update selected feature
                self.ReloadView(ids[0])

        if self.encontrado is False:
            qgsutils.showUserAndLogMessage(
                u"Information: ",
                u"You need a layer with images and set the name in the config.py file.",
            )

        return

    def FullScreen(self, value):
        """FullScreen action button"""
        qgsutils.showUserAndLogMessage(u"Information: ", u"Fullscreen.", onlyLog=True)
        if value:
            self.showFullScreen()
        else:
            self.showNormal()

    def UpdateOrientation(self, yaw=None):
        """Update Orientation"""
        self.bearing = self.selected_features.attribute(config.column_yaw)
        try:
            self.actualPointOrientation.reset()
        except Exception:
            pass

        self.actualPointOrientation = QgsRubberBand(
            self.iface.mapCanvas(), QgsWkbTypes.LineGeometry
        )
        self.actualPointOrientation.setColor(Qt.blue)
        self.actualPointOrientation.setWidth(5)
        self.actualPointOrientation.addPoint(self.actualPointDx)

        # End Point
        CS = self.canvas.mapUnitsPerPixel() * 25
        A1x = self.actualPointDx.x() - CS * math.cos(math.pi / 2)
        A1y = self.actualPointDx.y() + CS * math.sin(math.pi / 2)

        self.actualPointOrientation.addPoint(QgsPointXY(float(A1x), float(A1y)))

        # Vision Angle
        if yaw is not None:
            angle = float(self.bearing + yaw) * math.pi / -180
        else:
            angle = float(self.bearing) * math.pi / -180


        tmpGeom = self.actualPointOrientation.asGeometry()
        rotatePoint = self.rotateTool.rotate(tmpGeom, self.actualPointDx, angle)
        
        self.actualPointOrientation.setToGeometry(rotatePoint, self.dumLayer)
        # Set Azimut value
        tmpGeom = rotatePoint.asPolyline()
        azim = tmpGeom[0].azimuth(tmpGeom[1])
        if  azim < 0:
            azim += 360
        self.yawLbl.setText("Yaw : " + str(round(yaw,2)) + " Azimut : " + str(round(azim,2)))


    def setOrientation(self, yaw=None):
        """Set Orientation in the firt time"""
        self.bearing = self.selected_features.attribute(config.column_yaw)

        originalPoint = self.selected_features.geometry().asPoint()
        self.actualPointDx = qgsutils.convertProjection(
            originalPoint.x(),
            originalPoint.y(),
            self.layer.crs().authid(),
            self.canvas.mapSettings().destinationCrs().authid(),
        )

        self.actualPointOrientation = QgsRubberBand(
            self.iface.mapCanvas(), QgsWkbTypes.LineGeometry
        )
        self.actualPointOrientation.setColor(Qt.blue)
        self.actualPointOrientation.setWidth(5)

        self.actualPointOrientation.addPoint(self.actualPointDx)

        # End Point
        CS = self.canvas.mapUnitsPerPixel() * 25
        A1x = self.actualPointDx.x() - CS * math.cos(math.pi / 2)
        A1y = self.actualPointDx.y() + CS * math.sin(math.pi / 2)

        self.actualPointOrientation.addPoint(QgsPointXY(float(A1x), float(A1y)))
        # Vision Angle
        if yaw is not None:
            angle = float(self.bearing + yaw) * math.pi / -180
        else:
            angle = float(self.bearing) * math.pi / -180

        tmpGeom = self.actualPointOrientation.asGeometry()

        self.rotateTool = transformGeometry()
        epsg = self.canvas.mapSettings().destinationCrs().authid()
        self.dumLayer = QgsVectorLayer(
            "Point?crs=" + epsg, "temporary_points", "memory"
        )
        self.actualPointOrientation.setToGeometry(
            self.rotateTool.rotate(tmpGeom, self.actualPointDx, angle), self.dumLayer
        )

    def setPosition(self):
        """Set RubberBand Position"""
        # Transform Point
        originalPoint = self.selected_features.geometry().asPoint()
        self.actualPointDx = qgsutils.convertProjection(
            originalPoint.x(),
            originalPoint.y(),
            "EPSG:4326",
            self.canvas.mapSettings().destinationCrs().authid(),
        )

        self.positionDx = QgsRubberBand(
            self.iface.mapCanvas(), QgsWkbTypes.PointGeometry
        )
        self.positionDx.setWidth(6)
        self.positionDx.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.positionDx.setIconSize(6)
        self.positionDx.setColor(Qt.black)
        self.positionSx = QgsRubberBand(
            self.iface.mapCanvas(), QgsWkbTypes.PointGeometry
        )
        self.positionSx.setWidth(5)
        self.positionSx.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.positionSx.setIconSize(4)
        self.positionSx.setColor(Qt.blue)
        self.positionInt = QgsRubberBand(
            self.iface.mapCanvas(), QgsWkbTypes.PointGeometry
        )
        self.positionInt.setWidth(5)
        self.positionInt.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.positionInt.setIconSize(3)
        self.positionInt.setColor(Qt.white)

        self.positionDx.addPoint(self.actualPointDx)
        self.positionSx.addPoint(self.actualPointDx)
        self.positionInt.addPoint(self.actualPointDx)

    def closeEvent(self, _):
        """Close dialog"""
        self.resetQgsRubberBand()
        self.canvas.refresh()
        self.iface.actionPan().trigger()
        self.parent.orbitalViewer = None
        self.RemoveImage()

    def resetQgsRubberBand(self):
        """Remove RubbeBand"""
        try:
            self.yawLbl.setText("")
            self.positionSx.reset()
            self.positionInt.reset()
            self.positionDx.reset()
            self.actualPointOrientation.reset()
        except Exception:
            None
