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
import sys
from qgis.core import (QgsPointXY,
                       QgsProject,
                       QgsFeatureRequest,
                       QgsVectorLayer,
                       QgsWkbTypes)
from qgis.gui import QgsRubberBand
import qgis.utils
import shutil
import platform
import time

from PyQt5.QtCore import QObject, QSettings, Qt, QPropertyAnimation, QSize
from PyQt5.QtWidgets import QDialog, QWidget
from PyQt5.QtGui import QWindow
import EquirectangularViewer.config as config
from EquirectangularViewer.geom.transformgeom import transformGeometry
from EquirectangularViewer.gui.ui_orbitalDialog import Ui_orbitalDialog
from EquirectangularViewer.server.local_server import *
from EquirectangularViewer.utils.qgsutils import qgsutils

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

try:
    from PIL import Image
except ImportError:
    None

# Fix for PyCharm hints warnings when using static methods
WindowUtils = cef.WindowUtils()

# Platforms
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")


class CefWidget(QWidget):
    """ CefPython Viewer"""
    browser = None

    def __init__(self, parent=None):
        super(CefWidget, self).__init__(parent)
        self.parent = parent
        self.browser = None
        self.hidden_window = None  # Required for PyQt5 on Linux
        self.show()

    def focusInEvent(self, event):
        # This event seems to never get called on Linux, as CEF is
        # stealing all focus.
        if cef.GetAppSetting("debug"):
            print("[qt.py] CefWidget.focusInEvent")
        if self.browser:
            if WINDOWS:
                WindowUtils.OnSetFocus(self.getHandle(), 0, 0, 0)
            self.browser.SetFocus(True)

    def focusOutEvent(self, event):
        # This event seems to never get called on Linux, as CEF is
        # stealing all focus.
        if cef.GetAppSetting("debug"):
            print("[qt.py] CefWidget.focusOutEvent")
        if self.browser:
            self.browser.SetFocus(False)

    def embedBrowser(self):
        if LINUX:
            self.hidden_window = QWindow()
        windowInfo = cef.WindowInfo()
        rect = [0, 0, self.width(), self.height()]
        windowInfo.SetAsChild(self.getHandle(), rect)

        self.browser = cef.CreateBrowserSync(windowInfo,
                                                   browserSettings={'web_security_disabled': True},
                                                   url=config.DEFAULT_URL)

        # Add Handler
        self.browser.SetClientHandler(ClientHandler())

    def getHandle(self):
        if self.hidden_window:
            # PyQt5 on Linux
            return int(self.hidden_window.winId())
        try:
            # PyQt4 and PyQt5
            return int(self.winId())
        except Exception:
            # PySide:
            # | QWidget.winId() returns <PyCObject object at 0x02FD8788>
            # | Converting it to int using ctypes.
            ctypes.pythonapi.PyCapsule_GetPointer.restype = (ctypes.c_void_p)
            ctypes.pythonapi.PyCapsule_GetPointer.argtypes = ([
                ctypes.py_object
            ])
            return ctypes.pythonapi.PyCapsule_GetPointer(self.winId(), None)

    def moveEvent(self, _):
        self.x = 0
        self.y = 0
        if self.browser:
            if WINDOWS:
                WindowUtils.OnSize(self.getHandle(), 0, 0, 0)
            elif LINUX:
                self.browser.SetBounds(self.x, self.y, self.width(),
                                       self.height())
            self.browser.NotifyMoveOrResizeStarted()

    def resizeEvent(self, event):
        size = event.size()
        if self.browser:
            if WINDOWS:
                WindowUtils.OnSize(self.getHandle(), 0, 0, 0)
            elif LINUX:
                self.browser.SetBounds(self.x, self.y, size.width(),
                                       size.height())
            self.browser.NotifyMoveOrResizeStarted()


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

        self.actualPointDx = None
        self.actualPointSx = None
        self.actualPointOrientation = None

        self.selected_features = qgsutils.getToFeature(
            self.layer, self.featuresId)

        # Get image path
        self.current_image = self.GetImage()

        self.RestoreSize()
        # Check if image exist
        if os.path.exists(self.current_image) is False:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"There is no associated image.")
            self.resetQgsRubberBand()
            time.sleep(1)
            self.ChangeUrlViewer(config.DEFAULT_EMPTY)
            return

        # Copy file to local server
        self.CopyFile(self.current_image)

        # Set RubberBand
        self.resetQgsRubberBand()
        self.setOrientation()
        self.setPosition()
        
        # Create Viewer
        self.CreateViewer()

    def SetInitialYaw(self):
        ''' Set Initial Yaw '''
        self.bearing = self.selected_features.attribute(config.column_yaw)
        self.cef_widget.browser.GetMainFrame().ExecuteFunction("InitialYaw",
                                                         self.bearing)

    def CreateViewer(self):
        ''' Create Viewer '''
        qgsutils.showUserAndLogMessage(
            u"Information: ", u"Create viewer", onlyLog=True)

        self.cef_widget = CefWidget(self)
        self.ViewerLayout.addWidget(self.cef_widget, 1, 0)
        
        if WINDOWS:
            # On Windows with PyQt5 main window must be shown first
            # before CEF browser is embedded, otherwise window is
            # not resized and application hangs during resize.
            self.show()
            
        self.cef_widget.embedBrowser()
        
        if LINUX:
            # On Linux with PyQt5 the QX11EmbedContainer widget is
            # no more available. An equivalent in Qt5 is to create
            # a hidden window, embed CEF browser in it and then
            # create a container for that hidden window and replace
            # cef widget in the layout with the container.
            # noinspection PyUnresolvedReferences, PyArgumentList
            self.container = QWidget.createWindowContainer(
                    self.cef_widget.hidden_window, parent=self)
            self.ViewerLayout.addWidget(self.container, 1, 0)

    def RemoveImage(self):
        ''' Remove Image '''
        try:
            os.remove(self.plugin_path + "\\viewer\\image.jpg")
        except OSError:
            pass

    def CopyFile(self, src):
        ''' Copy Image File in Local Server '''
        qgsutils.showUserAndLogMessage(
            u"Information: ", u"Copiar imagem",
            onlyLog=True)

        src_dir = src
        dst_dir = self.plugin_path + "\\viewer"

        # Copy image in local folder
        # Uncomment for large images if viewer is blank screen
        img = Image.open(src_dir)
        newwidth = 8000
        dst_dir = dst_dir + "\\image.jpg"

        try:
            os.remove(dst_dir)
        except OSError:
            pass

        width, _ = img.size

        if width > newwidth:
            wpercent = (newwidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((newwidth, hsize), Image.ANTIALIAS)
            img.save(dst_dir, optimize=True, quality=95)

        # Comment for large images if viewer is blank screen
        else:
            shutil.copy(src_dir, dst_dir)

    def RestoreSize(self):
        ''' Restore Dialog Size '''
        dw = self.s.value("EquirectangularViewer/width")
        dh = self.s.value("EquirectangularViewer/height")

        if dw is None:
            return
        size = self.size()

        anim = QPropertyAnimation(self, b'size', self)
        anim.setStartValue(size)
        anim.setEndValue(QSize(int(dw), int(dh)))
        anim.setDuration(1)
        anim.start()

    def SaveSize(self):
        ''' Save Dialog Size '''
        dw = self.width()
        dh = self.height()
        self.s.setValue("EquirectangularViewer/width", dw)
        self.s.setValue("EquirectangularViewer/height", dh)

    def GetImage(self):
        ''' Get Selected Image '''
        try:
            path = qgsutils.getAttributeFromFeature(
                self.selected_features, config.column_name)
            if not os.path.isabs(path):  # Relative Path to Project
                path_project = QgsProject.instance().readPath("./")
                path = os.path.normpath(os.path.join(path_project, path))
        except Exception:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"Column not found.")
            return

        qgsutils.showUserAndLogMessage(u"Information: ", str(
            path), onlyLog=True)
        return path

    def ChangeUrlViewer(self, new_url):
        ''' Change Url Viewer '''
        self.cef_widget.browser.GetMainFrame().ExecuteJavascript(
            "window.location='%s'" % new_url)

    def ReloadView(self, newId):
        ''' Reaload Image viewer '''
        self.setWindowState(self.windowState() & ~
                            Qt.WindowMinimized | Qt.WindowActive)
        # this will activate the window
        self.activateWindow()
        self.selected_features = qgsutils.getToFeature(
            self.layer, newId)

        self.current_image = self.GetImage()

        # Check if image exist
        if os.path.exists(self.current_image) is False:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"There is no associated image.")
            self.ChangeUrlViewer(config.DEFAULT_EMPTY)
            self.resetQgsRubberBand()
            return

        # Set RubberBand
        self.resetQgsRubberBand()
        self.setOrientation()
        self.setPosition()

        # Copy file to local server
        self.CopyFile(self.current_image)

        self.ChangeUrlViewer(config.DEFAULT_URL)

    def ResizeDialog(self):
        ''' Expanded/Decreased Dialog '''
        sender = QObject.sender(self)

        w = self.width()
        h = self.height()

        size = self.size()
        anim = QPropertyAnimation(self, b'size', self)
        anim.setStartValue(size)

        if sender.objectName() == "btn_ZoomOut":
            anim.setEndValue(QSize(w - 50, h - 50))
        else:
            anim.setEndValue(QSize(w + 50, h + 50))

        anim.setDuration(300)
        anim.start()

    def GetBackNextImage(self):
        ''' Get to Back Image '''
        sender = QObject.sender(self)

        lys = self.canvas.layers()  # Check if mapa foto is loaded
        if len(lys) == 0:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"You need to upload the photo layer.")
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
                ids = [feat.id() for feat in layer.getFeatures(
                    QgsFeatureRequest().setFilterExpression(config.column_order + " ='" + 
                                                            str(new_lordem) + 
                                                            "'"))]

                if len(ids) == 0:
                    qgsutils.showUserAndLogMessage(
                        u"Information: ", u"There is no superiority that follows.")
                    # Filter mapa foto layer
                    ids = [feat.id() for feat in layer.getFeatures(
                        QgsFeatureRequest().setFilterExpression(config.column_order + " ='" + 
                                                                str(ac_lordem) + 
                                                                "'"))]
                # Update selected feature
                self.ReloadView(ids[0])

        if self.encontrado is False:
            qgsutils.showUserAndLogMessage(
                u"Information: ", u"You need to upload the photo layer.")

        return

    def FullScreen(self, value):
        ''' FullScreen action button '''
        qgsutils.showUserAndLogMessage(
            u"Information: ", u"Fullscreen.",
            onlyLog=True)
        if(value):
            self.showFullScreen()
        else:
            self.showNormal()

    @staticmethod
    def ActualOrientation(yaw):
        ''' Get Actual yaw '''
        geo360Plugin = qgis.utils.plugins["EquirectangularViewer"]
        if geo360Plugin is not None:
            geo360Dialog = qgis.utils.plugins["EquirectangularViewer"].dlg
            if geo360Dialog is not None:
                geo360Dialog.UpdateOrientation(yaw=float(yaw))

    def UpdateOrientation(self, yaw=None):
        ''' Update Orientation '''
        self.bearing = self.selected_features.attribute(config.column_yaw)
        try:
            self.actualPointOrientation.reset()
        except Exception:
            pass

        self.actualPointOrientation = QgsRubberBand(
            self.iface.mapCanvas(), QgsWkbTypes.LineGeometry)
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

        self.actualPointOrientation.setToGeometry(self.rotateTool.rotate(
            tmpGeom, self.actualPointDx, angle), self.dumLayer)

    def setOrientation(self, yaw=None):
        ''' Set Orientation in the firt time '''
        self.bearing = self.selected_features.attribute(config.column_yaw)

        self.actualPointDx = self.selected_features.geometry().asPoint()

        self.actualPointOrientation = QgsRubberBand(
            self.iface.mapCanvas(), QgsWkbTypes.LineGeometry)
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
            "Point?crs=" + epsg, "temporary_points", "memory")
        self.actualPointOrientation.setToGeometry(self.rotateTool.rotate(
            tmpGeom, self.actualPointDx, angle), self.dumLayer)

    def setPosition(self):
        ''' Set RubberBand Position '''
        self.actualPointDx = self.selected_features.geometry().asPoint()

        self.positionDx = QgsRubberBand(self.iface.mapCanvas(), QgsWkbTypes.PointGeometry)
        self.positionDx.setWidth(6)
        self.positionDx.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.positionDx.setIconSize(6)
        self.positionDx.setColor(Qt.black)
        self.positionSx = QgsRubberBand(self.iface.mapCanvas(), QgsWkbTypes.PointGeometry)
        self.positionSx.setWidth(5)
        self.positionSx.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.positionSx.setIconSize(4)
        self.positionSx.setColor(Qt.blue)
        self.positionInt = QgsRubberBand(self.iface.mapCanvas(), QgsWkbTypes.PointGeometry)
        self.positionInt.setWidth(5)
        self.positionInt.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.positionInt.setIconSize(3)
        self.positionInt.setColor(Qt.white)

        self.positionDx.addPoint(self.actualPointDx)
        self.positionSx.addPoint(self.actualPointDx)
        self.positionInt.addPoint(self.actualPointDx)

    def closeEvent(self, _):
        ''' Close dialog '''
        self.resetQgsRubberBand()
        self.canvas.refresh()
        self.iface.actionPan().trigger()
        self.SaveSize()
        self.parent.dlg = None
        self.RemoveImage()

    def resetQgsRubberBand(self):
        ''' Remove RubbeBand '''
        try:
            self.positionSx.reset()
            self.positionInt.reset()
            self.positionDx.reset()
            self.actualPointOrientation.reset()
        except Exception:
            None


class ClientHandler():
    ''' CefPython Event '''
    # hilarious method but work
    def OnConsoleMessage(self, browser, message, source, line, level):
        try:
            Geo360Dialog.ActualOrientation(yaw=message)
        except Exception:
            None
        return
