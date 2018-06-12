'''
File: general.py
Author: Adam Pah
Description: 
'''

def create_all_combinations(n):
    '''
    Creates all possible combinations up to length k, where k equals
    the size of list n. Maximum size is 10. because this would just 
    get stupid otherwise
    input:
        n - list of values
    output:
        combs - of all combinations
    '''
    from itertools import combinations 
    #exception
    if len(n)>10:
        import gale.general.errors as gerr
        m = 'List length too long for this function'
        gerr.generic_error_handler(message=m)
    #Go through the sizes 
    combs = []
    for i in range(len(n)):
        size = i + 1
        combs += combinations(n, size)
    return combs
