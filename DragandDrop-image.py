# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 14:24:31 2017

@author: guarind
"""

import cv2
import os
import sys
import numpy as np

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

"""
This class is in charge of drawing the picture and the landmarks in the main 
window, it also takes care of lifting and re-location of landmarks. 
"""

class ThumbNailViewer(QtWidgets.QGraphicsView):      
    
    dropped = QtCore.pyqtSignal(list)
    
    def __init__(self):
        #usual parameters to make sure the image can be zoom-in and out and is 
        #possible to move around the zoomed-in view
        super(ThumbNailViewer, self).__init__()
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(150,150,150)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        #self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        
        
        self.setAcceptDrops(True)
        self.dragOver = False
        

        
        
        self._validextensions = ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.PNG', '.JPG', '.JPEG', '.TIF', '.TIFF']

        #QtWidgets.QGraphicsView.RubberBandDrag
        
    def setPhoto(self, pixmap = None):
        #this function puts an image in the scece (if pixmap is not None), it
        #sets the zoom to zero  
        if pixmap and not pixmap.isNull():
            #self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self._photo.setPixmap(pixmap)
            self.fitInView()
        else:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())

    def fitInView(self):
        #this function takes care of accomodating the view so that it can fit
        #in the scene
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        self.setSceneRect(rect)
        if not rect.isNull():
            unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())        
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            factor = min(viewrect.width() / scenerect.width(),
                     viewrect.height() / scenerect.height())               
            self.scale(factor, factor)
            self.centerOn(rect.center())
            
    def resizeEvent(self, event):
        #this function assure that when the main window is resized the image 
        #is also resized preserving the h/w ratio
        self.fitInView()
        


    def dragEnterEvent(self, event):        
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            
            for url in event.mimeData().urls():
                
                local_address = str(url.toLocalFile())
                
                file_name,extension = os.path.splitext(local_address)
                if extension in self._validextensions:
                    event.setDropAction(QtCore.Qt.CopyAction)
                    event.accept()
                else:
                    event.ignore()
        else:
            event.ignore()
            

    def dropEvent(self, event):
        if event.mimeData().hasUrls():           
            for url in event.mimeData().urls():               
                local_address = str(url.toLocalFile())                
                file_name,extension = os.path.splitext(local_address)
                if extension in self._validextensions:
                    event.setDropAction(QtCore.Qt.CopyAction)                    
                    event.accept()
                    
                    pixmap = QtGui.QPixmap(local_address)
                    self.setPhoto(pixmap)
                else:
                    event.ignore()
        else:
            event.ignore()     
    

class window(QtWidgets.QWidget):
    
    def __init__(self):
        super(window, self).__init__()
        self.setWindowTitle('Auto-eFace')
        
      
        #initialize the User Interface
        self.initUI()
        
    def initUI(self):
        
        
        spacerh = QtWidgets.QWidget(self)
        spacerh.setFixedSize(10,0)
        
        spacerv = QtWidgets.QWidget(self)
        spacerv.setFixedSize(0,10)
        
        #the image will be displayed in the custom ImageViewer
        self.Rest = ThumbNailViewer() 
        self.Rest.setMinimumWidth(100)
        self.Rest.setMinimumHeight(150)
        self.Rest_title = QtWidgets.QLabel()
        self.Rest_title.setText('Rest:')
        self.Rest_title.setWordWrap(True)
        
        self.SmallSmile = ThumbNailViewer()
        self.SmallSmile.setMinimumWidth(100)
        self.SmallSmile.setMinimumHeight(150)
        self.SmallSmile_title = QtWidgets.QLabel()
        self.SmallSmile_title.setText('Small Smile:')      
        
        
        self.LargeSmile = ThumbNailViewer()
        self.LargeSmile.setMinimumWidth(100)
        self.LargeSmile.setMinimumHeight(150)
        self.LargeSmile_title = QtWidgets.QLabel()
        self.LargeSmile_title.setText('Large Smile:')   
        
        
        self.EyeBrow = ThumbNailViewer()
        self.EyeBrow.setMinimumWidth(100)
        self.EyeBrow.setMinimumHeight(150)
        self.EyeBrow_title = QtWidgets.QLabel()
        self.EyeBrow_title.setText('EyeBrow Elevation:')  
        
        Rest = QtWidgets.QGroupBox('Rest')
        RestLayout = QtWidgets.QGridLayout()
        RestLayout.addWidget(self.Rest,0,0,1,2)
        Rest.setLayout(RestLayout)
        
        

        
        #the main window consist of the toolbar and the ImageViewer
        #layout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QGridLayout()
        #layout.addWidget(self.Rest_title,0,0,1,1)
        #layout.addWidget(self.Rest,1,0,1,2)
        
        layout.addWidget(Rest,0,0,2,2)
        
        layout.addWidget(spacerv,0,2,2,1)
        
        layout.addWidget(self.SmallSmile_title,0,3,1,1)
        layout.addWidget(self.SmallSmile,1,3,1,2)        
        
        layout.addWidget(spacerv,0,5,2,1)
        
        layout.addWidget(self.LargeSmile_title,0,6,1,1)
        layout.addWidget(self.LargeSmile,1,6,1,2)       
        
        layout.addWidget(spacerv,0,8,2,1)
        
        layout.addWidget(self.EyeBrow_title,0,9,1,1)
        layout.addWidget(self.EyeBrow ,1,9,1,2)     
        
        
        self.setLayout(layout)
        

        
        self.show()        
            
if __name__ == '__main__':
    
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    
    app.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
        
    GUI = window()
    #GUI.show()
    app.exec_()
            
            
            

                        

    


        