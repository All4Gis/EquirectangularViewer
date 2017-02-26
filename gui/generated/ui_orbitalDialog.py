# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.resources\ui_orbitalDialog.ui'
#
# Created: Wed Feb 22 19:57:15 2017
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_orbitalDialog(object):
    def setupUi(self, orbitalDialog):
        orbitalDialog.setObjectName(_fromUtf8("orbitalDialog"))
        orbitalDialog.resize(446, 330)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/EquirectangularViewer/images/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        orbitalDialog.setWindowIcon(icon)
        self.verticalLayout_3 = QtGui.QVBoxLayout(orbitalDialog)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.ViewerLayout = QtGui.QVBoxLayout()
        self.ViewerLayout.setObjectName(_fromUtf8("ViewerLayout"))
        self.frame = QtGui.QFrame(orbitalDialog)
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Plain)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.ViewerLayout.addWidget(self.frame)
        self.verticalLayout.addLayout(self.ViewerLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btn_ZoomIn = QtGui.QPushButton(orbitalDialog)
        self.btn_ZoomIn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_ZoomIn.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/EquirectangularViewer/images/Zoom_in.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_ZoomIn.setIcon(icon1)
        self.btn_ZoomIn.setObjectName(_fromUtf8("btn_ZoomIn"))
        self.horizontalLayout.addWidget(self.btn_ZoomIn)
        self.btn_ZoomOut = QtGui.QPushButton(orbitalDialog)
        self.btn_ZoomOut.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_ZoomOut.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/EquirectangularViewer/images/Zoom_out.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_ZoomOut.setIcon(icon2)
        self.btn_ZoomOut.setObjectName(_fromUtf8("btn_ZoomOut"))
        self.horizontalLayout.addWidget(self.btn_ZoomOut)
        spacerItem = QtGui.QSpacerItem(5, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_back = QtGui.QPushButton(orbitalDialog)
        self.btn_back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_back.setText(_fromUtf8(""))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/EquirectangularViewer/images/Previous_Arrow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_back.setIcon(icon3)
        self.btn_back.setObjectName(_fromUtf8("btn_back"))
        self.horizontalLayout.addWidget(self.btn_back)
        self.btn_next = QtGui.QPushButton(orbitalDialog)
        self.btn_next.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_next.setText(_fromUtf8(""))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/EquirectangularViewer/images/Next_Arrow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_next.setIcon(icon4)
        self.btn_next.setObjectName(_fromUtf8("btn_next"))
        self.horizontalLayout.addWidget(self.btn_next)
        spacerItem1 = QtGui.QSpacerItem(5, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.btn_fullscreen = QtGui.QPushButton(orbitalDialog)
        self.btn_fullscreen.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_fullscreen.setText(_fromUtf8(""))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/EquirectangularViewer/images/full_screen.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_fullscreen.setIcon(icon5)
        self.btn_fullscreen.setCheckable(True)
        self.btn_fullscreen.setObjectName(_fromUtf8("btn_fullscreen"))
        self.horizontalLayout.addWidget(self.btn_fullscreen)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.retranslateUi(orbitalDialog)
        QtCore.QObject.connect(self.btn_fullscreen, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), orbitalDialog.FullScreen)
        QtCore.QObject.connect(self.btn_ZoomOut, QtCore.SIGNAL(_fromUtf8("clicked()")), orbitalDialog.ResizeDialog)
        QtCore.QObject.connect(self.btn_ZoomIn, QtCore.SIGNAL(_fromUtf8("clicked()")), orbitalDialog.ResizeDialog)
        QtCore.QObject.connect(self.btn_back, QtCore.SIGNAL(_fromUtf8("clicked()")), orbitalDialog.GetBackNextImage)
        QtCore.QObject.connect(self.btn_next, QtCore.SIGNAL(_fromUtf8("clicked()")), orbitalDialog.GetBackNextImage)
        QtCore.QMetaObject.connectSlotsByName(orbitalDialog)

    def retranslateUi(self, orbitalDialog):
        orbitalDialog.setWindowTitle(_translate("orbitalDialog", "Equirectangular Viewer", None))

import resources_rc
