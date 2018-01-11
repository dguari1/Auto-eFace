# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 18:41:24 2017

@author: Diego L.Guarin -- diego_guarin at meei.harvard.edu
"""
import os 
import sys
import cv2

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore



from results_window import ShowResults
from results_window import CustomTabResult

from ImageViewerandProcess import ImageViewer

from measurements import get_measurements_from_data

from utilities import estimate_lines
from utilities import get_info_from_txt
#from utilities import get_landmarks
#from utilities import get_pupil_from_image
from utilities import mark_picture
from utilities import save_txt_file

from save_window import SaveWindow




"""
This is the main window of the program, it contains a ToolBar and a GraphicsView objects. 

The toolbar includes actions for:
    
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
    difference based on the non-paralyzed side measurements. 
    
    - Save results: Produces two files in the selected folder. 
    One text (.txt) file containing the landmarks information, and an excel (.xls)
    file containing the facial metrics. 
    
    - Save current view: Saves the current view as png or jpg file. 
    
    - Exit: Exits the program 
"""


class Emotrics(QtWidgets.QDialog):
    
    def __init__(self, photograph, CalibrationType, CalibrationValue):
        super(Emotrics, self).__init__()
        #self.setGeometry(5,60,700,500)
        self.setWindowTitle(photograph._Tag)
        scriptDir = os.getcwd()#os.path.dirname(os.path.realpath(sys.argv[0]))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'meei_3WR_icon.ico'))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() |
                              QtCore.Qt.WindowSystemMenuHint |
                              QtCore.Qt.WindowMinMaxButtonsHint)
        
        self._file_name = photograph._file_name
        self._new_window = None
        self._tab1_results = None
        self._toggle_landmaks = True
        self._toggle_lines = True
        
        self._photograph = photograph
        
        
        self._Scale = 1  #this variable carries the scale of the image if it 
                        #needs to be resized, if Scale = 1 then the original 
                        #image was used for processing. If Scale > 1 then 
                        #the original image was too large and a resized image
                        #was used for processing
        
        
        # create Thread  to take care of the landmarks and iris estimation   
        #self.thread_landmarks = QtCore.QThread()  # no parent!
        
        self._CalibrationType = CalibrationType
        self._CalibrationValue = CalibrationValue
      
        #initialize the User Interface
        self.initUI()
        
    def initUI(self):
        #local directory
        scriptDir = os.getcwd()

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
        fitAction.triggered.connect(self.displayImage.show_entire_image)
        
        eyeAction = QtWidgets.QAction('Match iris diameter', self)
        eyeAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'eye_icon.png'))
        eyeAction.triggered.connect(self.match_iris)

        eyeLoad = QtWidgets.QAction('Import iris position and diameter', self)
        eyeLoad.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'eye_icon_import.png'))
        eyeLoad.triggered.connect(self.load_iris)
        
        centerAction = QtWidgets.QAction('Find face center', self)
        centerAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'center_icon.png'))
        centerAction.triggered.connect(self.face_center)
        
        toggleAction = QtWidgets.QAction('Toggle landmarks', self)
        toggleAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'toggle-icon.png'))
        toggleAction.triggered.connect(self.toggle_landmarks)
        
        measuresAction = QtWidgets.QAction('Facial metrics', self)
        measuresAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'ruler_icon.png'))
        measuresAction.triggered.connect(self.create_new_window)
        
        saveAction = QtWidgets.QAction('Save results', self)
        saveAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'save_icon.png'))
        saveAction.triggered.connect(self.save_results)
        
        snapshotAction = QtWidgets.QAction('Save current view', self)
        snapshotAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'snapshot_icon.png'))
        snapshotAction.triggered.connect(self.save_snapshot)
                
        exitAction = QtWidgets.QAction('Exit', self)
        exitAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'exit_icon.png'))
        exitAction.triggered.connect(self.close_app)
                
        
        #create the toolbar and add the actions 
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.addActions((fitAction, eyeAction, eyeLoad,centerAction, toggleAction,
                                 measuresAction, snapshotAction, saveAction, exitAction))
        
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
        

        
        self.load_file(self._photograph)
        self.displayImage.update_view()      
        self.show()
        
        
    def create_new_window(self):
        #this creates a new window to display all the facial metrics, there 

        
        if self.displayImage._shape is not None:
            #if the measurements window is already open then close it
            if self._new_window is not None:
                self._new_window.close()
                self._new_window = None
            
            #compute the facial metrics using the landmarks 
            MeasurementsLeft, MeasurementsRight, MeasurementsDeviation, MeasurementsPercentual = get_measurements_from_data(self.displayImage._shape, self.displayImage._lefteye, self.displayImage._righteye, self._CalibrationType, self._CalibrationValue)
            
            #send all the information the the appropiate places in the window 
            self._tab1_results  =  CustomTabResult()
            
            #filling t_new_window_tab1_results he info for the right
            self._tab1_results._CE_right.setText('{0:.2f}'.format(MeasurementsRight.CommissureExcursion))
            self._tab1_results._SA_right.setText('{0:.2f}'.format(MeasurementsRight.SmileAngle))
            self._tab1_results._DS_right.setText('{0:.2f}'.format(MeasurementsRight.DentalShow))
            self._tab1_results._MRD1_right.setText('{0:.2f}'.format(MeasurementsRight.MarginalReflexDistance1))
            self._tab1_results._MRD2_right.setText('{0:.2f}'.format(MeasurementsRight.MarginalReflexDistance2))
            self._tab1_results._BH_right.setText('{0:.2f}'.format(MeasurementsRight.BrowHeight))

            
            #filling the info for the left
            self._tab1_results._CE_left.setText('{0:.2f}'.format(MeasurementsLeft.CommissureExcursion))
            self._tab1_results._SA_left.setText('{0:.2f}'.format(MeasurementsLeft.SmileAngle))
            self._tab1_results._DS_left.setText('{0:.2f}'.format(MeasurementsLeft.DentalShow))
            self._tab1_results._MRD1_left.setText('{0:.2f}'.format(MeasurementsLeft.MarginalReflexDistance1))
            self._tab1_results._MRD2_left.setText('{0:.2f}'.format(MeasurementsLeft.MarginalReflexDistance2))
            self._tab1_results._BH_left.setText('{0:.2f}'.format(MeasurementsLeft.BrowHeight))
            
            #deviation
            self._tab1_results._CE_dev.setText('{0:.2f}'.format(MeasurementsDeviation.CommissureExcursion))
            self._tab1_results._SA_dev.setText('{0:.2f}'.format(MeasurementsDeviation.SmileAngle))
            self._tab1_results._MRD1_dev.setText('{0:.2f}'.format(MeasurementsDeviation.MarginalReflexDistance1))
            self._tab1_results._MRD2_dev.setText('{0:.2f}'.format(MeasurementsDeviation.MarginalReflexDistance2))
            self._tab1_results._BH_dev.setText('{0:.2f}'.format(MeasurementsDeviation.BrowHeight))
            self._tab1_results._DS_dev.setText('{0:.2f}'.format(MeasurementsDeviation.DentalShow))
            self._tab1_results._CH_dev.setText('{0:.2f}'.format(MeasurementsDeviation.CommisureHeightDeviation))
            self._tab1_results._UVH_dev.setText('{0:.2f}'.format(MeasurementsDeviation.UpperLipHeightDeviation))
            self._tab1_results._LVH_dev.setText('{0:.2f}'.format(MeasurementsDeviation.LowerLipHeightDeviation))
            
            self._tab1_results._CE_dev_p.setText('{0:.2f}'.format(MeasurementsPercentual.CommissureExcursion))
            self._tab1_results._SA_dev_p.setText('{0:.2f}'.format(MeasurementsPercentual.SmileAngle))
            self._tab1_results._MRD1_dev_p.setText('{0:.2f}'.format(MeasurementsPercentual.MarginalReflexDistance1))
            self._tab1_results._MRD2_dev_p.setText('{0:.2f}'.format(MeasurementsPercentual.MarginalReflexDistance2))
            self._tab1_results._BH_dev_p.setText('{0:.2f}'.format(MeasurementsPercentual.BrowHeight))
            self._tab1_results._DS_dev_p.setText('{0:.2f}'.format(MeasurementsPercentual.DentalShow))
            
            
            delimiter = os.path.sep
            temp=self._file_name.split(delimiter)
            photo_name=temp[-1]
            photo_name=photo_name[0:-4]
            self._tab1_results._tab_name=photo_name
            
            
            #say to the window that presents the results that there is only 1 tab
            self._new_window = ShowResults(self._tab1_results)
            #show the window with the results 
            self._new_window.show()
                
                    
                   
        
    def match_iris(self):
        #make both iris have the same diameter as the bigger one
        if self.displayImage._lefteye is not None :
            if self.displayImage._lefteye[2] < self.displayImage._righteye[2]:
                self.displayImage._lefteye[2] = self.displayImage._righteye[2]
            elif self.displayImage._lefteye[2] > self.displayImage._righteye[2]:
                self.displayImage._righteye[2] = self.displayImage._lefteye[2]
            elif self.displayImage._lefteye[2] == self.displayImage._righteye[2]:
                pass
            
            self._toggle_lines = True 
            self.displayImage._points = None
            self.displayImage.set_update_photo()  
        
        
    def face_center(self):
        #find a line connecting the center of both iris and then fit a perperdicular
        #line in the middle
        if self.displayImage._shape is not None:
            
            if self._toggle_lines == True:
                self._toggle_lines = False
                points =  estimate_lines(self.displayImage._opencvimage, 
                                     self.displayImage._lefteye, 
                                     self.displayImage._righteye)
                self.displayImage._points = points
                self.displayImage.set_update_photo()
            else:
                self.displayImage._points = None
                self.displayImage.set_update_photo()
                self._toggle_lines = True    
            
            
    def load_file(self, photograph):
        
        if self._new_window is not None:
            self._new_window.close()
            
        
        self.displayImage._opencvimage = self._photograph._photo
        self.displayImage._lefteye = self._photograph._lefteye
        self.displayImage._righteye = self._photograph._righteye
        self.displayImage._shape = self._photograph._shape
        self.displayImage._boundingbox = self._photograph._boundingbox
        self.displayImage._points = self._photograph._points
        self.displayImage.update_view()
        

    
    def load_iris(self):
        #load a file using the widget
        name,_ = QtWidgets.QFileDialog.getOpenFileName(
                self,'Load Iris Position and Diameter',
                '',"Image files (*.png *.jpg *.jpeg *.tif *.tiff *.PNG *.JPG *.JPEG *.TIF *.TIFF)")
        
        if not name:
            pass
        else:
            #if windows then transform / to \ (python stuffs)
            name = os.path.normpath(name)
            #if the measurements window is open then close it, the measures will be updated with the new eyes position
            if self._new_window is not None:
                self._new_window.close()

            #if the photo was already processed then get the information for the
            #txt file, otherwise process the photo using the landmark ans pupil
            #localization algorithms 
            file_txt=name[:-4]
            file_txt = (file_txt + '.txt')
            if os.path.isfile(file_txt):
                shape,lefteye,righteye,_ = get_info_from_txt(file_txt)
                
                dx_left = lefteye[0]-shape[27,0]
                dy_left = shape[27,1]-lefteye[1]
                
                dx_right = shape[27,0]-righteye[0]
                dy_right = shape[27,1]-righteye[1]
                
                self.displayImage._lefteye = [self.displayImage._shape[27,0]+dx_left, self.displayImage._shape[27,1]-dy_left,lefteye[2]]
                self.displayImage._righteye = [self.displayImage._shape[27,0]-dx_right, self.displayImage._shape[27,1]-dy_right,lefteye[2]]
                self.displayImage.set_update_photo()
                
            else:
                QtWidgets.QMessageBox.warning(self,"Warning",
                    "Iris information for this photograph is not avaliable",
                        QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)
                
#                self.displayImage._lefteye = lefteye
#                self.displayImage._righteye = righteye 
#                self.displayImage.set_update_photo()
            
        
            
    def toggle_landmarks(self):
        #Hide - show the landmarks 
        if self._toggle_landmaks is True:
            self._toggle_landmaks = False
            self.displayImage.set_update_photo(self._toggle_landmaks)
        elif self._toggle_landmaks is False:
            self._toggle_landmaks = True
            self.displayImage.set_update_photo(self._toggle_landmaks)
                        
            
    def save_snapshot(self):
        #save the current view 
        if self.displayImage._opencvimage is not None:
            proposed_name = self._file_name[:-4]+'-landmarks'
            name,_ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',proposed_name, 'png (*.png);;jpg (*.jpg);; jpeg (*.jpeg)')
            print('hola')
            if not name:
                pass
            else:
                #if shape then add shape to image
                temp_image  = self.displayImage._opencvimage.copy()
    
                #draw 68 landmark points       
                if self.displayImage._shape is not None:
                   temp_image = mark_picture(temp_image, self.displayImage._shape, self.displayImage._lefteye, self.displayImage._righteye, self.displayImage._points)
                   
                cv2.imwrite(temp_image,name)

    def save_results(self):
        #save the results in a txt and xls files. 
        if self._file_name is not None:
            if self.displayImage._shape is not None:
                MeasurementsLeft, MeasurementsRight, MeasurementsDeviation, MeasurementsPercentual = get_measurements_from_data(self.displayImage._shape, self.displayImage._lefteye, self.displayImage._righteye, self._CalibrationType, self._CalibrationValue)
#                    
                temp = SaveWindow(self, self._file_name, self._photograph._Tag, MeasurementsLeft, MeasurementsRight, MeasurementsDeviation, MeasurementsPercentual)
                temp.exec_()    
                
                if temp._acceptSave:
                
                    save_txt_file(self._file_name, self.displayImage._shape, self.displayImage._lefteye, self.displayImage._righteye, self.displayImage._boundingbox)


            

            
    def close_app(self):  
        
        self.close()
        
    def closeEvent(self, event):
        #we need to close all the windows before closing the program  
        if self._new_window is not None:
            self._new_window.close()
        event.accept()
        self.close()
        

if __name__ == '__main__':
    
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    
    app.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
        
    GUI = Emotrics()
    GUI.show()
    app.exec_()
    
