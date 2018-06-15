import os
import contextlib
import errno



def parameter_to_string(param, name):
    '''
    Convert a parameter value to a rounded, 100x value (e.g. 0.1 -> '10') and
    prefix it with "name"
    '''
    return '{name}{val:02.0f}'.format(val=round(param * 100), name=name)

def mkdir_p(path):
    'http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python'
    try:
        os.makedirs(path)
    except OSError as e:  # Python >2.5
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def make_filename(root, fname_primer, parameter_dictionary):
    """
    check if the file name exists in the folder
    input:
        root - save directory
        fname_primer - primer string for file name
        parameter_dictionary - dictionary of parameters
    return
        path - filename string

    """
    parameter_dictionary['i'] = 0
    filename = fname_primer.format(**parameter_dictionary)
    path = os.path.join(root, filename)

    while os.path.isfile(path):
        parameter_dictionary['i'] += 1
        filename = fname_primer.format(**parameter_dictionary)
        path = os.path.join(root, filename)
    return path

def save_file_json(df, path):
    """
    save file to given folder as given extension
    input:
        df - dataframe
        root - save directory
        fname_primer - primer string for file name
        parameter_dictionary - dictionary of parameters. must contain i
    output:
        saved file
    """
    #make path
    path_to_create = os.path.dirname(path)
    mkdir_p(path_to_create)
    
    with open(path, 'w') as f:
        df.to_json(f, orient='split')

def save_file_csv(df, root, fname_primer, parameter_dictionary):
    """
    save file to given folder as given extension
    input:
        df - dataframe
        root - save directory
        fname_primer - primer string for file name
        parameter_dictionary - dictionary of parameters. must contain i
    output:
        saved file
    """
    #make path
    path = make_filename(root, fname_primer, parameter_dictionary)
    path_to_create = os.path.dirname(path)
    mkdir_p(path_to_create)
    
    with open(path, 'w') as f:
        df.to_csv(f, sep=',')
