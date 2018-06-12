'''
File: healthlink.py
Author: Adam Pah
Description: 
Functions related explicitly to healthlink
'''

def translate_race(in_race):
    '''
    input:
        in_race as a float/int
    output:
        race as string
    '''
    race_trans = {1: 'American Indian', 
                  2: 'Asian', 
                  3: 'Black', 
                  4: 'Hispanic', 
                  5: 'Pacific Islander', 
                  6: 'White', 
                  7: 'Declined', 
                  8: 'Other'}
    try:
        trace = race_trans[int(in_race)]
    except:
        trace = in_race
    return trace

def translate_gender(in_gender):
    '''
    input:
        in_gender as a float/int
    output:
        gender as string
    '''
    gender_trans = {1: 'Male',
                    2: 'Female',
                    3: 'Other'}
    try:
        tgender = gender_trans[int(in_gender)]
    except:
        tgender = in_gender
    return tgender

def translate_insurance(in_insurance):
    insurance_trans = {1: 'Medicare',
                       2: 'Medicaid',
                       3: 'Private Insurance',
                       4: 'Self-pay',
                       5: 'No Charge',
                       6: 'Other'}
    try:
        tinsurance = insurance_trans[int(in_insurance)]
    except:
        tinsurance = in_insurance
    return tinsurance

    
