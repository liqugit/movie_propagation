'''
File: generic.py
Author: Adam Pah
Description: 
Generic fileIO handlers
'''

def random_file_namer(progname, extension):
    '''
    returns a random filename for saving a file

    input:
        progname : just __file__
        extension : the needed extension
    output:
        fname - randomized file name
    '''
    import os
    import random
    
    available = False
    while available==False:
        tempname = '-'.join([os.path.splitext(progname)[0], str(random.randint(0,10000))]) + '.' + extension
        if not os.path.exists(tempname):
            available=True
    return tempname
