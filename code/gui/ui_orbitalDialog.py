# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui_orbitalDialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_orbitalDialog(object):
    def setupUi(self, orbitalDialog):
        orbitalDialog.setObjectName("orbitalDialog")
        orbitalDialog.resize(563, 375)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(orbitalDialog.sizePolicy().hasHeightForWidth())
        orbitalDialog.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/EquirectangularViewer/images/icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        orbitalDialog.setWindowIcon(icon)
        orbitalDialog.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.ViewerLayout = QtWidgets.QGridLayout()
        self.ViewerLayout.setObjectName("ViewerLayout")
        self.verticalLayout_3.addLayout(self.ViewerLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.yawLbl = QtWidgets.QLabel(self.dockWidgetContents)
        self.yawLbl.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.yawLbl.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.yawLbl.setObjectName("yawLbl")
        self.horizontalLayout.addWidget(self.yawLbl)
        spacerItem = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_back = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btn_back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_back.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/EquirectangularViewer/images/Previous_Arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_back.setIcon(icon1)
        self.btn_back.setObjectName("btn_back")
        self.horizontalLayout.addWidget(self.btn_back)
        self.btn_next = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btn_next.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_next.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/EquirectangularViewer/images/Next_Arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_next.setIcon(icon2)
        self.btn_next.setObjectName("btn_next")
        self.horizontalLayout.addWidget(self.btn_next)
        spacerItem1 = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.btn_fullscreen = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btn_fullscreen.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_fullscreen.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/EquirectangularViewer/images/full_screen.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_fullscreen.setIcon(icon3)
        self.btn_fullscreen.setCheckable(True)
        self.btn_fullscreen.setObjectName("btn_fullscreen")
        self.horizontalLayout.addWidget(self.btn_fullscreen)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        orbitalDialog.setWidget(self.dockWidgetContents)

        self.retranslateUi(orbitalDialog)
        self.btn_fullscreen.clicked['bool'].connect(orbitalDialog.FullScreen)
        self.btn_back.clicked.connect(orbitalDialog.GetBackNextImage)
        self.btn_next.clicked.connect(orbitalDialog.GetBackNextImage)
        QtCore.QMetaObject.connectSlotsByName(orbitalDialog)

    def retranslateUi(self, orbitalDialog):
        _translate = QtCore.QCoreApplication.translate
        orbitalDialog.setWindowTitle(_translate("orbitalDialog", "Equirectangular Viewer"))
        self.yawLbl.setText(_translate("orbitalDialog", "Yaw:"))
from EquirectangularViewer.gui import resources_rc
