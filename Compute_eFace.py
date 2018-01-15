# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 13:45:49 2018

@author: guarind
"""

import numpy as np
import os

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QGridLayout, QDialog

from measurements import get_measurements_from_data

def palpebral_fissure(photograph, CalibrationType, CalibrationValue):
    
    shape = photograph._shape
    left_pupil = photograph._lefteye
    right_pupil = photograph._righteye
    
    
    right_upper = [(shape[38,0]+shape[37,0])/2 , (shape[38,1]+shape[37,1])/2]
    right_lower = [(shape[40,0]+shape[41,0])/2 , (shape[40,1]+shape[41,1])/2]
    
    left_upper = [(shape[44,0]+shape[43,0])/2 , (shape[44,1]+shape[43,1])/2]
    left_lower = [(shape[46,0]+shape[47,0])/2 , (shape[46,1]+shape[47,1])/2]    
    
    
    if CalibrationType == 'Iris': #Iris radius will be used as calibration
        radius=(left_pupil[2]+right_pupil[2])/2
        Calibration = CalibrationValue/(2*radius)
    else:  #user provided calibration value
        Calibration = CalibrationValue
    
    palpebral_fissure = [np.sqrt((right_upper[0]-right_lower[0])**2 + (right_upper[1]-right_lower[1])**2)*Calibration , np.sqrt((left_upper[0]-left_lower[0])**2 + (left_upper[1]-left_lower[1])**2)*Calibration]
    
    return palpebral_fissure
    

def Compute_eFace(Patient):
    
    #compute the different measures from each photo
    
    LeftRest, RightRest, _, _ = get_measurements_from_data(Patient._Rest._shape, Patient._Rest._lefteye, Patient._Rest._righteye, Patient._CalibrationType, Patient._CalibrationValue)
    
    LeftSmallSmile, RightSmallSmile, _, _ = get_measurements_from_data(Patient._SmallSmile._shape, Patient._SmallSmile._lefteye, Patient._SmallSmile._righteye, Patient._CalibrationType, Patient._CalibrationValue)
    
    LeftLargeSmile, RightLargeSmile, _, _ = get_measurements_from_data(Patient._LargeSmile._shape, Patient._LargeSmile._lefteye, Patient._LargeSmile._righteye, Patient._CalibrationType, Patient._CalibrationValue)
    
    LeftEyeBrow, RightEyeBrow, _, _ = get_measurements_from_data(Patient._EyeBrow._shape, Patient._EyeBrow._lefteye, Patient._EyeBrow._righteye, Patient._CalibrationType, Patient._CalibrationValue)
    
    LeftEyeClosureGently, RightEyeClosureGently, _, _ = get_measurements_from_data(Patient._EyeClosureGently._shape, Patient._EyeClosureGently._lefteye, Patient._EyeClosureGently._righteye, Patient._CalibrationType, Patient._CalibrationValue)
    
    LeftEyeClosureTight, RightEyeClosureTight, _, _ = get_measurements_from_data(Patient._EyeClosureTight._shape, Patient._EyeClosureTight._lefteye, Patient._EyeClosureTight._righteye, Patient._CalibrationType, Patient._CalibrationValue)
    
    LeftPuckeringLips, RightPuckeringLips, DeviationPuckeringLips, _ = get_measurements_from_data(Patient._PuckeringLips._shape, Patient._PuckeringLips._lefteye, Patient._PuckeringLips._righteye, Patient._CalibrationType, Patient._CalibrationValue)
    
    LeftDentalShow, RightDentalShow, _, _ = get_measurements_from_data(Patient._DentalShow._shape, Patient._DentalShow._lefteye, Patient._DentalShow._righteye, Patient._CalibrationType, Patient._CalibrationValue)


    #Brow at Rest
    if Patient._HealthySide == 'Right':
        
        DeltaBrow = RightEyeBrow.BrowHeight - RightRest.BrowHeight
        
        BrowatRest =  (RightRest.BrowHeight - LeftRest.BrowHeight)/DeltaBrow
        
    elif Patient._HealthySide == 'Left':
        
        DeltaBrow = LeftEyeBrow.BrowHeight - LeftRest.BrowHeight
        
        BrowatRest =  (LeftRest.BrowHeight - RightRest.BrowHeight)/DeltaBrow
      
    #Brow Elevantion with Brow Raising 
    if Patient._HealthySide == 'Right':
        
        DeltaBrow = RightEyeBrow.BrowHeight - RightRest.BrowHeight
        
        BrowatRaising =  (RightEyeBrow.BrowHeight - LeftEyeBrow.BrowHeight)/DeltaBrow
        
    elif Patient._HealthySide == 'Left':
        
        DeltaBrow = LeftEyeBrow.BrowHeight - LeftRest.BrowHeight
        
        BrowatRaising =  (LeftEyeBrow.BrowHeight - RightEyeBrow.BrowHeight)/DeltaBrow
    

    #Palpebral Fisure at Rest
    PalpebralFissureRest = palpebral_fissure(Patient._Rest, Patient._CalibrationType, Patient._CalibrationValue) #[Rigth, Left]
    if Patient._HealthySide == 'Right':
        
        DeltaPalpebralFissureRest = PalpebralFissureRest[0] - PalpebralFissureRest[1]
        
    elif Patient._HealthySide == 'Left':
        
        DeltaPalpebralFissureRest = PalpebralFissureRest[1] - PalpebralFissureRest[0]
    

    #Oral commisure at rest
    if Patient._HealthySide == 'Right':
        
        DeltaOralCommissure = RightLargeSmile.CommissureExcursion - RightRest.CommissureExcursion
        
        OralCommissureatRest = (RightRest.CommissureExcursion - LeftRest.CommissureExcursion)/DeltaOralCommissure
        
    elif Patient._HealthySide == 'Left':
        
        DeltaOralCommissure = LeftLargeSmile.CommissureExcursion - LeftRest.CommissureExcursion
        
        OralCommissureatRest = (LeftRest.CommissureExcursion - RightRest.CommissureExcursion)/DeltaOralCommissure


    #Oral commisure with Smile
    if Patient._HealthySide == 'Right':
        
        DeltaOralCommissure = RightLargeSmile.CommissureExcursion - RightRest.CommissureExcursion
        
        OralCommissureatSmile = (RightLargeSmile.CommissureExcursion - LeftLargeSmile.CommissureExcursion)/DeltaOralCommissure
        
    elif Patient._HealthySide == 'Left':
        
        DeltaOralCommissure = LeftLargeSmile.CommissureExcursion - LeftRest.CommissureExcursion
        
        OralCommissureatSmile = (LeftLargeSmile.CommissureExcursion - RightLargeSmile.CommissureExcursion)/DeltaOralCommissure
        
        
    #Palpebral Fisure at Gentle eye closure 
    PalpebralFissureEyeClosureGently = palpebral_fissure(Patient._EyeClosureGently, Patient._CalibrationType, Patient._CalibrationValue) #[Rigth, Left]
    if Patient._HealthySide == 'Right':
        #Right eye is healthy, measure how much left eye is open with respect to paralized eye at rest 
        GentleEyeClossure = PalpebralFissureEyeClosureGently[1]/PalpebralFissureRest[1]
        
    elif Patient._HealthySide == 'Left':
         #Left eye is healthy, measure how much right eye is open with respect to paralized eye at rest 
        GentleEyeClossure = PalpebralFissureEyeClosureGently[0]/PalpebralFissureRest[0]
        
        
    #Palpebral Fisure at Tight eye closure 
    PalpebralFissureEyeClosureTight = palpebral_fissure(Patient._EyeClosureTight, Patient._CalibrationType, Patient._CalibrationValue) #[Rigth, Left]
    if Patient._HealthySide == 'Right':
        #Right eye is healthy, measure how much left eye is open with respect to paralized eye at rest 
        EyeClosureTight = PalpebralFissureEyeClosureTight[1]/PalpebralFissureRest[1]
        
    elif Patient._HealthySide == 'Left':
         #Left eye is healthy, measure how much right eye is open with respect to paralized eye at rest 
        EyeClosureTight = PalpebralFissureEyeClosureTight[0]/PalpebralFissureRest[0]

    #lower lip movement with EEEE
    LowerLipMovementEEEE = DeviationPuckeringLips.CommisureHeightDeviation
    
    #Ocular Synkinesis 
    PalpebralFissureLargeSmile = palpebral_fissure(Patient._LargeSmile, Patient._CalibrationType, Patient._CalibrationValue) #[Rigth, Left]
    PalpebralFissurePuckeringLips = palpebral_fissure(Patient._PuckeringLips, Patient._CalibrationType, Patient._CalibrationValue) #[Rigth, Left]
    if Patient._HealthySide == 'Right':
        
        DeltaPalpebralFissureLargeSmile = PalpebralFissureLargeSmile[0] - PalpebralFissureLargeSmile[1]
        DeltaPalpebralFissurePuckeringLips = PalpebralFissurePuckeringLips[0] - PalpebralFissurePuckeringLips[1]
        
    elif Patient._HealthySide == 'Left':
        
        DeltaPalpebralFissureLargeSmile = PalpebralFissureLargeSmile[1] - PalpebralFissureLargeSmile[0]
        DeltaPalpebralFissurePuckeringLips = PalpebralFissurePuckeringLips[1] - PalpebralFissurePuckeringLips[0]
    

    if abs(DeltaPalpebralFissureLargeSmile) >= abs(DeltaPalpebralFissurePuckeringLips):
        OcularSynkinesis = DeltaPalpebralFissureLargeSmile
    else:
        OcularSynkinesis = DeltaPalpebralFissurePuckeringLips
    
    
    return BrowatRest, DeltaPalpebralFissureRest, OralCommissureatRest, BrowatRaising, GentleEyeClossure, EyeClosureTight, OralCommissureatSmile, LowerLipMovementEEEE,OcularSynkinesis
        
class ReportCard(QDialog):
    
    def __init__(self, Patient):
        super(ReportCard, self).__init__()
        
        #self.parent = parent
        
        self._Patient = Patient
        
        self.initUI()
        
    def initUI(self):
        
        self.setWindowTitle('Report Card. Patient ID: ' + self._Patient._Patient_ID)
        scriptDir = os.getcwd()#os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'report_card.ico'))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() |
                              QtCore.Qt.WindowSystemMenuHint |
                              QtCore.Qt.WindowMinMaxButtonsHint)
        
        
        self.main_Widget = QtWidgets.QWidget(self)
        
        spacerh = QtWidgets.QWidget(self)
        spacerh.setFixedSize(20,0)
        
        spacerv = QtWidgets.QWidget(self)
        spacerv.setFixedSize(0,20)
        
       
        
        newfont = QtGui.QFont("Times", 12)
        
        RestingBrow_label = QLabel('Resting Brow:')
        RestingBrow_label.setFont(newfont)
        self._RestingBrow_measure =QLineEdit(self)
        self._RestingBrow_measure.setFont(newfont)
        self._RestingBrow_eFACE =QLineEdit(self)
        self._RestingBrow_eFACE.setFont(newfont)        


        RestingPalpebralFissure_label = QLabel('Resting Palpebral Fissure:')
        RestingPalpebralFissure_label.setFont(newfont)
        self._RestingPalpebralFissure_measure =QLineEdit(self)
        self._RestingPalpebralFissure_measure.setFont(newfont)
        self._RestingPalpebralFissure_eFACE =QLineEdit(self)
        self._RestingPalpebralFissure_eFACE.setFont(newfont)
        
        
        OralCommissureatRest_label = QLabel('Oral Commissure at Rest:\t\t')
        OralCommissureatRest_label.setFont(newfont)
        OralCommissureatRest_label.setFixedWidth(300)
        self._OralCommissureatRest_measure =QLineEdit(self)
        self._OralCommissureatRest_measure.setFont(newfont)
        self._OralCommissureatRest_eFACE =QLineEdit(self)
        self._OralCommissureatRest_eFACE.setFont(newfont)
        
        
        
        StaticBox = QtWidgets.QGroupBox('Static Measures')
        StaticBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        StaticBoxLayout = QtWidgets.QGridLayout()
        
        
        StaticBoxLayout.addWidget(RestingBrow_label,0,0,1,1)
        StaticBoxLayout.addWidget(self._RestingBrow_measure,0,1,1,1)
        StaticBoxLayout.addWidget(spacerv,0,2,1,1)
        StaticBoxLayout.addWidget(self._RestingBrow_eFACE,0,3,1,1)
        
        StaticBoxLayout.addWidget(RestingPalpebralFissure_label,1,0,1,1)
        StaticBoxLayout.addWidget(self._RestingPalpebralFissure_measure,1,1,1,1)
        StaticBoxLayout.addWidget(spacerv,1,2,1,1)
        StaticBoxLayout.addWidget(self._RestingPalpebralFissure_eFACE,1,3,1,1)
        
        StaticBoxLayout.addWidget(OralCommissureatRest_label,2,0,1,1)
        StaticBoxLayout.addWidget(self._OralCommissureatRest_measure,2,1,1,1)
        StaticBoxLayout.addWidget(spacerv,2,2,1,1)
        StaticBoxLayout.addWidget(self._OralCommissureatRest_eFACE,2,3,1,1)

        StaticBox.setLayout(StaticBoxLayout)
        
        
        
        
        BrowElevation_label = QLabel('Brow Elevation:')
        BrowElevation_label.setFont(newfont)
        self._BrowElevation_measure =QLineEdit(self)
        self._BrowElevation_measure.setFont(newfont)
        self._BrowElevation_eFACE =QLineEdit(self)
        self._BrowElevation_eFACE.setFont(newfont)
        
        
        GentleEyeClosure_label = QLabel('Gentle Eye Closure:')
        GentleEyeClosure_label.setFont(newfont)
        self._GentleEyeClosure_measure =QLineEdit(self)
        self._GentleEyeClosure_measure.setFont(newfont)
        self._GentleEyeClosure_eFACE =QLineEdit(self)
        self._GentleEyeClosure_eFACE.setFont(newfont)
        
        
        FullEyeClosure_label = QLabel('Full Eye Closure:')
        FullEyeClosure_label.setFont(newfont)
        self._FullEyeClosure_measure =QLineEdit(self)
        self._FullEyeClosure_measure.setFont(newfont)
        self._FullEyeClosure_eFACE =QLineEdit(self)
        self._FullEyeClosure_eFACE.setFont(newfont)    
        
        
        OralCommissureMovementwithSmile_label = QLabel('Oral Commissure Movement with Smile:')
        OralCommissureMovementwithSmile_label.setFont(newfont)
        OralCommissureMovementwithSmile_label.setFixedWidth(300)
        self._OralCommissureMovementwithSmile_measure =QLineEdit(self)
        self._OralCommissureMovementwithSmile_measure.setFont(newfont)
        self._OralCommissureMovementwithSmile_eFACE =QLineEdit(self)
        self._OralCommissureMovementwithSmile_eFACE.setFont(newfont) 
        
        
        LowerLipMovement_label = QLabel('Lower Lip Movement:')
        LowerLipMovement_label.setFont(newfont)
        self._LowerLipMovement_measure =QLineEdit(self)
        self._LowerLipMovement_measure.setFont(newfont)
        self._LowerLipMovement_eFACE =QLineEdit(self)
        self._LowerLipMovement_eFACE.setFont(newfont)      
        
        
        DynamicBox = QtWidgets.QGroupBox('Dynamic Measures')
        DynamicBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        DynamicBoxLayout = QtWidgets.QGridLayout()
        
        DynamicBoxLayout.addWidget(BrowElevation_label,0,0,1,1)
        DynamicBoxLayout.addWidget(self._BrowElevation_measure,0,1,1,1)
        DynamicBoxLayout.addWidget(spacerv,0,2,1,1)
        DynamicBoxLayout.addWidget(self._BrowElevation_eFACE,0,3,1,1)
        
        DynamicBoxLayout.addWidget(GentleEyeClosure_label,1,0,1,1)
        DynamicBoxLayout.addWidget(self._GentleEyeClosure_measure,1,1,1,1)
        DynamicBoxLayout.addWidget(spacerv,1,2,1,1)
        DynamicBoxLayout.addWidget(self._GentleEyeClosure_eFACE,1,3,1,1)
        
        DynamicBoxLayout.addWidget(FullEyeClosure_label,2,0,1,1)
        DynamicBoxLayout.addWidget(self._FullEyeClosure_measure,2,1,1,1)
        DynamicBoxLayout.addWidget(spacerv,2,2,1,1)
        DynamicBoxLayout.addWidget(self._FullEyeClosure_eFACE,2,3,1,1)     
        
        DynamicBoxLayout.addWidget(OralCommissureMovementwithSmile_label,3,0,1,1)
        DynamicBoxLayout.addWidget(self._OralCommissureMovementwithSmile_measure,3,1,1,1)
        DynamicBoxLayout.addWidget(spacerv,3,2,1,1)
        DynamicBoxLayout.addWidget(self._OralCommissureMovementwithSmile_eFACE,3,3,1,1)         
        
        DynamicBoxLayout.addWidget(LowerLipMovement_label,4,0,1,1)
        DynamicBoxLayout.addWidget(self._LowerLipMovement_measure,4,1,1,1)
        DynamicBoxLayout.addWidget(spacerv,4,2,1,1)
        DynamicBoxLayout.addWidget(self._LowerLipMovement_eFACE,4,3,1,1)   
        
        DynamicBox.setLayout(DynamicBoxLayout)
        
        
        OcularSynkenisis_label = QLabel('Ocular Synkenisis:                  ')
        OcularSynkenisis_label.setFont(newfont)
        OcularSynkenisis_label.setFixedWidth(300)
        self._OcularSynkenisis_measure =QLineEdit(self)
        self._OcularSynkenisis_measure.setFont(newfont)
        self._OcularSynkenisis_eFACE =QLineEdit(self)
        self._OcularSynkenisis_eFACE.setFont(newfont) 
        
        SynkenisisBox = QtWidgets.QGroupBox('Synkenisis Measures')
        SynkenisisBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        SynkenisisBoxLayout = QtWidgets.QGridLayout()
        
        SynkenisisBoxLayout.addWidget(OcularSynkenisis_label,0,0,1,1)
        SynkenisisBoxLayout.addWidget(self._OcularSynkenisis_measure,0,1,1,1)
        SynkenisisBoxLayout.addWidget(spacerv,0,2,1,1)
        SynkenisisBoxLayout.addWidget(self._OcularSynkenisis_eFACE,0,3,1,1)
        
        SynkenisisBox.setLayout(SynkenisisBoxLayout)
        
        
        #buttons        
        DoneButton = QPushButton('&Save', self)
        DoneButton.setFixedWidth(150)
        DoneButton.setFont(newfont)
        DoneButton.clicked.connect(self.Done)
        
        CancelButton = QPushButton('&Cancel', self)
        CancelButton.setFixedWidth(150)
        CancelButton.setFont(newfont)
        CancelButton.clicked.connect(self.Cancel)
        
        ButtonLayout = QtWidgets.QHBoxLayout()
        ButtonLayout.addWidget(DoneButton)
        ButtonLayout.addWidget(CancelButton)
        
        
        #Top Labels
        Measure_Label = QLabel('Measures')
        Measure_Label.setFont(newfont)
        
        eFACE_Label = QLabel('eFACE')
        eFACE_Label.setFont(newfont)
        
        TopLabelsLayout = QtWidgets.QHBoxLayout()
        TopLabelsLayout.addWidget(QLabel(''))
        TopLabelsLayout.addWidget(QLabel(''))
        TopLabelsLayout.addWidget(Measure_Label)
        TopLabelsLayout.addWidget(eFACE_Label)
        

        
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(TopLabelsLayout)
        layout.addWidget(spacerv)
        layout.addWidget(StaticBox)
        layout.addWidget(spacerv)
        layout.addWidget(DynamicBox)
        layout.addWidget(spacerv)
        layout.addWidget(SynkenisisBox)
        layout.addWidget(spacerv)
        layout.addLayout(ButtonLayout)
                
        self.setLayout(layout)
        
        
        #compute measures and update window
        BrowatRest, DeltaPalpebralFissureRest, OralCommissureatRest, BrowatRaising, GentleEyeClossure, EyeClosureTight, OralCommissureatSmile, LowerLipMovementEEEE,OcularSynkinesis = Compute_eFace(self._Patient)
        
        self._RestingBrow_measure.setText(str(np.round(BrowatRest,2)*100) + ' %')
        self._RestingPalpebralFissure_measure.setText(str(np.round(DeltaPalpebralFissureRest,2)) + ' mm')
        self._OralCommissureatRest_measure.setText(str(np.round(OralCommissureatRest,2)*100) + ' %')
        self._BrowElevation_measure.setText(str(np.round(BrowatRaising,2)*100) + ' %')
        self._GentleEyeClosure_measure.setText(str(np.round(GentleEyeClossure,2)*100) + ' %')
        self._FullEyeClosure_measure.setText(str(np.round(EyeClosureTight,2)*100) + ' %')
        self._OralCommissureMovementwithSmile_measure.setText(str(np.round(OralCommissureatSmile,2)*100) + ' %') 
        self._LowerLipMovement_measure.setText(str(np.round(LowerLipMovementEEEE,2)) + ' mm')
        self._OcularSynkenisis_measure.setText(str(np.round(OcularSynkinesis,2)) + ' mm')

    def Cancel(self):
        #user doesn't want to continue, close this window
        self.close()  

        
    def Done(self):
        #all is done, close this window and return to the main window 

        
        self.close()

       
    def closeEvent(self, event):

        event.accept()
        
    #this function read the style sheet used to presents the GroupBox, 
    #it is located in .\include\GroupBoxStyle.qss
    def getStyleSheet(self, path):
        f = QFile(path)
        f.open(QFile.ReadOnly | QFile.Text)
        stylesheet = QTextStream(f).readAll()
        f.close()
        return stylesheet

        
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
#    if not QtWidgets.QApplication.instance():
#        app = QtWidgets.QApplication(sys.argv)
#    else:
#        app = QtWidgets.QApplication.instance()
       
    GUI = ReportCard()
    GUI.show()
    app.exec_()    