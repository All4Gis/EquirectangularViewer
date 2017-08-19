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
import os
import os.path 
from qgis.core import *
from qgis.core import QGis, QgsFeatureRequest, QgsPoint, QgsVectorLayer
from qgis.gui import *
from qgis.gui import QgsRubberBand, QgsMessageBar
from qgis.utils import *
import qgis.utils
import re
import shutil

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtCore import Qt, QTextCodec 
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtXml import *

import config
from geom.transformgeom import transformGeometry
from gui.generated.ui_orbitalDialog import Ui_orbitalDialog
from server.local_server import *
from utils.qgsutils import qgsutils


try:
    import sys
    from pydevd import *
except:
    None
 
try:
    import ctypes
    from cefpython3 import cefpython
except:
    None

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
      
"""Clase Visor CefPython"""           

class CefWidget(QWidget):
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
 

"""Geo360 Dialog Class"""
      
class Geo360Dialog(QWidget, Ui_orbitalDialog):
    
    """QGIS Plugin Implementation."""
    
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

        # defaults
        self.actualPointDx = None
        self.actualPointSx = None
        self.actualPointOrientation = None
 
        self.selected_features = qgsutils.getToFeature(self.canvas, self.layer, self.featuresId) 
 
        # Get image path  
        self.current_image = self.GetImage()
        QtGui.qApp.processEvents()
  
        # Create Viewer
        self.CreateViewer()
        QtGui.qApp.processEvents()
        
        # Check if image exist
        if os.path.exists(self.current_image) is False:
            qgsutils.showUserAndLogMessage(self, u"Information: ", u"There is no associated image.", QgsMessageBar.INFO)
            self.ChangeUrlViewer(config.DEFAULT_EMPTY)
            self.setPosition() 
            return 
         
        # Set RubberBand
        self.setOrientation()
        self.setPosition() 
        QtGui.qApp.processEvents()
        
        # Copy file to local server
        self.CopyFile(self.current_image) 
        QtGui.qApp.processEvents()

    # Set Initial Yaw
    def SetInitialYaw(self): 
        self.bearing = self.selected_features.attribute(config.column_yaw)
        self.view.browser.GetMainFrame().ExecuteFunction("InitialYaw", self.bearing)
        return  
    
    # Create Viewer
    def CreateViewer(self):
        
        qgsutils.showUserAndLogMessage(self, u"Information: ", u"Create viewer", QgsMessageBar.INFO, onlyLog=True)   

        self.view = CefWidget(self)
        self.m_vbox = QVBoxLayout()     
        self.m_vbox.addWidget(self.view)
        QtGui.qApp.processEvents()
  
        self.frame.setLayout(self.m_vbox) 
        QtGui.qApp.processEvents()
        self.view.embed()
        QtGui.qApp.processEvents()
 
        return
    
    # Copy Image File in Local Server
    def CopyFile(self, src):
        
        qgsutils.showUserAndLogMessage(self, u"Information: ", u"Copiar imagem", QgsMessageBar.INFO, onlyLog=True)   

        pattern = "^(?P<photo_id>\d+)[^\d].*jpg$"
        src_dir = src
        dst_dir = self.plugin_path + "\\viewer"
        
        # Delete images on first time
        for root, dirs, files in os.walk(dst_dir):
            for file in filter(lambda x: re.match(pattern, x), files):
                os.remove(os.path.join(root, file))

        # Copy image in local folder       
        dst_dir = dst_dir + "\\image.jpg"       
        shutil.copy(src_dir, dst_dir)
        QtGui.qApp.processEvents()   
        return 
    
    # Restore Dialog Size
    def RestoreSize(self):
        dw = self.s.value("EquirectangularViewer/width")
        dh = self.s.value("EquirectangularViewer/height")
        
        if  dw == None:return      
        size = self.size()
 
        anim = QtCore.QPropertyAnimation(self, 'size', self)
        anim.setStartValue(size)
        anim.setEndValue(QtCore.QSize(dw, dh))
        anim.setDuration(1)
        anim.start()   
        QtGui.qApp.processEvents()     
        return
    
    # Save Dialog Size
    def SaveSize(self):
        dw = self.width()
        dh = self.height() 
        self.s.setValue("EquirectangularViewer/width", dw)
        self.s.setValue("EquirectangularViewer/height", dh)
        QtGui.qApp.processEvents()
        return
 
            
    # Get Selected Image
    def GetImage(self):
        try:
            path = qgsutils.getAttributeFromFeature(self.selected_features, config.column_name)  
        except:
            qgsutils.showUserAndLogMessage(self, u"Information: ", u"Column not found.", QgsMessageBar.INFO)
            return
             
        qgsutils.showUserAndLogMessage(self, u"Information: ", str(path), QgsMessageBar.INFO, onlyLog=True)                        
        return path
    
    # Change Url Viewer
    def ChangeUrlViewer(self, new_url):
        self.view.browser.GetMainFrame().ExecuteJavascript("window.location='%s'" % new_url)
        QtGui.qApp.processEvents()
        return
      
    # Reaload Image viewer
    def ReloadView(self, newId):
        
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        # this will activate the window
        self.activateWindow()
        QtGui.qApp.processEvents()
        
        self.selected_features = qgsutils.getToFeature(self.canvas, self.layer, newId) 
 
        self.current_image = self.GetImage()
        
        # Check if image exist    
        if os.path.exists(self.current_image) is False:
            qgsutils.showUserAndLogMessage(self, u"Information: ", u"It is not in the associated image.", QgsMessageBar.INFO)
            self.ChangeUrlViewer(config.DEFAULT_EMPTY)
            self.setPosition() 
            return  
                 
        # Set RubberBand
        self.setOrientation()
        self.setPosition() 
        
        # Copy file to local server
        self.CopyFile(self.current_image) 
 
        self.ChangeUrlViewer(config.DEFAULT_URL)
        QtGui.qApp.processEvents()
 
        return
    
    # Expanded/Decreased Dialog
    def ResizeDialog(self): 

        sender = QObject.sender(self)      
        
        w = self.width()
        h = self.height()
        
        size = self.size() 
        anim = QtCore.QPropertyAnimation(self, 'size', self)
        anim.setStartValue(size)
        
        if sender.objectName() == "btn_ZoomOut":  
            anim.setEndValue(QtCore.QSize(w - 50, h - 50))
        else:
            anim.setEndValue(QtCore.QSize(w + 50, h + 50))
        
        anim.setDuration(300)
        anim.start()
        QtGui.qApp.processEvents()
        
        return
 
    # Get to Back Image
    def GetBackNextImage(self): 
              
        qgsutils.removeAllHighlightFeaturesFromCanvasScene(self.canvas)
    
        sender = QObject.sender(self)
        
        lys = self.canvas.layers()  # Check if mapa foto is loaded
        if len(lys) == 0:
            qgsutils.showUserAndLogMessage(self, u"Information: ", u"You need to upload the photo layer.", QgsMessageBar.INFO)  
            return
  
        for layer in lys:
            if layer.name() == config.layer_name:
                self.encontrado = True
                self.iface.setActiveLayer(layer)
                QtGui.qApp.processEvents()
                
                f = self.selected_features
  
                ac_lordem = f.attribute(config.column_order)
 
                if sender.objectName() == "btn_back":  
                    new_lordem = int(ac_lordem) - 1
                else:
                    new_lordem = int(ac_lordem) + 1
                    
                # Filter mapa foto layer                    
                ids = [feat.id() for feat in layer.getFeatures(QgsFeatureRequest().setFilterExpression("order ='" + str(new_lordem) + "'"))]      
                
                if len(ids) == 0:
                    qgsutils.showUserAndLogMessage(self, u"Information: ", u"There is no superiority that follows.", QgsMessageBar.INFO) 
                    # Filter mapa foto layer                    
                    ids = [feat.id() for feat in layer.getFeatures(QgsFeatureRequest().setFilterExpression("order ='" + str(ac_lordem) + "'"))]      
                    # Update selected feature
                    self.ReloadView(ids[0])
                    return
    
                self.ReloadView(ids[0])
                QtGui.qApp.processEvents()
 
 
        if self.encontrado == False:
            qgsutils.showUserAndLogMessage(self, u"Information: ", u"You need to upload the photo layer.", QgsMessageBar.INFO)   
 
        return
    
    
    # FullScreen action button
    def FullScreen(self, bool):
        qgsutils.showUserAndLogMessage(self, u"Information: ", u"Fullscreen.", QgsMessageBar.INFO, onlyLog=True)   
        if(bool):self.showFullScreen()
        else:self.showNormal()
        QtGui.qApp.processEvents()
        return 
    
 
    @staticmethod    
    def ActualOrientation(yaw):                
        geo360Plugin = qgis.utils.plugins["EquirectangularViewer"]
        if geo360Plugin is not None:            
            geo360Dialog = qgis.utils.plugins["EquirectangularViewer"].dlg
            if geo360Dialog is not None:
                geo360Dialog.UpdateOrientation(yaw=float(yaw))
        return
 
    # Update Orientation
    def UpdateOrientation(self, yaw=None):
        self.bearing = self.selected_features.attribute(config.column_yaw)
        try:
            self.actualPointOrientation.reset()
        except:
            pass
 
        self.actualPointOrientation = QgsRubberBand(self.iface.mapCanvas(), QGis.Line)
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

        self.actualPointOrientation.setToGeometry(self.rotateTool.rotate(tmpGeom, self.actualPointDx, angle), self.dumLayer)
        QtGui.qApp.processEvents()
        
    # Set Orientation in the firt time
    def setOrientation(self, yaw=None):
        
        self.bearing = self.selected_features.attribute(config.column_yaw)
        
        self.actualPointDx = self.selected_features.geometry().asPoint()
        
        try:
            self.actualPointOrientation.reset()
        except:
            pass
        
        QtGui.qApp.processEvents()

        self.actualPointOrientation = QgsRubberBand(self.iface.mapCanvas(), QGis.Line)
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
        self.dumLayer = QgsVectorLayer("Point?crs=EPSG:4326", "temporary_points", "memory")
        self.actualPointOrientation.setToGeometry(self.rotateTool.rotate(tmpGeom, self.actualPointDx, angle), self.dumLayer)
        QtGui.qApp.processEvents()
        
         
    # Set RubberBand Position  
    def setPosition(self):

        self.actualPointDx = self.selected_features.geometry().asPoint()
        
        try:
            self.positionDx.reset()
            self.positionSx.reset()
            self.positionInt.reset()
        except:
            pass
        
        QtGui.qApp.processEvents()

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
 
        QtGui.qApp.processEvents()
 
        self.positionDx.addPoint(self.actualPointDx)
        self.positionSx.addPoint(self.actualPointDx)
        self.positionInt.addPoint(self.actualPointDx)
        
        QtGui.qApp.processEvents()
          

    # Close dialog
    def closeEvent(self, evt):
        qgsutils.showUserAndLogMessage(self, u"Information: ", u"Close dialog", QgsMessageBar.INFO, onlyLog=True)     
        qgsutils.removeAllHighlightFeaturesFromCanvasScene(self.canvas)
        QtGui.qApp.processEvents()
        
        self.canvas.refresh()        
        self.iface.actionPan().trigger()
        self.SaveSize()
        #shutdown()
        QtGui.qApp.processEvents()     
        return     

# CefPython Event       
class ClientHandler():
    # hilarious method but work
    def OnConsoleMessage(self, browser, message, source, line):
        source = config.DEFAULT_URL
        Geo360Dialog.ActualOrientation(yaw=message)
        return
