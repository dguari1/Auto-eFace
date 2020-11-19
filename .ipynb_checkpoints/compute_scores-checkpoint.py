# -*- coding: utf-8 -*-
"""
Created on Fri May 31 10:34:10 2019

@author: GUARIND
"""

import numpy as np
import pandas as pd
import os
from utilities import get_info_from_txt
from measurements import get_measurements_from_data
import cv2

def compute_health_score(path_, Healthy_Side, pandas_df=None):
    
    path_= path_
    all_Files = os.listdir(path_)
    all_Files.sort()
    ext_txt=('.txt')
    Files = [i for i in all_Files if i.endswith(tuple(ext_txt))];  
    ext_jpg=('.jpg')
    Images = [i for i in all_Files if i.endswith(tuple(ext_jpg))];  
    
    shape=[]
    lefteye = []
    righteye = []
    boundingbox = []
    for file in Files:
        try:
            shape_, lefteye_, righteye_, boundingbox_ = get_info_from_txt(os.path.join(path_,file))
        except:
            print(os.path.join(path_,file))
            return
        
        shape.append(shape_) 
        lefteye.append(lefteye_)
        righteye.append(righteye_)
        boundingbox.append(boundingbox_)  
        
    CalibrationType='Iris'
    CalibrationValue=11.77
    LeftRest, RightRest, _, _,IPrest = get_measurements_from_data(shape[0], lefteye[0],righteye[0], CalibrationType, CalibrationValue)
    LeftEyeBrow, RightEyeBrow, _, _, IPEyeBrow = get_measurements_from_data(shape[1], lefteye[1],righteye[1], CalibrationType, CalibrationValue)
    LeftEyeClosureGently, RightEyeClosureGently, _, _, IPEyeClosureGently = get_measurements_from_data(shape[2], lefteye[2],righteye[2], CalibrationType, CalibrationValue)
    LeftEyeClosureTight, RightEyeClosureTight, _, _, IPEyeClosureTight = get_measurements_from_data(shape[3], lefteye[3],righteye[3], CalibrationType, CalibrationValue)
    LeftSmallSmile, RightSmallSmile, _, _, IPSmallSmile = get_measurements_from_data(shape[4], lefteye[4],righteye[4], CalibrationType, CalibrationValue)
    LeftLargeSmile, RightLargeSmile, _, _, IPLargeSmile = get_measurements_from_data(shape[5], lefteye[5],righteye[5], CalibrationType, CalibrationValue)
    LeftPuckeringLips, RightPuckeringLips, _, _, IPPuckeringLips = get_measurements_from_data(shape[6], lefteye[6],righteye[6], CalibrationType, CalibrationValue)
    LeftDentalShow, RightDentalShow, _, _, IPDentalShow = get_measurements_from_data(shape[7], lefteye[7],righteye[7], CalibrationType, CalibrationValue)
    
    
    ##Static Measures 
    # I'm following Tessa's nomenclature 

    # 1) EyeBrow Elevation at rest
    a_left, a_right = LeftRest.BrowHeight, RightRest.BrowHeight
    if Healthy_Side == 'Right':
        Brow_at_rest = a_left/a_right
    else:
        Brow_at_rest = a_right/a_left
    
    Brow_at_rest = np.round(Brow_at_rest*100,1)
    
    
    # 2) Palpebral Fissure width at rest
    c_left, c_right = LeftRest.PalpebralFissureHeight, RightRest.PalpebralFissureHeight

    if Healthy_Side == 'Right':
        PalpebralFissure_at_rest = c_right/c_left
    else:
        PalpebralFissure_at_rest = c_left/c_right
    
    PalpebralFissure_at_rest = np.round(PalpebralFissure_at_rest*100,1)
    
    # 3) Oral commissure at rest 
    e_right, d_right = np.sin((RightRest.SmileAngle-90)*np.pi/180)*RightRest.CommissureExcursion, np.cos((RightRest.SmileAngle-90)*np.pi/180)*RightRest.CommissureExcursion
    e_left, d_left = np.sin((LeftRest.SmileAngle-90)*np.pi/180)*LeftRest.CommissureExcursion, np.cos((LeftRest.SmileAngle-90)*np.pi/180)*LeftRest.CommissureExcursion
    if Healthy_Side == 'Right':
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
    if Healthy_Side == 'Right':
        EyeBrowElevation = (b_left - a_left)/(b_right - a_right)
    else:
        EyeBrowElevation = (b_right - a_right)/(b_left - a_left)
    
    
    EyeBrowElevation = np.round(EyeBrowElevation*100,1)
    
    # 5)Eye closure gentle 
    g_left_gentle, g_right_gentle = LeftEyeClosureGently.PalpebralFissureHeight , RightEyeClosureGently.PalpebralFissureHeight
    if g_left_gentle<1:g_left_gentle=0
    if g_right_gentle<1:g_right_gentle=0
    #g might be negative (measurement errors)
    if Healthy_Side == 'Right':
        GentleEyeClosure = (c_left - abs(g_left_gentle))/c_left
    else:
        GentleEyeClosure = (c_right - abs(g_right_gentle))/c_right
        
    GentleEyeClosure = np.round(GentleEyeClosure*100,1)
    
    # 6)Eye closure full 
    g_left_full, g_right_full = LeftEyeClosureTight.PalpebralFissureHeight, RightEyeClosureTight.PalpebralFissureHeight 
    if g_left_full<1:g_left_full=0
    if g_right_full<1:g_right_full=0
    if Healthy_Side == 'Right':
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
    if Healthy_Side == 'Right':
        OralCommissureWithSmile =  (h_left - f_left)/(h_right - f_right)
    else:
        OralCommissureWithSmile = (h_right - f_right)/(h_left - f_left)
        
    OralCommissureWithSmile = np.round(OralCommissureWithSmile*100,1)
    
    #7) Lower Lip EEE
    
    j_left, j_right = LeftDentalShow.DentalShow, RightDentalShow.DentalShow
    if Healthy_Side == 'Right':
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
    if Healthy_Side == 'Right':
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

    print(score_brow_rest ,score_PalpebralFissure_rest,score_OralCommissure_rest)

    StaticScore = (score_brow_rest + score_PalpebralFissure_rest + score_OralCommissure_rest)/3
    DynamicScore = (score_EyeBrowElevation+score_GentleEyeClosure+ score_FullEyeClosure+score_OralCommissureWithSmile+score_LowerLipEEE)/5
    SynkinesisScore = score_OcularSynkinesis
    
    
    TotalScore = (StaticScore+DynamicScore+SynkinesisScore)/3
    #StaticScore, DynamicScore, SynkinesisScore ,TotalScore 
    
    
    if pandas_df is not None: #Save results in a data frame
        
        df_columns = ['Diagnosis', 'Subject', 'Healthy_Side', 'Eyebrow at Rest','Palpebral Fissure at Rest', 'Oral Commissure at Rest', 'Static Score', 'Eyebrow Elevation',
                      'Gentle Eye Closure','Full Eye Closure', 'Oral Commissure with Smile','Lower Lip with EEE', 'Dynamic Score','Ocular Synkenisis', 'Total Score']
        
        #create the dataframe and set the index
        if os.path.isfile(pandas_df): #the dataframe alreasy exists, opne it
            DataFrame = pd.read_csv(pandas_df, index_col = 0 )
        else: #the file doesn't exist, create it 
            DataFrame = pd.DataFrame(columns = df_columns)
        
        if 'normal' in path_:
            diag = 'normal'
        elif 'completeflaccid' in path_:
            diag = 'completeflaccid'
        else:
            diag = 'completeSynkinetic'
                
        subject = path_.split('\\')[-1]
        
        #datus = [diag, subject, Healthy_Side, Brow_at_rest, PalpebralFissure_at_rest, OralCommissure_at_rest, StaticScore,
        #         EyeBrowElevation, GentleEyeClosure, FullEyeClosure, OralCommissureWithSmile, LowerLipEEE, DynamicScore,
        #         OcularSynkinesis, TotalScore]
        
        datus = [diag, subject, Healthy_Side, Brow_at_rest, PalpebralFissure_at_rest, OralCommissure_at_rest, StaticScore,
                 score_EyeBrowElevation, score_GentleEyeClosure, score_FullEyeClosure, score_OralCommissureWithSmile, score_LowerLipEEE, DynamicScore,
                 score_OcularSynkinesis, TotalScore]
        
        DataFrame = DataFrame.append(pd.Series(datus,index = df_columns), 
                           ignore_index = True)
        
        DataFrame.to_csv(pandas_df)
        
        

    