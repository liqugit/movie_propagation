'''
File: populateMongo.py
Author: Adam Pah
Description: 
Populating mongo collections from standard types
'''

def from_list(settings, data, naming_scheme, exclusions = [], chunk_size = 100000, inclusion = {}):
    '''
    input:
        settings - mongo connection settings (mongoConnect standard)
        data - list of lists. must correspond to headers in nameing scheme
        naming_scheme - dictionary mapping inset list index to column/key name to use
        (optional)
        exclusions - headers to ignore in naming_scheme. Must be value in dictionary.
    output:
        None
    
    dependencies: gale
    '''
    import gale.databases.mongoConnect as mcxn
    import gale.general.errors as err

    def _transform_row(theader, trow):
        if inclusion:
            tdict = dict(inclusion)
        else:
            tdict = {}
        for i, tkey in theader.items(): 
            if trow[i].lower()!='null':
                tdict[tkey] = trow[i]
        return tdict

    #Handle the exclusion first
    if exclusions:
        for tval in exclusions:
            itemset = [i for i,j in naming_scheme.items() if j==tval]
            if len(itemset) > 1:
                m = 'populateMongo.from_list, line 28\n'
                m += 'More than one value in naming scheme matches the exclusion value'
                err.generic_error_handler(message=m)
            del naming_scheme[itemset[0]]

    #Check to make sure all values are distinct
    if len(naming_scheme.values()) !=  len(list(set(naming_scheme.values()))):
        m = 'populateMongo.from_list, line 28\n'
        m += 'Values in naming scheme not unique'
        err.generic_error_handler(message=m)

    data = [_transform_row(naming_scheme, datarow) for datarow in data]
    
    #iterate over subsets of the list
    tdb = mcxn.MongoConnection(settings)
    if len(data) < chunk_size:
        tdb.collection.insert(data)
    else:
        for i in range(0,len(data),chunk_size):
            tdb.collection.insert(data[i:i+chunk_size])
    tdb.tearDown()

def from_csv(settings, fhandle, exclusions = [], inclusion = {}, chunk_size = 100000):
    '''
    input:
        fhandle: CSV file with fully qualified header
    output:
        none

    Uses pandas to populate a database
    '''
    import gale.databases.mongoConnect as mcxn
    try:
        import pandas as pd
    except ImportError:
        print "Error: Pandas is not installed, using from_list method"
        import gale.fileIO.csvHandlers as csvh
        import sys
        indata, header = csvh.read_as_list(fhandle)
        from_list(settings, indata, header)
        sys.exit()
    
    df = pd.read_csv(fhandle)
    header = list(df.columns)
    if exclusions:
        for excl in exclusions:
            header.remove(excl)
    datalist = [] 
    for tline in df.ix[:,header].values:
        tdict = dict(dict(inclusion).items() + dict(zip(header, list(tline))).items())
        datalist.append(tdict)
    ####
    tdb = mcxn.MongoConnection(settings)
    if len(datalist) < chunk_size:
        tdb.collection.insert(datalist)
    else:
        for i in range(0,len(datalist),chunk_size):
            tdb.collection.insert(datalist[i:i+chunk_size])
    tdb.tearDown()
