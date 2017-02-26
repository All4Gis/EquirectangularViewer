import os
import sys
import subprocess

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QSettings, QSize
from PyQt4.QtGui import QApplication, QWidget, QPushButton, QScrollArea, QGroupBox, QDesktopWidget, QFileDialog


try:
    from sys import settrace
    from pydevd import *
except:
    None

class Gui(object):
    
    @staticmethod
    def adjustUISize(dialog, styleSheet=None):   
        Gui.setGlobalFont(dialog, dialog.findChildren(QWidget))        
        Gui.updateIconSize(QSettings().value("/IconSize", 24), dialog.findChildren(QPushButton))
        dialog.setStyleSheet(styleSheet)
        Gui.adjustUIObjectsSize(dialog)
        Gui.centerDialog(dialog)
        return
    
    
    @staticmethod
    def adjustUIObjectsSize(dialog):    
        Gui.adjustScrollArea(dialog)        
        Gui.adjustGroupBox(dialog)
        Gui.adjustMinMaxSize(dialog)
    
       
    @staticmethod  
    def adjustScrollArea(dialog):      
        scrollArea = dialog.findChildren(QScrollArea)
        for area in scrollArea:
            if area.styleSheet is None:
                w=area.widget() 
                w.adjustSize()
                area.adjustSize()
    
            
    @staticmethod  
    def adjustGroupBox(dialog):
        GroupBox  = dialog.findChildren(QGroupBox)
        for group in GroupBox:
            group.adjustSize()
    
    
    @staticmethod
    def adjustMinMaxSize(dialog):      
        dialog.adjustSize()
        dialog.setMinimumSize(dialog.size())
        dialog.setMaximumSize(dialog.size()) 
        
           
    @staticmethod  
    def setGlobalFont(dialog, widgets=None): 
        font = dialog.font()
        font.setPointSize(QSettings().value("Qgis/stylesheet/fontPointSize", 8))
        font.setFamily(QSettings().value("Qgis/stylesheet/fontFamily", "Arial"))
        app = QApplication.instance()
        app.setFont(font)
        return
    
    
    @staticmethod  
    def updateIconSize(iconSize, widgets): 
        try:
            for widget in widgets:
                if type(widget)==QtGui.QPushButton :
                    widget.setIconSize(QSize(int(iconSize), int(iconSize)))
                    if widget.text==None:
                        widget.adjustSize()
                        widget.setMinimumSize(widget.size())
                        widget.setMaximumSize(widget.size())
        except:
            None;
        return
 
    
    @staticmethod
    def centerDialog(dialog):
        size=dialog.size()
        desktopSize=QDesktopWidget().screenGeometry()
        top=(desktopSize.height()/2)-(size.height()/2)
        left=(desktopSize.width()/2)-(size.width()/2)
        dialog.move(left, top)
    
    
    @staticmethod
    def loadLatin1Encoding():
        reload(sys)
        sys.setdefaultencoding("latin-1")
        a = u'\xa1'
        print str(a)
    
 

     
        