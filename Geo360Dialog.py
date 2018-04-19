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
# Import the PyQt and QGIS libraries
import math
import re
import shutil

from PyQt4.QtCore import Qt, QSettings, QPropertyAnimation, QSize, QObject
from PyQt4.QtGui import QWidget, QDialog, QVBoxLayout, qApp
from geom.transformgeom import transformGeometry
from gui.generated.ui_orbitalDialog import Ui_orbitalDialog
from qgis.core import QgsProject, QGis, QgsFeatureRequest, QgsPoint, QgsVectorLayer
from qgis.gui import QgsRubberBand, QgsMessageBar
import qgis.utils
from server.local_server import *
from utils.qgsutils import qgsutils


try:
    from pydevd import *
except ImportError:
    None

try:
    from cefpython3 import cefpython
except ImportError:
    None

try:
    from PIL import Image
except ImportError:
    None
       


class CefWidget(QWidget):
    """ CefPython Viewer"""
    browser = None

    def __init__(self, parent=None):
        super(CefWidget, self).__init__(parent)
        self.show()

    def embed(self):
        windowInfo = cefpython.WindowInfo()
        windowInfo.SetAsChild(int(self.winIdFixed()))

        self.browser = cefpython.CreateBrowserSync(windowInfo,
                                                   browserSettings={},
                                                   navigateUrl=config.DEFAULT_URL)

        # Add Handler
        self.browser.SetClientHandler(ClientHandler())

    def winIdFixed(self):
        try:
            return int(self.winId())
        except:
            return

    def moveEvent(self, event):
        cefpython.WindowUtils.OnSize(int(self.winIdFixed()), 0, 0, 0)

    def resizeEvent(self, event):
        cefpython.WindowUtils.OnSize(int(self.winIdFixed()), 0, 0, 0)


class Geo360Dialog(QWidget, Ui_orbitalDialog):

    """Geo360 Dialog Class"""

    def __init__(self, iface, parent=None, featuresId=None, layer=None):

        QDialog.__init__(self)

        self.setupUi(self)
        self.s = QSettings()

        self.plugin_path = os.path.dirname(os.path.realpath(__file__))

        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.parent = parent

        # Orientation from image
        self.yaw = math.pi
        self.bearing = None

        self.layer = layer
        self.featuresId = featuresId

        # Restore Previous size
        self.RestoreSize()

        self.actualPointDx = None
        self.actualPointSx = None
        self.actualPointOrientation = None

        self.selected_features = qgsutils.getToFeature(
            self.layer, self.featuresId)

        # Get image path
        self.current_image = self.GetImage()
        qApp.processEvents()

        # Create Viewer
        self.CreateViewer()
        qApp.processEvents()

        # Check if image exist
        if os.path.exists(self.current_image) is False:
            qgsutils.showUserAndLogMessage(
                self, u"Information: ", u"There is no associated image.",
                QgsMessageBar.INFO)
            self.ChangeUrlViewer(config.DEFAULT_EMPTY)
            self.setPosition()
            return

        # Set RubberBand
        self.setOrientation()
        self.setPosition()
        qApp.processEvents()

        # Copy file to local server
        self.CopyFile(self.current_image)
        qApp.processEvents()

    def SetInitialYaw(self):
        ''' Set Initial Yaw '''
        self.bearing = self.selected_features.attribute(config.column_yaw)
        self.view.browser.GetMainFrame().ExecuteFunction("InitialYaw",
                                                         self.bearing)
        return

    def CreateViewer(self):
        ''' Create Viewer '''
        qgsutils.showUserAndLogMessage(
            self, u"Information: ", u"Create viewer", QgsMessageBar.INFO, onlyLog=True)

        self.view = CefWidget(self)
        self.m_vbox = QVBoxLayout()
        self.m_vbox.addWidget(self.view)
        qApp.processEvents()

        self.frame.setLayout(self.m_vbox)
        qApp.processEvents()
        self.view.embed()
        qApp.processEvents()

        return

    def CopyFile(self, src):
        ''' Copy Image File in Local Server '''
        qgsutils.showUserAndLogMessage(
            self, u"Information: ", u"Copiar imagem",
            QgsMessageBar.INFO,
            onlyLog=True)

        pattern = "^(?P<photo_id>\d+)[^\d].*jpg$"
        src_dir = src
        dst_dir = self.plugin_path + "\\viewer"

        # Delete images on first time
        for root, dirs, files in os.walk(dst_dir):
            for file in filter(lambda x: re.match(pattern, x), files):
                os.remove(os.path.join(root, file))

        # Copy image in local folder
        # Uncomment for large images if viewer is blank screen
        img = Image.open(src_dir)
        newwidth = 8000
        dst_dir = dst_dir + "\\image.jpg"
        width, height = img.size

        if width > newwidth:
            wpercent = (newwidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((newwidth, hsize), Image.ANTIALIAS)
            img.save(dst_dir, optimize=True, quality=95)

        # Comment for large images if viewer is blank screen
        else:
            shutil.copy(src_dir, dst_dir)

        qApp.processEvents()
        return

    def RestoreSize(self):
        ''' Restore Dialog Size '''
        dw = self.s.value("EquirectangularViewer/width")
        dh = self.s.value("EquirectangularViewer/height")

        if dw is None:
            return
        size = self.size()

        anim = QPropertyAnimation(self, 'size', self)
        anim.setStartValue(size)
        anim.setEndValue(QSize(dw, dh))
        anim.setDuration(1)
        anim.start()
        qApp.processEvents()
        return

    def SaveSize(self):
        ''' Save Dialog Size '''
        dw = self.width()
        dh = self.height()
        self.s.setValue("EquirectangularViewer/width", dw)
        self.s.setValue("EquirectangularViewer/height", dh)
        qApp.processEvents()
        return

    def GetImage(self):
        ''' Get Selected Image '''
        try:
            path = qgsutils.getAttributeFromFeature(
                self.selected_features, config.column_name)
            if not os.path.isabs(path):  # Relative Path to Project
                path_project = QgsProject.instance().readPath("./")
                path = os.path.normpath(os.path.join(path_project, path))
        except:
            qgsutils.showUserAndLogMessage(
                self, u"Information: ", u"Column not found.",
                QgsMessageBar.INFO)
            return

        qgsutils.showUserAndLogMessage(self, u"Information: ", str(
            path), QgsMessageBar.INFO, onlyLog=True)
        return path

    def ChangeUrlViewer(self, new_url):
        ''' Change Url Viewer '''
        self.view.browser.GetMainFrame().ExecuteJavascript(
            "window.location='%s'" % new_url)
        qApp.processEvents()
        return

    def ReloadView(self, newId):
        ''' Reaload Image viewer '''
        self.setWindowState(self.windowState() & ~
                            Qt.WindowMinimized | Qt.WindowActive)
        # this will activate the window
        self.activateWindow()
        qApp.processEvents()

        self.selected_features = qgsutils.getToFeature(
            self.layer, newId)

        self.current_image = self.GetImage()

        # Check if image exist
        if os.path.exists(self.current_image) is False:
            qgsutils.showUserAndLogMessage(
                self, u"Information: ", u"It is not in the associated image.",
                QgsMessageBar.INFO)
            self.ChangeUrlViewer(config.DEFAULT_EMPTY)
            self.setPosition()
            return

        # Set RubberBand
        self.setOrientation()
        self.setPosition()

        # Copy file to local server
        self.CopyFile(self.current_image)

        self.ChangeUrlViewer(config.DEFAULT_URL)
        qApp.processEvents()

        return

    def ResizeDialog(self):
        ''' Expanded/Decreased Dialog '''
        sender = QObject.sender(self)

        w = self.width()
        h = self.height()

        size = self.size()
        anim = QPropertyAnimation(self, 'size', self)
        anim.setStartValue(size)

        if sender.objectName() == "btn_ZoomOut":
            anim.setEndValue(QSize(w - 50, h - 50))
        else:
            anim.setEndValue(QSize(w + 50, h + 50))

        anim.setDuration(300)
        anim.start()
        qApp.processEvents()

        return

    def GetBackNextImage(self):
        ''' Get to Back Image '''
        qgsutils.removeAllHighlightFeaturesFromCanvasScene(self.canvas)

        sender = QObject.sender(self)

        lys = self.canvas.layers()  # Check if mapa foto is loaded
        if len(lys) == 0:
            qgsutils.showUserAndLogMessage(
                self, u"Information: ", u"You need to upload the photo layer.",
                QgsMessageBar.INFO)
            return

        for layer in lys:
            if layer.name() == config.layer_name:
                self.encontrado = True
                self.iface.setActiveLayer(layer)
                qApp.processEvents()

                f = self.selected_features

                ac_lordem = f.attribute(config.column_order)

                if sender.objectName() == "btn_back":
                    new_lordem = int(ac_lordem) - 1
                else:
                    new_lordem = int(ac_lordem) + 1

                # Filter mapa foto layer
                ids = [feat.id() for feat in layer.getFeatures(
                    QgsFeatureRequest().setFilterExpression(config.column_order + " ='" + 
                                                            str(new_lordem) + 
                                                            "'"))]

                if len(ids) == 0:
                    qgsutils.showUserAndLogMessage(
                        self, u"Information: ", u"There is no superiority that follows.",
                        QgsMessageBar.INFO)
                    # Filter mapa foto layer
                    ids = [feat.id() for feat in layer.getFeatures(
                        QgsFeatureRequest().setFilterExpression(config.column_order + " ='" + 
                                                                str(ac_lordem) + 
                                                                "'"))]
                    # Update selected feature
                    self.ReloadView(ids[0])
                    return

                self.ReloadView(ids[0])
                qApp.processEvents()

        if self.encontrado is False:
            qgsutils.showUserAndLogMessage(
                self, u"Information: ", u"You need to upload the photo layer.",
                QgsMessageBar.INFO)

        return

    def FullScreen(self, bool):
        ''' FullScreen action button '''
        qgsutils.showUserAndLogMessage(
            self, u"Information: ", u"Fullscreen.", QgsMessageBar.INFO,
            onlyLog=True)
        if(bool):
            self.showFullScreen()
        else:
            self.showNormal()
        qApp.processEvents()
        return

    @staticmethod
    def ActualOrientation(yaw):
        ''' Get Actual yaw '''
        geo360Plugin = qgis.utils.plugins["EquirectangularViewer"]
        if geo360Plugin is not None:
            geo360Dialog = qgis.utils.plugins["EquirectangularViewer"].dlg
            if geo360Dialog is not None:
                geo360Dialog.UpdateOrientation(yaw=float(yaw))
        return

    def UpdateOrientation(self, yaw=None):
        ''' Update Orientation '''
        self.bearing = self.selected_features.attribute(config.column_yaw)
        try:
            self.actualPointOrientation.reset()
        except:
            pass

        self.actualPointOrientation = QgsRubberBand(
            self.iface.mapCanvas(), QGis.Line)
        self.actualPointOrientation.setColor(Qt.blue)
        self.actualPointOrientation.setWidth(5)
        self.actualPointOrientation.addPoint(self.actualPointDx)

        # End Point
        CS = self.canvas.mapUnitsPerPixel() * 25
        A1x = self.actualPointDx.x() - CS * math.cos(math.pi / 2)
        A1y = self.actualPointDx.y() + CS * math.sin(math.pi / 2)

        self.actualPointOrientation.addPoint(QgsPoint(A1x, A1y))

        # Vision Angle
        if yaw is not None:
            angle = float(self.bearing + yaw) * math.pi / -180
        else:
            angle = float(self.bearing) * math.pi / -180

        tmpGeom = self.actualPointOrientation.asGeometry()

        self.actualPointOrientation.setToGeometry(self.rotateTool.rotate(
            tmpGeom, self.actualPointDx, angle), self.dumLayer)
        qApp.processEvents()

    def setOrientation(self, yaw=None):
        ''' Set Orientation in the firt time '''
        self.bearing = self.selected_features.attribute(config.column_yaw)

        self.actualPointDx = self.selected_features.geometry().asPoint()

        try:
            self.actualPointOrientation.reset()
        except:
            pass

        qApp.processEvents()

        self.actualPointOrientation = QgsRubberBand(
            self.iface.mapCanvas(), QGis.Line)
        self.actualPointOrientation.setColor(Qt.blue)
        self.actualPointOrientation.setWidth(5)

        self.actualPointOrientation.addPoint(self.actualPointDx)

        # End Point
        CS = self.canvas.mapUnitsPerPixel() * 25
        A1x = self.actualPointDx.x() - CS * math.cos(math.pi / 2)
        A1y = self.actualPointDx.y() + CS * math.sin(math.pi / 2)

        self.actualPointOrientation.addPoint(QgsPoint(A1x, A1y))
        # Vision Angle
        if yaw is not None:
            angle = float(self.bearing + yaw) * math.pi / -180
        else:
            angle = float(self.bearing) * math.pi / -180

        tmpGeom = self.actualPointOrientation.asGeometry()

        self.rotateTool = transformGeometry()
        epsg = self.canvas.mapRenderer().destinationCrs().authid()
        self.dumLayer = QgsVectorLayer(
            "Point?crs=" + epsg, "temporary_points", "memory")
        self.actualPointOrientation.setToGeometry(self.rotateTool.rotate(
            tmpGeom, self.actualPointDx, angle), self.dumLayer)
        qApp.processEvents()

    def setPosition(self):
        ''' Set RubberBand Position '''
        self.actualPointDx = self.selected_features.geometry().asPoint()

        try:
            self.positionDx.reset()
            self.positionSx.reset()
            self.positionInt.reset()
        except:
            pass

        qApp.processEvents()

        self.positionDx = QgsRubberBand(self.iface.mapCanvas(), QGis.Point)
        self.positionDx.setWidth(6)
        self.positionDx.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.positionDx.setIconSize(6)
        self.positionDx.setColor(Qt.black)
        self.positionSx = QgsRubberBand(self.iface.mapCanvas(), QGis.Point)
        self.positionSx.setWidth(5)
        self.positionSx.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.positionSx.setIconSize(4)
        self.positionSx.setColor(Qt.blue)
        self.positionInt = QgsRubberBand(self.iface.mapCanvas(), QGis.Point)
        self.positionInt.setWidth(5)
        self.positionInt.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.positionInt.setIconSize(3)
        self.positionInt.setColor(Qt.white)

        qApp.processEvents()

        self.positionDx.addPoint(self.actualPointDx)
        self.positionSx.addPoint(self.actualPointDx)
        self.positionInt.addPoint(self.actualPointDx)

        qApp.processEvents()

    def closeEvent(self, evt):
        ''' Close dialog '''
        qgsutils.showUserAndLogMessage(
            self, u"Information: ", u"Close dialog", QgsMessageBar.INFO,
            onlyLog=True)
        qgsutils.removeAllHighlightFeaturesFromCanvasScene(self.canvas)
        qApp.processEvents()

        self.canvas.refresh()
        self.iface.actionPan().trigger()
        self.SaveSize()
        qApp.processEvents()
        return


class ClientHandler():
    ''' CefPython Event '''
    # hilarious method but work

    def OnConsoleMessage(self, browser, message, source, line):
        try:
            Geo360Dialog.ActualOrientation(yaw=message)
        except:
            None
        return
