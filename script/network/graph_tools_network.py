"""
Object: Open movie schedule from database 
        1. make network using graph_tool (bipartite)
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
src_dir = os.path.abspath(os.path.join(os.pardir, 'src'))
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
    sub_sample = args.sample #number of node samples to draw hierarchy graph
    # file_names = [join(data_dir,f) for f in listdir(data_dir) if isfile(join(data_dir, f))]

    with open(os.path.abspath(data_file)) as f:
        movie_fiel = f.read()
        movie_data = json.loads(movie_file)

    role = 'producing'
    role_key = role + '_gender_percentage'
    all_movies = support.get_movies_df(role_key)
    print('Got_all movies')

    #read movies during the period of interest
    movies_period = all_movies[(all_movies.year >= start_year) & (all_movies.year < end_year)]
    movie_producer_df = movies_period[['_id', 'producers', 'producing_gender_percentage', 'title', 'year', 'genres']]
    #sort movies by year
    movie_producer_df = movie_producer_df.sort_values('year')

    #make movies into dictionary
    movie_producer_df = movie_producer_df.set_index('_id')
    movie_producer_dict = movie_producer_df.to_dict(orient='index')

    print('Make bipartite graph')
    g = sgm.make_graph(movie_producer_dict)
    print('Save graph')
    g.save(os.path.join(result_dir, 'gt_bipartite_network'), fmt='gt')
    state = gt.minimize_nested_blockmodel_dl(g, deg_corr=True, overlap=False, state_args={'clabel':clabel, 'pclabel':clabel},)

    if sub_sample == None:
        sub_sample = g.num_vertices()

    save_name  = os.path.join(result_dir, 'gt_bipartite_community.pdf')
    gt.draw_hierarchy(state,layout='bipartite',\
                  output=save_name,\
                  fmt='pdf',\
                  subsample_edges=sub_sample,\
                  hshortcuts=1, hide=0,\
                  dpi=300
                  )


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
    parser.add_argument('--sample', default=None, type=int,
                    help='''number of sub samples to draw from when drawing graph''')  
    args = parser.parse_args()
    main(args)
 
