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
from utilities import get_info_from_txt
from ProcessLandmarks import GetLandmarks


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
        self._Tag = '' #this is the tag that goes in the Emotrics window
        self._OpenEmotrics = True #this informs the main prgram if it should open Emotrics 
                                  #for landmark localization. Emotrics will be open only 
                                  #if the user double clikc on a photo

"""
This class is in charge of drawing the picture and the landmarks in the main 
window, it also takes care of lifting and re-location of landmarks. 
"""

class ThumbNailViewer(QtWidgets.QGraphicsView):      
    
    dropped = QtCore.pyqtSignal(object)
    
    def __init__(self, ModelName, InfoPhotograph):
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
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(255,204,204)))
  
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        #self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        
        
        self.setAcceptDrops(True)
        self._hasImage = False
        self._ImageAddress = None
        
        
        
        
        self._validextensions = ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.PNG', '.JPG', '.JPEG', '.TIF', '.TIFF']
        
        self.setBackground()

        #QtWidgets.QGraphicsView.RubberBandDrag         
        
        self.WidgetName = None
        
        
        self.InfoPhotograph = InfoPhotograph #this variable contains all 
                            #the information from the photo, including the
                            #file, name, location, ID, and the results that 
                            #are produced by dlib
                            
        
        
        self._Scale = 1  #this variable carries the scale of the image if it 
                        #needs to be resized, if Scale = 1 then the original 
                        #image was used for processing. If Scale > 1 then 
                        #the original image was too large and a resized image
                        #was used for processing
        
        
        # create Thread  to take care of the landmarks and iris estimation   
        self.thread_landmarks = QtCore.QThread()  # no parent!
        
        self._ModelName = ModelName
        
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
                    
                    
                    #now verify if there is a txt file already avaliable 
                    if os.path.isfile(file_name+'.txt'):
                        #if the txt file already exists then the user can inmediatly start working with the data
                        #put some info in the appropiate place
                        self.InfoPhotograph._file_name = self._ImageAddress
                        self.InfoPhotograph._photo = cv2.imread(self._ImageAddress)
                        
                        #split the file name from its extension
                        file_name,extension = os.path.splitext(self.InfoPhotograph._file_name)
                        delimiter = os.path.sep
                        name=file_name.split(delimiter)
                
                        self.InfoPhotograph._name =  name[-1] #keep only the last portion (the rest is the physical address of the file)
                        self.InfoPhotograph._extension = extension[1:]
                        self.InfoPhotograph._ID = self.WidgetName
                        
                        if self.WidgetName == "Rest":
                            self.InfoPhotograph._Tag = "Rest"
                        elif self.WidgetName == "SmallSmile":
                            self.InfoPhotograph._Tag = "Best Smile"
                        elif self.WidgetName == "LargeSmile":
                            self.InfoPhotograph._Tag = "Biggest Smile"
                        elif self.WidgetName == "EyeBrow":   
                            self.InfoPhotograph._Tag = "Brow Elevation"
                        elif self.WidgetName == "EyeClosureGently":   
                            self.InfoPhotograph._Tag = "Gentle Eye Closure"
                        elif self.WidgetName == "EyeClosureTight": 
                            self.InfoPhotograph._Tag = "Tight Eye Closure"
                        elif self.WidgetName == "PuckeringLips":    
                            self.InfoPhotograph._Tag = "Pucker Lips"
                        elif self.WidgetName == "DentalShow":     
                            self.InfoPhotograph._Tag = "Show Teeth"
                
                        shape,lefteye,righteye,boundingbox = get_info_from_txt(file_name+'.txt')
                        self.InfoPhotograph._lefteye = lefteye
                        self.InfoPhotograph._righteye = righteye 
                        self.InfoPhotograph._shape = shape
                        self.InfoPhotograph._boundingbox = boundingbox
                        self.InfoPhotograph._points = None
                        
                        #set background green to inform that shape information is already avaliable
                        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(204,255,204)))
                        
                        self.InfoPhotograph._OpenEmotrics = False
                        
                        
                        #we now have all the info, emit the information to the main widget
                        self.dropped.emit(self.InfoPhotograph)    
                    
                else:
                    event.ignore()
        else:
            event.ignore()     
            
#    def mouseDoubleClickEvent(self, event):
#        if self._hasImage :
#            InfoPhotograph = PatientPhotograph()
#            InfoPhotograph._photo = cv2.imread(self._ImageAddress)
#            InfoPhotograph._file_name = self._ImageAddress
#            #split the file name from its extension
#            file_name,extension = os.path.splitext(InfoPhotograph._file_name)
#            delimiter = os.path.sep
#            name=file_name.split(delimiter)
#            #
#            InfoPhotograph._name = name = name[-1] #keep only the last porion (the rest is the physical address of the file)
#            InfoPhotograph._extension = extension[1:]
#            InfoPhotograph._ID = self.WidgetName
#            
#            self.dropped.emit(InfoPhotograph)    
            
            
    def mouseDoubleClickEvent(self, event):
        if self._hasImage:
            event.accept()
            #the user wants to open Emotrics 
            #if the landmark information is already avaliable simply open Emotrics
            if self.InfoPhotograph._shape is not None:

                self.InfoPhotograph._OpenEmotrics = True
                self.dropped.emit(self.InfoPhotograph)  
            else:  
                #if not, then first estimate it and then open Emotrics 
                self.InfoPhotograph._OpenEmotrics = True
                self.Process_File()
                
        else:
            event.ignore()
            
            
    def Process_File(self):
        
        #put some info in the appropiate place
        self.InfoPhotograph._file_name = self._ImageAddress
        self.InfoPhotograph._photo = cv2.imread(self._ImageAddress)
        
        #split the file name from its extension
        file_name,extension = os.path.splitext(self.InfoPhotograph._file_name)
        delimiter = os.path.sep
        name=file_name.split(delimiter)

        self.InfoPhotograph._name =  name[-1] #keep only the last portion (the rest is the physical address of the file)
        self.InfoPhotograph._extension = extension[1:]
        self.InfoPhotograph._ID = self.WidgetName
        
        if self.WidgetName == "Rest":
            self.InfoPhotograph._Tag = "Rest"
        elif self.WidgetName == "SmallSmile":
            self.InfoPhotograph._Tag = "Best Smile"
        elif self.WidgetName == "LargeSmile":
            self.InfoPhotograph._Tag = "Biggest Smile"
        elif self.WidgetName == "EyeBrow":   
            self.InfoPhotograph._Tag = "Brow Elevation"
        elif self.WidgetName == "EyeClosureGently":   
            self.InfoPhotograph._Tag = "Gentle Eye Closure"
        elif self.WidgetName == "EyeClosureTight": 
            self.InfoPhotograph._Tag = "Tight Eye Closure"
        elif self.WidgetName == "PuckeringLips":    
            self.InfoPhotograph._Tag = "Pucker Lips"
        elif self.WidgetName == "DentalShow":     
            self.InfoPhotograph._Tag = "Show Teeth"

        #if the photo was already processed then get the information for the
        #txt file, otherwise process the photo using the landmark ans pupil
        #localization algorithms 
        name = os.path.normpath(self._ImageAddress)
        file_txt=name[:-4]
        file_txt = (file_txt + '.txt')
        if os.path.isfile(file_txt):
            shape,lefteye,righteye,boundingbox = get_info_from_txt(file_txt)
            self.InfoPhotograph._lefteye = lefteye
            self.InfoPhotograph._righteye = righteye 
            self.InfoPhotograph._shape = shape
            self.InfoPhotograph._boundingbox = boundingbox
            self.InfoPhotograph._points = None
            
            
            #we now have all the info, emit the information to the main widget
            self.dropped.emit(self.InfoPhotograph)    
        else:
            #if the image is too large then it needs to be resized....
            h,w,d = self.InfoPhotograph._photo.shape

            #if the image is too big then we need to resize it so that the landmark 
            #localization process can be performed in a reasonable time 
            self._Scale = 1  #start from a clear initial scale
            if h > 1500 or w > 1500 :
                if h >= w :
                    h_n = 1500
                    self._Scale = h/h_n
                    w_n = int(np.round(w/self._Scale,0))
                    temp_image = cv2.resize(self.InfoPhotograph._photo, (w_n, h_n), interpolation=cv2.INTER_AREA)
                else :
                    w_n = 1500
                    self._Scale = w/w_n
                    h_n = int(np.round(h/self._Scale,0))
                    temp_image = cv2.resize(self.InfoPhotograph._photo, (w_n, h_n), interpolation=cv2.INTER_AREA)

            else:
                #the image is of appropiate dimensions so no need for modification
                temp_image = self.InfoPhotograph._photo.copy()
                #pass
            
            #get the landmarks using dlib, and the and the iris 
            #using Dougman's algorithm  
            #This is done in a separate thread to prevent the gui from 
            #freezing and crashing
            

            #create worker, pass the image to the worker
            #self.landmarks = GetLandmarks(self.displayImage._opencvimage)
            self.landmarks = GetLandmarks(temp_image, self._ModelName)
            #move worker to new thread
            self.landmarks.moveToThread(self.thread_landmarks)
            #start the new thread where the landmark processing will be performed
            self.thread_landmarks.start() 
            #Connect Thread started signal to Worker operational slot method
            self.thread_landmarks.started.connect(self.landmarks.getlandmarks)
            #connect signal emmited by landmarks to a function
            self.landmarks.landmarks.connect(self.ProcessShape)
            #define the end of the thread
            self.landmarks.finished.connect(self.thread_landmarks.quit) 

            
    def ProcessShape(self, shape, numFaces, lefteye, righteye, boundingbox):
        if numFaces == 1 :
            
            if self._Scale is not 1: #in case that a smaller image was used for 
                                     #processing, then update the landmark 
                                     #position with the scale factor
                for k in range(0,68):
                    shape[k] = [int(np.round(shape[k,0]*self._Scale,0)) ,
                                int(np.round(shape[k,1]*self._Scale,0))]
                    
                for k in range(0,3):
                    lefteye[k] = int(np.round(lefteye[k]*self._Scale,0))
                    righteye[k] = int(np.round(righteye[k]*self._Scale,0))
                    
                for k in range(0,4):
                    boundingbox[k] = int(np.round(boundingbox[k]*self._Scale,0))
            
            self.InfoPhotograph._shape = shape
            self.InfoPhotograph._lefteye = lefteye
            self.InfoPhotograph._righteye = righteye
            self.InfoPhotograph._boundingbox = boundingbox

            self.InfoPhotograph._points = None
            
            #we now have all the info, emit the information to the main widget
            self.dropped.emit(self.InfoPhotograph)   
        elif numFaces == 0:
            #no face in image then shape is None
            self.InfoPhotograph._shape = None
            self.InfoPhotograph._lefteye = None
            self.InfoPhotograph._righteye = None
            self.InfoPhotograph._boundingbox = None
            #inform the user
            QtWidgets.QMessageBox.warning(self,"Warning",
                    "No face in the image.\nIf the image does contain a face plase modify the brightness and try again.",
                        QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)
        elif numFaces > 1:
            #multiple faces in image then shape is None
            self.InfoPhotograph._shape = None
            self.InfoPhotograph._lefteye = None
            self.InfoPhotograph._righteye = None
            self.InfoPhotograph._boundingbox = None
            #inform the user
            QtWidgets.QMessageBox.warning(self,"Warning",
                    "Multiple faces in the image.\nPlease load an image with a single face.",
                        QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)
          
        
 
            

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
        
        
        
        #these are the windows that will show the Emotris app
        self.show_me_rest = None
        self.show_me_smallsmile = None
        self.show_me_largesmile = None
        self.show_me_eyebrow = None
        self.show_me_eyeclosuregently = None
        self.show_me_eyeclosuretight= None
        self.show_me_puckeringlips = None
        self.show_me_dentalshow = None
        
      
        #initialize the User Interface
        self.initUI()
        
    def initUI(self):
        scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))
        
        spacerh = QtWidgets.QWidget(self)
        
        
        spacerh.setFixedSize(15,0)
        
        spacerv = QtWidgets.QWidget(self)
        spacerv.setFixedSize(0,15)
        
        #the image will be displayed in the custom ImageViewer
        self.Rest = ThumbNailViewer(self._ModelName, self._Rest)
        self.Rest.WidgetName = "Rest"
        self.Rest.dropped.connect(self.pictureDropped)
        self.Rest.setMinimumWidth(100)
        self.Rest.setMinimumHeight(150)
        RestBox = QtWidgets.QGroupBox('Rest')
        RestBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        RestLayout = QtWidgets.QGridLayout()
        RestLayout.addWidget(self.Rest,0,0,1,1)
        RestBox.setLayout(RestLayout)
  
        
        self.SmallSmile = ThumbNailViewer(self._ModelName, self._SmallSmile)
        self.SmallSmile.WidgetName = "SmallSmile"
        self.SmallSmile.dropped.connect(self.pictureDropped)
        self.SmallSmile.setMinimumWidth(100)
        self.SmallSmile.setMinimumHeight(150)
        SmallSmileBox = QtWidgets.QGroupBox('Best Smile')
        SmallSmileBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        SmallSmileLayout = QtWidgets.QGridLayout()
        SmallSmileLayout.addWidget(self.SmallSmile,0,0,1,1)
        SmallSmileBox.setLayout(SmallSmileLayout)
        
        
        self.LargeSmile = ThumbNailViewer(self._ModelName, self._LargeSmile)
        self.LargeSmile.WidgetName = "LargeSmile"
        self.LargeSmile.dropped.connect(self.pictureDropped)
        self.LargeSmile.setMinimumWidth(100)
        self.LargeSmile.setMinimumHeight(150)
        LargeSmileBox = QtWidgets.QGroupBox('Biggest Smile')
        LargeSmileBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        LargeSmileLayout = QtWidgets.QGridLayout()
        LargeSmileLayout.addWidget(self.LargeSmile,0,0,1,1)
        LargeSmileBox.setLayout(LargeSmileLayout)

        
        
        self.EyeBrow = ThumbNailViewer(self._ModelName, self._EyeBrow)
        self.EyeBrow.WidgetName = "EyeBrow"
        self.EyeBrow.dropped.connect(self.pictureDropped)
        self.EyeBrow.setMinimumWidth(100)
        self.EyeBrow.setMinimumHeight(150)
        EyeBrowBox = QtWidgets.QGroupBox('Brow Elevation')
        EyeBrowBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        EyeBrowLayout = QtWidgets.QGridLayout()
        EyeBrowLayout.addWidget(self.EyeBrow,0,0,1,1)
        EyeBrowBox.setLayout(EyeBrowLayout)
        
        self.EyeClosureGently = ThumbNailViewer(self._ModelName, self._EyeClosureGently)
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
        
        self.EyeClosureTight = ThumbNailViewer(self._ModelName, self._EyeClosureTight)
        self.EyeClosureTight.WidgetName = "EyeClosureTight"
        self.EyeClosureTight.dropped.connect(self.pictureDropped)
        self.EyeClosureTight.setMinimumWidth(100)
        self.EyeClosureTight.setMinimumHeight(150)
        EyeClosureTightBox = QtWidgets.QGroupBox('Tight Eye Closure')
        EyeClosureTightBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        EyeClosureTightLayout = QtWidgets.QGridLayout()
        EyeClosureTightLayout.addWidget(self.EyeClosureTight,0,0,1,1)
        EyeClosureTightBox.setLayout(EyeClosureTightLayout)
        
        self.PuckeringLips = ThumbNailViewer(self._ModelName, self._PuckeringLips)
        self.PuckeringLips.WidgetName = "PuckeringLips"
        self.PuckeringLips.dropped.connect(self.pictureDropped)
        self.PuckeringLips.setMinimumWidth(100)
        self.PuckeringLips.setMinimumHeight(150)
        PuckeringLipsBox = QtWidgets.QGroupBox('Pucker Lips')
        PuckeringLipsBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        PuckeringLipsLayout = QtWidgets.QGridLayout()
        PuckeringLipsLayout.addWidget(self.PuckeringLips,0,0,1,1)
        PuckeringLipsBox.setLayout(PuckeringLipsLayout)
        
        self.DentalShow = ThumbNailViewer(self._ModelName, self._DentalShow)
        self.DentalShow.WidgetName = "DentalShow"
        self.DentalShow.dropped.connect(self.pictureDropped)
        self.DentalShow.setMinimumWidth(100)
        self.DentalShow.setMinimumHeight(150)
        DentalShowBox = QtWidgets.QGroupBox('Show Teeth')
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
        ReportAction.triggered.connect(self.report_card)
        
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
#        print(photograph._file_name)
#        show_me = Emotrics(photograph, self._CalibrationType, self._CalibrationValue)
#        show_me.exec_()
#        
#        print(photograph._ID)
        
        if photograph._ID == "Rest":
            #the user wants to modify the Rest photo
                       
            #verify that the window is not already open
            if self.show_me_rest is not None: 
                self.show_me_rest.close() #if it is, close it
                
            if photograph._OpenEmotrics is True: #Emotrics should be open 
                self.show_me_rest = Emotrics(photograph, self._CalibrationType, self._CalibrationValue)
                self.show_me_rest.exec_()
                
                self._Rest._photo = photograph._photo
                self._Rest._file_name = photograph._file_name
                self._Rest._name = photograph._name
                self._Rest._extension = photograph._extension
                self._Rest._ID = photograph._ID
                self._Rest._shape = self.show_me_rest.displayImage._shape
                self._Rest._lefteye = self.show_me_rest.displayImage._lefteye
                self._Rest._righteye = self.show_me_rest.displayImage._righteye
                self._Rest._points = self.show_me_rest.displayImage._points
                self._Rest._boundingbox = self.show_me_rest.displayImage._boundingbox
                
                #modify thumbnail view to indicate that landmark position information is now avaliable
                self.Rest.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(204,255,204)))
                
                #the window is now closed, let's remove it from memory 
                self.show_me_rest = None
                
            else:
                #Emotrics doesn't need to be open, all the information is already avaliable
                self._Rest._photo = photograph._photo
                self._Rest._file_name = photograph._file_name
                self._Rest._name = photograph._name
                self._Rest._extension = photograph._extension
                self._Rest._ID = photograph._ID
                self._Rest._shape = photograph._shape
                self._Rest._lefteye = photograph._lefteye
                self._Rest._righteye = photograph._righteye
                self._Rest._points = photograph._points
                self._Rest._boundingbox = photograph._boundingbox                
            
        elif photograph._ID == "SmallSmile":
            #the user wants to modify the small smile photo
            
            #verify that the window is not already open
            if self.show_me_smallsmile is not None: 
                self.show_me_smallsmile.close() #if it is, close it
            
            if photograph._OpenEmotrics is True: #Emotrics should be open 
                self.show_me_smallsmile = Emotrics(photograph, self._CalibrationType, self._CalibrationValue)
                self.show_me_smallsmile.exec_()
                
                
                self._SmallSmile._photo = photograph._photo
                self._SmallSmile._file_name = photograph._file_name
                self._SmallSmile._name = photograph._name
                self._SmallSmile._extension = photograph._extension
                self._SmallSmile._ID = photograph._ID
                self._SmallSmile._shape = self.show_me_smallsmile.displayImage._shape
                self._SmallSmile._lefteye = self.show_me_smallsmile.displayImage._lefteye
                self._SmallSmile._righteye = self.show_me_smallsmile.displayImage._righteye
                self._SmallSmile._points = self.show_me_smallsmile.displayImage._points
                self._SmallSmile._boundingbox = self.show_me_smallsmile.displayImage._boundingbox 
                
                #modify thumbnail view to indicate that landmark position information is now avaliable
                self.SmallSmile.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(204,255,204)))
                
                #the window is now closed, let's remove it from memory 
                self.show_me_smallsmile = None
                
            else:
                #Emotrics doesn't need to be open, all the information is already avaliable
                self._SmallSmile._photo = photograph._photo
                self._SmallSmile._file_name = photograph._file_name
                self._SmallSmile._name = photograph._name
                self._SmallSmile._extension = photograph._extension
                self._SmallSmile._ID = photograph._ID
                self._SmallSmile._shape = photograph._shape
                self._SmallSmile._lefteye = photograph._lefteye
                self._SmallSmile._righteye = photograph._righteye
                self._SmallSmile._points = photograph._points
                self._SmallSmile._boundingbox = photograph._boundingbox                 
            
        elif photograph._ID == "LargeSmile":
            #the user wants to modify the large smile photo
            
            #verify that the window is not already open
            if self.show_me_largesmile is not None: 
                self.show_me_largesmile.close() #if it is, close it

            if photograph._OpenEmotrics is True: #Emotrics should be open                 
                self.show_me_largesmile = Emotrics(photograph, self._CalibrationType, self._CalibrationValue)
                self.show_me_largesmile.exec_()
                
                self._LargeSmile._photo = photograph._photo
                self._LargeSmile._file_name = photograph._file_name
                self._LargeSmile._name = photograph._name
                self._LargeSmile._extension = photograph._extension
                self._LargeSmile._ID = photograph._ID
                self._LargeSmile._shape = self.show_me_largesmile.displayImage._shape
                self._LargeSmile._lefteye = self.show_me_largesmile.displayImage._lefteye
                self._LargeSmile._righteye = self.show_me_largesmile.displayImage._righteye
                self._LargeSmile._points = self.show_me_largesmile.displayImage._points
                self._LargeSmile._boundingbox = self.show_me_largesmile.displayImage._boundingbox   
                
                #modify thumbnail view to indicate that landmark position information is now avaliable
                self.LargeSmile.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(204,255,204)))
                
                #the window is now closed, let's remove it from memory 
                self.show_me_largesmile = None
                
            else:
                #Emotrics doesn't need to be open, all the information is already avaliable
                self._LargeSmile._photo = photograph._photo
                self._LargeSmile._file_name = photograph._file_name
                self._LargeSmile._name = photograph._name
                self._LargeSmile._extension = photograph._extension
                self._LargeSmile._ID = photograph._ID
                self._LargeSmile._shape = photograph._shape
                self._LargeSmile._lefteye = photograph._lefteye
                self._LargeSmile._righteye = photograph._righteye
                self._LargeSmile._points = photograph._points
                self._LargeSmile._boundingbox = photograph._boundingbox   
            
        elif photograph._ID == "EyeBrow":
            #the user wants to modify the eye brow photo
            
            #verify that the window is not already open
            if self.show_me_eyebrow is not None: 
                self.show_me_eyebrow.close() #if it is, close it

            if photograph._OpenEmotrics is True: #Emotrics should be open                    
                self.show_me_eyebrow = Emotrics(photograph, self._CalibrationType, self._CalibrationValue)
                self.show_me_eyebrow.exec_()
                
                self._EyeBrow._photo = photograph._photo
                self._EyeBrow._file_name = photograph._file_name
                self._EyeBrow._name = photograph._name
                self._EyeBrow._extension = photograph._extension
                self._EyeBrow._ID = photograph._ID
                self._EyeBrow._shape = self.show_me_eyebrow.displayImage._shape
                self._EyeBrow._lefteye = self.show_me_eyebrow.displayImage._lefteye
                self._EyeBrow._righteye = self.show_me_eyebrow.displayImage._righteye
                self._EyeBrow._points = self.show_me_eyebrow.displayImage._points
                self._EyeBrow._boundingbox = self.show_me_eyebrow.displayImage._boundingbox 
                
                #modify thumbnail view to indicate that landmark position information is now avaliable
                self.EyeBrow.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(204,255,204)))
                
                #the window is now closed, let's remove it from memory 
                self.show_me_eyebrow = None
                
            else:
                #Emotrics doesn't need to be open, all the information is already avaliable                
                self._EyeBrow._photo = photograph._photo
                self._EyeBrow._file_name = photograph._file_name
                self._EyeBrow._name = photograph._name
                self._EyeBrow._extension = photograph._extension
                self._EyeBrow._ID = photograph._ID
                self._EyeBrow._shape = photograph._shape
                self._EyeBrow._lefteye = photograph._lefteye
                self._EyeBrow._righteye = photograph._righteye
                self._EyeBrow._points = photograph._points
                self._EyeBrow._boundingbox = photograph._boundingbox 
            
        elif photograph._ID == "EyeClosureGently":
            #the user wants to modify the gentle eye closure photo
            
            #verify that the window is not already open
            if self.show_me_eyeclosuregently is not None: 
                self.show_me_eyeclosuregently.close() #if it is, close it
            
            if photograph._OpenEmotrics is True: #Emotrics should be open  
                self.show_me_eyeclosuregently = Emotrics(photograph, self._CalibrationType, self._CalibrationValue)
                self.show_me_eyeclosuregently.exec_()
                
                self._EyeClosureGently._photo = photograph._photo
                self._EyeClosureGently._file_name = photograph._file_name
                self._EyeClosureGently._name = photograph._name
                self._EyeClosureGently._extension = photograph._extension
                self._EyeClosureGently._ID = photograph._ID
                self._EyeClosureGently._shape = self.show_me_eyeclosuregently.displayImage._shape
                self._EyeClosureGently._lefteye = self.show_me_eyeclosuregently.displayImage._lefteye
                self._EyeClosureGently._righteye = self.show_me_eyeclosuregently.displayImage._righteye
                self._EyeClosureGently._points = self.show_me_eyeclosuregently.displayImage._points
                self._EyeClosureGently._boundingbox = self.show_me_eyeclosuregently.displayImage._boundingbox  
                
                #modify thumbnail view to indicate that landmark position information is now avaliable
                self.EyeClosureGently.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(204,255,204)))
    
    
                #the window is now closed, let's remove it from memory 
                self.show_me_eyeclosuregently = None  
                
            else:
                #Emotrics doesn't need to be open, all the information is already avaliable
                
                self._EyeClosureGently._photo = photograph._photo
                self._EyeClosureGently._file_name = photograph._file_name
                self._EyeClosureGently._name = photograph._name
                self._EyeClosureGently._extension = photograph._extension
                self._EyeClosureGently._ID = photograph._ID
                self._EyeClosureGently._shape = photograph._shape
                self._EyeClosureGently._lefteye = photograph._lefteye
                self._EyeClosureGently._righteye = photograph._righteye
                self._EyeClosureGently._points = photograph._points
                self._EyeClosureGently._boundingbox = photograph._boundingbox  
     
        elif photograph._ID == "EyeClosureTight":
            #the user wants to modify the tight eye closure photo
            
            #verify that the window is not already open
            if self.show_me_eyeclosuretight is not None: 
                self.show_me_eyeclosuretight.close() #if it is, close it
                
            
            if photograph._OpenEmotrics is True: #Emotrics should be open                  
                self.show_me_eyeclosuretight = Emotrics(photograph, self._CalibrationType, self._CalibrationValue)
                self.show_me_eyeclosuretight.exec_()
                
                self._EyeClosureTight._photo = photograph._photo
                self._EyeClosureTight._file_name = photograph._file_name
                self._EyeClosureTight._name = photograph._name
                self._EyeClosureTight._extension = photograph._extension
                self._EyeClosureTight._ID = photograph._ID
                self._EyeClosureTight._shape = self.show_me_eyeclosuretight.displayImage._shape
                self._EyeClosureTight._lefteye = self.show_me_eyeclosuretight.displayImage._lefteye
                self._EyeClosureTight._righteye = self.show_me_eyeclosuretight.displayImage._righteye
                self._EyeClosureTight._points = self.show_me_eyeclosuretight.displayImage._points
                self._EyeClosureTight._boundingbox = self.show_me_eyeclosuretight.displayImage._boundingbox    
                
                #modify thumbnail view to indicate that landmark position information is now avaliable
                self.EyeClosureTight.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(204,255,204)))
                
                #the window is now closed, let's remove it from memory 
                self.show_me_eyeclosuretight = None   
                
            else:
                #Emotrics doesn't need to be open, all the information is already avaliable
                
                self._EyeClosureTight._photo = photograph._photo
                self._EyeClosureTight._file_name = photograph._file_name
                self._EyeClosureTight._name = photograph._name
                self._EyeClosureTight._extension = photograph._extension
                self._EyeClosureTight._ID = photograph._ID
                self._EyeClosureTight._shape = photograph._shape
                self._EyeClosureTight._lefteye = photograph._lefteye
                self._EyeClosureTight._righteye = photograph._righteye
                self._EyeClosureTight._points = photograph._points
                self._EyeClosureTight._boundingbox = photograph._boundingbox   
            
        elif photograph._ID == "PuckeringLips":
            #the user wants to modify the puckering lips photo
            
            #verify that the window is not already open
            if self.show_me_puckeringlips is not None: 
                self.show_me_puckeringlips.close() #if it is, close it
                
                
            if photograph._OpenEmotrics is True: #Emotrics should be open      
                self.show_me_puckeringlips = Emotrics(photograph, self._CalibrationType, self._CalibrationValue)
                self.show_me_puckeringlips.exec_()
                
                self._PuckeringLips._photo = photograph._photo
                self._PuckeringLips._file_name = photograph._file_name
                self._PuckeringLips._name = photograph._name
                self._PuckeringLips._extension = photograph._extension
                self._PuckeringLips._ID = photograph._ID
                self._PuckeringLips._shape = self.show_me_puckeringlips.displayImage._shape
                self._PuckeringLips._lefteye = self.show_me_puckeringlips.displayImage._lefteye
                self._PuckeringLips._righteye = self.show_me_puckeringlips.displayImage._righteye
                self._PuckeringLips._points = self.show_me_puckeringlips.displayImage._points
                self._PuckeringLips._boundingbox = self.show_me_puckeringlips.displayImage._boundingbox   
                
                #modify thumbnail view to indicate that landmark position information is now avaliable
                self.PuckeringLips.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(204,255,204)))
                
                #the window is now closed, let's remove it from memory 
                self.show_me_puckeringlips = None 
                
            else:
                #Emotrics doesn't need to be open, all the information is already avaliable
                self._PuckeringLips._photo = photograph._photo
                self._PuckeringLips._file_name = photograph._file_name
                self._PuckeringLips._name = photograph._name
                self._PuckeringLips._extension = photograph._extension
                self._PuckeringLips._ID = photograph._ID
                self._PuckeringLips._shape = photograph._shape
                self._PuckeringLips._lefteye = photograph._lefteye
                self._PuckeringLips._righteye = photograph._righteye
                self._PuckeringLips._points = photograph._points
                self._PuckeringLips._boundingbox = photograph._boundingbox 
            
        elif photograph._ID == "DentalShow":
            #the user wants to modify the deltal show photo
            
            #verify that the window is not already open
            if self.show_me_dentalshow is not None: 
                self.show_me_dentalshow.close() #if it is, close it
                
            if photograph._OpenEmotrics is True: #Emotrics should be open        
                self.show_me_dentalshow = Emotrics(photograph, self._CalibrationType, self._CalibrationValue)
                self.show_me_dentalshow.exec_()
                
                self._DentalShow._photo = photograph._photo
                self._DentalShow._file_name = photograph._file_name
                self._DentalShow._name = photograph._name
                self._DentalShow._extension = photograph._extension
                self._DentalShow._ID = photograph._ID
                self._DentalShow._shape = self.show_me_dentalshow.displayImage._shape
                self._DentalShow._lefteye = self.show_me_dentalshow.displayImage._lefteye
                self._DentalShow._righteye = self.show_me_dentalshow.displayImage._righteye
                self._DentalShow._points = self.show_me_dentalshow.displayImage._points
                self._DentalShow._boundingbox = self.show_me_dentalshow.displayImage._boundingbox   
                
                #modify thumbnail view to indicate that landmark position information is now avaliable
                self.DentalShow.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(204,255,204)))
                
                #the window is now closed, let's remove it from memory 
                self.show_me_dentalshow = None
                
            else:
                #Emotrics doesn't need to be open, all the information is already avaliable
                self._DentalShow._photo = photograph._photo
                self._DentalShow._file_name = photograph._file_name
                self._DentalShow._name = photograph._name
                self._DentalShow._extension = photograph._extension
                self._DentalShow._ID = photograph._ID
                self._DentalShow._shape = photograph._shape
                self._DentalShow._lefteye = photograph._lefteye
                self._DentalShow._righteye = photograph._righteye
                self._DentalShow._points = photograph._points
                self._DentalShow._boundingbox = photograph._boundingbox  
            
    def report_card(self):
        
        if self._Rest._photo is None or self._SmallSmile._photo is None or self._LargeSmile._photo is None or self._EyeBrow._photo is None or self._EyeClosureGently._photo is None or self._EyeClosureTight._photo is None or self._DentalShow._photo is None:
            
            QtWidgets.QMessageBox.warning(self,"Warning",
                    "Some images haven't been processed",
                        QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)
        
#        QtWidgets.QMessageBox.warning(self,"Warning",
#                    'hola',
#                        QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)

    
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
        
        
    def closeEvent(self, event):
        event.accept()

        #verify if any of the Emotrics windows in still open
        if self.show_me_rest is not None: 
            self.show_me_rest.close() #if it is, close it

        if self.show_me_smallsmile is not None: 
            self.show_me_smallsmile.close() #if it is, close it

        if self.show_me_largesmile is not None: 
            self.show_me_largesmile.close() #if it is, close it

        if self.show_me_eyebrow is not None: 
            self.show_me_eyebrow.close() #if it is, close it

        if self.show_me_eyeclosuregently is not None: 
            self.show_me_eyeclosuregently.close() #if it is, close it

        if self.show_me_eyeclosuretight is not None: 
            self.show_me_eyeclosuretight.close() #if it is, close it

        if self.show_me_puckeringlips is not None: 
            self.show_me_puckeringlips.close() #if it is, close it

        if self.show_me_dentalshow is not None: 
            self.show_me_dentalshow.close() #if it is, close it        

            
if __name__ == '__main__':
    
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    
    app.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
  
        
    GUI = window()
    GUI.show()
    app.exec_()
            
            
            

                        

    


        