# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:31:28 2018

@author: guarind
"""

import cv2
import os
import sys
import numpy as np

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore


from utilities import get_info_from_txt
from ProcessLandmarks import GetLandmarks


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
            
    def picture_loaded(self, local_address):
        
        pixmap = QtGui.QPixmap(local_address)
        self.setPhoto(pixmap)
        self._hasImage = True  #indicate that there is an image
        self._ImageAddress = os.path.normpath(local_address) #store the image address in a class variable
        
        file_name,extension = os.path.splitext(local_address)
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
#            self.InfoPhotograph._ID = self.WidgetName
#            
#            if self.WidgetName == "Rest":
#                self.InfoPhotograph._Tag = "Rest"
#            elif self.WidgetName == "SmallSmile":
#                self.InfoPhotograph._Tag = "Best Smile"
#            elif self.WidgetName == "LargeSmile":
#                self.InfoPhotograph._Tag = "Biggest Smile"
#            elif self.WidgetName == "EyeBrow":   
#                self.InfoPhotograph._Tag = "Brow Elevation"
#            elif self.WidgetName == "EyeClosureGently":   
#                self.InfoPhotograph._Tag = "Gentle Eye Closure"
#            elif self.WidgetName == "EyeClosureTight": 
#                self.InfoPhotograph._Tag = "Tight Eye Closure"
#            elif self.WidgetName == "PuckeringLips":    
#                self.InfoPhotograph._Tag = "Pucker Lips"
#            elif self.WidgetName == "DentalShow":     
#                self.InfoPhotograph._Tag = "Show Teeth"
    
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
          
        
 
            