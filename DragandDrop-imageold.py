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
from settings_window import ShowSettings


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
        self.setWindowTitle('auto-eFACE')
        scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'meei_3WR_icon.ico'))
        #self.setStyleSheet('background:Aliceblue')

        
        self._CalibrationType = 'Iris'  #_CalibrationType can be 'Iris' or 'Manual'
        self._CalibrationValue = 11.77 #calibration parameter
        
        self._ModelName = 'iBUG' #_ModelType can be 'iBUGS' or 'MEE'
        
        
        
        #Each photogaph will have its own class that stores all the relevant 
        #information, this class will be updated everytime the user double 
        #clicks on a Thumbnail viewer element. The report card will be generated 
        #with the information stored in these elements, so they all have to 
        #be filled before generating the report card
        self._Rest = PatientPhotograph()
        self._SmallSmile = PatientPhotograph()
        self._LargeSmile = PatientPhotograph()
        self._EyeBrow = PatientPhotograph()
        self._EyeClosureGently = PatientPhotograph()
        self._EyeClosureTight = PatientPhotograph()
        self._PuckeringLips = PatientPhotograph()
        self._DentalShow = PatientPhotograph()
        
      
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
        self.SmallSmile.dropped.connect(self.pictureDropped)
        self.SmallSmile.setMinimumWidth(100)
        self.SmallSmile.setMinimumHeight(150)
        SmallSmileBox = QtWidgets.QGroupBox('Best Smile')
        SmallSmileBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        SmallSmileLayout = QtWidgets.QGridLayout()
        SmallSmileLayout.addWidget(self.SmallSmile,0,0,1,1)
        SmallSmileBox.setLayout(SmallSmileLayout)
        
        
        self.LargeSmile = ThumbNailViewer()
        self.LargeSmile.WidgetName = "LargeSmile"
        self.LargeSmile.dropped.connect(self.pictureDropped)
        self.LargeSmile.setMinimumWidth(100)
        self.LargeSmile.setMinimumHeight(150)
        LargeSmileBox = QtWidgets.QGroupBox('Biggest Smile')
        LargeSmileBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        LargeSmileLayout = QtWidgets.QGridLayout()
        LargeSmileLayout.addWidget(self.LargeSmile,0,0,1,1)
        LargeSmileBox.setLayout(LargeSmileLayout)

        
        
        self.EyeBrow = ThumbNailViewer()
        self.EyeBrow.WidgetName = "EyeBrow"
        self.EyeBrow.dropped.connect(self.pictureDropped)
        self.EyeBrow.setMinimumWidth(100)
        self.EyeBrow.setMinimumHeight(150)
        EyeBrowBox = QtWidgets.QGroupBox('Brow Elevation')
        EyeBrowBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        EyeBrowLayout = QtWidgets.QGridLayout()
        EyeBrowLayout.addWidget(self.EyeBrow,0,0,1,1)
        EyeBrowBox.setLayout(EyeBrowLayout)
        
        self.EyeClosureGently = ThumbNailViewer()
        self.EyeClosureGently.WidgetName = "EyeClosureGently"
        self.EyeClosureGently.dropped.connect(self.pictureDropped)
        self.EyeClosureGently.setMinimumWidth(100)
        self.EyeClosureGently.setMinimumHeight(150)
        EyeClosureGentlyBox = QtWidgets.QGroupBox('Gentle Eye Closure')
#        EyeClosureGentlyBox.setMinimumWidth(100)
#        EyeClosureGentlyBox.setMinimumHeight(150)
        EyeClosureGentlyBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        EyeClosureGentlyLayout = QtWidgets.QGridLayout()
        EyeClosureGentlyLayout.addWidget(self.EyeClosureGently,0,0,1,1)
        EyeClosureGentlyBox.setLayout(EyeClosureGentlyLayout)
        
        self.EyeClosureTight = ThumbNailViewer()
        self.EyeClosureTight.WidgetName = "EyeClosureTight"
        self.EyeClosureTight.dropped.connect(self.pictureDropped)
        self.EyeClosureTight.setMinimumWidth(100)
        self.EyeClosureTight.setMinimumHeight(150)
        EyeClosureTightBox = QtWidgets.QGroupBox('Tight Eye Closure')
        EyeClosureTightBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        EyeClosureTightLayout = QtWidgets.QGridLayout()
        EyeClosureTightLayout.addWidget(self.EyeClosureTight,0,0,1,1)
        EyeClosureTightBox.setLayout(EyeClosureTightLayout)
        
        self.PuckeringLips = ThumbNailViewer()
        self.PuckeringLips.WidgetName = "PuckeringLips"
        self.PuckeringLips.dropped.connect(self.pictureDropped)
        self.PuckeringLips.setMinimumWidth(100)
        self.PuckeringLips.setMinimumHeight(150)
        PuckeringLipsBox = QtWidgets.QGroupBox('Pucker Lips')
        PuckeringLipsBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        PuckeringLipsLayout = QtWidgets.QGridLayout()
        PuckeringLipsLayout.addWidget(self.PuckeringLips,0,0,1,1)
        PuckeringLipsBox.setLayout(PuckeringLipsLayout)
        
        self.DentalShow = ThumbNailViewer()
        self.DentalShow.WidgetName = "DentalShow"
        self.DentalShow.dropped.connect(self.pictureDropped)
        self.DentalShow.setMinimumWidth(100)
        self.DentalShow.setMinimumHeight(150)
        DentalShowBox = QtWidgets.QGroupBox('Show Theet')
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
        
        layout.addWidget(EyeBrowBox,0,2,1,1)        
        
        layout.addWidget(spacerv,0,3,2,1)
        
        layout.addWidget(EyeClosureGentlyBox,0,4,1,1)       
        
        layout.addWidget(spacerv,0,5,2,1)
        
        layout.addWidget(EyeClosureTightBox ,0,6,1,1)  
        
        layout.addWidget(spacerh,1,0,1,6)
        
        layout.addWidget(SmallSmileBox,2,0,1,1)
        
        layout.addWidget(LargeSmileBox,2,2,1,1)
        
        layout.addWidget(PuckeringLipsBox,2,4,1,1)
        
        layout.addWidget(DentalShowBox,2,6,1,1)
        
        
        
        
        #toolbar         
        loadAction = QtWidgets.QAction('Load images from folder', self)
        loadAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'load_icon2.png'))
        #loadAction.triggered.connect(self.load_file)
        
        saveAction = QtWidgets.QAction('Save results', self)
        saveAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'save_icon2.png'))
        #saveAction.triggered.connect(self.save_results)
        
        settingsAction = QtWidgets.QAction('Change settings', self)
        settingsAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'settings-icon2.png'))
        settingsAction.triggered.connect(self.settings)
        
        ReportAction = QtWidgets.QAction('Generate report', self)
        ReportAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'report_card.png'))
        #ReportAction.triggered.connect(self.report_card)
        
        exitAction = QtWidgets.QAction('Exit', self)
        exitAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'exit_icon2.png'))
        exitAction.triggered.connect(self.close_app)
        
        
        
        #create the toolbar and add the actions 
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.addActions((loadAction, ReportAction, settingsAction,   saveAction,  exitAction))
        
        #set the size of each icon to 50x50
        self.toolBar.setIconSize(QtCore.QSize(50,50))
        
        for action in self.toolBar.actions():
            widget = self.toolBar.widgetForAction(action)
            widget.setFixedSize(50, 50)
            
        self.toolBar.setMinimumSize(self.toolBar.sizeHint())
        self.toolBar.setStyleSheet('QToolBar{spacing:5px;}')
        
        LargeLayout = QtWidgets.QVBoxLayout(self)
        LargeLayout.addWidget(self.toolBar)
        LargeLayout.addLayout(layout)
        self.setLayout(LargeLayout)
        
        
        self.show()     
        self.move(QtWidgets.QApplication.desktop().screen().rect().center()- self.rect().center())
        
      
    #this function read the style sheet used to presents the GroupBox, 
    #it is located in .\include\GroupBoxStyle.qss
    def getStyleSheet(self, path):
        f = QFile(path)
        f.open(QFile.ReadOnly | QFile.Text)
        stylesheet = QTextStream(f).readAll()
        f.close()
        return stylesheet
    
    
    def pictureDropped(self, photograph):
        #print(photograph._file_name)
        show_me = Emotrics(photograph._file_name, self._CalibrationType, self._CalibrationValue, self._ModelName)
        show_me.exec_()
        
#        if photograph._ID == "Rest":
#            #the user modified the Rest photo
#            self._Rest._photo = photograph._photo
#            self._Rest._file_name = photograph._file_name
#            self._Rest._name = photograph._name
#            self._Rest._extension = photograph._extension
#            self._Rest._ID = photograph._ID
#            self._Rest._shape = show_me.displayImage._shape
#            self._Rest._lefteye = show_me.displayImage._lefteye
#            self._Rest._righteye = show_me.displayImage._righteye
#            self._Rest._points = show_me.displayImage._points
#            self._Rest._boundingbox = show_me.displayImage._boundingbox
#            
#        elif photograph._ID == "SmallSmile":
#            #the user modified the small smile photo
#            self._SmallSmile._photo = photograph._photo
#            self._SmallSmile._file_name = photograph._file_name
#            self._SmallSmile._name = photograph._name
#            self._SmallSmile._extension = photograph._extension
#            self._SmallSmile._ID = photograph._ID
#            self._SmallSmile._shape = show_me.displayImage._shape
#            self._SmallSmile._lefteye = show_me.displayImage._lefteye
#            self._SmallSmile._righteye = show_me.displayImage._righteye
#            self._SmallSmile._points = show_me.displayImage._points
#            self._SmallSmile._boundingbox = show_me.displayImage._boundingbox 
#            
#        elif photograph._ID == "LargeSmile":
#            #the user modified the large smile photo
#            self._LargeSmile._photo = photograph._photo
#            self._LargeSmile._file_name = photograph._file_name
#            self._LargeSmile._name = photograph._name
#            self._LargeSmile._extension = photograph._extension
#            self._LargeSmile._ID = photograph._ID
#            self._LargeSmile._shape = show_me.displayImage._shape
#            self._LargeSmile._lefteye = show_me.displayImage._lefteye
#            self._LargeSmile._righteye = show_me.displayImage._righteye
#            self._LargeSmile._points = show_me.displayImage._points
#            self._LargeSmile._boundingbox = show_me.displayImage._boundingbox             
#            
#        elif photograph._ID == "EyeBrow":
#            #the user modified the eye brow photo
#            self._EyeBrow._photo = photograph._photo
#            self._EyeBrow._file_name = photograph._file_name
#            self._EyeBrow._name = photograph._name
#            self._EyeBrow._extension = photograph._extension
#            self._EyeBrow._ID = photograph._ID
#            self._EyeBrow._shape = show_me.displayImage._shape
#            self._EyeBrow._lefteye = show_me.displayImage._lefteye
#            self._EyeBrow._righteye = show_me.displayImage._righteye
#            self._EyeBrow._points = show_me.displayImage._points
#            self._EyeBrow._boundingbox = show_me.displayImage._boundingbox   
#            
#        elif photograph._ID == "EyeClosureGently":
#            #the user modified the gentle eye closure photo
#            self._EyeClosureGently._photo = photograph._photo
#            self._EyeClosureGently._file_name = photograph._file_name
#            self._EyeClosureGently._name = photograph._name
#            self._EyeClosureGently._extension = photograph._extension
#            self._EyeClosureGently._ID = photograph._ID
#            self._EyeClosureGently._shape = show_me.displayImage._shape
#            self._EyeClosureGently._lefteye = show_me.displayImage._lefteye
#            self._EyeClosureGently._righteye = show_me.displayImage._righteye
#            self._EyeClosureGently._points = show_me.displayImage._points
#            self._EyeClosureGently._boundingbox = show_me.displayImage._boundingbox               
#     
#        elif photograph._ID == "EyeClosureTight":
#            #the user modified the tight eye closure photo
#            self._EyeClosureTight._photo = photograph._photo
#            self._EyeClosureTight._file_name = photograph._file_name
#            self._EyeClosureTight._name = photograph._name
#            self._EyeClosureTight._extension = photograph._extension
#            self._EyeClosureTight._ID = photograph._ID
#            self._EyeClosureTight._shape = show_me.displayImage._shape
#            self._EyeClosureTight._lefteye = show_me.displayImage._lefteye
#            self._EyeClosureTight._righteye = show_me.displayImage._righteye
#            self._EyeClosureTight._points = show_me.displayImage._points
#            self._EyeClosureTight._boundingbox = show_me.displayImage._boundingbox    
#            
#        elif photograph._ID == "PuckeringLips":
#            #the user modified the puckering lips photo
#            self._PuckeringLips._photo = photograph._photo
#            self._PuckeringLips._file_name = photograph._file_name
#            self._PuckeringLips._name = photograph._name
#            self._PuckeringLips._extension = photograph._extension
#            self._PuckeringLips._ID = photograph._ID
#            self._PuckeringLips._shape = show_me.displayImage._shape
#            self._PuckeringLips._lefteye = show_me.displayImage._lefteye
#            self._PuckeringLips._righteye = show_me.displayImage._righteye
#            self._PuckeringLips._points = show_me.displayImage._points
#            self._PuckeringLips._boundingbox = show_me.displayImage._boundingbox   
#            
#        elif photograph._ID == "DentalShow":
#            #the user modified the deltal show photo
#            self._DentalShow._photo = photograph._photo
#            self._DentalShow._file_name = photograph._file_name
#            self._DentalShow._name = photograph._name
#            self._DentalShow._extension = photograph._extension
#            self._DentalShow._ID = photograph._ID
#            self._DentalShow._shape = show_me.displayImage._shape
#            self._DentalShow._lefteye = show_me.displayImage._lefteye
#            self._DentalShow._righteye = show_me.displayImage._righteye
#            self._DentalShow._points = show_me.displayImage._points
#            self._DentalShow._boundingbox = show_me.displayImage._boundingbox   
    
    def settings(self):
        #this new window allows the user to:
            #1) modify the calibration parameter used to compute all the real-life measurements 
            #2) Select the model used for landmakr estimation
        #we send the current values to the window so that the values can be preserved when a new photo is loaded
        Settings = ShowSettings(self, self._ModelName, self._CalibrationType, self._CalibrationValue)
        Settings.exec_()
        
        #get values from the window and update appropiate parameters 
        if Settings.tab1._checkBox1.isChecked() == True:
            self._CalibrationType = 'Iris'
            self._CalibrationValue = float(Settings.tab1._IrisDiameter_Edit.text())
        elif Settings.tab1._checkBox2.isChecked() == True:
            self._CalibrationType = 'Manual'
            self._CalibrationValue = float(Settings.tab1._Personalized_Edit.text())
            
        if Settings.tab2._checkBox2.isChecked() == True:
            self._ModelName = 'iBUG'
        elif Settings.tab2._checkBox1.isChecked() == True:
            self._ModelName = 'MEE'
            

        
        
        
        
    def close_app(self):  
        
        #ask is the user really wants to close the app
        choice = QtWidgets.QMessageBox.question(self, 'Message', 
                            'Do you want to exit?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if choice == QtWidgets.QMessageBox.Yes :
            self.close()
            app.exec_()
        else:
            pass 
            
if __name__ == '__main__':
    
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    
    app.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
  
        
    GUI = window()
    GUI.show()
    app.exec_()
            
            
            

                        

    


        