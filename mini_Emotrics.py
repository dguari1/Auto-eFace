# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 22:17:26 2017

@author: GUARIND
"""

import os 
import sys
import cv2
import numpy as np

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore



#from results_window import ShowResults
#from results_window import CustomTabResult
#
from ImageViewerandProcess import ImageViewer
#from patient_window import CreatePatient
#
#
#from measurements import get_measurements_from_data
#
#from utilities import estimate_lines
#from utilities import get_info_from_txt
##from utilities import get_landmarks
##from utilities import get_pupil_from_image
#from utilities import mark_picture
#from utilities import save_snaptshot_to_file
#from utilities import save_txt_file
#from utilities import save_xls_file
#from utilities import save_xls_file_patient
#
#from ProcessLandmarks import GetLandmarks



"""
This is the main window of the program, it contains a ToolBar and a GraphicsView objects. 

The toolbar includes actions for:
    - Load Image: Loads an image and localizes the landmarks and iris in the image. 
    If the image is not a single face then it skips the landmark and iris 
    localization. If the landmark information is available in a txt file then 
    the program uses this to place the landmarks and skips the automatic landmark
    localization.
    
    - Create Patient: Opens up a new window where the user can load two images 
    that will be compared, the landmark and iris localization is perform during
    the image loading so that if the image is not a single face the user will be
    informed and won't be allowed to continue. The only ways to close the new 
    window are by loading to valid images (single faces) or cancelling. In this
    window is possible to assign an ID to the patient (by default is the current
    date) and to each photo. 
    Future improvements might include facial recognition to verify that both 
    photos are from the same patient 
    
    - Change photo: allows to move between the patient photos. It is un-active  
    if there is no patient. Once the patient is created this action becomes 
    active
    
    - Fit image to window: Fits the image to the current size of the window. 
    Useful after zoom-in the picture to go back to full-view in one click
    
    - Match iris diameter: Makes sure that both iris have the same diameter by 
    enlarging the smaller circle fitted to the iris. Is usefull when one eye is 
    closed and is difficul to properly find the iris size.
    
    - Find face center: It fits a line connecting the center of both iris and 
    a new, perperdicular line in the middle. It is usefull to divide the 
    face vertically. 
    
    - Toggle landmarks: It toggles on or off the landmarks from the face, is 
    usefull if you want to see the face without anything added to it.
    
    - Facial metrics: It opens up a new window displaying a set of important 
    facial metrics. In there is possible to see a description and a graphical 
    explanation of each metric. It has two different modes: If a single image 
    is being processed, the new window will present a table containing the 
    metrics for both sides of the face, the absolute difference and a percent
    difference based on the non-paralyzed side measurements. If a patient is
    being analyzed (two photos) the new window contains three tabs, one for each 
    image and a third one computing the variation in the metrics between both
    images. This is useful to compare pre and post-operative cases.
    
    - Save results: Produces two files in the folder where the image is located. 
    One text (.txt) file containing the landmarks information, and an excel (.xls)
    file containing the facial metrics. If the a patient is being processed (two
    images) then the excel file contains information about each image and the 
    difference. The excel file will inherit the name of the image file or the 
    patient ID depending on the mode.
    
    - Save current view: Saves the current view as png or jpg file. 
    
    - Settings (not implemented yet): Allows for further customization of the 
    software. It facilitates the selection of scale (currently we assume that 
    the iris diamater is 11.77mm), and the diameter and color of the landmaks
    
    - Exit: Exits the program 
"""


class Emotrics(QtWidgets.QDialog):
    
    def __init__(self, parent = None):
        super(Emotrics, self).__init__(parent)
        #self.setGeometry(5,60,700,500)
        self.setWindowTitle('Emotrics')
        scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'meei_3WR_icon.ico'))
        
        self._new_window = None
        self._file_name = None
        self._Patient = None
        self._tab1_results = None
        self._tab2_results = None         
        self._tab3_results = None    
        self._toggle_landmaks = True
        self._toggle_lines = True
        
        
        self._Scale = 1  #this variable carries the scale of the image if it 
                        #needs to be resized, if Scale = 1 then the origina 
                        #image was used for processing. If Scale > 1 then 
                        #the original image was too large and a resized image
                        #was used for processing
        
        
        # create Thread  to take care of the landmarks and iris estimation   
        self.thread_landmarks = QtCore.QThread()  # no parent!
      
        #initialize the User Interface
        self.initUI()
        
    def initUI(self):
        #local directory
        scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))

        #image
        #read the image from file        
        img_Qt = QtGui.QImage(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'Facial-Nerve-Center.jpg')
        img_show = QtGui.QPixmap.fromImage(img_Qt)
        
        #the image will be displayed in the custom ImageViewer
        self.displayImage = ImageViewer()      
        self.displayImage.setPhoto(img_show)    
        
        #toolbar                 
        fitAction = QtWidgets.QAction('Fit image to window', self)
        fitAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'fit_to_size_icon.png'))
#        fitAction.triggered.connect(self.displayImage.show_entire_image)
        
        eyeAction = QtWidgets.QAction('Match iris diameter', self)
        eyeAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'eye_icon.png'))
#        eyeAction.triggered.connect(self.match_iris)
        
        centerAction = QtWidgets.QAction('Find face center', self)
        centerAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'center_icon.png'))
#        centerAction.triggered.connect(self.face_center)
        
        toggleAction = QtWidgets.QAction('Toggle landmarks', self)
        toggleAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'toggle-icon.png'))
#        toggleAction.triggered.connect(self.toggle_landmarks)
        
        measuresAction = QtWidgets.QAction('Facial metrics', self)
        measuresAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'ruler_icon.png'))
#        measuresAction.triggered.connect(self.create_new_window)
        
        saveAction = QtWidgets.QAction('Save results', self)
        saveAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'save_icon.png'))
#        saveAction.triggered.connect(self.save_results)
        
        snapshotAction = QtWidgets.QAction('Save current view', self)
        snapshotAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'snapshot_icon.png'))
#        snapshotAction.triggered.connect(self.save_snapshot)
        
        exitAction = QtWidgets.QAction('Exit', self)
        exitAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'exit_icon.png'))
#        exitAction.triggered.connect(self.close_app)
                
        
        #create the toolbar and add the actions 
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.addActions((fitAction, eyeAction, centerAction, toggleAction,
                                 measuresAction, snapshotAction, saveAction,  exitAction))
        
        #set the size of each icon to 50x50
        self.toolBar.setIconSize(QtCore.QSize(50,50))
        
        for action in self.toolBar.actions():
            widget = self.toolBar.widgetForAction(action)
            widget.setFixedSize(50, 50)
           
        self.toolBar.setMinimumSize(self.toolBar.sizeHint())
        self.toolBar.setStyleSheet('QToolBar{spacing:5px;}')

        
        #the main window consist of the toolbar and the ImageViewer
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolBar)
        layout.addWidget(self.displayImage)
        self.setLayout(layout)
        

        
        #self.show()
        
#    def match_iris(self):
#        #make both iris have the same diameter as the bigger one
#        if self.displayImage._lefteye is not None :
#            if self.displayImage._lefteye[2] < self.displayImage._righteye[2]:
#                self.displayImage._lefteye[2] = self.displayImage._righteye[2]
#            elif self.displayImage._lefteye[2] > self.displayImage._righteye[2]:
#                self.displayImage._righteye[2] = self.displayImage._lefteye[2]
#            elif self.displayImage._lefteye[2] == self.displayImage._righteye[2]:
#                pass
#            
#            self._toggle_lines = True 
#            self.displayImage._points = None
#            self.displayImage.set_update_photo()  
#        
#        
#    def face_center(self):
#        #find a line connecting the center of both iris and then fit a perperdicular
#        #line in the middle
#        if self.displayImage._shape is not None:
#            
#            if self._toggle_lines == True:
#                self._toggle_lines = False
#                points =  estimate_lines(self.displayImage._opencvimage, 
#                                     self.displayImage._lefteye, 
#                                     self.displayImage._righteye)
#                self.displayImage._points = points
#                self.displayImage.set_update_photo()
#            else:
#                self.displayImage._points = None
#                self.displayImage.set_update_photo()
#                self._toggle_lines = True    
#            
#            
#    def load_file(self):
#        
#        #load a file using the widget
#        name,_ = QtWidgets.QFileDialog.getOpenFileName(
#                self,'Load Image',
#                '',"Image files (*.png *.jpg *.jpeg *.tif *.tiff *.PNG *.JPG *.JPEG *.TIF *.TIFF)")
#        
#        if not name:
#            pass
#        else:
#            #the user will load an single image so get rid of Patient and the
#            # changephotoAction in the toolbar
#            self._Patient = None
#            self.changephotoAction.setEnabled(False)
#            
#            #if windows then transform / to \ (python stuffs)
#            name = os.path.normpath(name)
#            self._file_name = name
#            #if the measurements window is open then close it
#            if self._new_window is not None:
#                self._new_window.close()
#            #load image
#            self.displayImage._opencvimage = cv2.imread(name)
#
#            #if the photo was already processed then get the information for the
#            #txt file, otherwise process the photo using the landmark ans pupil
#            #localization algorithms 
#            file_txt=name[:-4]
#            file_txt = (file_txt + '.txt')
#            if os.path.isfile(file_txt):
#                shape,lefteye,righteye,boundingbox = get_info_from_txt(file_txt)
#                self.displayImage._lefteye = lefteye
#                self.displayImage._righteye = righteye 
#                self.displayImage._shape = shape
#                self.displayImage._boundingbox = boundingbox
#                self.displayImage._points = None
#                self.displayImage.update_view()
#            else:
#                #if the image is too large then it needs to be resized....
#                h,w,d = self.displayImage._opencvimage.shape
#
#                #if the image is too big then we need to resize it so that the landmark 
#                #localization process can be performed in a reasonable time 
#                self._Scale = 1  #start from a clear initial scale
#                if h > 1500 or w > 1500 :
#                    if h >= w :
#                        h_n = 1500
#                        self._Scale = h/h_n
#                        w_n = int(np.round(w/self._Scale,0))
#                        #self.displayImage._opencvimage=cv2.resize(self.displayImage._opencvimage, (w_n, h_n), interpolation=cv2.INTER_AREA)
#                        temp_image = cv2.resize(self.displayImage._opencvimage, (w_n, h_n), interpolation=cv2.INTER_AREA)
#                        #self._image = image
#                    else :
#                        w_n = 1500
#                        self._Scale = w/w_n
#                        h_n = int(np.round(h/self._Scale,0))
#                        #self.displayImage._opencvimage=cv2.resize(self.displayImage._opencvimage, (w_n, h_n), interpolation=cv2.INTER_AREA)
#                        temp_image = cv2.resize(self.displayImage._opencvimage, (w_n, h_n), interpolation=cv2.INTER_AREA)
#                        #self._image = image     
#                 
#                    
##                    #now that the image has been reduced, ask the user if the image 
##                    #should be saved for continue the processing, otherwise the 
##                    #processing cannot continue with the large image
##                    
##                    #get the image name (separete it from the path)
##                    delimiter = os.path.sep
##                    split_name=name.split(delimiter)
##            
##                    #the variable 'name' contains the file name and the path, we now
##                    #get the file name and assign it to the photo object
##                    file_name = split_name[-1]
##                    new_file_name = file_name[:-4]+'_small.png'
##                    
##                    choice = QtWidgets.QMessageBox.information(self, 'Large Image', 
##                            'The image is too large to process.\n\nPressing OK will create a new file\n%s\nin the current folder. This file will be used for processing.\nOtherwise, click Close to finalize the App.'%new_file_name, 
##                            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Close, QtWidgets.QMessageBox.Ok)
##
##                    if choice == QtWidgets.QMessageBox.Close :
##                        self.close()
##                        app.exec_()
##                    else:
##                        #create a new, smaller image and use that for processing
##                        name = name[:-4]+'_small.png'
##                        self._file_name = name
##                        cv2.imwrite(name,self.displayImage._opencvimage)
#                else:
#                    #the image is of appropiate dimensions so no need for modification
#                    temp_image = self.displayImage._opencvimage.copy()
#                    #pass
#                
#                #get the landmarks using dlib, and the and the iris 
#                #using Dougman's algorithm  
#                #This is done in a separate thread to prevent the gui from 
#                #freezing and crashing
#                
#
#                #create worker, pass the image to the worker
#                #self.landmarks = GetLandmarks(self.displayImage._opencvimage)
#                self.landmarks = GetLandmarks(temp_image)
#                #move worker to new thread
#                self.landmarks.moveToThread(self.thread_landmarks)
#                #start the new thread where the landmark processing will be performed
#                self.thread_landmarks.start() 
#                #Connect Thread started signal to Worker operational slot method
#                self.thread_landmarks.started.connect(self.landmarks.getlandmarks)
#                #connect signal emmited by landmarks to a function
#                self.landmarks.landmarks.connect(self.ProcessShape)
#                #define the end of the thread
#                self.landmarks.finished.connect(self.thread_landmarks.quit) 
#
#            
#    def ProcessShape(self, shape, numFaces, lefteye, righteye, boundingbox):
#        if numFaces == 1 :
#            
#            if self._Scale is not 1: #in case that a smaller image was used for 
#                                     #processing, then update the landmark 
#                                     #position with the scale factor
#                for k in range(0,68):
#                    shape[k] = [int(np.round(shape[k,0]*self._Scale,0)) ,
#                                int(np.round(shape[k,1]*self._Scale,0))]
#                    
#                for k in range(0,3):
#                    lefteye[k] = int(np.round(lefteye[k]*self._Scale,0))
#                    righteye[k] = int(np.round(righteye[k]*self._Scale,0))
#                    
#                for k in range(0,4):
#                    boundingbox[k] = int(np.round(boundingbox[k]*self._Scale,0))
#            
#            self.displayImage._shape = shape
#            self.displayImage._lefteye = lefteye
#            self.displayImage._righteye = righteye
#            self.displayImage._boundingbox = boundingbox
#            
#            #
#            self.displayImage._points = None
#        elif numFaces == 0:
#            #no face in image then shape is None
#            self.displayImage._shape = None
#            #inform the user
#            QtWidgets.QMessageBox.warning(self,"Warning",
#                    "No face in the image.\nIf the image does contain a face plase modify the brightness and try again.",
#                        QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)
#        elif numFaces > 1:
#            #multiple faces in image then shape is None
#            self.displayImage._shape = None
#            #inform the user
#            QtWidgets.QMessageBox.warning(self,"Warning",
#                    "Multiple faces in the image.\nPlease load an image with a single face.",
#                        QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)
#          
#        self.displayImage.update_view()
#            
#            
#    def toggle_landmarks(self):
#        #Hide - show the landmarks 
#        if self._toggle_landmaks is True:
#            self._toggle_landmaks = False
#            self.displayImage.set_update_photo(self._toggle_landmaks)
#        elif self._toggle_landmaks is False:
#            self._toggle_landmaks = True
#            self.displayImage.set_update_photo(self._toggle_landmaks)
#                        
#            
#    def save_snapshot(self):
#        #save the current view 
#        if self.displayImage._opencvimage is not None:
#            proposed_name = self._file_name[:-4]+'-landmarks'
#            name,_ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',proposed_name, 'png (*.png);;jpg (*.jpg);; jpeg (*.jpeg)')
#            if not name:
#                pass
#            else:
#                #if shape then add shape to image
#                temp_image  = self.displayImage._opencvimage.copy()
#    
#                #draw 68 landmark points       
#                if self.displayImage._shape is not None:
#                   temp_image = mark_picture(temp_image, self.displayImage._shape, self.displayImage._lefteye, self.displayImage._righteye, self.displayImage._points)
#                   
#                save_snaptshot_to_file(temp_image,name)
#
#    def save_results(self):
#        #save the results in a txt and xls files. There are two modes, one if 
#        #there is no patient and another is the is a patient (two photos)
#        if self._Patient is None: #this implies that there is a single photo
#            if self._file_name is not None:
#                if self.displayImage._shape is not None:
#                    save_txt_file(self._file_name, self.displayImage._shape, self.displayImage._lefteye, self.displayImage._righteye, self.displayImage._boundingbox)
#                    MeasurementsLeft, MeasurementsRight, MeasurementsDeviation, MeasurementsPercentual = get_measurements_from_data(self.displayImage._shape, self.displayImage._lefteye, self.displayImage._righteye)
#                    save_xls_file(self._file_name, MeasurementsLeft, MeasurementsRight, MeasurementsDeviation, MeasurementsPercentual)
#        else:#this implies that the user created a patient and wants to analize two photos
#            save_txt_file(self._Patient.FirstPhoto._file_name, self._Patient.FirstPhoto._shape, self._Patient.FirstPhoto._lefteye, self._Patient.FirstPhoto._righteye,  self._Patient.FirstPhoto._boundingbox)    
#            save_txt_file(self._Patient.SecondPhoto._file_name, self._Patient.SecondPhoto._shape, self._Patient.SecondPhoto._lefteye, self._Patient.SecondPhoto._righteye, self._Patient.SecondPhoto._boundingbox)
#            save_xls_file_patient(self._file_name,self._Patient)

            
                
            
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
        #we need to close all the windows before closing the program  
        if self._new_window is not None:
            self._new_window.close()
        event.accept()
        

if __name__ == '__main__':
    
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    
    app.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
        
    GUI = window()
    #GUI.show()
    app.exec_()
    

