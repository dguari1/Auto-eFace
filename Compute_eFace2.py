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
        
        BrowatRaising =  (LeftRest.BrowHeight - LeftEyeBrow.BrowHeight)/DeltaBrow
        
    elif Patient._HealthySide == 'Left':
        
        DeltaBrow = LeftEyeBrow.BrowHeight - LeftRest.BrowHeight
        
        BrowatRaising =  (RightRest.BrowHeight - RightEyeBrow.BrowHeight)/DeltaBrow
    

    #Palpebral Fisure at Rest
    PalpebralFissureRest = palpebral_fissure(Patient._Rest, Patient._CalibrationType, Patient._CalibrationValue) #[Rigth, Left]
    if Patient._HealthySide == 'Right':
        
        DeltaPalpebralFissureRest = PalpebralFissureRest[1]/PalpebralFissureRest[0]
        
    elif Patient._HealthySide == 'Left':
        
        DeltaPalpebralFissureRest = PalpebralFissureRest[0]/PalpebralFissureRest[1]  
    

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
        GentleEyeClossure = 1 - PalpebralFissureEyeClosureGently[1]/PalpebralFissureRest[1]
        
    elif Patient._HealthySide == 'Left':
         #Left eye is healthy, measure how much right eye is open with respect to paralized eye at rest 
        GentleEyeClossure = 1 - PalpebralFissureEyeClosureGently[0]/PalpebralFissureRest[0]
        
        
    #Palpebral Fisure at Tight eye closure 
    PalpebralFissureEyeClosureTight = palpebral_fissure(Patient._EyeClosureTight, Patient._CalibrationType, Patient._CalibrationValue) #[Rigth, Left]
    if Patient._HealthySide == 'Right':
        #Right eye is healthy, measure how much left eye is open with respect to paralized eye at rest 
        EyeClosureTight = 1 - PalpebralFissureEyeClosureTight[1]/PalpebralFissureRest[1]
        
    elif Patient._HealthySide == 'Left':
         #Left eye is healthy, measure how much right eye is open with respect to paralized eye at rest 
        EyeClosureTight = 1 - PalpebralFissureEyeClosureTight[0]/PalpebralFissureRest[0]

    #lower lip movement with EEEE
    if Patient._HealthySide == 'Right':
        
        LowerLipMovementEEEE = LeftDentalShow.LoweLipActivation/RightDentalShow.LoweLipActivation

        
    elif Patient._HealthySide == 'Left':
        
        LowerLipMovementEEEE = RightDentalShow.LoweLipActivation/LeftDentalShow.LoweLipActivation

    #Ocular Synkinesis 
    PalpebralFissureLargeSmile = palpebral_fissure(Patient._LargeSmile, Patient._CalibrationType, Patient._CalibrationValue) #[Rigth, Left]
    PalpebralFissurePuckeringLips = palpebral_fissure(Patient._PuckeringLips, Patient._CalibrationType, Patient._CalibrationValue) #[Rigth, Left]
    if Patient._HealthySide == 'Right':
        
        DeltaPalpebralFissureLargeSmile = PalpebralFissureLargeSmile[1]/PalpebralFissureLargeSmile[0]
        DeltaPalpebralFissurePuckeringLips = PalpebralFissurePuckeringLips[1]/PalpebralFissurePuckeringLips[0]
                
        OcularSynkinesis_Smile = (PalpebralFissureLargeSmile[1]/PalpebralFissureRest[1]) / (PalpebralFissureLargeSmile[0]/PalpebralFissureRest[0])
        OcularSynkinesis_Pucker = (PalpebralFissurePuckeringLips[1]/PalpebralFissureRest[1]) / (PalpebralFissurePuckeringLips[0]/PalpebralFissureRest[0])

        
    elif Patient._HealthySide == 'Left':
        
        DeltaPalpebralFissureLargeSmile = PalpebralFissureLargeSmile[0]/PalpebralFissureLargeSmile[1]
        DeltaPalpebralFissurePuckeringLips = PalpebralFissurePuckeringLips[0]/PalpebralFissurePuckeringLips[1]
        
        OcularSynkinesis_Smile = (PalpebralFissureLargeSmile[0]/PalpebralFissureRest[0]) / (PalpebralFissureLargeSmile[1]/PalpebralFissureRest[1])
        OcularSynkinesis_Pucker = (PalpebralFissurePuckeringLips[0]/PalpebralFissureRest[0]) / (PalpebralFissurePuckeringLips[1]/PalpebralFissureRest[1])
    

    if OcularSynkinesis_Smile <= OcularSynkinesis_Pucker:
        OcularSynkinesis = OcularSynkinesis_Smile
    else:
        OcularSynkinesis = OcularSynkinesis_Pucker
    
    
    return BrowatRest, DeltaPalpebralFissureRest, OralCommissureatRest, BrowatRaising, GentleEyeClossure, EyeClosureTight, OralCommissureatSmile, LowerLipMovementEEEE,OcularSynkinesis
        
class ReportCard(QDialog):
    
    def __init__(self, Patient=None):
        super(ReportCard, self).__init__()
        
        #self.parent = parent
        
        self._Patient = Patient
        
        self.initUI()
        
    def initUI(self):
        
       # self.setWindowTitle('Report Card. Patient ID: ' + self._Patient._Patient_ID)
        scriptDir = os.getcwd()#os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'report_card.ico'))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() |
                              QtCore.Qt.WindowSystemMenuHint |
                              QtCore.Qt.WindowMinMaxButtonsHint)
        
        
        
        self._scene = QtWidgets.QGraphicsScene(self)
        #self._scene.setSceneRect(0, 0, 500, 500)
        self.view = QtWidgets.QGraphicsView(self)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.view.setScene(self._scene)
        self.view.setFocusPolicy(QtCore.Qt.NoFocus)
        color = self.palette().color(QtGui.QPalette.Background)
        self.view.setBackgroundBrush(color)
        
        
        self.spacerh = QtWidgets.QWidget(self)
        self.spacerh.setFixedSize(20,0)
        
        self.spacerv = QtWidgets.QWidget(self)
        self.spacerv.setFixedSize(0,20)
        
       
        
        newfont = QtGui.QFont("Times", 12)
                

        
        self._RestingBrow_label = QLabel('Resting Brow:')
        self._RestingBrow_label.setFont(newfont)
        self._RestingBrow_label.setFixedWidth(250)
        self._RestingBrow_measure = QLabel('hi')
        self._RestingBrow_measure.setFont(newfont)
        self._RestingBrow_measure.setFixedWidth(100)
        self._RestingBrow_eFACE =QLabel('')
        self._RestingBrow_eFACE.setFont(newfont)   
        self._RestingBrow_eFACE.setFixedWidth(300)
        
        LayoutRest1 = QtWidgets.QHBoxLayout()
        LayoutRest1.addWidget(self.spacerh)
        LayoutRest1.addWidget(self._RestingBrow_label)
        LayoutRest1.addWidget(self._RestingBrow_measure)
        LayoutRest1.addWidget(self._RestingBrow_eFACE)
        LayoutRest1.addWidget(self.spacerh)
        LayoutRest1.addWidget(self.spacerh)


        RestingPalpebralFissure_label = QLabel('Resting Palpebral Fissure:')
        RestingPalpebralFissure_label.setFont(newfont)
        RestingPalpebralFissure_label.setFixedWidth(250)
        self._RestingPalpebralFissure_measure =QLabel('')
        self._RestingPalpebralFissure_measure.setFont(newfont)
        self._RestingPalpebralFissure_measure.setFixedWidth(100)
        self._RestingPalpebralFissure_eFACE = QLabel('')
        self._RestingPalpebralFissure_eFACE.setFont(newfont)
        self._RestingPalpebralFissure_eFACE.setFixedWidth(300)
        
        LayoutRest2 = QtWidgets.QHBoxLayout()
        LayoutRest2.addWidget(self.spacerh)
        LayoutRest2.addWidget(RestingPalpebralFissure_label)
        LayoutRest2.addWidget(self._RestingPalpebralFissure_measure)
        LayoutRest2.addWidget(self._RestingPalpebralFissure_eFACE)
        LayoutRest2.addWidget(self.spacerh)
        LayoutRest2.addWidget(self.spacerh)

        
        OralCommissureatRest_label = QLabel('Oral Commissure at Rest:')
        OralCommissureatRest_label.setFont(newfont)
        OralCommissureatRest_label.setFixedWidth(250)
        self._OralCommissureatRest_measure =QLabel('')
        self._OralCommissureatRest_measure.setFont(newfont)
        self._OralCommissureatRest_measure.setFixedWidth(100)
        self._OralCommissureatRest_eFACE = QLabel('')
        self._OralCommissureatRest_eFACE.setFont(newfont)
        self._OralCommissureatRest_eFACE.setFixedWidth(300)
        
        LayoutRest3 = QtWidgets.QHBoxLayout()
        LayoutRest3.addWidget(self.spacerh)
        LayoutRest3.addWidget(OralCommissureatRest_label)
        LayoutRest3.addWidget(self._OralCommissureatRest_measure)
        LayoutRest3.addWidget(self._OralCommissureatRest_eFACE)
        LayoutRest3.addWidget(self.spacerh)
        LayoutRest3.addWidget(self.spacerh)

  
        
        StaticBox = QtWidgets.QGroupBox('Static Parameters')
        StaticBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        StaticBoxLayout = QtWidgets.QVBoxLayout()
        
        StaticBoxLayout.addWidget(self.spacerv)
        StaticBoxLayout.addLayout(LayoutRest1)
        StaticBoxLayout.addWidget(self.spacerv)
        StaticBoxLayout.addLayout(LayoutRest2)
        StaticBoxLayout.addWidget(self.spacerv)
        StaticBoxLayout.addLayout(LayoutRest3)
        StaticBoxLayout.addWidget(self.spacerv)
        StaticBox.setLayout(StaticBoxLayout)
        
#        self._scene.addWidget(self.spacerv)
#        self._scene.addWidget(self.spacerh)
        
        self._scene.addWidget(StaticBox)
        
        
#        BrowElevation_label = QLabel('Brow Elevation:')
#        BrowElevation_label.setFont(newfont)
#        self._BrowElevation_measure =QLineEdit(self)
#        self._BrowElevation_measure.setFont(newfont)
#        self._BrowElevation_measure.setFixedWidth(100)
#        self._BrowElevation_eFACE =QLineEdit(self)
#        self._BrowElevation_eFACE.setFont(newfont)
#        self._BrowElevation_eFACE.setFixedWidth(100)
#        
#        
#        GentleEyeClosure_label = QLabel('Gentle Eye Closure:')
#        GentleEyeClosure_label.setFont(newfont)
#        self._GentleEyeClosure_measure =QLineEdit(self)
#        self._GentleEyeClosure_measure.setFont(newfont)
#        self._GentleEyeClosure_measure.setFixedWidth(100)
#        self._GentleEyeClosure_eFACE =QLineEdit(self)
#        self._GentleEyeClosure_eFACE.setFont(newfont)
#        self._GentleEyeClosure_eFACE.setFixedWidth(100)
#        
#        
#        FullEyeClosure_label = QLabel('Full Eye Closure:')
#        FullEyeClosure_label.setFont(newfont)
#        self._FullEyeClosure_measure =QLineEdit(self)
#        self._FullEyeClosure_measure.setFont(newfont)
#        self._FullEyeClosure_measure.setFixedWidth(100)
#        self._FullEyeClosure_eFACE =QLineEdit(self)
#        self._FullEyeClosure_eFACE.setFont(newfont)    
#        self._FullEyeClosure_eFACE.setFixedWidth(100)
#        
#        
#        OralCommissureMovementwithSmile_label = QLabel('Oral Commissure Movement with Smile:')
#        OralCommissureMovementwithSmile_label.setFont(newfont)
#        OralCommissureMovementwithSmile_label.setFixedWidth(300)
#        self._OralCommissureMovementwithSmile_measure =QLineEdit(self)
#        self._OralCommissureMovementwithSmile_measure.setFont(newfont)
#        self._OralCommissureMovementwithSmile_measure.setFixedWidth(100)
#        self._OralCommissureMovementwithSmile_eFACE =QLineEdit(self)
#        self._OralCommissureMovementwithSmile_eFACE.setFont(newfont) 
#        self._OralCommissureMovementwithSmile_eFACE.setFixedWidth(100)
#        
#        
#        LowerLipMovement_label = QLabel('Lower Lip Movement:')
#        LowerLipMovement_label.setFont(newfont)
#        self._LowerLipMovement_measure =QLineEdit(self)
#        self._LowerLipMovement_measure.setFont(newfont)
#        self._LowerLipMovement_measure.setFixedWidth(100)
#        self._LowerLipMovement_eFACE =QLineEdit(self)
#        self._LowerLipMovement_eFACE.setFont(newfont) 
#        self._LowerLipMovement_eFACE.setFixedWidth(100)
#        
#        
#        DynamicBox = QtWidgets.QGroupBox('Dynamic Parameters')
#        DynamicBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
#        DynamicBoxLayout = QtWidgets.QGridLayout()
#        
#        DynamicBoxLayout.addWidget(BrowElevation_label,0,0,1,1)
#        DynamicBoxLayout.addWidget(self._BrowElevation_measure,0,1,1,1)
#        percent_Label=QLabel('%'); percent_Label.setFont(newfont)
#        DynamicBoxLayout.addWidget(percent_Label,0,2,1,1)
#        DynamicBoxLayout.addWidget(self.spacerv,0,3,1,1)
#        DynamicBoxLayout.addWidget(self._BrowElevation_eFACE,0,4,1,1)
#        
#        DynamicBoxLayout.addWidget(GentleEyeClosure_label,1,0,1,1)
#        DynamicBoxLayout.addWidget(self._GentleEyeClosure_measure,1,1,1,1)
#        percent_Label=QLabel('%'); percent_Label.setFont(newfont)
#        DynamicBoxLayout.addWidget(percent_Label,1,2,1,1)
#        DynamicBoxLayout.addWidget(self.spacerv,1,3,1,1)
#        DynamicBoxLayout.addWidget(self._GentleEyeClosure_eFACE,1,4,1,1)
#        
#        DynamicBoxLayout.addWidget(FullEyeClosure_label,2,0,1,1)
#        DynamicBoxLayout.addWidget(self._FullEyeClosure_measure,2,1,1,1)
#        percent_Label=QLabel('%'); percent_Label.setFont(newfont)
#        DynamicBoxLayout.addWidget(percent_Label,2,2,1,1)
#        DynamicBoxLayout.addWidget(self.spacerv,2,3,1,1)
#        DynamicBoxLayout.addWidget(self._FullEyeClosure_eFACE,2,4,1,1)     
#        
#        DynamicBoxLayout.addWidget(OralCommissureMovementwithSmile_label,3,0,1,1)
#        DynamicBoxLayout.addWidget(self._OralCommissureMovementwithSmile_measure,3,1,1,1)
#        percent_Label=QLabel('%'); percent_Label.setFont(newfont)
#        DynamicBoxLayout.addWidget(percent_Label,3,2,1,1)
#        DynamicBoxLayout.addWidget(self.spacerv,3,3,1,1)
#        DynamicBoxLayout.addWidget(self._OralCommissureMovementwithSmile_eFACE,3,4,1,1)         
#        
#        DynamicBoxLayout.addWidget(LowerLipMovement_label,4,0,1,1)
#        DynamicBoxLayout.addWidget(self._LowerLipMovement_measure,4,1,1,1)
#        percent_Label=QLabel('%'); percent_Label.setFont(newfont)
#        DynamicBoxLayout.addWidget(percent_Label,4,2,1,1)
#        DynamicBoxLayout.addWidget(self.spacerv,4,3,1,1)
#        DynamicBoxLayout.addWidget(self._LowerLipMovement_eFACE,4,4,1,1)   
#        
#        DynamicBox.setLayout(DynamicBoxLayout)
#        
#        
#        OcularSynkenisis_label = QLabel('Ocular Synkinesis:')
#        OcularSynkenisis_label.setFont(newfont)
#        OcularSynkenisis_label.setFixedWidth(300)
#        self._OcularSynkenisis_measure =QLineEdit(self)
#        self._OcularSynkenisis_measure.setFont(newfont)
#        self._OcularSynkenisis_measure.setFixedWidth(100)
#        self._OcularSynkenisis_eFACE =QLineEdit(self)
#        self._OcularSynkenisis_eFACE.setFont(newfont) 
#        self._OcularSynkenisis_eFACE.setFixedWidth(100)
#        
#        
#        SynkenisisBox = QtWidgets.QGroupBox('Synkinesis Parameters')
#        SynkenisisBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
#        SynkenisisBoxLayout = QtWidgets.QGridLayout()
#        
#        SynkenisisBoxLayout.addWidget(OcularSynkenisis_label,0,0,1,1)
#        SynkenisisBoxLayout.addWidget(self._OcularSynkenisis_measure,0,1,1,1)
#        percent_Label=QLabel('%'); percent_Label.setFont(newfont)
#        SynkenisisBoxLayout.addWidget(percent_Label,0,2,1,1)
#        SynkenisisBoxLayout.addWidget(self.spacerv,0,3,1,1)
#        SynkenisisBoxLayout.addWidget(self._OcularSynkenisis_eFACE,0,4,1,1)
#        
#        SynkenisisBox.setLayout(SynkenisisBoxLayout)
        
        
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
        
        
        
        
        layout = QtWidgets.QVBoxLayout()
        layout.addSpacing(5)
        layout.addWidget(self.view)
        layout.addLayout(ButtonLayout)
                
        self.setLayout(layout)
        
        
#        #compute measures and update window
#        BrowatRest, DeltaPalpebralFissureRest, OralCommissureatRest, BrowatRaising, GentleEyeClossure, EyeClosureTight, OralCommissureatSmile, LowerLipMovementEEEE,OcularSynkinesis = Compute_eFace(self._Patient)
#        
#        self._RestingBrow_measure.setText(str(np.round(BrowatRest,3)*100))
#        self._RestingPalpebralFissure_measure.setText(str(np.round(DeltaPalpebralFissureRest,3)*100))
#        self._OralCommissureatRest_measure.setText(str(np.round(OralCommissureatRest,3)*100))
#        self._BrowElevation_measure.setText(str(np.round(BrowatRaising,3)*100))
#        self._GentleEyeClosure_measure.setText(str(np.round(GentleEyeClossure,3)*100))
#        self._FullEyeClosure_measure.setText(str(np.round(EyeClosureTight,3)*100))
#        self._OralCommissureMovementwithSmile_measure.setText(str(np.round(OralCommissureatSmile,3)*100)) 
#        self._LowerLipMovement_measure.setText(str(np.round(LowerLipMovementEEEE,3)*100))
#        self._OcularSynkenisis_measure.setText(str(np.round(OcularSynkinesis,3)*100))
        
        
        #self.setFixedSize(self.size())
        self.DrawSomeLines(self._RestingBrow_eFACE, 1,2,0,'Ptotic','Balanced','Elevated')
        self.DrawSomeLines(self._RestingPalpebralFissure_eFACE,1,2,0, 'Wide','Balanced','Narrow')
        self.DrawSomeLines(self._OralCommissureatRest_eFACE, 1,2,0,'Inf Malpositioned', 'Balanced', 'Sup Malpositioned')
        self.view.setScene(self._scene)
        w = self._scene.width()
        h = self._scene.height()
        self.view.setSceneRect(-10,-10,w+20,h+20)

        self._scene.update()
       
        self.show() 

        
    
    def DrawSomeLines(self, label, value, max_value, min_value, text1, text2, text3):
        x = label.pos().x()
        y = label.pos().y() 
        h = label.height()
        w = label.width()
        
        
        #pen = QtGui.QPen(QtCore.Qt.black)
        pen = QtGui.QPen(QtGui.QColor(192,192,192))
        pen.setStyle(QtCore.Qt.SolidLine)        
        pen.setWidth(6)        
        self._scene.addLine(QtCore.QLineF(x+2,y+int(h/2),x+w-2,y+int(h/2)), pen)
        
        
        pen.setWidth(1)
        self._scene.addLine(QtCore.QLineF(x,y+2,x,y+h-2), pen)
        self._scene.addLine(QtCore.QLineF(x+w,y+2,x+w,y+h-2), pen)
        self._scene.addLine(QtCore.QLineF(x+int(w/2),y+2,x+int(w/2),y+h-2), pen)
        
        
        pen = QtGui.QPen(QtGui.QColor(105,105,105))
        pen.setStyle(QtCore.Qt.SolidLine)        
        pen.setWidth(6)        
        self._scene.addLine(QtCore.QLineF(x+2,y+int(h/2),x+int(w/2)-2,y+int(h/2)), pen)
        
        
        
        TextItem = QtWidgets.QGraphicsSimpleTextItem()
        brush=QtGui.QBrush(QtCore.Qt.black)
        TextItem.setBrush(brush)
        TextItem.setText(text1)        
        w_text  =  TextItem.boundingRect().width()
        #h_text = TextItem.boundingRect().height()
        TextItem.setPos(QtCore.QPointF(x-int(w_text/2),y+h+2))       
        self._scene.addItem(TextItem)
        
        
        TextItem = QtWidgets.QGraphicsSimpleTextItem()
        brush=QtGui.QBrush(QtCore.Qt.black)
        TextItem.setBrush(brush)
        TextItem.setText(text2)        
        w_text  =  TextItem.boundingRect().width()
        #h_text = TextItem.boundingRect().height()
        TextItem.setPos(QtCore.QPointF(x-int(w_text/2)+int(w/2),y+h+2))       
        self._scene.addItem(TextItem)
        
        
        TextItem = QtWidgets.QGraphicsSimpleTextItem()
        brush=QtGui.QBrush(QtCore.Qt.black)
        TextItem.setBrush(brush)
        TextItem.setText(text3)        
        w_text  =  TextItem.boundingRect().width()
        #h_text = TextItem.boundingRect().height()
        TextItem.setPos(QtCore.QPointF(x-int(w_text/2)+w,y+h+2))       
        self._scene.addItem(TextItem)
        
        
        Ellipse = QtWidgets.QGraphicsEllipseItem(0,0,14,14)
        #ellipse will be red
        pen = QtGui.QPen(QtGui.QColor(112,128,144))
        pen.setWidth(1)            
        Ellipse.setPen(pen)      
        #if I want to fill the ellipse i should do this:
        brush = QtGui.QBrush(QtGui.QColor(112,128,144)) 
        Ellipse.setBrush(brush)

        
        #this is the position of the top-left corner of the ellipse.......
        Ellipse.setPos(x+int(w/2)-7,y+int(h/2)-7)
        Ellipse.setTransform(QtGui.QTransform())        
        self._scene.addItem(Ellipse)
    
    def Cancel(self):
        #user doesn't want to continue, close this window
        self.close()  

        
    def Done(self):
        #all is done, close this window and return to the main window 
        
        #lets save things in a .eFace file for the moment
        
        folder_name,extension = os.path.split(self._Patient._Rest._file_name)

        
        file_name = os.path.join(folder_name,self._Patient._Patient_ID+'.eFACE')
        
        #remove any existing files
        if os.path.isfile(file_name):
            os.remove(file_name)       
            
        with open(file_name,'a') as f:
            
            f.write('# Patient ID { \n')
            f.write(self._Patient._Patient_ID)
            f.write('\n# } \n')
                    
            f.write('# Medical Record Number { \n')
            f.write(self._Patient._MRN)
            f.write('\n# } \n')
                    
            f.write('# Aditional Comments { \n')
            f.write(self._Patient._MRN)
            f.write('\n# } \n')      
                    

            f.write('# Results (Meausure, eFACE Score) { \n')
            f.write('---Static Measures \n')
            f.write("Brow at Rest:    %s %%,    %s \n" % (self._RestingBrow_measure.text(), self._RestingBrow_eFACE.text()))
            f.write("Palpebral Fissure at Rest:    %s %%,    %s \n" % (self._RestingPalpebralFissure_measure.text(), self._RestingPalpebralFissure_eFACE.text()))
            f.write("Oral Commisure at Rest:    %s mm,    %s \n" % (self._OralCommissureatRest_measure.text(), self._OralCommissureatRest_eFACE.text()))
            f.write('---Dynamic Measures \n')
            f.write("Brow Elevation:    %s %%,    %s \n" % (self._BrowElevation_measure.text(), self._BrowElevation_eFACE.text()))
            f.write("Gentle Eye Closure:    %s %%,    %s \n" % (self._GentleEyeClosure_measure.text(), self._GentleEyeClosure_eFACE.text()))
            f.write("Full Eye Closure:    %s %%,    %s \n" % (self._FullEyeClosure_measure.text(), self._FullEyeClosure_eFACE.text()))
            f.write("Oral Commissure Movement with Smile:    %s %%,    %s \n" % (self._OralCommissureMovementwithSmile_measure.text(), self._OralCommissureMovementwithSmile_eFACE.text()))
            f.write("Lower Lip Movement:    %s mm,    %s \n" % (self._LowerLipMovement_measure.text(), self._LowerLipMovement_eFACE.text()))
            f.write('---Synkenisis Measures \n')
            f.write("Ocular Synkenisis:    %s mm,    %s" % (self._OcularSynkenisis_measure.text(), self._OcularSynkenisis_eFACE.text()))
            f.write('\n# } \n') 

            f.write('# Calibration Type { \n')
            f.write(self._Patient._CalibrationType)
            f.write('\n# } \n')        
                    
            f.write('# Calibration Value { \n')
            f.write(str(self._Patient._CalibrationValue))
            f.write('\n# } \n') 
                    
            f.write('# Model Name { \n')
            f.write(self._Patient._ModelName)
            f.write('\n# } \n')                     
        
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
#    app = QtWidgets.QApplication([])
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
       
    GUI = ReportCard()
    GUI.show()
    app.exec_()    