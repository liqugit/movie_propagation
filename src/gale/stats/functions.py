'''
Generic statistical functions.
'''

def gini(data):
    '''
    Calculates the gini coefficient for a given dataset.
    input:
        data- list of values, either raw counts or frequencies. 
              Frequencies MUST sum to 1.0, otherwise will be transformed to frequencies
              If raw counts data will be transformed to frequencies.
    output:
        gini- float, from 0.0 to 1.0 (1.0 most likely never realized since it is
              only achieved in the limit)
    '''
    
    def _unit_area(height, value, width):
        '''
        Calculates a single bars area.
        Area is composed of two parts:
            The height of the bar up until that point
            The addition from the current value (calculated as a triangle)
        input:
            height: previous bar height or sum of values up to current value
            value: current value
            width: width of individual bar
        output:
            bar_area: area of current bar
        '''
        bar_area = (height * width) + ((value * width) / 2.)
        return bar_area
    
    #Fair area will always be 0.5 when frequencies are used
    fair_area = 0.5
    #Check that input data has non-zero values, if not throw an error
    datasum = float(sum(data))
    if datasum==0:
        import gale.general.errors as gerr
        m = 'Data sum is 0.0.\nCannot calculate Gini coefficient for non-responsive population.'
        gerr.generic_error_handler(message=m)
    #If data does not sum to 1.0 transform to frequencies
    if datasum!=1.0:
        data = [x/datasum for x in data]
    #Calculate the area under the curve for the current dataset
    data.sort()
    width = 1/float(len(data))
    height, area = 0.0, 0.0
    for value in data:
        area += _unit_area(height, value, width)
        height += value
    #Calculate the gini
    gini = (fair_area-area)/fair_area
    return gini

def calc_z(obs, exp):
    '''
    Calculates the z for two independent quantities as:
    z = (obs - exp)/se_diff
    where se_diff is
    se_diff = sqrt(a**2 + b**2)
    with a being the SE for the first quantity and b the SE for the second quantity
    Input:
        obs - Tuple containing (quantity, SE)
        exp - Tuple containing (quantity, SE)
    Output:
        z - float
    '''
    import numpy as np
    se_diff = np.sqrt(obs[1]**2 + exp[1]**2)
    if se_diff != 0:
        z = (obs[0] - exp[0])/se_diff
    else:
        z = 0
    return z

def baseline_normalizer(obs, exp):
    '''
    Rescales the observation (either a single value or list) by the expected value
    input:
        obs -- int/float or list of int/floats
        exp -- int/float
    output:
        norm -- int/float or list of int/floats
    '''
    if type(obs)==list:
        norm = [ival/float(exp) for ival in obs]
    else:
        norm = ival/float(exp)
    return norm
