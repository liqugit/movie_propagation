"""
Contagion model
without any training options

Summary:
1. Call on the data
2. Convert it to networkx format
3. Iterate through Shifts
4.  4-1. If one of the doctors in the same shift is adoptor resistance and adoptation
        B1(t+1) = B1(t) - RP[B1(t) - B2(t)]
        B2(t+1) = B2(t) + P[B1(t) - B2(t)]
    4-2. If none of the doctors in the same shift they stay the same
        B1(t+1) = B1(t)
        B2(t+2) = B2(t)
    4-3 if both are adoptors: mutual encouragement 
        B1(t+1) = B1(t) + M
        B2(t+1) = B2(t) + M
    *Each shift has different shift_order even if they might have happend on the same date
    *There are shifts that happened on the same date, but the team of doctors were working in different 

Made by Hyojun Ada Lee October 13, 2016
"""

##########Packages##########
#System
import random
import sys
import os
from argparse import ArgumentParser
import pandas as pd
import numpy as np
from copy import deepcopy
import errno
import contextlib
from os import listdir
from os.path import isfile, join
import re
import json
import matplotlib.pyplot as plt

#Local
src_dir = os.path.abspath(os.path.join(os.pardir, os.pardir, 'src'))
sys.path[0] = src_dir
from parser.support import ROLES, CREDITS
from parser.my_mongo_db_login import DB_LOGIN_INFO
import gale.general.errors as gerr
import parser.support as support


def make_filename(directory, network_type, parameter_dict, ver=None):
    """
    save the pandas dataframe to csv
    Input
        directory - name of save directory
        network_type - string type of nework type
        parameter_dict - dict {p:0.1, d:1.0, t:1.0}
    output
        save_name - string of save_name
    """
    valid = {'real', 'synthetic', 'agg_2year', 'agg_3year', 'agg_4year' 'agg_5year'}
    if network_type not in valid:
        network_type = input("network_type must be one of: {}".format(", ".join(valid)))
    network_dict = {'real':0, 'synthetic':1, 'agg_2year':2, 'agg_3year':3, 'agg_4year':4, 'agg_5year':5}
    if ver==None: #version is none for real network, however, synthetic network will have versions already
        ver = random.randint(10000, 99999)
    #Generate the name
    # file name startw with contagion and the networktype
    file_name = '_'.join(['contagion', str(network_dict[network_type])])
    # add parameters
    file_name = '_'.join([file_name, '{p:}_{d:}_{t:}'.format(**parameter_dict)])
    # add verson 
    file_name_iter = '_'.join([file_name, 'ver', str(ver)])
    file_name_iter = '.'.join([file_name_iter, 'json'])

    save_name = os.path.abspath(os.path.join(directory, file_name_iter))
    #order of contagion_[sched_type]_[parameters]_ver_[network version]_[iteration of the version].json
    return save_name

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

def read_files_w_parameter(result_dir, param,N=1):
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
    
def mean_ci(df, high=0.975, low=0.025):
    mean = df.mean(axis=1).tolist()
    low_ci = df.quantile(low, axis=1).tolist()
    high_ci = df.quantile(high, axis=1).tolist()
    return mean, low_ci, high_ci

def median_ci(df, high=0.975, low=0.025):
    mean = df.median(axis=1).tolist()
    low_ci = df.quantile(low, axis=1).tolist()
    high_ci = df.quantile(high, axis=1).tolist()
    return mean, low_ci, high_ci

###Functions###
def main(args):
    #input file as args[0] transform final_schedule.csv
    data_dir = args.data_dir
    result_dir = args.result_dir
    normed = args.norm

    # get files
    file_list = [join(data_dir, f) for f in listdir(data_dir) if isfile(join(data_dir, f))]

    #get number of nodes
    print('getting N')
    if normed == True:
        producer_file = '/home/projects/movie-network/data/raw_data/movies.json'
        with open(producer_file) as f:
            movie_file = f.read()
            movie_data = json.loads(movie_file)
        role = 'producing'
        role_key = role+'_gender_percentage'
        all_movies = support.get_movies_df(role_key)
        movie_period = all_movies[(all_movies.year >= 1990) & (all_movies.year < 2000)]
        producer_series = movie_period.producers.tolist()
        all_producers = list(set([i[0] for sublist in producer_series for i in sublist]))
        N = len(all_producers)
    else:
        N = 1
    param_list = get_parameters(file_list)
    print(param_list)
    for param in param_list:
        print(param)
        print('reading files')
        print('N', N)
        df_list = read_files_w_parameter(data_dir, param,N)
        print('len df_list', len(df_list))
        df_param = pd.concat(df_list, axis=1)
        print('columns', len(df_param.columns))
        #check if all year columns have the same value
        year_columns = [col for col in df_param.columns if 'year' in col]
        #check if the columns are same to reference column
        year_same_df = df_param[year_columns].eq(df_param['year_ver_0'], axis=0).all(axis=0)
        #check if all columns are same
        year_true = year_same_df.all() #supposed return 
        print(year_true)
        if year_true == True:
            none_year_columns = [c for c in df_param.columns if c not in year_columns]
            mean, low_ci, high_ci = median_ci(df_param[none_year_columns])
            color='teal'
            fontsize=12
            #plot the figure:
            fig, ax = plt.subplots(figsize=(5,3))
            #get the bipartite data:
            #plot bipartite results
            print('mean', mean[-1])
            ax.plot(df_param.index, mean, label='Multipartite', color=color)
            ax.fill_between(df_param.index, low_ci, high_ci, color=color, alpha=0.2)
            ax.set_ylim([0, 1])
            #figure style
            ax.set_ylabel('Adopter ratio', fontsize=1.3*fontsize)
            ax.set_xlabel('Number of cumulative movies', fontsize=1.3*fontsize)
            ax.tick_params(axis='both', which='major', labelsize=fontsize)
            ax.tick_params(axis='both', which='minor', labelsize=fontsize)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)

            plt.tight_layout()
            plt.savefig(os.path.join(result_dir, 'adoption_curve_{}.pdf'.format(param)), 
                dpi=300, transparent=True)
            del df_param
        else:
            print('years dont line up')
if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('data_dir', help='data directory')
    parser.add_argument('result_dir', help='result directory')
    parser.add_argument('--norm', type=bool, default=True, help='whether to normalize value')
    
    args = parser.parse_args()
    main(args)
 
