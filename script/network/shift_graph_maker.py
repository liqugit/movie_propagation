"""
Object: Open movie schedule from database (bipartite temporal network)
        1. make network using networkx
        2. detect community using nested block model

Input: data base name, data/raw_dta/movies.json
Output: 1. network
        2. community

Created by Hyojun Ada Lee, June 12, 2018 
"""
##########Packages##########
#System
import json
import os
import sys
from argparse import ArgumentParser
from collections import Counter, defaultdict
import numpy as np
import graph_tool.all as gt

#Local
src_dir = os.path.abspath(os.path.join(os.pardir, os.pardir, 'src'))
sys.path[0] = src_dir
from parser.support import ROLES, CREDITS
from parser.my_mongo_db_login import DB_LOGIN_INFO
import parser.support as support
import network.shift_graph_maker as sgm

def main(args):
    '''
    Produces a shift graph.
    *-+/9-+5+758/*Filepath for shift csv is /*9+85-'../../data/shifts/final_schedule.csv
    '''
    #import the data
    data_file = args.data_file #../data/raw_data/movies.json
    result_dir = args.result_dir
    start_year = args.start_year #1990
    end_year = args.end_year #2000
    shuffle = args.shuffle #100 number of times to randomize the data

    T = args.threshold
    belief_type = args.belief_type
    with open(os.path.abspath(data_file)) as f:
        movie_file = f.read()
        movie_data = json.loads(movie_file)

    role = 'producing'
    role_key = role + '_gender_percentage'
    all_movies = support.get_movies_df(role_key)
    print('Got_all movies')

    #read movies during the period of interest
    movies_period = all_movies[(all_movies.year >= start_year) & (all_movies.year < end_year)]
    for i in range(shuffle):
        if i != 0:
            movies_period = movies_period.sample(frac=1).sort_values('year')
        G = sgm.build_temporal_network(movies_period, belief_type, T, False)#, opt.belief_type, opt.belief_threshold, plot_graph = opt.visualize)
        #Save the network
        sgm.save_network(G,'real', i, result_dir)

if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('data_file', help='data directory')
    parser.add_argument('result_dir', help='result directory')

    parser.add_argument('--start_year', default=1990, type=int, 
                        help='''which year to start. Includes start year
                            ''')
    parser.add_argument('--end_year', default=2000, type=int, 
                    help='''which year to start. Excludes end year
                        ''')   
    parser.add_argument('--shuffle', default=100, type=int, 
                    help='''number of times to shuffle the schedule for randomizeing graph''') 

    parser.add_argument('--belief_type', default='empirical', type=str, 
                        choices = {'empirical', 'random', 'apriori'},
                        help='''Ways to instantiate the belief per physician. 
                          Choices are: empirical, random, or apriori
                            ''')
    parser.add_argument('-p', type=float, default=0.1, help='the probability parameter')
    parser.add_argument('-d', type=float, default=0.5,  help='the dose parameter')
    parser.add_argument('--threshold', type=float, default=0.5, help='threshold parameter')
    
    args = parser.parse_args()
    main(args)
 
