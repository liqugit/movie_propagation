'''
File: csvHandlers.py
Author: Adam Pah
Description: 
Handles csv files
'''

def read_as_list(fpath, header=False, yieldable=False):
    '''
    Input: csv file path
    Output: 
    Yieldable False: csv data, enumerated header as dictionary {index : header_name} with header=True
    Yieldable True: csv.reader object
    Dependencies: csv

    Given a filepath it reads a csv file and returns the data as a list of lists.
    If header true then it returns a dictionary of the header names with index.  
    Deletes header from list.
    '''
    import sys
    import csv
    csv.field_size_limit(sys.maxsize)

    with open(fpath, 'rb') as csvfile:
        dialect_error=False
        try:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
        except:
            dialect_error=True
        csvfile.seek(0)
        if not dialect_error:
            reader = csv.reader(csvfile, dialect)
        else:
            reader = csv.reader(csvfile)
        if yieldable==True:
            return reader
        #Read the data to list
        data = []
        for l in reader:
            data.append(l)
    if header==True:
        enumHeader = {}
        for i,j in enumerate(data[0]):
            enumHeader[i] = j
        del data[0]
        return data, enumHeader
    else:
        return data

