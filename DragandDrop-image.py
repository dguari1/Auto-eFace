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

from PyQt5.QtCore import QFile, QTextStream


from mini_Emotrics import Emotrics


class PatientPhotograph(object):
    
    #this class contains all the information associated with a photo
    def __init__(self):
        self._photo = None  #this is a open cv image element
        self._file_name = None  #is the physical address of the photo
        self._name = '' #this is the file name
        self._extension = '' #this is the file extension
        self._ID = '' #this is the photo ID, there are eight different types of photos
        self._shape = None #this is the landmark localization provided by dlib
        self._lefteye = None #this si the position and diameter of left iris
        self._righteye = None #this si the position and diameter of right iris
        self._points = None
        self._boundingbox = None #this is the facial bounding-box provided by dlib

"""
This class is in charge of drawing the picture and the landmarks in the main 
window, it also takes care of lifting and re-location of landmarks. 
"""

class ThumbNailViewer(QtWidgets.QGraphicsView):      
    
    dropped = QtCore.pyqtSignal(object)
    
    def __init__(self, parent=None):
        #usual parameters to make sure the image can be zoom-in and out and is 
        #possible to move around the zoomed-in view
        super(ThumbNailViewer, self).__init__(parent)
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(227,227,227)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        #self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        
        
        self.setAcceptDrops(True)
        self._hasImage = False
        self._ImageAddress = None
        
        
        
        
        self._validextensions = ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.PNG', '.JPG', '.JPEG', '.TIF', '.TIFF']
        
        self.setBackground()

        #QtWidgets.QGraphicsView.RubberBandDrag         
        
        self.WidgetName = None
        
    def setBackground(self):
        scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))
        pixmap = QtGui.QPixmap(scriptDir + os.path.sep + 'include' + os.path.sep + 'drophere.jpg')
        
        self.setPhoto(pixmap)
               
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
                    self._hasImage = True  #indicate that there is an image
                    self._ImageAddress = os.path.normpath(local_address) #store the image address in a class variable
                    
                else:
                    event.ignore()
        else:
            event.ignore()     
            
    def mouseDoubleClickEvent(self, event):
        if self._hasImage :
            InfoPhotograph = PatientPhotograph()
            InfoPhotograph._photo = cv2.imread(self._ImageAddress)
            InfoPhotograph._file_name = self._ImageAddress
            #split the file name from its extension
            file_name,extension = os.path.splitext(InfoPhotograph._file_name)
            delimiter = os.path.sep
            name=file_name.split(delimiter)
            #
            InfoPhotograph._name = name = name[-1] #keep only the last porion (the rest is the physical address of the file)
            InfoPhotograph._extension = extension[1:]
            InfoPhotograph._ID = self.WidgetName
            
            self.dropped.emit(InfoPhotograph)    

class window(QtWidgets.QWidget):
    
    def __init__(self):
        super(window, self).__init__()
        self.setWindowTitle('Auto-eFace')
        
        
      
        #initialize the User Interface
        self.initUI()
        
    def initUI(self):
        scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))
        
        spacerh = QtWidgets.QWidget(self)
        spacerh.setFixedSize(15,0)
        
        spacerv = QtWidgets.QWidget(self)
        spacerv.setFixedSize(0,15)
        
        #the image will be displayed in the custom ImageViewer
        self.Rest = ThumbNailViewer()
        self.Rest.WidgetName = "Rest"
        self.Rest.dropped.connect(self.pictureDropped)
        self.Rest.setMinimumWidth(100)
        self.Rest.setMinimumHeight(150)
        RestBox = QtWidgets.QGroupBox('Rest')
        RestBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        RestLayout = QtWidgets.QGridLayout()
        RestLayout.addWidget(self.Rest,0,0,1,1)
        RestBox.setLayout(RestLayout)
  
        
        self.SmallSmile = ThumbNailViewer()
        self.SmallSmile.WidgetName = "SmallSmile"
        self.SmallSmile.setMinimumWidth(100)
        self.SmallSmile.setMinimumHeight(150)
        SmallSmileBox = QtWidgets.QGroupBox('Small Smile')
        SmallSmileBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        SmallSmileLayout = QtWidgets.QGridLayout()
        SmallSmileLayout.addWidget(self.SmallSmile,0,0,1,1)
        SmallSmileBox.setLayout(SmallSmileLayout)
        
        
        self.LargeSmile = ThumbNailViewer()
        self.LargeSmile.WidgetName = "LargeSmile"
        self.LargeSmile.setMinimumWidth(100)
        self.LargeSmile.setMinimumHeight(150)
        LargeSmileBox = QtWidgets.QGroupBox('Large Smile')
        LargeSmileBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        LargeSmileLayout = QtWidgets.QGridLayout()
        LargeSmileLayout.addWidget(self.LargeSmile,0,0,1,1)
        LargeSmileBox.setLayout(LargeSmileLayout)

        
        
        self.EyeBrow = ThumbNailViewer()
        self.EyeBrow.WidgetName = "EyeBrow"
        self.EyeBrow.setMinimumWidth(100)
        self.EyeBrow.setMinimumHeight(150)
        EyeBrowBox = QtWidgets.QGroupBox('EyeBrow Elevation')
        EyeBrowBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        EyeBrowLayout = QtWidgets.QGridLayout()
        EyeBrowLayout.addWidget(self.EyeBrow,0,0,1,1)
        EyeBrowBox.setLayout(EyeBrowLayout)
        
        self.EyeClosureGently = ThumbNailViewer()
        self.EyeClosureGently.WidgetName = "EyeClosureGently"
        self.EyeClosureGently.setMinimumWidth(100)
        self.EyeClosureGently.setMinimumHeight(150)
        EyeClosureGentlyBox = QtWidgets.QGroupBox('Gently Eye Closure')
        EyeClosureGentlyBox.setMinimumWidth(100)
        EyeClosureGentlyBox.setMinimumHeight(150)
        EyeClosureGentlyBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        EyeClosureGentlyLayout = QtWidgets.QGridLayout()
        EyeClosureGentlyLayout.addWidget(self.EyeClosureGently,0,0,1,1)
        EyeClosureGentlyBox.setLayout(EyeClosureGentlyLayout)
        
        self.EyeClosureTight = ThumbNailViewer()
        self.EyeClosureTight.WidgetName = "EyeClosureTight"
        self.EyeClosureTight.setMinimumWidth(100)
        self.EyeClosureTight.setMinimumHeight(150)
        EyeClosureTightBox = QtWidgets.QGroupBox('Tight Eye Closure')
        EyeClosureTightBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        EyeClosureTightLayout = QtWidgets.QGridLayout()
        EyeClosureTightLayout.addWidget(self.EyeClosureTight,0,0,1,1)
        EyeClosureTightBox.setLayout(EyeClosureTightLayout)
        
        self.PuckeringLips = ThumbNailViewer()
        self.PuckeringLips.WidgetName = "PuckeringLips"
        self.PuckeringLips.setMinimumWidth(100)
        self.PuckeringLips.setMinimumHeight(150)
        PuckeringLipsBox = QtWidgets.QGroupBox('Puckering Lips')
        PuckeringLipsBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        PuckeringLipsLayout = QtWidgets.QGridLayout()
        PuckeringLipsLayout.addWidget(self.PuckeringLips,0,0,1,1)
        PuckeringLipsBox.setLayout(PuckeringLipsLayout)
        
        self.DentalShow = ThumbNailViewer()
        self.DentalShow.WidgetName = "DentalShow"
        self.DentalShow.setMinimumWidth(100)
        self.DentalShow.setMinimumHeight(150)
        DentalShowBox = QtWidgets.QGroupBox('Showing theet')
        DentalShowBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        DentalShowLayout = QtWidgets.QGridLayout()
        DentalShowLayout.addWidget(self.DentalShow,0,0,1,1)
        DentalShowBox.setLayout(DentalShowLayout)
        

        
        

        
        #the main window consist of the toolbar and the ImageViewer
        #layout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QGridLayout()
        #layout.addWidget(self.Rest_title,0,0,1,1)
        #layout.addWidget(self.Rest,1,0,1,2)
        
        layout.addWidget(RestBox,0,0,1,1)
        
        layout.addWidget(spacerv,0,1,2,1)
        
        layout.addWidget(SmallSmileBox,0,2,1,1)        
        
        layout.addWidget(spacerv,0,3,2,1)
        
        layout.addWidget(LargeSmileBox,0,4,1,1)       
        
        layout.addWidget(spacerv,0,5,2,1)
        
        layout.addWidget(EyeBrowBox ,0,6,1,1)  
        
        layout.addWidget(spacerh,1,0,1,6)
        
        layout.addWidget(EyeClosureGentlyBox,2,0,1,1)
        
        layout.addWidget(EyeClosureTightBox,2,2,1,1)
        
        layout.addWidget(PuckeringLipsBox,2,4,1,1)
        
        layout.addWidget(DentalShowBox,2,6,1,1)
        
        self.setLayout(layout)
        

        
        self.show()     
        
      
    #this function read the style sheet used to presents the GroupBox, 
    #it is located in .\include\GroupBoxStyle.qss
    def getStyleSheet(self, path):
        f = QFile(path)
        f.open(QFile.ReadOnly | QFile.Text)
        stylesheet = QTextStream(f).readAll()
        f.close()
        return stylesheet
    
    
    def pictureDropped(self, photograph):
        print(photograph._name)
        show_me = Emotrics()
        show_me.exec_()
            
if __name__ == '__main__':
    
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    
    app.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
        
    GUI = window()
    #GUI.show()
    app.exec_()
            
            
            

                        

    


        