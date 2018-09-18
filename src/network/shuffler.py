"""
Unfortunately 3rd synthetic model needs shuffling...
"""

import json
import os
import sys
import argparse
from collections import Counter, defaultdict
from random import shuffle
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

### Function ###

def find_distances(real_data, gen_data):
    """
    Find the distance between realData and genData for each data point
    input:
        realData - list or numpy array of real Data
        genData - list or numpy array of genearted Data
    output:
        dfDistance - dataframe with data points as index, cdf of real data, gen data and distance between each data point
    """
    data1, data2 = map(np.asarray, (real_data, gen_data))
    n1 = len(data1)
    n2 = len(data2)
    data1 = np.sort(data1)
    data2 = np.sort(data2)
    data_all = np.concatenate([data1, data2])
    cdf1 = np.searchsorted(data1, data_all, side='right')/(1.0*n1)
    cdf2 = (np.searchsorted(data2, data_all, side='right'))/(1.0*n2)
    d = cdf1 - cdf2
    distance_array = np.array([data_all, cdf1, cdf2, d]).T
    df_distance = pd.DataFrame(distance_array, columns =['data_all', 'real', 'gen', 'distances'])
    df_distance = df_distance.drop_duplicates()
    df_distance = df_distance.set_index('data_all')

    df_distance_pdf = df_distance.diff()
    df_distance_pdf.loc[0] = df_distance.loc[0]
    return df_distance_pdf

def find_max_distance(df_distance):
    """
    Find the maximum distance between the data points and the proportion of data
    Input
        df_distance - DataFrame of cdf of the original data, generated data and distance between the data frame
    Output
        maxPoint - float, data point where the maximum distance happens
        maxDistance - float, the difference between two data at maxPoint
    """
    df_max_dist = df_distance.reindex(df_distance.distances.abs().sort_values().index)
    df_max_dist_row = df_max_dist.iloc[-1]
    max_point = df_max_dist_row.name
    max_distance = df_max_dist_row.distances
    return max_point, max_distance

def find_max_distance_gaps(df_producers, max_p):
    """
    Find the shifts with the max distant gaps
    Input:
        df_producers - DataFrame of unlistified producers
        max_p - float, data point where the maximum distance happens
    Output:
        df_match - DataFrame with  matching gaps
    """
    df_producers = df_producers.copy(deep=True)
    df_match = pd.DataFrame(columns=['_id', 'producers', 'year', 'gaps'])
    producers = df_producers.producers.unique().tolist()
    for p, df_select in df_producers.groupby('producers'):
        df_select = df_select.sort_values('year')
        df_select['gaps'] = df_select.year.diff()
        df_select = df_select.dropna()
        df_select = df_select[df_select['gaps']==max_p]
        if (df_select.empty) == False:
            df_match = df_match.append(df_select[['_id', 'producers', 'year', 'gaps']])
    return df_match

def get_area(gap_data, gap_gen):
    """
    get the area between the two probabilities
    """
    df_distance = find_distances(gap_data, gap_gen)
    area = df_distance.distances.abs().sum()
   
    return area

def acceptance_probability(area, area_new, temp):
    """
    Are we going to accept the new state?
    """
    k = 0.001
    ap = exp((area-area_new)/(k*temp))
    return ap

##### Shuffle function #########
def shuffle(df_gen, gap_data, temp = 1):
    """
    Using simmulated annealing as the shuffle parameter. 
    note: the p value is not significant, but can find the minimum area between teh two probabilities.
    Input:
        df_producers - unlistyfied producer dataframe
        gap_data - gap list from the data
    Output:
        df_gen - shuffled df_producers (unlistyfied)
    """
    
    col_name = 'producers'
#     df_gen = df_producers.copy(deep=True)
    alpha = 0.99
    pvalue_old = 0
    shuf = 3
    # counter = 1 #every time counter hits %10 == 0, s is decreased by 1

    gap_gen = generate.get_gaps(df_gen, col_name)
    area = get_area(gap_data, gap_gen)
    counter = 0
    while temp > 0.01:
        print(temp)
        #for s in range(shuf):
        df_gen_new = shuffle_direction(df_gen, gap_data, gap_gen)
        #get the new area
        gap_gen_new = generate.get_gaps(df_gen_new, col_name)
        area_new = get_area(gap_data, gap_gen_new)
        #Accept if area_new < area
        if area_new < area:
            print('\t New area smaller than old, {:.3f}'.format(area_new))
            df_gen = df_gen_new
            area = copy(area_new)
            temp = temp*alpha
        #if new area is bigger than old area, do probability acceptance
        else:
            print('\t New area larger than old, {:.3f}'.format(area_new))
            ap = acceptance_probability(area, area_new, temp)
            p = random()
            if ap > p:
                print('\t\t Accepted, ap>p {:.3f}'.format(ap))
                print('\t ***Accept True***')
                df_gen = df_gen_new.copy(deep=True)
                area = area_new
            else:
                print('\t\t Not accepted')
#         if area <= 0.18:
#             stop_count = counter
#             print(stop_count, temp, area)
#             temp = 0.01
        if temp < 0.09:
            print(temp, area)
       
        counter += 1
        gap_gen = generate.get_gaps(df_gen, col_name)
        D, pvalue = ks_2samp(gap_data, gap_gen)
        if pvalue > 0.1:
            temp = 0.00001
        print('\t\t P value: {:.3f}, D {:.3f}, counter {}'.format(pvalue, D, counter))    
        print(pvalue)
    return df_gen

def shuffle_direction(df, gap_data, gap_gen):
    """
    shuffle according to the distance
    Input:
        df - unlistyfied producer dataframe
        gap_data - gap list from data
        gap_gen - gap list from generated data
    Output: 
        df_new - unlistyfied producer dataframe
    """
    df_distance = find_distances(gap_data, gap_gen)
    maxP, maxD = find_max_distance(df_distance)
    if maxD < 0:
        print('\t\t Negative shuffle')
        df_new = shuffle_negative(df, maxP)
    if maxD >= 0:
        print('\t\t Positive shuffle')
        df_new = shuffle_positive(df, maxP)
    return df_new

def shuffle_negative(df, maxP):
    """
    Shuffle the cases when the max distance is negative
    Probability of the gap for generated data > real data
    Input:
        df - unlistyfied producer schedules
        maxP - float, the point of the maximum distance between to data
    Output:
        df_new - DataFrame shuffled
    """
    df_new = df.copy(deep=True)

    df_match = find_max_distance_gaps(df_new, maxP)

    if len(df_match) >= 2:
        # print('From samples')
        movie1, movie2, producer1, producer2, p_list1, p_list2 = pick_producers(df_new, df_match)
        counter = 0
        while (producer1 in p_list2) or (producer2 in p_list1): #if producer1 and producer2's movies overlap
            # print('\t Still choosing from the samples', samples)
            movie1, movie2, producer1, producer2, p_list1, p_list2 = pick_producers(df_new, df_match)
            counter += 1
            if counter > 100: #if while goes too long, break
                # print('\t Switching to random')
                movie1, movie2, producer1, producer2, p_list1, p_list2 = pick_producers(df_new, df_new)
    else: #if the doctors in df_atch is less than 2 pick random doctors
        # print('Random')
        movie1, movie2, producer1, producer2, p_list1, p_list2 = pick_producers(df_new, df_new)

    #swap
    df_new.loc[(df_new._id == movie1) & (df_new.producers == producer1), 'producers'] = producer2
    df_new.loc[(df_new._id == movie2) & (df_new.producers == producer2), 'producers'] = producer1

    return df_new

def pick_producers(df, df_match, n=2):
    """
    pick producers to switch, condition - cannot be in the same movie
    Input:
        df - unlistyfied movie-producer dataframe
        df_match - matching dataframe
    Output:
        movie1, movie2, producer1, producer2 - movies and producers to swap
        p_list1 and plist2 - list of producers so that we are not switching overlapping producers
    """
    samples = df_match.sample(n=n)
    #choose random shifts with max distance gap
    movie1, movie2 = samples._id
    producer1, producer2 = samples.producers
    p_list1 = df['producers'][df['_id'] == movie1].tolist()
    p_list2 = df['producers'][df['_id'] == movie2].tolist()
    return movie1, movie2, producer1, producer2, p_list1, p_list2

def shuffle_positive(df_input, maxP):
    """
    Shuffle the cases when the max distance is positive
    Probability of the gap for generated data < real data
    Input:
        df - unlistyfied producer schedules
        maxP - float, the point of the maximum distance between to data
    Output:
        df_new - DataFrame shuffled
    """
    df = df_input.copy(deep=True)
    
    # get producers that have > 1 movies:
    producers_multi_movie = list(set(df[df.producers.duplicated(keep=False)].producers.tolist()))
    producers_one_movie = list(set(df[~df.producers.duplicated(keep=False)].producers.tolist()))
    df_swap, producer1, movie1, year1 = get_swap_movie(df, producers_multi_movie, maxP)
    while len(df_swap) == 0:
        print('df_swap is 0, means that producer did not participate in >1 movies')
        df_swap, producer1, movie1, year1 = get_swap_movie(df, producers_multi_movie, maxP)
    m_swap = df_swap.sample(1)
    movie_swap = m_swap._id.iloc[0]
    #get movies that have the matching gaps
    ## find movies that have producer1 in
    movies_with_p1 = df[df.producers==producer1]._id.tolist()
    ## find movies with matching gap that producer did not work for
    df_match_gap = df[df.year.isin([year1+maxP, year1-maxP]) & ~df._id.isin(movies_with_p1)]
    ## choose producer2 from producers with only one movie - makes it easier
    producer2 = np.random.choice(producers_one_movie)
    ## choose movie that has the movie in year1 +-1 by producer 2
    movie_match_gap = df_match_gap[df_match_gap.producers == producer2]
    while len(movie_match_gap) != 1: # producer2 might not work in the year2 
        producer2 = np.random.choice(producers_one_movie)
        movie_match_gap = df_match_gap[df_match_gap.producers == producer2]
    movie2 = movie_match_gap._id.iloc[0]
    
    #check if we did not make mistake in choosing two movies and producers
    ## whether producer2 is in movie_swap
    check1 = len(df[(df.producers == producer2)& (df._id==movie_swap)])
    ## whether producer1 is in movie2
    check2 = len(df[(df.producers == producer1)& (df._id==movie2)])
    if check1 != 0 or check2 != 0:
        raise ValueError('Your algorithm is wrong, check it. I dont know where it went wrong')
        
    #swap
    df.loc[(df._id == movie_swap) & (df.producers == producer1), 'producers'] = producer2
    df.loc[(df._id == movie2) & (df.producers == producer2), 'producers'] = producer1    
    return df


def get_swap_movie(df, producers_multi_movie, maxP):
    """
    Potential movies to be swapped, also prducer1, movie1, year1
    Input:
        df - unlistified
    Output:
        df_swap - pick a movie that will be swapped 
        producer1 - producer that will be swapped to match the maxP
        movie1 - movie that will be the baseline
        year1 - year of movie1 
    """
    producer1 = np.random.choice(producers_multi_movie)
    # choose a movie made by producer 1
    producer1_movies = df[df.producers == producer1]
    m1_list = producer1_movies._id.tolist()
    movie1 = np.random.choice(m1_list)
    # year that the movie was produced
    year1 = producer1_movies[producer1_movies._id == movie1].year.iloc[0]
    # choose another movie by producer1 that is not year1 +- maxp
    df_swap = producer1_movies[~producer1_movies.year.isin([year1+maxP, year1-maxP])]
    return df_swap, producer1, movie1, year1

def aggregate(df, key_col='_id', val_col='producers'):
    keys, values = df[[key_col, val_col]].sort_values(key_col).values.T
    ukeys, index = np.unique(keys,True)
    arrays = np.split(values,index[1:])
    df2 = pd.DataFrame({key_col:ukeys,val_col:[list(a) for a in arrays]})
    return df2


def organize_dataframe(df_input, key_col='_id', val_col='producers'):
    """
    when the movie-producer unlistyfied result is finalized, put it together into format that is read by the model
    Input:
        df_input - unorgazined dataframe
        key_col - 
        val_col - 
    Output:
        df_output - aggregated dataframe
    """
    df1 = aggregate(df_input, key_col, val_col)
    df2 = df_input[['_id', 'year', 'producer_num']].drop_duplicates()
    
    df_output = pd.merge(df1, df2, on=key_col).sort_values('year').dropna()
    return df_output
