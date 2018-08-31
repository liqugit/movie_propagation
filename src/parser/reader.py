from os import listdir
from os.path import isfile, join
import re
import pandas as pd
import os

def get_parameters(file_names):
    """
    get list of parameters from the file
    """
    param_list = []
    for path in file_names:
        f_name = os.path.basename(path)
        p = re.compile(r'p[0-9]+\_d[0-9]+\_t[0-9]+')
        param = p.search(f_name).group()
        param_list.append(param)
    param_list = list(set(param_list))
    return param_list

def read_raw_files_w_parameter(result_dir, param,N=1):
    '''
    read files with the given parameter divided by N, either 1 or total number of players
    '''
    df_list = []
    file_names = [join(result_dir, f) for f in listdir(result_dir) if isfile(join(result_dir, f))]
    file_param = [fs for fs in file_names if param in fs]
    v = re.compile(r'ver_[0-9]+')
    for fs in file_param:
        df = pd.read_json(fs, orient='split')
        ver = v.search(fs).group()
        df.name = ver
        #divide df by N except for the year column
        df.loc[:,df.columns != 'year'] = df.loc[:,df.columns != 'year']/N
        #rename columns to drop duplicate columns
        rename_col = {col:'{}_{}'.format(col, ver) for col in df.columns}
        df = df.rename(columns=rename_col)
        df_list.append(df)
    return df_list

def read_mean_files_w_parameter(result_dir, param):
    '''
    read files with the given parameter
    '''
    file_names = [join(result_dir, f) for f in listdir(result_dir) if isfile(join(result_dir, f))]
    file_param = [fs for fs in file_names if param in fs]
    v = re.compile(r'ver_[0-9]+')
    if len(file_param) == 1:
        df = pd.read_json(file_param[0], orient='split')
    else:
        print(file_param)
        raise ValueError('Multiple files exist files for the mean')

    return df
    