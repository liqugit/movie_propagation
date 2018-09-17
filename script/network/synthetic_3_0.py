import json
import os
import sys
from argparse import ArgumentParser

from collections import Counter, defaultdict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import factorial
from scipy import stats
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import ks_2samp
from operator import itemgetter
from copy import copy
from random import random
from math import exp


src_dir = os.path.abspath(os.path.join(os.pardir, os.pardir,'src'))
sys.path[0] = src_dir
from parser.support import ROLES, CREDITS
from parser.my_mongo_db_login import DB_LOGIN_INFO
import parser.support as support
import network.network_builder as build
import network.network_generator as generate
import network.shuffler as shuffle



def main(args):
    start_year = args.start_year
    end_year = args.end_year
    iter_num = args.iter_num
    # read original data
    movie_producer_df = generate.open_movie_data(start_year, end_year)
    # expand the producer list
    unlistyfied_producer_df = generate.unlistify(movie_producer_df, 'producers')
    # get rid of producer roles
    unlistyfied_producer_df['producer_id'] = unlistyfied_producer_df.producers.apply(lambda x: x[0])
    # get gender info
    gender_df = support.get_staff_df('producers')[['_id', 'female_count', 'first_movie', 'last_movie', 'gender']]
    females = build.generate_gender_seeds(gender_df)
    unlistyfied_producer_df['gender'] = unlistyfied_producer_df.apply(generate.assign_gender, args=(gender_df,), axis=1)
    # females are seeds
    seeds = unlistyfied_producer_df[unlistyfied_producer_df.gender == 'female'].producer_id.unique().tolist()

    # total number of producers
    total_num_producers = len(unlistyfied_producer_df.producer_id.unique().tolist())
    number_of_producers_per_year = unlistyfied_producer_df.groupby('year').producer_id.nunique().to_dict()

    #get movie num
    movie_per_producer_gender = unlistyfied_producer_df.groupby('gender').apply(lambda x: x.groupby('producer_id')._id.count().tolist()).to_dict()
    #get gaps
    gap_dict = generate.get_gaps_gender(unlistyfied_producer_df)
    gap_data = generate.get_gaps(unlistyfied_producer_df)
    for i in range(iter_num):
        #generate new producers every round
        generated_producers = generate.generate_producers(total_num_producers)
        generated_producers_dict = {}
        generated_producers_dict['female'] = generated_producers[:len(seeds)]
        generated_producers_dict['male'] = generated_producers[len(seeds):]
        total_movie_frame = movie_producer_df[['_id', 'producers', 'year', 'producer_num']].copy(deep=True)
        total_movie_frame['producers'] = [[]]*len(total_movie_frame)

        # make team size the mean of the team size of the year
        total_movie_frame = generate.assign_team_size(total_movie_frame, number_of_producers_per_year)
        total_num_teams = total_movie_frame.producer_num.sum()

        #generate movies
        movie_dict = generate.generate_movie_num(total_num_teams, generated_producers_dict, movie_per_producer_gender)
        # assign gaps by gender
        movie_dict_per_producer, gap_dict_per_producer = generate.assign_gaps(movie_dict, gap_dict)
        # distribute movies
        final_movie_frame = generate.distribute_movies(total_movie_frame, gap_dict_per_producer)

        #get ready to shuffle
        unlistyfied_result_df = generate.unlistify(final_movie_frame, 'producers')
        # distributions of gaps
        gap_result = generate.get_gaps(unlistyfied_result_df, 'producers')
        pvalue, D = ks_2samp(gap_data, gap_result)
        #if pvalue is small, go into shuffling
        if pvalue < 0.1:
            df_distance = shuffle.find_distances(gap_data, gap_result)
            max_p, max_d = shuffle.find_max_distance(df_distance)
            df_match = shuffle.find_max_distance_gaps(unlistyfied_result_df, max_p)
            shuffle.shuffle(unlistyfied_result_df, gap_data)    

if __name__ == '__main__':
    parser = ArgumentParser()

#     parser.add_argument('data_file', help='data directory')

    parser.add_argument('--start_year', default=1990, type=int, 
                        help='''which year to start. Includes start year
                            ''')
    parser.add_argument('--end_year', default=1999, type=int, 
                    help='''which year to start. Includes start year
                        ''')
    parser.add_argument('--iter_num', default=10, type=int, 
                        help='''how many movie-producer dataframe to make
                            ''')
    args = parser.parse_args()
    main(args)