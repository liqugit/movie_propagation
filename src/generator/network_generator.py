"""
Helper functions to generate synthetic network
"""
##########Packages##########
#System
import sys
import os
import json
import random
import argparse
from copy import deepcopy

#needed functions
from collections import Counter, defaultdict
from itertools import combinations
from operator import itemgetter
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import ks_2samp
import networkx as nx
from networkx.readwrite import json_graph

#graphs
import graph_tool.all as gt
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

###Local###
src_dir = os.path.abspath(os.path.join(os.pardir, os.pardir,'src'))
sys.path[0] = src_dir

import gale.general.errors as gerr
from parser.support import ROLES, CREDITS
from parser.my_mongo_db_login import DB_LOGIN_INFO
import parser.support as support
import network.shift_graph_maker as sgm


### Classes ###


### Functions ###
def open_movie_data(start_year=1990, end_year=2000):
	"""
	Read movie data, 
	Input:
		start_year - beginning of the network, included
		end_year - end of the network, excluded
	Return:
		movie_producer_df - dataframe containing info on movie and producers
	"""
    with open('/home/projects/movie-network/data/raw_data/movies.json') as f:
        movie_file = f.read()
        movie_data = json.loads(movie_file)
    role = 'producing'
    role_key = role + "_gender_percentage"
    all_movies = support.get_movies_df(role_key)
    print('Got all_movies')
    #getting movies during set period
    movie_period = all_movies[(all_movies.year >= start_year) & (all_movies.year < end_year)]
    #getting columns related to movies and producers
    movie_producer_df = movie_period[['_id', 'producers', 'producing_gender_percentage', 'title', 'year']]
    movie_producer_df = movie_producer_df.sort_values('year')
    #add producer team sizes
    movie_producer_df['producer_num'] = movie_producer_df['producers'].apply(lambda x: len(x))

	return movie_producer_df

def unlistify(df, column):
    """
    Expand column with list as elements, each element to row
    """
    matches = [i for i,n in enumerate(df.columns)
             if n==column]

    if len(matches)==0:
        raise Exception('Failed to find column named ' + column +'!')
    if len(matches)>1:
        raise Exception('More than one column named ' + column +'!')

    col_idx = matches[0]

    # Helper function to expand and repeat the column col_idx
    def fnc(d):
        row = list(d.values[0])
        bef = row[:col_idx]
        aft = row[col_idx+1:]
        col = row[col_idx]
        z = [bef + [c] + aft for c in col]
        return pd.DataFrame(z)

    col_idx += len(df.index.shape) # Since we will push reset the index
    index_names = list(df.index.names)
    column_names = list(index_names) + list(df.columns)
    return (df
          .reset_index()
          .groupby(level=0,as_index=0)
          .apply(fnc)
          .rename(columns = lambda i :column_names[i])
          .set_index(index_names)
          )
