def reverse_dictionary(tdict):
    '''
    Reverses the input dictionary
    Input:
        tdict: input dictionary with lists as values
    Output:
        sdict: yeah, just reversed 
    '''
    sdict = {}
    for i, tlist in tdict.items():
        for tval in tlist:
            if tval not in sdict:
                sdict[tval] = []
            sdict[tval].append(i)
    return sdict
