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
import glob
import errno
import contextlib
from os import listdir
from os.path import isfile, join
import re
import json
#Local
src_dir = os.path.abspath(os.path.join(os.pardir, os.pardir, 'src'))
sys.path[0] = src_dir
import model.contagion as contagion
import network.shift_graph_maker as sgm
import gale.general.errors as gerr
import parser.saver as save
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

###Functions###
def main(args):
    #input file as args[0] transform final_schedule.csv
    data_dir = args.data_dir
    result_dir = args.result_dir

    print ('Data_file', data_dir)
    print ('Result_dir', result_dir)
    
    P, D, T = args.p, args.d, args.t
    belief_type = args.belief_type
    iter_no = args.i
    n = args.n #number of times to generate new nework
    #year
    start_year = args.start_year #1990
    end_year = args.end_year #2000
    #Read data
    file_list = [join(data_dir, f) for f in listdir(data_dir) if isfile(join(data_dir, f)) and f.endswith('json')]
    print(file_list)
    for data_file in file_list:
        print('Reading file: ', data_file)
        movie_df = pd.read_json(data_file, orient='split')
        ver = re.findall(r'\d{6}', data_file)[0]


        #make movie data into dataframe
        movies_period = movie_df[(movie_df.year >= start_year) & (movie_df.year < end_year)]
        num_seeds = 1064
        total_producers = list(set([i for sublist in movies_period.producers.tolist() for i in sublist]))
        seeds = np.random.choice(total_producers, size=num_seeds, replace=False)
        #starting the dynamics
        print ('Making data with parameter prob: {:.2f}, dose: {:.2f}, threshold: {:.2f}'.format(P, D, T))
    
        print('\t Iteration: {}'.format(n))
        #Build network
        if n == 0:
            movies_period = movies_period.sort_values('year')
        else:
            movies_period = movies_period.sample(frac=1).sort_values('year')
        #for the real schedule
        print('\t\t Building network')
        print('\t\t Contagion propagation!')
        for i in range(iter_no):
            G = sgm.build_temporal_network(movies_period, seeds, belief_type, T)
            adopter_history = contagion.contagion_belief_propagation_temporal_network(G, P, D, T)
            if i == 0:
                print('\t\t Initializing df')
                df_adopter = pd.DataFrame(adopter_history, columns=['movie_order', 'year', '{}'.format(i)])
                df_adopter = df_adopter.set_index('movie_order')
                year_list = adopter_history[:,1]
            else:
                print('\t\t appending df')
                if np.array_equal(year_list,adopter_history[:,1]):
                    df_adopter['{}'.format(i)] = pd.Series(adopter_history[:, 2], index=adopter_history[:, 0])
                else:
                    m = "years are not matching"
                    gerr.generic_error_handler(message=m)
            if i % int(iter_no/2) and i!= 0: # save half way
                print('Half way saving')
                param_dict = {'p':P, 'd':D, 't':T}
                formatted_parameters = {k: save.parameter_to_string(v, k) for k, v in param_dict.items()}    
                save_path = make_filename(result_dir, 'synthetic', formatted_parameters, '_'.join([ver, str(n)]))
                save.save_file_json(df_adopter, save_path)

        print('Saving result')
        param_dict = {'p':P, 'd':D, 't':T}
        formatted_parameters = {k: save.parameter_to_string(v, k) for k, v in param_dict.items()}
        
        save_path = make_filename(result_dir, 'synthetic', formatted_parameters, '_'.join([ver, str(n)]))
        save.save_file_json(df_adopter, save_path)
        del df_adopter


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('data_dir', help='data directory')
    parser.add_argument('result_dir', help='result directory')

    parser.add_argument('--sched_type', help='schedule type', type=str, default='real',
                        choices={'real', 'synthetic', 'agg'})
    parser.add_argument('--belief_type', default='empirical', type=str, 
                        choices = {'empirical', 'random', 'apriori'},
                        help='''Ways to instantiate the belief per physician. 
                          Choices are: empirical, random, or apriori
                            ''')
    parser.add_argument('--start_year', default=1990, type=int, 
                        help='''which year to start. Includes start year
                            ''')
    parser.add_argument('--end_year', default=2000, type=int, 
                    help='''which year to start. Excludes end year''')


    parser.add_argument('-p', type=float, default=0.1, help='the probability parameter')
    parser.add_argument('-d', type=float, default=1.0,  help='the dose parameter')
    parser.add_argument('-t', type=float, default=1.0, help='threshold parameter')
    

    parser.add_argument('-i', type=int, default=100, help='number of iterations')
    parser.add_argument('-n', type=int, default=10, help='number of network generation')
    parser.add_argument('-r', action='store_true', default=False, help='is it real schedule?')
    
    args = parser.parse_args()
    main(args)
 
