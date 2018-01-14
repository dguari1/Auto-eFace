# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 13:45:49 2018

@author: guarind
"""

import numpy as np

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
    
    LeftPuckeringLips, RightPuckeringLips, _, _ = get_measurements_from_data(Patient._PuckeringLips._shape, Patient._PuckeringLips._lefteye, Patient._PuckeringLips._righteye, Patient._CalibrationType, Patient._CalibrationValue)
    
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
    

    
    print(BrowatRest, BrowatRaising,DeltaPalpebralFissureRest, OralCommissureatRest, OralCommissureatSmile)
        
    