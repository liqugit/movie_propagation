'''
File: conversions.py
Author: Adam Pah
Description: 
Converts a time series between formats
'''

def convert_timeseries_to_intervalseries(timeseries, yaxis_only=False):
    '''
    input:
        timeseries: [[numeric_date_from_start, arbitrary value of interest], []....
        yaxis_only: False, by default. if True then the return is [20, 6, ...]
    output:
        intervalseries: [[0, 20], [1, 6], ...

    Outputs the orderd series of gaps between dates
    '''
    intervalseries = []
    for i, dtpoint in enumerate(timeseries[:-1]):
        idate = dtpoint[0]
        jdate = timeseries[i+1][0]
        if yaxis_only:
            intervalseries.append(jdate - idate)
        else:
            intervalseries.append([i, jdate - idate])
    return intervalseries
