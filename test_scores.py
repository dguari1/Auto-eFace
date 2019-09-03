# -*- coding: utf-8 -*-
"""
Created on Fri May 31 13:17:28 2019

@author: GUARIND
"""


from compute_scores import compute_health_score


directories =[
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\normal\normal1',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\normal\normal2',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\normal\normal3',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\normal\normal4',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\normal\normal5',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\normal\normal6',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\normal\normal7',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\normal\normal8',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\normal\normal9',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\normal\normal10',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\completeflaccid\1095725',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\completeflaccid\1106559',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\completeflaccid\1114470',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\completeflaccid\1126204',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\completeflaccid\Cleary',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\completesynkinetic\1117761',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\completesynkinetic\1119591',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\completesynkinetic\1126430',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\completesynkinetic\7757439',
        r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\Corrected\completesynkinetic\Roth'
        ]


Healthy_side = [
        'Right',
        'Right',
        'Right',
        'Right',
        'Right',
        'Right',
        'Right',
        'Right',
        'Right',
        'Right',
        'Right', 
        'Left',
        'Left', 
        'Right',
        'Right',
        'Left',
        'Left',
        'Right',
        'Right',
        'Right',
        ]

pd =  r'C:\Users\guarind\Documents\GitHub\Auto-eFace\images\results_new2.csv'

for directory, side in zip(directories, Healthy_side):
    compute_health_score(directory, side, pd)
    