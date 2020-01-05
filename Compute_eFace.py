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


#import matplotlib
#matplotlib.use('QT5Agg')


#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#import matplotlib.pyplot as plt


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

    LeftRest, RightRest, _ , _ ,IPrest = get_measurements_from_data(Patient._Rest._shape, Patient._Rest._lefteye, Patient._Rest._righteye, Patient._CalibrationType, Patient._CalibrationValue)

   # LeftSmallSmile, RightSmallSmile, _, _, IPSmallSmile = get_measurements_from_data(Patient._SmallSmile._shape, Patient._SmallSmile._lefteye, Patient._SmallSmile._righteye, Patient._CalibrationType, Patient._CalibrationValue)

    LeftLargeSmile, RightLargeSmile, _, _, IPLargeSmile = get_measurements_from_data(Patient._LargeSmile._shape, Patient._LargeSmile._lefteye, Patient._LargeSmile._righteye, Patient._CalibrationType, Patient._CalibrationValue)

    LeftEyeBrow, RightEyeBrow, _, _, IPEyeBrow= get_measurements_from_data(Patient._EyeBrow._shape, Patient._EyeBrow._lefteye, Patient._EyeBrow._righteye, Patient._CalibrationType, Patient._CalibrationValue)

    LeftEyeClosureGently, RightEyeClosureGently, _, _, IPEyeClosureGently = get_measurements_from_data(Patient._EyeClosureGently._shape, Patient._EyeClosureGently._lefteye, Patient._EyeClosureGently._righteye, Patient._CalibrationType, Patient._CalibrationValue)

    LeftEyeClosureTight, RightEyeClosureTight, _, _, IPEyeClosureTight = get_measurements_from_data(Patient._EyeClosureTight._shape, Patient._EyeClosureTight._lefteye, Patient._EyeClosureTight._righteye, Patient._CalibrationType, Patient._CalibrationValue)

    LeftPuckeringLips, RightPuckeringLips, _, _, IPPuckeringLips = get_measurements_from_data(Patient._PuckeringLips._shape, Patient._PuckeringLips._lefteye, Patient._PuckeringLips._righteye, Patient._CalibrationType, Patient._CalibrationValue)

    LeftDentalShow, RightDentalShow, _, _, IPDentalShow = get_measurements_from_data(Patient._DentalShow._shape, Patient._DentalShow._lefteye, Patient._DentalShow._righteye, Patient._CalibrationType, Patient._CalibrationValue)

        # 1) EyeBrow Elevation at rest
    a_left, a_right = LeftRest.BrowHeight, RightRest.BrowHeight
    if Patient._HealthySide == 'Right':
        Brow_at_rest = a_left/a_right
    else:
        Brow_at_rest = a_right/a_left
    
    Brow_at_rest = np.round(Brow_at_rest*100,1)
    
    
    # 2) Palpebral Fissure width at rest
    c_left, c_right = LeftRest.PalpebralFissureHeight, RightRest.PalpebralFissureHeight

    if Patient._HealthySide == 'Right':
        PalpebralFissure_at_rest = c_right/c_left
    else:
        PalpebralFissure_at_rest = c_left/c_right
    
    PalpebralFissure_at_rest = np.round(PalpebralFissure_at_rest*100,1)
    
    # 3) Oral commissure at rest 
    e_right, d_right = np.sin((RightRest.SmileAngle-90)*np.pi/180)*RightRest.CommissureExcursion, np.cos((RightRest.SmileAngle-90)*np.pi/180)*RightRest.CommissureExcursion
    e_left, d_left = np.sin((LeftRest.SmileAngle-90)*np.pi/180)*LeftRest.CommissureExcursion, np.cos((LeftRest.SmileAngle-90)*np.pi/180)*LeftRest.CommissureExcursion
    if Patient._HealthySide == 'Right':
        #e_left is the disease side
        if e_left < e_right and e_left > 0:
            OralCommissure_at_rest = 1-((e_right - e_left)/e_right)
        else:
            OralCommissure_at_rest = d_left/d_right
    else:
        #e_right is the disease side
        if e_right < e_left and e_right > 0:
            OralCommissure_at_rest = 1-((e_left - e_right)/e_left)
        else:
            OralCommissure_at_rest = d_right/d_left
    
    OralCommissure_at_rest = np.round(OralCommissure_at_rest*100,1)
    
    #Static_Score = np.array([abs(100-Brow_at_rest), abs(100-PalpebralFissure_at_rest), abs(100-OralCommissure_at_rest )]).sum()
    #np.round(Static_Score,1)
    
    ##Dynamic Measures 
    # 4) Brow Elevation 
    b_left, b_right = LeftEyeBrow.BrowHeight, RightEyeBrow.BrowHeight
    if Patient._HealthySide == 'Right':
        EyeBrowElevation = (b_left - a_left)/(b_right - a_right)
    else:
        EyeBrowElevation = (b_right - a_right)/(b_left - a_left)
    
    
    EyeBrowElevation = np.round(EyeBrowElevation*100,1)
    
    # 5)Eye closure gentle 
    g_left_gentle, g_right_gentle = LeftEyeClosureGently.PalpebralFissureHeight , RightEyeClosureGently.PalpebralFissureHeight
    if g_left_gentle<1:g_left_gentle=0
    if g_right_gentle<1:g_right_gentle=0
    #g might be negative (measurement errors)
    if Patient._HealthySide == 'Right':
        GentleEyeClosure = (c_left - abs(g_left_gentle))/c_left
    else:
        GentleEyeClosure = (c_right - abs(g_right_gentle))/c_right
        
    GentleEyeClosure = np.round(GentleEyeClosure*100,1)
    
    # 6)Eye closure full 
    g_left_full, g_right_full = LeftEyeClosureTight.PalpebralFissureHeight, RightEyeClosureTight.PalpebralFissureHeight 
    if g_left_full<1:g_left_full=0
    if g_right_full<1:g_right_full=0
    if Patient._HealthySide == 'Right':
        FullEyeClosure = (c_left - abs(g_left_full))/c_left
    else:
        FullEyeClosure = (c_right - abs(g_right_full))/c_right
        
    FullEyeClosure = np.round(FullEyeClosure*100,1)
    
    
    # 6) Oral Commissure with Smile
    # question for Tessa -> Is this with small or large smile? I'll do it with large smile for the moment
    f_left, f_right = LeftRest.CommissureExcursion, RightRest.CommissureExcursion
    h_left, h_right = LeftLargeSmile.CommissureExcursion, RightLargeSmile.CommissureExcursion
    #if with small smile, then comment above line an uncomment line below
    # h_left, h_right = LeftSmallSmile.CommissureExcursion, RightSmallSmile.CommissureExcursion
    print(f_left, f_right,h_left, h_right)
    if Patient._HealthySide == 'Right':
        OralCommissureWithSmile =  (h_left - f_left)/(h_right - f_right)
    else:
        OralCommissureWithSmile = (h_right - f_right)/(h_left - f_left)
        
    OralCommissureWithSmile = np.round(OralCommissureWithSmile*100,1)
    
    #7) Lower Lip EEE
    
    j_left, j_right = LeftDentalShow.MouthOpen, RightDentalShow.MouthOpen
    if Patient._HealthySide == 'Right':
        #making sure that it will work if j_right is zero 
        try:
            LowerLipEEE = j_left/j_right
        except:
            LowerLipEEE = np.nan
    else:
        #making sure that it will work if j_left is zero 
        try:
            LowerLipEEE = j_right/j_left
        except:
            LowerLipEEE = np.nan  
        
    LowerLipEEE = np.round(LowerLipEEE*100,1)    
    
    #Dynamic_Score = np.array([abs(100-EyeBrowElevation), abs(100-GentleEyeClosure), abs(100-FullEyeClosure), abs(100-OralCommissureWithSmile), abs(100-LowerLipEEE)]).sum()
    #np.round(Dynamic_Score,1)
    
    
    ##Synkineis Measurements
    #Ocular synkinesis 
    k1_left, k1_right = LeftLargeSmile.PalpebralFissureHeight, RightLargeSmile.PalpebralFissureHeight
    k2_left, k2_right = LeftPuckeringLips.PalpebralFissureHeight, RightPuckeringLips.PalpebralFissureHeight
    if Patient._HealthySide == 'Right':
        OcularSynkinesis1 = k1_left/k1_right
        OcularSynkinesis2 = k2_left/k2_right
    else:
        OcularSynkinesis1 = k1_right/k1_left
        OcularSynkinesis2 = k2_right/k2_left
    
    if  OcularSynkinesis1 <=  OcularSynkinesis2:
         OcularSynkinesis =  OcularSynkinesis1 
    else:
         OcularSynkinesis =  OcularSynkinesis2
            
    OcularSynkinesis = np.round(OcularSynkinesis*100,1)
    
    
        #apply corrections to remove everything less than zero 
    if Brow_at_rest<0:Brow_at_rest=0
    if PalpebralFissure_at_rest<0:PalpebralFissure_at_rest=0
    if OralCommissure_at_rest<0:OralCommissure_at_rest=0
    if EyeBrowElevation<0:EyeBrowElevation=0
    if GentleEyeClosure<0:GentleEyeClosure=0
    if FullEyeClosure<0:FullEyeClosure=0
    if OralCommissureWithSmile<0:OralCommissureWithSmile=0
    if LowerLipEEE<0:LowerLipEEE=0
    if OcularSynkinesis<0:OcularSynkinesis=0
    
    
    
#    ##Computing the score based on Tessa's idea 
#    if Brow_at_rest<= 100:
    score_brow_rest = 100 - abs(100-Brow_at_rest)
    score_PalpebralFissure_rest = 100 - abs(100-PalpebralFissure_at_rest)
    score_OralCommissure_rest = 100 - abs(100-OralCommissure_at_rest)
    
    score_EyeBrowElevation = 100-abs(100-EyeBrowElevation)
    score_GentleEyeClosure = 100-abs(100-GentleEyeClosure)
    score_FullEyeClosure = 100- abs(100-FullEyeClosure)
    score_OralCommissureWithSmile = 100 - abs(100-OralCommissureWithSmile)
    score_LowerLipEEE = 100 - abs(100-LowerLipEEE)
    
    score_OcularSynkinesis = 100-abs(100-OcularSynkinesis)

    StaticScore = (score_brow_rest + score_PalpebralFissure_rest + score_OralCommissure_rest)/3
    DynamicScore = (score_EyeBrowElevation+score_GentleEyeClosure+ score_FullEyeClosure+score_OralCommissureWithSmile+score_LowerLipEEE)/5
    SynkinesisScore = score_OcularSynkinesis
    
    
    return Brow_at_rest, PalpebralFissure_at_rest, OralCommissure_at_rest, EyeBrowElevation, GentleEyeClosure, FullEyeClosure, OralCommissureWithSmile, LowerLipEEE, OcularSynkinesis, StaticScore, DynamicScore, SynkinesisScore

    
    #return Brow_at_rest, PalpebralFissure_at_rest, OralCommissure_at_rest, score_EyeBrowElevation, score_GentleEyeClosure, score_FullEyeClosure, score_OralCommissureWithSmile, score_LowerLipEEE, score_OcularSynkinesis, StaticScore, DynamicScore, SynkinesisScore

#    #Brow at Rest
#    if Patient._HealthySide == 'Right':
#        
#        DeltaBrow = RightEyeBrow.BrowHeight - RightRest.BrowHeight
#        
#        BrowatRest =  (LeftRest.BrowHeight - RightRest.BrowHeight)/DeltaBrow
#        
#    elif Patient._HealthySide == 'Left':
#        
#        DeltaBrow = LeftEyeBrow.BrowHeight - LeftRest.BrowHeight
#        
#        BrowatRest =  (RightRest.BrowHeight - LeftRest.BrowHeight)/DeltaBrow
#
#    #BrowatRest = abs(RightRest.BrowHeight - LeftRest.BrowHeight)
#      
#    #Brow Elevantion with Brow Raising 
#    if Patient._HealthySide == 'Right':
#        
#        DeltaBrow = RightEyeBrow.BrowHeight - RightRest.BrowHeight
#        
#        BrowatRaising =  (LeftEyeBrow.BrowHeight-LeftRest.BrowHeight)/DeltaBrow
#        
#        #BrowatRaising = LeftEyeBrow.BrowHeight - LeftRest.BrowHeight
#        
#    elif Patient._HealthySide == 'Left':
#        
#        DeltaBrow = LeftEyeBrow.BrowHeight - LeftRest.BrowHeight
#        
#        BrowatRaising =  (RightEyeBrow.BrowHeight - RightRest.BrowHeight)/DeltaBrow
#        
#        #BrowatRaising = RightEyeBrow.BrowHeight - RightRest.BrowHeight
#        
#
#
#    #Palpebral Fisure at Rest
#    PalpebralFissureRest = palpebral_fissure(Patient._Rest, Patient._CalibrationType, Patient._CalibrationValue) #[Rigth, Left]
#    if Patient._HealthySide == 'Right':
#        
#        DeltaPalpebralFissureRest = 1 - PalpebralFissureRest[1]/PalpebralFissureRest[0]
#        
#    elif Patient._HealthySide == 'Left':
#        
#        DeltaPalpebralFissureRest = 1 - PalpebralFissureRest[0]/PalpebralFissureRest[1] 
#      
#
#    #Oral commisure at rest
#    if Patient._HealthySide == 'Right':
#
#        #DeltaOralCommissure = RightLargeSmile.CommissureExcursion - RightRest.CommissureExcursion
#        
#        #OralCommissureatRest = (RightRest.CommissureExcursion - LeftRest.CommissureExcursion)/DeltaOralCommissure
#        
#        Comm_position_right = Patient._Rest._shape[48,1]
#        Comm_position_left = Patient._Rest._shape[54,1]
#        
#        if Comm_position_left <= Comm_position_right :
#            OralCommissureatRest = DeviationRest.CommisureHeightDeviation
#        else:
#            OralCommissureatRest = -DeviationRest.CommisureHeightDeviation    
#        
#        
#    elif Patient._HealthySide == 'Left':
#        #DeltaOralCommissure = LeftLargeSmile.CommissureExcursion - LeftRest.CommissureExcursion
#        
#        #OralCommissureatRest = (LeftRest.CommissureExcursion - RightRest.CommissureExcursion)/DeltaOralCommissure
#
#        Comm_position_right = Patient._Rest._shape[48,0]
#        Comm_position_left = Patient._Rest._shape[54,0]
#
#        if Comm_position_left <= Comm_position_right :
#            OralCommissureatRest = DeviationRest.CommisureHeightDeviation
#        else:
#            OralCommissureatRest = -DeviationRest.CommisureHeightDeviation
#
#
#    #Oral commisure with Smile
#    if Patient._HealthySide == 'Right':
#        
#        DeltaOralCommissure = RightLargeSmile.CommissureExcursion - RightRest.CommissureExcursion
#        
#        OralCommissureatSmile = (RightLargeSmile.CommissureExcursion - LeftLargeSmile.CommissureExcursion)/DeltaOralCommissure
#        
#        OralCommissureatSmile = LeftLargeSmile.CommissureExcursion/RightLargeSmile.CommissureExcursion-1 
#        
#    elif Patient._HealthySide == 'Left':
#
#        DeltaOralCommissure = LeftLargeSmile.CommissureExcursion - LeftRest.CommissureExcursion
#
#        OralCommissureatSmile = (LeftLargeSmile.CommissureExcursion - RightLargeSmile.CommissureExcursion)/DeltaOralCommissure
#
#        OralCommissureatSmile = RightLargeSmile.CommissureExcursion/LeftLargeSmile.CommissureExcursion - 1
#
#
#    #Palpebral Fisure at Gentle eye closure 
#    PalpebralFissureEyeClosureGently = palpebral_fissure(Patient._EyeClosureGently, Patient._CalibrationType, Patient._CalibrationValue) #[Rigth, Left]
#    if Patient._HealthySide == 'Right':
#        #Right eye is healthy, measure how much left eye is open with respect to paralized eye at rest 
#        GentleEyeClossure =  (PalpebralFissureEyeClosureGently[0]-PalpebralFissureEyeClosureGently[1])/PalpebralFissureRest[0]
#        
#    elif Patient._HealthySide == 'Left':
#         #Left eye is healthy, measure how much right eye is open with respect to paralized eye at rest 
#        GentleEyeClossure = (PalpebralFissureEyeClosureGently[1]-PalpebralFissureEyeClosureGently[0])/PalpebralFissureRest[1]
#        
#
#    #Palpebral Fisure at Tight eye closure 
#    PalpebralFissureEyeClosureTight = palpebral_fissure(Patient._EyeClosureTight, Patient._CalibrationType, Patient._CalibrationValue) #[Rigth, Left]
#    if Patient._HealthySide == 'Right':
#        #Right eye is healthy, measure how much left eye is open with respect to paralized eye at rest 
#        EyeClosureTight = (PalpebralFissureEyeClosureTight[0]-PalpebralFissureEyeClosureTight[1])/PalpebralFissureRest[0]
#        
#    elif Patient._HealthySide == 'Left':
#         #Left eye is healthy, measure how much right eye is open with respect to paralized eye at rest 
#        EyeClosureTight = (PalpebralFissureEyeClosureTight[1]-PalpebralFissureEyeClosureTight[0])/PalpebralFissureRest[1]
#
#    #lower lip movement with EEEE
#    if Patient._HealthySide == 'Right':
#        
#        #LowerLipMovementEEEE = LeftDentalShow.LoweLipActivation/RightDentalShow.LoweLipActivation
#        LowerLipMovementEEEE =  RightDentalShow.LowerLipElevation -  LeftDentalShow.LowerLipElevation 
#
#        
#    elif Patient._HealthySide == 'Left':
#        
#        #LowerLipMovementEEEE = RightDentalShow.LoweLipActivation/LeftDentalShow.LoweLipActivation
#        LowerLipMovementEEEE =  LeftDentalShow.LowerLipElevation - RightDentalShow.LowerLipElevation 
#
#    #Ocular Synkinesis 
#    PalpebralFissureLargeSmile = palpebral_fissure(Patient._LargeSmile, Patient._CalibrationType, Patient._CalibrationValue) #[Rigth, Left]
#    PalpebralFissurePuckeringLips = palpebral_fissure(Patient._PuckeringLips, Patient._CalibrationType, Patient._CalibrationValue) #[Rigth, Left]
#    if Patient._HealthySide == 'Right':
#        
#        DeltaPalpebralFissureLargeSmile = PalpebralFissureLargeSmile[1]/PalpebralFissureLargeSmile[0]
#        DeltaPalpebralFissurePuckeringLips = PalpebralFissurePuckeringLips[1]/PalpebralFissurePuckeringLips[0]
#                
#        OcularSynkinesis_Smile =   -(PalpebralFissureLargeSmile[0]-PalpebralFissureLargeSmile[1])/PalpebralFissureRest[0]        
#        #(PalpebralFissureLargeSmile[1]/PalpebralFissureRest[1]) / (PalpebralFissureLargeSmile[0]/PalpebralFissureRest[0])
#        OcularSynkinesis_Pucker =  -(PalpebralFissurePuckeringLips[0]-PalpebralFissurePuckeringLips[1])/PalpebralFissureRest[0]
#        #(PalpebralFissurePuckeringLips[1]/PalpebralFissureRest[1]) / (PalpebralFissurePuckeringLips[0]/PalpebralFissureRest[0])
#
#        
#    elif Patient._HealthySide == 'Left':
#        
#        DeltaPalpebralFissureLargeSmile = PalpebralFissureLargeSmile[0]/PalpebralFissureLargeSmile[1]
#        DeltaPalpebralFissurePuckeringLips = PalpebralFissurePuckeringLips[0]/PalpebralFissurePuckeringLips[1]
#        
#        OcularSynkinesis_Smile =  -(PalpebralFissureLargeSmile[1]-PalpebralFissureLargeSmile[0])/PalpebralFissureRest[1]  
#        #(PalpebralFissureLargeSmile[0]/PalpebralFissureRest[0]) / (PalpebralFissureLargeSmile[1]/PalpebralFissureRest[1])
#        OcularSynkinesis_Pucker =  -(PalpebralFissurePuckeringLips[1]-PalpebralFissurePuckeringLips[0])/PalpebralFissureRest[1]
#        #(PalpebralFissurePuckeringLips[0]/PalpebralFissureRest[0]) / (PalpebralFissurePuckeringLips[1]/PalpebralFissureRest[1])
#    
#
#    if OcularSynkinesis_Smile <= OcularSynkinesis_Pucker:
#        OcularSynkinesis = OcularSynkinesis_Smile
#    else:
#        OcularSynkinesis = OcularSynkinesis_Pucker
#    
#    
#    return BrowatRest, DeltaPalpebralFissureRest, OralCommissureatRest, BrowatRaising, GentleEyeClossure, EyeClosureTight, OralCommissureatSmile, LowerLipMovementEEEE,OcularSynkinesis
        
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
        
        self.spacerh = QtWidgets.QWidget(self)
        self.spacerh.setFixedSize(10,0)
        
        self.spacerv = QtWidgets.QWidget(self)
        self.spacerv.setFixedSize(0,10)
        
       
        
        newfont = QtGui.QFont("Times", 12)
                

        
        RestingBrow_label = QLabel('Resting Brow:')
        RestingBrow_label.setFont(newfont)
        self._RestingBrow_measure =QLineEdit(self)
        self._RestingBrow_measure.setFont(newfont)
        self._RestingBrow_measure.setFixedWidth(100)
        #self._RestingBrow_eFACE =QLineEdit(self)
        #self._RestingBrow_eFACE.setFont(newfont)   
        #self._RestingBrow_eFACE.setFixedWidth(100)


        RestingPalpebralFissure_label = QLabel('Resting Palpebral Fissure:')
        RestingPalpebralFissure_label.setFont(newfont)
        self._RestingPalpebralFissure_measure =QLineEdit(self)
        self._RestingPalpebralFissure_measure.setFont(newfont)
        self._RestingPalpebralFissure_measure.setFixedWidth(100)
        #self._RestingPalpebralFissure_eFACE =QLineEdit(self)
        #self._RestingPalpebralFissure_eFACE.setFont(newfont)
        #self._RestingPalpebralFissure_eFACE.setFixedWidth(100)
        
        
        OralCommissureatRest_label = QLabel('Oral Commissure at Rest:')
        OralCommissureatRest_label.setFont(newfont)
        OralCommissureatRest_label.setFixedWidth(300)
        self._OralCommissureatRest_measure =QLineEdit(self)
        self._OralCommissureatRest_measure.setFont(newfont)
        self._OralCommissureatRest_measure.setFixedWidth(100)
        #self._OralCommissureatRest_eFACE =QLineEdit(self)
        #self._OralCommissureatRest_eFACE.setFont(newfont)
        #self._OralCommissureatRest_eFACE.setFixedWidth(100)
        
        
        
        StaticBox = QtWidgets.QGroupBox('Static Parameters')
        StaticBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        StaticBoxLayout = QtWidgets.QGridLayout()
        
        
        StaticBoxLayout.addWidget(RestingBrow_label,0,0,1,1)
        StaticBoxLayout.addWidget(self._RestingBrow_measure,0,1,1,1)
        #percent_Label=QLabel('%'); percent_Label.setFont(newfont)
        #StaticBoxLayout.addWidget(percent_Label,0,2,1,1)
        #StaticBoxLayout.addWidget(self.spacerv,0,3,1,1)
        #StaticBoxLayout.addWidget(self._RestingBrow_eFACE,0,4,1,1)
        
        StaticBoxLayout.addWidget(RestingPalpebralFissure_label,1,0,1,1)
        StaticBoxLayout.addWidget(self._RestingPalpebralFissure_measure,1,1,1,1)
        #percent_Label=QLabel('%'); percent_Label.setFont(newfont)
        #StaticBoxLayout.addWidget(percent_Label,1,2,1,1)
        #StaticBoxLayout.addWidget(self.spacerv,1,3,1,1)
        #StaticBoxLayout.addWidget(self._RestingPalpebralFissure_eFACE,1,4,1,1)
        
        StaticBoxLayout.addWidget(OralCommissureatRest_label,2,0,1,1)
        StaticBoxLayout.addWidget(self._OralCommissureatRest_measure,2,1,1,1)
        #percent_Label=QLabel('%'); percent_Label.setFont(newfont)
        #StaticBoxLayout.addWidget(percent_Label,2,2,1,1)
        #StaticBoxLayout.addWidget(self.spacerv,2,3,1,1)
        #StaticBoxLayout.addWidget(self._OralCommissureatRest_eFACE,2,4,1,1)

        StaticBox.setLayout(StaticBoxLayout)
        
        
        
        
        BrowElevation_label = QLabel('Brow Elevation:')
        BrowElevation_label.setFont(newfont)
        self._BrowElevation_measure =QLineEdit(self)
        self._BrowElevation_measure.setFont(newfont)
        self._BrowElevation_measure.setFixedWidth(100)
        #self._BrowElevation_eFACE =QLineEdit(self)
        #self._BrowElevation_eFACE.setFont(newfont)
        #self._BrowElevation_eFACE.setFixedWidth(100)
        
        
        GentleEyeClosure_label = QLabel('Gentle Eye Closure:')
        GentleEyeClosure_label.setFont(newfont)
        self._GentleEyeClosure_measure =QLineEdit(self)
        self._GentleEyeClosure_measure.setFont(newfont)
        self._GentleEyeClosure_measure.setFixedWidth(100)
        #self._GentleEyeClosure_eFACE =QLineEdit(self)
        #self._GentleEyeClosure_eFACE.setFont(newfont)
        #self._GentleEyeClosure_eFACE.setFixedWidth(100)
        
        
        FullEyeClosure_label = QLabel('Full Eye Closure:')
        FullEyeClosure_label.setFont(newfont)
        self._FullEyeClosure_measure =QLineEdit(self)
        self._FullEyeClosure_measure.setFont(newfont)
        self._FullEyeClosure_measure.setFixedWidth(100)
        #self._FullEyeClosure_eFACE =QLineEdit(self)
        #self._FullEyeClosure_eFACE.setFont(newfont)    
        #self._FullEyeClosure_eFACE.setFixedWidth(100)
        
        
        OralCommissureMovementwithSmile_label = QLabel('Oral Commissure Movement with Smile:')
        OralCommissureMovementwithSmile_label.setFont(newfont)
        OralCommissureMovementwithSmile_label.setFixedWidth(300)
        self._OralCommissureMovementwithSmile_measure =QLineEdit(self)
        self._OralCommissureMovementwithSmile_measure.setFont(newfont)
        self._OralCommissureMovementwithSmile_measure.setFixedWidth(100)
        #self._OralCommissureMovementwithSmile_eFACE =QLineEdit(self)
        #self._OralCommissureMovementwithSmile_eFACE.setFont(newfont) 
        #self._OralCommissureMovementwithSmile_eFACE.setFixedWidth(100)
        
        
        LowerLipMovement_label = QLabel('Lower Lip Movement:')
        LowerLipMovement_label.setFont(newfont)
        self._LowerLipMovement_measure =QLineEdit(self)
        self._LowerLipMovement_measure.setFont(newfont)
        self._LowerLipMovement_measure.setFixedWidth(100)
        #self._LowerLipMovement_eFACE =QLineEdit(self)
        #self._LowerLipMovement_eFACE.setFont(newfont) 
        #self._LowerLipMovement_eFACE.setFixedWidth(100)
        
        
        DynamicBox = QtWidgets.QGroupBox('Dynamic Parameters')
        DynamicBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        DynamicBoxLayout = QtWidgets.QGridLayout()
        
        DynamicBoxLayout.addWidget(BrowElevation_label,0,0,1,1)
        DynamicBoxLayout.addWidget(self._BrowElevation_measure,0,1,1,1)
        #percent_Label=QLabel('%'); percent_Label.setFont(newfont)
        #DynamicBoxLayout.addWidget(percent_Label,0,2,1,1)
        #DynamicBoxLayout.addWidget(self.spacerv,0,3,1,1)
        #DynamicBoxLayout.addWidget(self._BrowElevation_eFACE,0,4,1,1)
        
        DynamicBoxLayout.addWidget(GentleEyeClosure_label,1,0,1,1)
        DynamicBoxLayout.addWidget(self._GentleEyeClosure_measure,1,1,1,1)
        #percent_Label=QLabel('%'); percent_Label.setFont(newfont)
        #DynamicBoxLayout.addWidget(percent_Label,1,2,1,1)
        #DynamicBoxLayout.addWidget(self.spacerv,1,3,1,1)
        #DynamicBoxLayout.addWidget(self._GentleEyeClosure_eFACE,1,4,1,1)
        
        DynamicBoxLayout.addWidget(FullEyeClosure_label,2,0,1,1)
        DynamicBoxLayout.addWidget(self._FullEyeClosure_measure,2,1,1,1)
        #percent_Label=QLabel('%'); percent_Label.setFont(newfont)
        #DynamicBoxLayout.addWidget(percent_Label,2,2,1,1)
        #DynamicBoxLayout.addWidget(self.spacerv,2,3,1,1)
        #DynamicBoxLayout.addWidget(self._FullEyeClosure_eFACE,2,4,1,1)     
        
        DynamicBoxLayout.addWidget(OralCommissureMovementwithSmile_label,3,0,1,1)
        DynamicBoxLayout.addWidget(self._OralCommissureMovementwithSmile_measure,3,1,1,1)
        #percent_Label=QLabel('%'); percent_Label.setFont(newfont)
        #DynamicBoxLayout.addWidget(percent_Label,3,2,1,1)
        #DynamicBoxLayout.addWidget(self.spacerv,3,3,1,1)
        #DynamicBoxLayout.addWidget(self._OralCommissureMovementwithSmile_eFACE,3,4,1,1)         
        
        DynamicBoxLayout.addWidget(LowerLipMovement_label,4,0,1,1)
        DynamicBoxLayout.addWidget(self._LowerLipMovement_measure,4,1,1,1)
        #percent_Label=QLabel('mm'); percent_Label.setFont(newfont)
        #DynamicBoxLayout.addWidget(percent_Label,4,2,1,1)
        #DynamicBoxLayout.addWidget(self.spacerv,4,3,1,1)
        #DynamicBoxLayout.addWidget(self._LowerLipMovement_eFACE,4,4,1,1)   
        
        DynamicBox.setLayout(DynamicBoxLayout)
        
        
        OcularSynkenisis_label = QLabel('Ocular Synkinesis:')
        OcularSynkenisis_label.setFont(newfont)
        OcularSynkenisis_label.setFixedWidth(300)
        self._OcularSynkenisis_measure =QLineEdit(self)
        self._OcularSynkenisis_measure.setFont(newfont)
        self._OcularSynkenisis_measure.setFixedWidth(100)
        #self._OcularSynkenisis_eFACE =QLineEdit(self)
        #self._OcularSynkenisis_eFACE.setFont(newfont) 
        #self._OcularSynkenisis_eFACE.setFixedWidth(100)
        
        
        SynkenisisBox = QtWidgets.QGroupBox('Synkinesis Parameter')
        SynkenisisBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        SynkenisisBoxLayout = QtWidgets.QGridLayout()
        
        SynkenisisBoxLayout.addWidget(OcularSynkenisis_label,0,0,1,1)
        SynkenisisBoxLayout.addWidget(self._OcularSynkenisis_measure,0,1,1,1)
        #percent_Label=QLabel('%'); percent_Label.setFont(newfont)
        #SynkenisisBoxLayout.addWidget(percent_Label,0,2,1,1)
        #SynkenisisBoxLayout.addWidget(self.spacerv,0,3,1,1)
        #SynkenisisBoxLayout.addWidget(self._OcularSynkenisis_eFACE,0,4,1,1)
        
        SynkenisisBox.setLayout(SynkenisisBoxLayout)
        
        
        #buttons        
        DoneButton = QPushButton('&Save', self)
        DoneButton.setFixedWidth(150)
        DoneButton.setFont(newfont)
        DoneButton.clicked.connect(self.Done)
        
        CancelButton = QPushButton('&Close', self)
        CancelButton.setFixedWidth(150)
        CancelButton.setFont(newfont)
        CancelButton.clicked.connect(self.Cancel)
        
        ButtonLayout = QtWidgets.QHBoxLayout()
        ButtonLayout.addWidget(DoneButton)
        ButtonLayout.addWidget(CancelButton)
        
        
        #Top Labels
        #Measure_Label = QLabel('Scores')
        #Measure_Label.setFont(newfont)
        #Measure_Label.setFixedWidth(100)
        #Measure_Label.setAlignment(QtCore.Qt.AlignCenter)
        
        
        
        #eFACE_Label = QLabel('Total')
        #eFACE_Label.setFont(newfont)
        #eFACE_Label.setFixedWidth(100)
        #eFACE_Label.setAlignment(QtCore.Qt.AlignCenter)
        
        #empty_Label = QLabel('')
        #empty_Label.setFixedWidth(325)
        
#        TopLabelsLayout = QtWidgets.QHBoxLayout()
#        TopLabelsLayout.addWidget(empty_Label)
#        TopLabelsLayout.addWidget(Measure_Label)
#        TopLabelsLayout.addWidget(QLabel(''))
#        TopLabelsLayout.addWidget(eFACE_Label)
#        
        #TopLabelsLayout = QGridLayout()
        #TopLabelsLayout.addWidget(empty_Label,0,0)
        #TopLabelsLayout.addWidget(Measure_Label,0,1)
        #TopLabelsLayout.addWidget(QLabel(''),0,2)
        #TopLabelsLayout.addWidget(self.spacerv,0,3)
        #TopLabelsLayout.addWidget(eFACE_Label,0,4)
        
    
        
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
       

        StaticScore_label = QLabel('Static Score:')
        StaticScore_label.setFont(newfont)
        self._StaticScore_measure =QLineEdit(self)
        self._StaticScore_measure.setFont(newfont)
        self._StaticScore_measure.setFixedWidth(100)

        DynamicScore_label = QLabel('Dynamic Score:')
        DynamicScore_label.setFont(newfont)
        self._DynamicScore_measure =QLineEdit(self)
        self._DynamicScore_measure.setFont(newfont)
        self._DynamicScore_measure.setFixedWidth(100)
        
        
        SynkinesisScore_label = QLabel('Synkinesis Score:')
        SynkinesisScore_label.setFont(newfont)
        self._SynkinesisScore_measure =QLineEdit(self)
        self._SynkinesisScore_measure.setFont(newfont)
        self._SynkinesisScore_measure.setFixedWidth(100)
        
        TotalScore_label = QLabel('Total Score:')
        TotalScore_label.setFont(newfont)
        self._TotalScore_measure =QLineEdit(self)
        self._TotalScore_measure.setFont(newfont)
        self._TotalScore_measure.setFixedWidth(100)
        
        TotalsBox = QtWidgets.QGroupBox('Total Scores')
        TotalsBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        TotalsBoxLayout = QtWidgets.QGridLayout()
        TotalsBoxLayout.addWidget(StaticScore_label,0,0,1,1)
        TotalsBoxLayout.addWidget(self._StaticScore_measure,0,1,1,1)
        TotalsBoxLayout.addWidget(DynamicScore_label,1,0,1,1)
        TotalsBoxLayout.addWidget(self._DynamicScore_measure,1,1,1,1)       
        TotalsBoxLayout.addWidget(SynkinesisScore_label,2,0,1,1)
        TotalsBoxLayout.addWidget(self._SynkinesisScore_measure,2,1,1,1)
        TotalsBoxLayout.addWidget(TotalScore_label,3,0,1,1)
        TotalsBoxLayout.addWidget(self._TotalScore_measure,3,1,1,1)

        TotalsBox.setLayout(TotalsBoxLayout)
        
        
        
        layout = QtWidgets.QVBoxLayout()
        #layout.addLayout(TopLabelsLayout)
        #layout.addWidget(self.spacerv)
        layout.addWidget(StaticBox)
        layout.addWidget(self.spacerv)
        layout.addWidget(DynamicBox)
        layout.addWidget(self.spacerv)
        layout.addWidget(SynkenisisBox)
        layout.addWidget(self.spacerv)
        layout.addWidget(TotalsBox)
        layout.addWidget(self.spacerv)
        layout.addLayout(ButtonLayout)
                
        self.setLayout(layout)
        #self.main_widget.setFocus()
        #self.setCentralWidget(self.main_widget)
        
       
                #compute measures and update window
        BrowatRest, DeltaPalpebralFissureRest, OralCommissureatRest, BrowatRaising, GentleEyeClossure, EyeClosureTight, OralCommissureatSmile, LowerLipMovementEEEE,OcularSynkinesis, StaticScore, DynamicScore, SynkinesisScore = Compute_eFace(self._Patient)
    

        self._RestingBrow_measure.setText(str(np.round(BrowatRest,1)))
        self._RestingPalpebralFissure_measure.setText(str(np.round(DeltaPalpebralFissureRest,1)))
        self._OralCommissureatRest_measure.setText(str(np.round(OralCommissureatRest,3)))
        self._BrowElevation_measure.setText(str(np.round(BrowatRaising,1)))
        self._GentleEyeClosure_measure.setText(str(np.round(GentleEyeClossure,1)))
        self._FullEyeClosure_measure.setText(str(np.round(EyeClosureTight,1)))
        self._OralCommissureMovementwithSmile_measure.setText(str(np.round(OralCommissureatSmile,1))) 
        self._LowerLipMovement_measure.setText(str(np.round(LowerLipMovementEEEE,1)))
        self._OcularSynkenisis_measure.setText(str(np.round(OcularSynkinesis,1)))
        
        self._StaticScore_measure.setText(str(np.round(StaticScore,1)))
        self._DynamicScore_measure.setText(str(np.round(DynamicScore,1)))
        self._SynkinesisScore_measure.setText(str(np.round(SynkinesisScore,1)))
        self._TotalScore_measure.setText(str(np.round((StaticScore + DynamicScore + SynkinesisScore)/3,1)))
        
        #self.setFixedSize(self.size())

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
            f.write("Brow at Rest:    %s %%,    %s \n" % (self._RestingBrow_measure.text()))
            f.write("Palpebral Fissure at Rest:    %s %%,    %s \n" % (self._RestingPalpebralFissure_measure.text()))
            f.write("Oral Commisure at Rest:    %s mm,    %s \n" % (self._OralCommissureatRest_measure.text()))
            f.write('---Dynamic Measures \n')
            f.write("Brow Elevation:    %s %%,    %s \n" % (self._BrowElevation_measure.text()))
            f.write("Gentle Eye Closure:    %s %%,    %s \n" % (self._GentleEyeClosure_measure.text()))
            f.write("Full Eye Closure:    %s %%,    %s \n" % (self._FullEyeClosure_measure.text()))
            f.write("Oral Commissure Movement with Smile:    %s %%,    %s \n" % (self._OralCommissureMovementwithSmile_measure.text()))
            f.write("Lower Lip Movement:    %s mm,    %s \n" % (self._LowerLipMovement_measure.text(), self._LowerLipMovement_eFACE.text()))
            f.write('---Synkenisis Measures \n')
            f.write("Ocular Synkenisis:    %s mm,    %s" % (self._OcularSynkenisis_measure.text()))
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
    app = QtWidgets.QApplication([])
#    if not QtWidgets.QApplication.instance():
#        app = QtWidgets.QApplication(sys.argv)
#    else:
#        app = QtWidgets.QApplication.instance()
       
    GUI = ReportCard()
    GUI.show()
    app.exec_()    