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

#Local
src_dir = os.path.abspath(os.path.join(os.pardir, os.pardir, 'src'))
sys.path[0] = src_dir
import model.contagion as contagion
import network.shift_graph_maker as sgm
import parsers.reader as read
import gale.general.errors as gerr
import parsers.saver as save


###Functions###
def main(args):
    #input file as args[0] transform final_schedule.csv
    data_dir = args.data_dir
    result_dir = args.result_dir

    # data_dir += '*.csv'
    print ('Data_dir', data_dir)
    print ('Result_dir', result_dir)
    
    p, d, b = args.p, args.d, args.b
    belief_type = args.belief_type
    iter_no = args.i
    
    file_list = [join(data_dir, f) for f in listdir(data_dir) if isfile(join(data_dir, f))]
    #print(file_list)
    # m, r, b, = 0.1, 0.2, 0.5 
    #starting the dynamics
    print ('Making data with parameter prob: {:.2f}, dose: {:.2f}, threshold: {:.2f}'.format(p, d, b))
    for f in range(len(file_list)):
        f_name = file_list[f]
        print('Reading file', f_name)
        file_path = os.path.splitext(f_name)[0].split('_')
        file_base = os.path.basename(f_name)
        y = re.compile(r'\d{4}')
        year = y.search(file_base).group()
        if args.r == False:
            df_data, header = read.read_csv_file(f_name)
            version = file_path[-1]
            # year = file_path[-3]
            sched_type = file_path[-4]
        if args.r == True:
            df_data, header = read.read_xlsx_file(f_name)
            # year = file_path[-1]
            sched_type = 'real'
            version='orig'

        print('\t\t\t version', version)
        #for the real schedule
        for i in range(iter_no):
            print('\t Building network for iter {}'.format(i))
            G = sgm.build_temporal_network(df_data, belief_type, b)

            #############3Code block for checking if all the nodes are correct########
            # doctors_in_order = {G.node[node]['start_date']:[] for node in G.nodes() 
            #                             if G.node[node]['node_type'] == 'S'} 
            # for node in G.nodes():
            #     if G.node[node]['node_type'] == 'D':
            #         first_shift = G.node[node]['shifts'][0]
            #         print(first_shift)
            #         print(G.node[node]['shifts'])
            #         print(G.nodes())
            #         first_date = G.node[first_shift]['start_date']
            #         for happen_date in doctors_in_order.keys():
            #             if happen_date > first_date:
            #                 doctors_in_order[happen_date].append(node)

            # change = 0
            # for key, val in sorted(doctors_in_order.items()):
            #     print(key, len(val))
            #     if len(val) > 40:
            #         print(key.date(), len(val))
            #         break
            # date_per_physician = {}
            # phys_list = []
            # for i, row in df_data.iterrows():
            #     att = row.Attending
            #     fel = row.Fellow
            #     date = row.Date.to_datetime()
            #     if att not in  phys_list:
            #         phys_list.append(att)
            #     if fel not in phys_list:
            #         phys_list.append(fel)
            #     if date not in date_per_physician:
            #         date_per_physician[date] = deepcopy(phys_list)
            # for key, val in sorted(date_per_physician.items()):
            #     print(key, len(val))
            # input()
            ############################################################################

            adopter_history = contagion.contagion_belief_propagation_temporal_network(G, p, d, b)
            if i == 0:
                print('\t initializing df')
                df_adopter = pd.DataFrame(adopter_history, columns=['Days', '{}_{}'.format(version, i)])
                df_adopter = df_adopter.set_index('Days')
            else:
                print('\t appending df')
                df_adopter['{}_{}'.format(version, i)] = pd.Series(adopter_history[:, 1], index=adopter_history[:, 0])

        param_dict = {'p':p, 'd':d, 'b':b}

        formatted_parameters = {k: save.parameter_to_string(v, k) for k, v in param_dict.items()}
        formatted_parameters['year'] = year
        formatted_parameters['type'] = sched_type
        formatted_parameters['ver'] = version
        fname_primer = 'contagion_adopter_{type:}_{p:}_{d:}_{b:}_{year:}_{ver:}_{i:}.json'
        save.save_file_json(df_adopter, result_dir, fname_primer, formatted_parameters)
        del df_adopter


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('data_dir', help='data directory')
    parser.add_argument('result_dir', help='result directory')

    parser.add_argument('--belief_type', default='empirical', type=str, 
                        choices = {'empirical', 'random', 'apriori'},
                        help='''Ways to instantiate the belief per physician. 
                          Choices are: empirical, random, or apriori
                            ''')
    parser.add_argument('--run_type', default='original', action='store',
                    help='''Decide whether we are going to be doing training sets or not
                            training: do training, end at the given date
                            testing: do testing, start at the given date
                            original: just run the contagion model. 
                        ''')
    parser.add_argument('-p', type=float, default=0.1, help='the probability parameter')
    parser.add_argument('-d', type=float, default=0.5,  help='the dose parameter')
    parser.add_argument('-b', type=float, default=0.5, help='threshold parameter')
    parser.add_argument('-i', type=int, default=100, help='number of iterations')
    parser.add_argument('-r', action='store_true', default=False, help='is it real schedule?')
    
    args = parser.parse_args()
    main(args)
 
