"""
Helper functions to generate synthetic network
"""
##########Packages##########
#System
import sys
import os
import json
import random
import string
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



### Classes ###


### Functions ###

### general functions for all synthetic networks ### 
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
    movie_producer_df.loc[:,'producer_num'] = movie_producer_df['producers'].apply(lambda x: len(x))

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
def id_generator(size=8, chars=string.ascii_uppercase, nums=string.digits):
    """
    Generate ids of size 8, starting with 2 characters and 6 numbers
    """
    uid = ''.join(random.choice(chars) for i in range(2))
    uid += ''.join(random.choice(nums) for i in range(size-2))
    return uid


def generate_producers(size):
    """
    generate unique producer ids for given size
    input:
        size - int number of total producers
    output:
        producer_list - list of generated producer list
    """
    producer_list = []
    while len(producer_list) < size:
        new_id = id_generator()
        if new_id not in producer_list:
            producer_list.append(new_id)
    return producer_list


def sample_producers(generated_producers, year, num_producers, year_assignment):
    """
    Sample producers from the total so that unique(sum) of producers per year adds up to the total producers
    input:
        generated_producers - list of ids of the total producers
        year - the year of the interest
        num_producers - int of the number of producers for the year
        year_assignment - dict {producer_id: year}, the baseline assginment of the year
    output:
        producer_list - list of the producer ids for the year
    """
    #get the producers that have the year as the assignment
    baseline_producers = [p for p, y in year_assignment.items() if y == year ]
    #get the producers that does not have the year of interest assgined
    non_baseline_producers = [p for p in generated_producers if p not in baseline_producers]
    #pick random producers from non baseline producers 
    #so that the total sum of the baseline + addition will be the number of producers needed
    add_producers = np.random.choice(non_baseline_producers, size=num_producers-len(baseline_producers), replace=False)
    
    producer_list = baseline_producers + list(add_producers)
    return producer_list

def bootstrap(movie_num, num_producers):
    """returns movie numbers per producers based  on movie_num"""
    n = len(movie_num)
    movie_num = np.array(movie_num)
    idx = np.random.randint(0, n, (num_producers, 1))
    samples = movie_num[idx]
    samples = samples.reshape((num_producers, )).tolist()
    return samples

### assign team number
def assign_team_size(df_input, number_of_producers_per_year):
    
    for year, df in df_input.groupby('year'):
        num_producers = number_of_producers_per_year[year] #duplicate producers are already dropped
        mean_size = np.mean(df.producer_num.tolist())
        mean_ceil = np.ceil(mean_size)
        mean_floor = np.floor(mean_size)
        #fix the team size to its mean
        df.loc[:,'producer_num'] = df.producer_num.apply(team_size, args=(mean_ceil, mean_floor))
        df_input['producer_num'].update(df.producer_num)
    return df_input

### define producers ###
def team_size(x, mean_ceil, mean_floor):
    return random.choice([int(mean_ceil), int(mean_floor)])

def assign_gender(row, gender_df):
    try:
        gender = gender_df[gender_df._id == row.producer_id].gender.values[0]
    except IndexError:
        gender='male'
    return gender

### make version ###
def make_version(num_schedules, size=6, nums=string.digits):
    version_list = []
    while len(version_list) < num_schedules:
        uid = ''.join(random.choice(nums) for i in range(size))
        if uid not in version_list:
            version_list.append(uid)
    return version_list


### synthetic 1 ###
def assign_producers(producers, values):
    """
    Assign producers to certain year or movie
    input:
        producers - list of producer ids
        values - value that will be assigned to the producer
    output:
        assignment_dict - {producer:val} dict
    """
    sampling = np.random.choice(values, size=len(producers))
    assignment_dict = dict(zip(producers, sampling))
    return assignment_dict


### synthetic 2 ###
def generate_movie_num(tot_num_movie, producers_dict, movies_dict):
    '''
    Generate exact number of movies per producer
    Input
        tot_num_movies - integer of total number of movies needed
        producer - dictionary of gender list of producers names that are generated 
        num_movies - dictionary of gender list of number of movies in the original data
    Output
        dict_movies - dictionary of key:producer and value:number of movies
    '''
    dict_movies = {}
    #female movies:
    f_movie_list = bootstrap(movies_dict['female'], len(producers_dict['female']))
    #male movies:
    m_movie_list = bootstrap(movies_dict['male'], len(producers_dict['male']))
    movie_list = f_movie_list + m_movie_list
    #the sum of total movies for producers has to match the total producers in each team
    while sum(movie_list) != tot_num_movie:
        #female movies:
        f_movie_list = bootstrap(movies_dict['female'], len(producers_dict['female']))
        #male movies:
        m_movie_list = bootstrap(movies_dict['male'], len(producers_dict['male']))
        movie_list = f_movie_list + m_movie_list
        #the sum of total movies for producers has
    f_dict_movies = dict(zip(producers_dict['female'], f_movie_list))
    m_dict_movies = dict(zip(producers_dict['male'], m_movie_list))
    dict_movies['female'] = f_dict_movies
    dict_movies['male'] = m_dict_movies
    return dict_movies

def assign_team(producers_unique, team_size_list):
    """
    Assign producers to each team so that each team consists of unique producers 
    and all producers participate in at least one movie
    input:
        producers - list of unique producer ids
        team_size_list - list of team sizes
    output:
        producer_list - list of producers with the team sizes
    """
    add_num = int(sum(team_size_list))-len(producers_unique)
    add_producers = np.random.choice(producers_unique, size=add_num, replace=True)
    producers = producers_unique + list(add_producers)
    
    producer_dict = dict(Counter(producers))
    producer_team = []
    for ts in team_size_list:
        team = [1,1]
        while len(set(team)) != len(team):
            #use producer list with duplicates 
            #to increase the change of picking producers with many movie appearnces
            team = list(np.random.choice(producers, size=ts, replace=False))
        producer_team.append(team)
        for p in team:
            producer_dict[p] -= 1
            if producer_dict[p] == 0:
                producer_dict.pop(p, None)
                producers = [i for i in producers if i != p]
    return producer_team

### synthetic 3 ###
def get_gaps_gender(df_producers, col_name='producer_id'):
    """
    df - dataframe with columns with movie-producer-year-gender
    """
    gap_dict = {}
    for gender, df in df_producers.groupby('gender'):
        gap_dict[gender] = []
        for p, group in df.groupby(col_name):
            group_sorted = group.sort_values('year')
            diff = group_sorted.year.diff().values
            gap_dict[gender].extend(diff[~np.isnan(diff)])
    return gap_dict

def get_gaps(df_producers, col_name='producer_id'):
    gap_result = []
    for p, group in df_producers.groupby(col_name):
        group_sorted = group.sort_values('year')
        diff = group_sorted.year.diff().values
        gap_result.extend(diff[~np.isnan(diff)])
    return gap_result
    
def assign_gaps(movie_dict, gap_dict, years=10):
    """
    assigns gaps list to each producer
    Input:
        movie_dict - {gender:producer:number of movies}
        gap_dict - {gender:[gap_numbers]}
        years - year section (1990-1999)
    Output:
        gap_dict_per_producer {producer:[gap_list]}
        movie_dict_per_producer {producer:movie_num}
    """
    gap_dict_per_producer = {}
    movie_dict_per_producer = {}
    for gender, m_dict in movie_dict.items():
        for producer, m_num in m_dict.items():
            g_list = gap_dict[gender] #gaps to choose from
            if m_num >= 20:
                g_list = [g for g in g_list if g in [0, 1, 2, 3]]
                g_list.extend([0]*len(g_list))
            gaps = [100]
            while sum(gaps) >= years:
                gap_list, occur = zip(*Counter(g_list).items())
                gap_list = np.array(gap_list)
                occur = np.array(occur)/sum(occur)
                gaps = np.random.choice(gap_list, size=m_num-1, replace=True, p=occur)
            gap_dict_per_producer[producer] = gaps
            movie_dict_per_producer[producer] = m_num
    return movie_dict_per_producer, gap_dict_per_producer

def distribute_movies(df, gap_dict_per_producer):
    """
    Distribute movies according to the gap dist
    Input:
        df - dataframe for movies
        gap_dict_per_producer - dictionary of gaps per producer
    Output:
        df - dataframe for movies now filled with producers
    """

    df = df.copy(deep=True)
    sorted_gap_dict_per_producer = sorted(gap_dict_per_producer.items(), key=lambda kv: (sum(kv[1]), len(kv[1])), reverse=True)
    producers = [p[0] for p in sorted_gap_dict_per_producer]

    for p in producers:
        gaps = gap_dict_per_producer[p]
        np.random.shuffle(gaps)
        first_movie = find_first_available_movie(df, sum(gaps))
        available_movies = find_unfilled_movies(df)
        # when is the producer's first active year
        start_year = df[df._id == first_movie].year.values[0]
        # find the years that the producer made movie
        working_years = calculate_years(start_year, gaps)
        chosen_movies = choose_movies(available_movies, working_years)
        df = add_producers(df, p, chosen_movies)
    return df

def add_producers(df, p, movie_list):
    """
    Append producer p to the producer list in df for the movie list
    Input:
        df - dataframe of the movies and producers
        p - producer
        movie_list - list of the movies that producer participated in
    Output:
        df - dataframe with the appended producer
    """
    mask = df['_id'].isin(movie_list)
    df_valid = df[mask]
    df.loc[mask, 'producers'] += [p]
    return df

def find_first_available_movie(df, N):
    """
    get the first movie to start
    """
    # find movies that are not filled with producers
    df['availability'] = df.producers.apply(lambda x: len(x))
    df_available = df[df.availability < df.producer_num]
    # find movies that has the possibe years considering the sum of gaps N
    last_year = df.iloc[-1].year
    possible_year = last_year - N
    df_available = df_available[df_available.year <= possible_year]
    available_movie = np.random.choice(df_available._id.tolist())
    return available_movie

def calculate_years(start_year, gaps):
    """
    producers active year
    """
    years = [start_year]
    for g in gaps:
        years.append(years[-1]+g)
    return years

def find_unfilled_movies(df):
    df['availability'] = df.producers.apply(lambda x: len(x))
    df_available = df[df.availability < df.producer_num]
    available_movies = df_available.groupby('year')['_id'].apply(list).to_dict()
    return available_movies

def choose_movies(available_movies, working_years):
    """
    available_movies - {year:[list of movies]}
    workign_years - years that prodcer produced movie
    """
    participating_movies = []
    for key, values in Counter(working_years).items():
        participating_movies.extend(np.random.choice(available_movies[key], values, replace=False))
    return participating_movies

def append_producer(row, p, movies):
    if row._id in movies:
        row.producers.append(p)
    return row  