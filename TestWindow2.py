# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 12:54:17 2017

@author: Diego L.Guarin -- diego_guarin at meei.harvard.edu
"""

import os
import sys

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QPushButton, QDialog, QSpinBox
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QFile, QTextStream
"""

"""

        
class DrawWindow(QDialog):
        
    
    def __init__(self):
        super(DrawWindow, self).__init__()
        
#        self._scene = QtWidgets.QGraphicsScene(self)
#        self.setScene(self._scene)
        
        self.initUI()
        

        
    def initUI(self):
        
        self.setWindowTitle('Go To Frame')
        scriptDir = os.getcwd()
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'face_icon.ico'))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() |
                              QtCore.Qt.WindowSystemMenuHint |
                              QtCore.Qt.WindowMinMaxButtonsHint)
        
        
        
        
        self._scene = QtWidgets.QGraphicsScene(self)
        #self._scene.setSceneRect(0, 0, 500, 500)
        self.view = QtWidgets.QGraphicsView(self)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
        
        self.view.setFocusPolicy(QtCore.Qt.NoFocus)
        color = self.palette().color(QtGui.QPalette.Background)
        self.view.setBackgroundBrush(color)
        
        
        self.spacerh = QtWidgets.QWidget(self)
        self.spacerh.setFixedSize(20,0)
        
        self.spacerv = QtWidgets.QWidget(self)
        self.spacerv.setFixedSize(0,5)

        
        newfont = QtGui.QFont("Times", 12)
        
        self.label1 = QLabel('Resting Palpebral Fissure:')
        self.label1.setFont(newfont)
        self.label1.setFixedWidth(250)
        
        self.label2 = QLabel('Hi')
        self.label2.setFont(newfont)
        self.label2.setFixedWidth(100)
        #self.label2.setAlignment(QtCore.Qt.AlignCenter)
        
        self.label3 = QLabel('')
        self.label3.setFont(newfont)
        self.label3.setFixedWidth(150)
        
        textLayout = QtWidgets.QHBoxLayout()
        textLayout.addWidget(self.spacerh)
        textLayout.addWidget(self.label1)
        textLayout.addWidget(self.label2)
        textLayout.addWidget(self.label3)
        textLayout.addWidget(self.spacerh)
        
        Box = QtWidgets.QGroupBox('Dynamic Parameters')
        Box.setStyleSheet(self.getStyleSheet(os.getcwd() + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        BoxLayout = QtWidgets.QVBoxLayout()
        BoxLayout.addWidget(self.spacerv)
        BoxLayout.addLayout(textLayout)
        BoxLayout.addWidget(self.spacerv)
        Box.setLayout(BoxLayout)
        
        self._scene.addWidget(Box)
        
        print(Box.size().width())
        
        #self._scene.addWidget(self.label1)
        #self._scene.addWidget(self.label2)
        
        
#        textLayout = QtWidgets.QHBoxLayout()
#        textLayout.addWidget(self.label)
#        textLayout.addWidget(self.label2)
        
        
        #buttons       
        
        DoneButton = QPushButton('&Accept', self)
        DoneButton.setFixedWidth(75)
        DoneButton.setFont(newfont)
        DoneButton.clicked.connect(self.Done)
        
        CancelButton = QPushButton('&Cancel', self)
        CancelButton.setFixedWidth(75)
        CancelButton.setFont(newfont)
        CancelButton.clicked.connect(self.Cancel)
        
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(DoneButton)
        buttonLayout.addWidget(CancelButton)
        
        
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.view)
        layout.addLayout(buttonLayout)
        

        
        self.setLayout(layout)

        

        #fix the size, the user cannot change it 
        #self.resize(self.sizeHint())
        #self.setFixedSize(self.size())
        
        self.DrawSomeLines(self.label3)
        self.view.setScene(self._scene)
        self.show()   
        
    def DrawSomeLines(self, label, value = None):
        x = label.pos().x()
        y = label.pos().y() 
        h = label.height()
        w = label.width()
        
        
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(2)
        pen.setStyle(QtCore.Qt.SolidLine)
        self._scene.addLine(QtCore.QLineF(x,y+int(h/2),x+w,y+int(h/2)), pen)
        self._scene.addLine(QtCore.QLineF(x,y,x,y+h), pen)
        self._scene.addLine(QtCore.QLineF(x+w,y,x+w,y+h), pen)
        self._scene.addLine(QtCore.QLineF(x+int(w/2),y,x+int(w/2),y+h), pen)
        
        TextItem = QtWidgets.QGraphicsSimpleTextItem()
        brush=QtGui.QBrush(QtCore.Qt.black)
        TextItem.setBrush(brush)
        TextItem.setText("Wide")        
        w_text  =  TextItem.boundingRect().width()
        #h_text = TextItem.boundingRect().height()
        TextItem.setPos(QtCore.QPointF(x-int(w_text/2),y+h+2))       
        self._scene.addItem(TextItem)
        
        
        TextItem = QtWidgets.QGraphicsSimpleTextItem()
        brush=QtGui.QBrush(QtCore.Qt.black)
        TextItem.setBrush(brush)
        TextItem.setText("Balanced")        
        w_text  =  TextItem.boundingRect().width()
        #h_text = TextItem.boundingRect().height()
        TextItem.setPos(QtCore.QPointF(x-int(w_text/2)+int(w/2),y+h+2))       
        self._scene.addItem(TextItem)
        
        
        TextItem = QtWidgets.QGraphicsSimpleTextItem()
        brush=QtGui.QBrush(QtCore.Qt.black)
        TextItem.setBrush(brush)
        TextItem.setText("Narrow")        
        w_text  =  TextItem.boundingRect().width()
        #h_text = TextItem.boundingRect().height()
        TextItem.setPos(QtCore.QPointF(x-int(w_text/2)+w,y+h+2))       
        self._scene.addItem(TextItem)
#        print(x,y,h,w)
#        qp = QtGui.QPainter()
#        qp.begin(self)
#        pen1 = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
#        #pen2 = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.DotLine)        
#        qp.setPen(pen1)
#        qp.drawLine(x, y-int(h/4), x+w, y-int(h/4))
#        print(x, y-int(h/4), x+w, y-int(h/4))
#        qp.end()
#        
    def getStyleSheet(self, path):
        f = QFile(path)
        f.open(QFile.ReadOnly | QFile.Text)
        stylesheet = QTextStream(f).readAll()
        f.close()
        return stylesheet

        
    def Done(self):
        self.Canceled = False
        self.close()
        
#    def Connection(self, obj):
#        obj.NewValue.connect(self.change_value)
#        
#    @pyqtSlot(int)
#    def change_value(self, val):
#        self.label2.setText(str(val))

    def Cancel(self):
        
        self.close()  

       
    def closeEvent(self, event):
        event.accept()

        
if __name__ == '__main__':
#    app = QtWidgets.QApplication([])
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
       
    GUI = DrawWindow()
    GUI.show()
    app.exec_()
    

