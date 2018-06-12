"""
Object: Open doctor schedule csv file and 
        1. Make artificial schedules
        2. Make networks
Input: Transformed csv file ex: "../Transformed_Data/Transformed_Final_Schedule_10-3-11_to_06-30-12.csv
Output: 1. Artificial schedules csv file
        2. Doctors network

Created by Hyojun Ada Lee, October 13, 2016 
"""
##########Packages##########
#System
import networkx as nx
from networkx.readwrite import json_graph
import json
import sys
import random
from copy import copy
import numpy as np
import os
from copy import deepcopy
import graph_tool.all as gt
from collections import Counter, defaultdict

#Local



###Local###
src_dir = os.path.abspath(os.path.join(os.pardir, os.pardir,'src'))
sys.path[0] = src_dir

import gale.general.errors as gerr
# import parsers.reader as read


#Classes
class Producers(object):
    def __init__(self):
        self.node_ID = None        #Last name
        self.type = 'P'
        self.belief = None
        self.status = None
        self.role = [] #role of the producers, if the role has changed each movie
        self.movie_ids = []

    def instantiate_belief(self, belief_type, b_threshold, seeds):
        '''
        Instantiate the belief of an individual
        '''
        #Do empirical, Weiss and Wunderink are 1.0,
        # all others are 0.0
        if belief_type=='empirical':
            if self.node_ID in seeds:
                self.belief = 1.0
                self.status = 'Adopter'
            else:
                self.belief = 0.0
                self.status = 'NonAdopter'
        #Combination of empirical and random
        elif belief_type=='empirical-random':
            if self.node_ID in seeds:
                self.belief = 1.0
                self.status = 'Adopter'
            else:
                self.belief = random.uniform(0.0, b_threshold)
                self.status = 'NonAdopter'
        #Supplied by file
        elif belief_type=='apriori':
            pass
        else:
            m = "I do not recognize the method of: %s, to instantiate the belief"
            gerr.generic_error_handler(message=m)

class Movies(object):
    def __init__(self):  
        self.node_ID = None
        self.type = 'M'          
        self.title = None
        self.producers = None
        self.year = None

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)
##########Functions##########
##########################
## Generate attributes
##########################

def make_attribute_list(df_raw, belief_type, belief_threshold=1.0):
    """
    Making attribute dictionary: Shifts and Doctors
    Input:
        df_raw - DataFrame with freshly read data
        belief_type - string, what kind of belief 'empirical', 'empirical-random', 'apirori' + to be added
        belief_threshold - float 0-1
    Output:
        movies - list of movie class (NODE)
        producers - list of producer classes (NODE)
    """
    df = df_raw.copy(deep=True).dropna()
    producer_ids = [] #producer id list
    producers = [] #producer class list
    movies = [] #movie class list
    years = []
    #Start of experiment date
    exp_start_year = df['year'].iloc[0]
    seeds = []
    first_producers = [p[0] for p in df.producers.iloc[0]]
    #check for movies that have only one producer
    if len(first_producers) == 1:
        seeds = first_producers
        second_producers = [p[0] for p in df.producers.iloc[1]]
        seeds.append(random.choice(second_producers))
    else:
        seeds =  random.sample(first_producers, 2)#first 2 producers
    

    #get shifts as class
    for i, row in df.iterrows():
        #get list of producers for the movie
        movie_producers = [i[0] for i in row['producers']] #get only producers ids, get rid of producer roles
        #add movies, assume that there are no duplicate movie rows
        movie = Movies()
        movie_id = row['_id']
        movie.node_ID = movie_id
        movie.type = 'M'
        movie.producers = movie_producers
        movie.year = row['year']
        movie.title = row.title
        years.append(movie.year)
        movies.append(movie)
        
        # self.node_ID = None        #Last name
        # self.type = 'P'
        # self.belief = None
        # self.status = None
        # self.role = [] #role of the producers, if the role has changed each movie
        # self.movie_ids = []

        for p, role in row['producers']:
            #instiantiate producer if the producer is not already in the systme
            if p not in producer_ids:
                producer = Producers()
                producer.node_ID = p
                producer.instantiate_belief(belief_type, belief_threshold, seeds)
                producer.type='P'
                producer.role.append([role, movie_id, movie.year])
                producer.movie_ids.append(movie_id)
                producer_ids.append(p)
                producers.append(producer)
            else:
                #add the movie
                for p_class in producers:
                    if p_class.node_ID == p:
                        p_class.role.append([role, movie_id, movie.year])
                        p_class.movie_ids.append(movie_id)
    return movies, producers
#########################
#### Make schedules  ####
#########################
def build_temporal_network(df_data, belief_type, b_threshold=1.0, plot_graph = False):
    """
    Create network between doctors and shifts
    input:
        df_data - DataFrame, shift data without header, from csv
        belief_type: Way to generate belief value.
                     choices are: empirical, random, apriori
        plot_graph: Boolean, make a networkx plot fo the graph
    output:
        G: NX Graph Object of shift network 
    """
    #Generate attributes for physicians and shifts

    movies, producers = make_attribute_list(df_data, belief_type, b_threshold)

    G = nx.Graph()
    # Add nodes - movies:
    for key in movies:
        att_dict = {'node_type': key.type, 'title': key.title, \
                    'producers': key.producers, 'year' : int(key.year)}

        G.add_node(key.node_ID, **att_dict)
    # Add nodes - producers:
    for key in producers:
        att_dict = {'node_type': key.type,'belief' : key.belief, \
                    'movies' : key.movie_ids, 'roles': key.role}
        G.add_node(key.node_ID, **att_dict)

    # Add edges - between movies and producers
    # Look Here to see the edge connection 
    for node1 in G.nodes():
        if G.node[node1]['node_type'] =='M':
            movie = node1
            for node2 in G.nodes():
                if G.node[node2]['node_type'] == 'P':
                    movies = G.node[node2]['movies']
                    if movie in movies:
                        G.add_edge(node1, node2) 
    #Graph visualization, if chosen
    if plot_graph:
        plot_network(G)
    return G





######################## From old code look at 
def build_projected_network(df, belief_type, b_threshold):
    """
    Create projected temporal network between doctors and shifts
    input:
        df - DataFrame, shift data without header
        belief_type - way to generate initial belief value.
                    choices: empirical, random, apriori
        b_threshold - belief status threshold. Use to generate the initial adoption state
        weight - True: make weight network, default is False
    output:
        G - NX graph object
    """

    shifts, doctors = make_attribute_list(df, belief_type, b_threshold)

    G = nx.MultiGraph()
    for key in doctors:
        doc_dict = {'doc_type':key.doc_type, 'belief': key.belief, 'shifts':key.shift_order, 'status':key.status}
        G.add_node(key.node_ID, doc_dict)

    for key in shifts:
        subject_id, object_id = key.attendings, key.fellows
        G.add_edge(subject_id, object_id, days=key.days, date=key.start_date)

    return G
    
def plot_network(G, wfname = '../../result/networks/shift_doctor_network_graph.eps'):
    '''
    Makes a networkx plot fo the network
    '''
    plt.figure(figsize=(12, 12))
    
    
    #Step1: Get the list of the graph:
    nodeTypeS = []
    nodeTypeDA = []
    nodeTypeDF = []
    for node in G.nodes():
        if G.node[node]['nodeType'] == 'S':
            nodeTypeS.append(node)
        if G.node[node]['nodeType'] == 'D':
            if G.node[node]['docType'] == 'F':
                nodeTypeDF.append(node)
            if G.node[node]['docType'] == 'A':
                nodeTypeDA.append(node)
    pos = nx.spring_layout(G)
    
    #Step2: Draw the nodes
    nx.draw_networkx_nodes(G, pos, nodelist = nodeTypeS, node_color = 'r', \
                           node_size = 100)
    nx.draw_networkx_nodes(G, pos, nodelist = nodeTypeDA, node_color = 'b', \
                           node_size = 100)
    nx.draw_networkx_nodes(G, pos, nodelist = nodeTypeDF, node_color = 'g', \
                          node_size = 100)
    #Step3: Draw the edges
    edge_list = G.edges()
    nx.draw_networkx_edges(G, pos, edgelist = edge_list, width = 1.0)
    #Step4: Node labels:
    label_dic = {}
    for node in G.nodes():
        if G.node[node]['nodeType'] == 'D':
            label_dic[node] = node
#         if G.node[node]['nodeType'] == 'S':
#             label_dic[node] = str(G.node[node]['startDate']) + '-' + str(G.node[node]['team'])
    
    nx.draw_networkx_labels(G, pos, labels = label_dic, font_size = 10)
    plt.savefig(wfname)
    plt.show()


def datetime_to_string_json(G):
    """
    for json.dump, change the datetime to datetime_to_string_json
    """
    for node in G.nodes():
        if G.node[node]['node_type'] == 'S':
            startDate = str(G.node[node]['start_date'])
            G.node[node]['start_date'] = startDate
    return G


def save_network(G, sched_type, sched_ver, result_dir = "../../result/networks/"):
    '''
    Saves the networkx graph object as a json file
    Input:
        G - networkx graph object
        sched_type - string, heuristic or random, False - if it is real schedule
        sched_ver - string, schedule version, so graph correlates with the schedule
        result_dir - string, result directory
    '''
    new_G = datetime_to_string_json(G)
    file_name = 'movie_producer_network_{}_{}.json'.format(sched_type, sched_ver)
    wfname = os.path.join(result_dir, file_name)
    with open(wfname, 'w') as outfile:
        json.dump(new_G.nodes(data=True), outfile, cls=ComplexEncoder)






#make bipartite network using graph_tools
def make_graph(movie_producer_dict):
    """
    Transform movie documents into a bipartite producer-movie netowrk with M moveis and P producers
    Input:
        movie dictionary: {movie_id:{title, producer_list, year, }}
    Output:
        movie graph
        nodes 0,...,M-1 Movie nodes
        nodes M,....,M+P-1 Producer nodes
    Vertex properties
        - 'id' id of the movies or producers
        - 'kind', 0 for movies, and 1 for producers
    Edge properties 
        - 'year' year for when the connection was made
    """

    M = len(set(movie_producer_dict.keys()))
    #make a graph
    g = gt.Graph(directed=False)
    #define node properties
    #id
    prop_id = g.vp['name'] = g.new_vertex_property("string")
    #bipartite group
    prop_kind = g.vp['kind'] = g.new_vertex_property("int")
    #edge property
    prop_edge = g.ep['year'] = g.new_edge_property("int")

    #add vertex dictionary
    movie_add = defaultdict(lambda: g.add_vertex())
    producer_add = defaultdict(lambda:g.add_vertex())
    
    #add all movies and producers as nodes
    for _id, movie_dict in movie_producer_dict.items():
        title = movie_dict['title']
        #vertex
        m = movie_add[_id]
    #add all movies and producers as nodes
    for _id, movie_dict in movie_producer_dict.items():
        title = movie_dict['title']
        producers = [lst[0] for lst in movie_dict['producers']]
        year = movie_dict['year']
        #vertex
        m = movie_add[_id]
        #property
        prop_id[m] = _id
        prop_kind[m] = 0
        for producer in producers:
            p = producer_add[producer]
            prop_id[p] = producer
            prop_kind[p] = 1
            e = g.add_edge(m, p)
            prop_edge[e] = year
    return g

def get_P(g):
    '''
    return number of producer-nodes == types
    '''
    return int(np.sum(g.vp['kind'].a==1)) # no. of types
def get_M(g):
    '''
    return number of movie-nodes == number of documents
    '''
    return int(np.sum(g.vp['kind'].a==0)) # no. of types
def get_E(g):
    '''
    return number of edges == tokens
    '''
    return int(g.num_edges()) # no. of types


def sbm_fit(g, overlap=False):
    '''
    Infer the block structure of the bipartite word-document network.
    Default: a hierarchical, nonoverlapping blockmodel.
    IN:
    - g, graph, see make_graph
    OUT:
    - result dictionary with groups, partitions, and prodperie
    '''

    #vertex property map to ensure that words and documents are not clustered together

    clabel = g.vp['kind']

    # inferecne 
    state = gt.minimize_blockmodel_dl(g, deg_corr=True, overlap=False, state_args={'clabel':clabel, 'pclabel':clabel})

    #collect all the results
    result = {}
    result['state'] = state
    result['mdl'] = state.entropy()

    # keep the list of movies and producers
    movies = [g.vp['name'][v] for v in g.vertices() if g.vp['kind'][v]==0]
    producers = [g.vp['name'][v] for v in g.vertices() if g.vp['kind'][v]==1]

    result['movies'] = movies
    result['producers'] = producers

    P = get_P(g) #get producer numbers
    M = get_M(g) #get movie numbers
    E = get_E(g) #get edge numbers

    #get the group membership statistics
    L = len(state.levels)
    result['L'] = L

    dict_stats_groups={}
    #martin what is this?
    #for each level in the hierachy we make a dictionary with the node-group statistics
    #e.g. group-membership
    # we omit the highest level in the hierarchy as there will be no more distinction between 
    # movie and producer groups

    for l in range(L-1):
        dict_stats_groups_l = get_groups(state,g,l=1)
        dict_stats_groups[l] = dict_stats_groups_l
    result['stats_groups'] = dict_stats_gropus

    return result