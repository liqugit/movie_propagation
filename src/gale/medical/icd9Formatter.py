'''
File: icd9Formatter.py
Author: Adam Pah
Description: 
Handling icd9 formatting and translation problems
'''

dbs = {
    'Phewas' : {
        'type': 'mongo',
        'host': 'evanston.chem-eng.northwestern.edu',
        'port': '27017',
        'db': 'standard_icd9_data',
        'collection': 'phewas_groupings',
        'user': 'ghostwriter',
        'password': 'safetynotguaranteed'
    },
    'Chronic' : {
        'type': 'mongo',
        'host': 'evanston.chem-eng.northwestern.edu',
        'port': '27017',
        'db': 'standard_icd9_data',
        'collection': 'chronic_icd9_codes',
        'user': 'ghostwriter',
        'password': 'safetynotguaranteed'
    }
}

def icd9_normalizer(icd9, check_decimal=False):
    '''
    input:
        icd9 - the icd9 code as a string
    output:
        formatted icd9 code, standardized
    '''
    icd9 = str(icd9)
    #First switch, is the icd9 in decimal format?
    if check_decimal:
        print icd9
        #Havent seen an icd9 code in deciimal format with a leading 0 yet
        if icd9[0]=='0':
            dicd9 = icd9[:3] + '.' + icd9[3:]
            sicd9 = dicd9.lstrip('0')
            return str(float(sicd9))
        #Handle the V codes now
        elif icd9[0]=='V':
            dicd9 = icd9[:3] + '.' + icd9[3:]
            return dicd9
        else:
            dicd9 = icd9[:3] + '.' + icd9[3:]
            return str(float(dicd9))
    else:
        try:
            return str(float(icd9))
        except ValueError:
            return icd9

def icd9_string(sicd9):
    '''
    input: icd9 string normalized
    output: icd9 description form phewas database
    '''
    import gale.databases.mongoConnect as mcxn

    tdb = mcxn.MongoConnection(dbs['Phewas'])
    doc = tdb.collection.find_one({'icd9': sicd9}, {'icd9_string': 1})
    tdb.tearDown()
    if doc:
        return doc['icd9_string']
    else:
        return 'Description not found'

def phewas_translator():
    '''
    input:
    output:
        dictionary of icd9 to phewas groups
    dependencies: gale
    '''
    import gale.databases.mongoConnect as mcxn

    tdb = mcxn.MongoConnection(dbs['Phewas'])
    docs = tdb.collection.find({}, {'icd9': 1, 'phewas_code': 1})
    #Condense to dictionary
    data = {}
    for i in docs:
        data[i['icd9']] = i['phewas_code']
    return data

def return_phewas_group(icd9, tdb=None):
    '''
    input: 
        icd9, the icd9 code to return
        mongoConnect database connection (optional, increases performance)
    output: phewas_group

    if item not found in database then 'None' value is returned.
    '''
    if not tdb:
        import gale.databases.mongoConnect as mcxn
        tdb = mcxn.MongoConnection(dbs['Phewas'])
    #Get it
    doc = tdb.collection.find_one({'icd9': icd9}, {'phewas_code': 1})
    if doc!=None:
        return doc['phewas_code']
    else:
        return doc

def return_phewas_group_string(icd9, tdb=None):
    '''
    input: 
        icd9, the icd9 code to return
        mongoConnect database connection (optional, increases performance)
    output: phewas_group

    if item not found in database then 'None' value is returned.
    '''
    if not tdb:
        import gale.databases.mongoConnect as mcxn
        tdb = mcxn.MongoConnection(dbs['Phewas'])
    #Get it
    doc = tdb.collection.find_one({'icd9': icd9}, {'phewas_string': 1})
    if doc!=None:
        return doc['phewas_string']
    else:
        return doc

def icd9_validator(icd9):
    '''
    input:
        icd9 code
    output:
        True/False if it is valid
    '''
    import numpy as np
    try:
        ficd9 = float(icd9)
        if np.isnan(ficd9)==False:
            return True
        else:
            return False
    except ValueError:
        return False
