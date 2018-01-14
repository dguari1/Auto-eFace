# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 12:54:17 2017

@author: Diego L.Guarin -- diego_guarin at meei.harvard.edu
"""

import os
import cv2
import numpy as np
import time
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QGridLayout, QFileDialog, QDialog, QComboBox


from utilities import get_info_from_txt
from Compute_eFace import Compute_eFace


"""

"""

 
        
class MyLineEdit(QLineEdit):
    #I created a custom LineEdit object that will clear its content when selected
    #is used for the Patient ID which is initialized by default to the current date
    def __init__(self, parent=None):
        super(MyLineEdit, self).__init__(parent)

    def mousePressEvent(self, event):
        self.clear()   

        
class ReportCardInit(QDialog):
    
    def __init__(self, parent,Patient):
        super(ReportCardInit, self).__init__(parent)
        
        self.parent = parent
        
        self._Patient = Patient
        
        self.initUI()
        
    def initUI(self):
        
        self.setWindowTitle('Report Card')
        scriptDir = os.getcwd()#os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'report_card.ico'))
        
        self.main_Widget = QtWidgets.QWidget(self)
        
        spacerh = QtWidgets.QWidget(self)
        spacerh.setFixedSize(20,0)
        
        spacerv = QtWidgets.QWidget(self)
        spacerv.setFixedSize(0,20)
        
        
        newfont = QtGui.QFont("Times", 12)
        
        Patient_ID_label = QLabel('Patient ID:')
        Patient_ID_label.setFont(newfont)
        self._Patient_ID = MyLineEdit(self)
        if self._Patient._Patient_ID is not None:
            self._Patient_ID.setText(self._Patient._Patient_ID)
        else:
            self._Patient_ID.setText(time.strftime("%d-%m-%Y"))
        self._Patient_ID.setFont(newfont)
        


        MRN_label = QLabel('Medical Record Number:')
        MRN_label.setFont(newfont)
        self._MRN = QLineEdit(self)
        if self._Patient._MRN is not None:
            self._MRN.setText(self._Patient._MRN)
        self._MRN.setFont(newfont)
        
        
        Disease_label = QLabel('Medical Condition:')
        Disease_label.setFont(newfont)
        self._diease = QLineEdit(self)
        self._diease.setFont(newfont)
        
        
        HealthySide_label = QLabel('Healthy Side:')
        HealthySide_label.setFont(newfont)
        self._HealthySide = QComboBox()
        self._HealthySide.setFixedWidth(150)
        self._HealthySide.addItem('')
        self._HealthySide.addItem('Right')
        self._HealthySide.addItem('Left')
        if self._Patient._HealthySide is not None:
            if self._Patient._HealthySide == 'Right':
                self._HealthySide.setCurrentIndex(1)
            elif self._Patient._HealthySide == 'Left':
                self._HealthySide.setCurrentIndex(2)
        self._HealthySide.setFont(newfont)
        
        #buttons        
        DoneButton = QPushButton('&Proceed', self)
        DoneButton.setFixedWidth(150)
        DoneButton.setFont(newfont)
        DoneButton.clicked.connect(self.Done)
        
        CancelButton = QPushButton('&Cancel', self)
        CancelButton.setFixedWidth(150)
        CancelButton.setFont(newfont)
        CancelButton.clicked.connect(self.Cancel)
        
        
        layout = QGridLayout()
        layout.addWidget(Patient_ID_label, 1,1,1,1)
        layout.addWidget(spacerh,1,2)
        layout.addWidget(self._Patient_ID, 1,3,1,1)
        
        layout.addWidget(spacerv,2,0)
       
        layout.addWidget(MRN_label, 3,1,1,1)
        layout.addWidget(spacerh,3,2)
        layout.addWidget(self._MRN, 3, 3, 1, 1)
        
        layout.addWidget(spacerv,4,0)
        
        layout.addWidget(Disease_label, 5,1,1,1)
        layout.addWidget(spacerh,5,2)
        layout.addWidget(self._diease, 5, 3, 1, 1)
        
        layout.addWidget(spacerv,6,0)
        
        layout.addWidget(HealthySide_label, 7,1,1,1)
        layout.addWidget(spacerh,7,2)
        layout.addWidget(self._HealthySide, 7, 3, 1, 1)
    
        
        layout.addWidget(spacerv,8,0)
        
        layout.addWidget(DoneButton,9,1,1,1)
        layout.addWidget(spacerh, 9,2)
        layout.addWidget(CancelButton,9,3,1,1)

        
        self.setLayout(layout)

    

    def Cancel(self):
        #user doesn't want to continue, close this window
        self.close()  

        
    def Done(self):
        #all is done, close this window and return to the main window 
        #update info in the photograph classes 
        self._Patient._Patient_ID = self._Patient_ID.text()
        self._Patient._MRN = self._MRN.text()
        self._Patient._HealthySide = str(self._HealthySide.currentText())
        
        if self._Patient._HealthySide == '':
            QtWidgets.QMessageBox.warning(self,"Warning",
                        "Cannot proceed without selecting the healthy side of the face",
                            QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.NoButton)
        else:
            
            Compute_eFace(self._Patient)
            self.close()

       
    def closeEvent(self, event):

        event.accept()

        
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
#    if not QtWidgets.QApplication.instance():
#        app = QtWidgets.QApplication(sys.argv)
#    else:
#        app = QtWidgets.QApplication.instance()
       
    GUI = ReportCardInit()
    GUI.show()
    app.exec_()
    

