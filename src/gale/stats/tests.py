'''
File: tests.py
Author: Adam Pah
Description: 
Standard statistical tests
'''

def stitch_dictionaries(di, dj, *args):
    '''
    input:
        Must be at least two, can be arbitrarily large
        * dictionary 1 (similarly keyed)
        * dictionary 2 (similarly keyed)
        * other argument dictionaries (could be arbitrary)
    ouptut:
        * pandas dataframe
    '''
    import pandas as pd
    
    def _transform_dictionary_to_keyvalue(tdict, i):
        '''
        input:
            * dictionary {'key': value}
            * i - enumerated to key the column to remove duplicates
        output:
            * dictionary {'key': ['key1', 'key2'], 'i': ['value1', 'value2']}
        '''
        rdict = {'key': [], i: []}
        for tk, tv in tdict.items():
            rdict['key'].append(tk)
            rdict[i].append(tv)
        return rdict

    def _merge_dataframe_list(tdf, tdf_list):
        '''
        Merge the dataframes in the list
        '''
        mtdf = pd.merge(tdf, tdf_list[0], on='key')
        del tdf_list[0]
        return mtdf, tdf_list
        
    #Assemble the list of dictionaries
    dlist = [di, dj]
    dlist += args
    #Transform the dictionaries to dataframes
    dlist = [pd.DataFrame(_transform_dictionary_to_keyvalue(x, str(i))) \
             for i, x in enumerate(dlist)]
    #Successively make the dataframe
    ftdf = dlist[0]
    del dlist[0]
    while dlist:
        ftdf, dlist = _merge_dataframe_list(ftdf, dlist)
    return ftdf

def calculate_mse_pt(known, predicted):
    '''
    Returns the mse for a point, provided known and predicted
    input:
        * known -- float type
        * predicted -- float type
    output:
        * mse
    '''
    return (known - predicted) ** 2

def calculate_mse(known, predicted):
    '''
    input:
        * dictionary of known values
        * dicionary of predicted values
    output:
        * mean squared error. (in latex)
          $\frac{1}{n} \sum_{i=1}^n (y_i - \hat{y}_i)^2$
    '''
    n = 0
    mse = 0.0
    for kkey, kvalue in known.items():
        if kkey in predict:
            pvalue = predicted[kkey]
            mse += (float(kvalue) - float(pvalue)) ** 2
            n += 1
    mse = mse/float(n)
    return mse

def calculate_rmse(known, predicted):
    '''
    input:
        * dictionary of known values
        * dicionary of predicted values
    output:
        * mean squared error. (in latex)
          $\sqrt{\frac{1}{n} \sum_{i=1}^n (y_i - \hat{y}_i)^2}$
    '''
    import numpy as np
    return np.sqrt(calculate_mse(known, predicted))

def calculate_mape(known, predicted):
    '''
    input:
        * dictionary of known values
        * dicionary of predicted values
    output:
        * mean absolute percentage error
          $M = \frac{100\%}{n} \sum_{i=1}^{n}\frac{y_i - \hat{y_i}}{y_i}$
    '''
    n = 0
    mape = 0.0
    for kkey, kvalue in known.items():
        if kkey in predict:
            pvalue = predicted[kkey]
            n_mape = np.abs((float(kvalue) - float(pvalue))/float(kvalue))
            mape += n_mape
            n += 1
    mape = 100.0 * mape/float(n)
    return mape
