 
"""
contagion model
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
#global
import sys
import os
from operator import itemgetter
from itertools import combinations
from math import ceil
import random
from copy import deepcopy
import numpy as np
import networkx as nx
import pandas as pd
#from dateutil import parse

#Local
src_dir = os.path.abspath(os.path.join(os.pardir, os.pardir, 'src'))
sys.path[0] = src_dir
import model.general as gen
import network.shift_graph_maker as sgm

#############Functions#########################3

def calculate_belief(agent_i, agent_j, probability, dose, threshold, weight=1):
    '''
    Calculate the change in belief values for the two agents
    Input:
        agent_i: Node dictionary of first agent
        agent_j: Node dictionary of second agent
        probability - probability of being infected
        dose - infection size
        threshold - belief threshold
    Output:
        belief_i: New belief value of agent i
        belief_j: New belief value of agent j
    '''
    w = weight
    #Update in beliefs
    #both non adopters
    belief_i = agent_i['belief']
    belief_j = agent_j['belief']
    prob_inf = random.random() #probability of getting infected
    # prob_imm = random.random() #probability of
    #i adopter, j non adopter
    if belief_i >= threshold and belief_j < threshold:
        #gets infected with probability 
        if prob_inf <= probability:
            belief_j += w*dose
    #j = adopter, i = non-adopter
    elif belief_i < threshold and belief_j >= threshold:
        #gets infected with probability 
        if prob_inf <= probability:
            belief_i += w * dose

    belief_i = gen.limit_belief(belief_i)
    belief_j = gen.limit_belief(belief_j)
    
    return belief_i, belief_j
    
def contagion_belief_propagation_temporal_network(G, prob, dose, threshold, interaction=20):
    """
    Runs the dynamics for the persusaion model on the shift network
    Input:
        G - The shift network
        prob - Probability of being infected
        dose - Size of the dose
        threshold - belief threshold
    Output:
        adopter_history - list of paired datapoints (day, number adopters)
    """
    #Find the first shift date (project start date)
    start_year = sorted([G.node[n]['year'] for n in G.nodes() \
                                if G.node[n]['node_type']=='M'])[0]

    #Make the movie nodes list of list (node_id, movie_id)
    movie_nodes = [[n, G.node[n]['movie_id']] for n in G.nodes() if G.node[n]['node_type']=='M']
    movie_nodes.sort(key=itemgetter(0, 1))

    #print shift_nodes
    #print '---------------'

    #Get the producer node ids
    producer_node_ids = [n for n in G.nodes() if G.node[n]['node_type']=='P']

    #Doctor Adopters, node ids
    adopters = [n for n in producer_node_ids if G.node[n]['status'] == 'Adopter']

    #Adopter dictionary and their time points: {time:#of adopters}
    adopter_history = [[0, start_year, len(adopters)]]
    #print 'START---->'
    #Iterate through the movies
    #Get the list of moives in order
    for movie_order, movie_id in movie_nodes:
        year = G.node[movie_order]['year']
        #Identify the movie node
        movie_node = G.node[movie_order]
        #Iterate through producer
        #If any of the producer in the group is an adopter, she will influce everyone
        movie_producer_ids = list(G.neighbors(movie_order))
        movie_adopters = [x for x in movie_producer_ids if G.node[x]['status'] == 'Adopter']
        movie_nonadopters = [x for x in movie_producer_ids if G.node[x]['status'] == 'NonAdopter']
        i = 0
        if any(movie_adopters): #if any of the producers in the movie is an adopter:
            while i < interaction and movie_nonadopters:
                adopter = random.choice(movie_adopters) #choose random adopters from the movie producers
                nonadopter = random.choice(movie_nonadopters) #choose random non adopter from ovie producers
                b_a, b_na = calculate_belief(G.node[adopter], G.node[nonadopter], prob, dose, threshold)
                G.node[adopter]['belief'] = b_a
                G.node[nonadopter]['belief'] = b_na
                #update producer status
                G = gen.update_adoption_status(G, producer_node_ids, threshold)
                #update movie adopter and movie non adopter
                movie_adopters = [x for x in movie_producer_ids if G.node[x]['status'] == 'Adopter']
                movie_nonadopters = [x for x in movie_producer_ids if G.node[x]['status'] == 'NonAdopter']
                i += 1
        #Calculate the number of adopters
        adopters = [n for n in producer_node_ids if (G.node[n]['status'] == 'Adopter')]# and (G.node[n]['doc_type'] == 'A')]
        #Calculate the order of the movie 1
        movie_count = movie_order
        # print(shift_node['start_date'], day_count, len(adopters))
        adopter_history.append([movie_count, year, len(adopters)])
    #get the end date
    final_year = year
    #Backfill the missing days
    # adopter_history = np.array(gen.backfill_dates(adopter_history, end_date = final_year))

    return np.array(adopter_history)


def contagion_sequential_projected_network(G, step, interval, prob, dose, threshold, iterations=20):
    """
    Sequential belief update of contagion
    input:
        G - network of only producers connected by movies
        step - int, number of movies in the G block
        interval - pandas object interval (start_year, end_year) of the aggregation block
        prob, dose, threshold, contagion model parameters 
        iterations - how many iterations I will use for so called one 'step' of belief update
    output:
        G - updated G
        adopter_history - number of adopter increase over the steps
    """
    G = G.copy()
    #get the initial adopters
    adopters = [n for n in G.nodes() if G.node[n]['status'] == 'Adopter']
    adopter_history = [[(interval.left, interval.right),0, len(adopters)]]


    for step in range(step): #one movie is noe step
        i = 0
        #chose a random node to start
        adopter = random.choice(adopters)
        neighbors = list(G.neighbors(adopter))
        nonadopter_neighbors = [x for x in neighbors if G.node[x]['status']=='NonAdopter']
        while i < iterations and nonadopter_neighbors:
            #choose non adopter from neighbors
            nonadopter = random.choice(nonadopter_neighbors)
            b_a, b_na = calculate_belief(G.node[adopter], G.node[nonadopter], prob, dose, threshold)
            G.node[adopter]['belief'] = b_a
            G.node[nonadopter]['belief'] = b_na
            #update network status
            G = gen.update_adoption_status(G, G.nodes(), threshold)
            #get adopters from the neighbors
            adopter_neighbors = [x for x in neighbors if G.node[x]['status']=='Adopter']
            if adopter_neighbors != []:
                adopter = random.choice(adopter_neighbors)
            nonadopter_neighbors = [x for x in neighbors if G.node[x]['status']=='NonAdopter']
            neighbors = list(G.neighbors(adopter))
            i += 1
        adopters = [n for n in G.nodes() if (G.node[n]['status'] == 'Adopter')]
        adopter_history.append([(interval.left, interval.right),step+1, len(adopters)])
    return G, np.array(adopter_history)

def cumulative_adopters_projected_network_sequential(df_raw, interval, seeds, belief_type, p, d, threshold):
    """
    Calculate cumulative of projected network over time
    input
        df_raw - df data with movies as rows
        interval - interval of aggregation
        seeds - initial adopters
    """
    start_year = df_raw.year.iloc[0] - 1
    end_year = df_raw.year.iloc[-1] + 1
    grouped_by_year = df_raw.groupby(pd.cut(df_raw['year'], np.arange(start_year, end_year, interval)))
    
    #make dictionary that keeps track of belief scale
    total_nodes = list(set([i[0] for sublist in df_raw.producers.tolist() for i in sublist]))
    belief_dict = {n:1 if n in seeds else 0 for n in total_nodes}
    
    existing_adopters = list(set(seeds))
    total_adopter_history = []
    total_steps = 0
    for interval, df in grouped_by_year:
        #make network
        G = sgm.build_projected_network(df, seeds, belief_type, threshold)
        #update beliefs in new G for the nodes that were already been in the system
        for n in G.nodes():
            G.node[n]['belief'] = belief_dict[n]
        #update adoption status
        G = gen.update_adoption_status(G, G.nodes(), threshold)
        #calculate adopter
        G_update, adopter_history = contagion_sequential_projected_network(G, len(df), interval, p, d, threshold)
        
        #calculating adopters that are in the system, but was not in G
        adopter_update = [n for n in G_update.nodes() if G_update.node[n]['status']=='Adopter'] 
        adopters_not_in_G = [k for k in belief_dict.keys() if (belief_dict[k] >= threshold) and (k not in adopter_update)]
        #add adopters that are not in the sub G but are actually in the system
        adopter_history[:,2] += len(adopters_not_in_G)

        if total_adopter_history == []:
            total_adopter_history = adopter_history    
        else:
            #add the dates
            adopter_history[:,1] += (len(total_adopter_history)-1)            
            total_adopter_history = np.append(total_adopter_history, adopter_history[1:], axis=0)
        #update the belief dictionary
        for k in G_update.nodes():
            belief_dict[k] = G_update.node[k]['belief']
        
    return total_adopter_history

#################################################################################################################################
#################################################################################################################################
#################################################################################################################################
#################################################################################################################################

def contagion_synchronous_belief_propagation_projected_network(G, prob, dose, threshold, weight_type, time_limit = 10000):
    """
    Objective: Synchronous belief updates of the projecte network, unweighted network
    Input: 
        G - NX graph of doctors, static
        prob - probability of infection
        dose - dosage of infection
        threshold - threshold for being infected
        weight_type - 'none', 'days', 'shift'
    Output:
        adopter_list - list of adopters by day
    """
    G = G.copy()
    G = calculate_weight(G, weight_type)
    t = 1
    adopters = [n for n in G.nodes() if G.node[n]['status'] == 'Adopter']
    # print('Adopters', len(adopters))
    adopter_history = [[0, len(adopters)]]
    while t < time_limit:
        #saving belief updates to new dictionary, because, if we update G itself, it can modify the beliefs at time t not time t+1
        belief_update = {}
        for subject_id in G.nodes():
            #Calculating subject id's new belief at time t. 
            old_belief = G.node[subject_id]['belief']
            new_belief = deepcopy(old_belief)
            total_edge_weights = sum([G[subject_id][key]['weight'] for key in G.edge[subject_id]])
            for object_id in G.neighbors(subject_id):
                shift_length = 1
                w = G[subject_id][object_id]['weight']/total_edge_weights
                b1, b2 = calculate_belief(G.node[subject_id], G.node[object_id], shift_length, prob, dose, threshold, w)
                new_belief += (b1 - old_belief) #only update teh delta
            new_belief = gen.limit_belief(new_belief)
            #Saving the new belief in the dictionary
            belief_update[subject_id] = new_belief
        #update belief for time t for G, 
        for node, belief in belief_update.items():
            G.node[node]['belief'] = belief
        #see if anybody became adopters
        G = gen.update_adoption_status(G, G.nodes(), threshold)

        adopters = [n for n in G.nodes()if G.node[n]['status'] == 'Adopter']
        adopter_history.append([t, len(adopters)])
        t+=1
    return G, np.array(adopter_history)



def calculate_weight(G, weight_type):
    """
    Add edge attribute depending on which weight type:
    type 'shifts' number of shifts together 'days' = number of days together
    input:
    G - Network graph
    weight_type - 'shifts', or 'days'
    return
    G - Netwrk graph with edge attributute 'weight' added
    """
    for edge_pair in set(G.edges()):
        node1, node2 = edge_pair
        if weight_type == 'shifts':
            weight = len([k for k in G.edge[node1][node2].keys() if type(k)==int])
        elif weight_type == 'days':
            weight = sum([att['days'] for k, att in G.edge[node1][node2].items() if type(k)==int])
        else:
            weight = 1
        G.edge[node1][node2]['weight'] = weight
    return G

def choose_neighbor(G, node, weight_choice):
    """
    returns one neighbor of given node to interacct
    input:
        G - network
        node - the given node
        weight - True/False weither we are going to consdier weighting
    return:
        neighbor - neighboring node of given node
    """
    #weigh in 
    if weight_choice == 'neighbor':
        neighbors = [n for n in G.neighbors(node) for i in range(G.edge[node][n]['weight'])]
        neighbor = random.choice(neighbors)
    else:
        neighbor = random.choice(G.neighbors(node))
    return neighbor    


def check_adopter(G, nodes_data, b):
    """
    if belief in node data is different from G nodes, update G
    input:
        G - 
        node_data - dictionary of nodes with belief as values
        b - threshold
    """
    for n in G.nodes():
        if n in nodes_data.keys():
            G.node[n]['belief'] = nodes_data[n]
            if G.node[n]['belief'] >= b:
                G.node[n]['status'] = 'Adopter'
    return G

"""
Here is the aggreagate of all the above partial functions
"""

def cumulative_adopters_over_time_projected_network_synchronous_update(physician_sched_dict, belief_type, p, d, b, weight_type, time_limit=10000):
    """
    When the schedule is cut into months, get the cumulative adopters over time for the projected network. 
    input:
        physcian_sched_dict: cut up sched. dictionary of dfs
        belieft_type: 'empirical' for the contagion model
        p, d, b - contagion model parameters
    output:
        entire_adopter_history: numpy array of cumulative adopters [days, adopters]
    """
    entire_adopter_history = np.empty([0,2],dtype=int)
    start_date = physician_sched_dict[0].Date.iloc[0]
    belief_dict = {}
    cumulative_adopters = [] #account for addional adopters
    for key in sorted(physician_sched_dict.keys()):
        df = physician_sched_dict[key]
        block_start_date = df['Date'].iloc[0] 
        block_end_date = df['Date'].iloc[-1]
        time_limit = (block_end_date - block_start_date).days + df['Days'].iloc[-1]
        add_up_date = (block_start_date-start_date).days
        G = sgm.build_projected_network(df, belief_type, b)
        #get the updated G and adopter history
        G = update_beliefs_for_existing_nodes(G, belief_dict, b)
        add_adopters = len([x for x in cumulative_adopters if x not in G.nodes()])

        G, adopter_history = contagion_synchronous_belief_propagation_projected_network(G, p, d, b, weight_type, time_limit)
        #get the beliefs for new G
        belief_dict.update({n:G.node[n]['belief'] for n in G.nodes()})
        #get the adopters for new G
        new_adopters = [n for n in G.nodes() if G.node[n]['status'] == 'Adopter']
        cumulative_adopters.extend(new_adopters)
        cumulative_adopters = list(set(cumulative_adopters))
        #adjust for the date and additionarl adopters
        adopter_history[:,0] += add_up_date
        adopter_history[:,1] += add_adopters
        entire_adopter_history = np.append(entire_adopter_history, adopter_history, 0)
    return entire_adopter_history

def update_beliefs_for_existing_nodes(G, belief_dict, threshold):
    """
    update beliefs for nodes whose starting belief is already given
    input:
        G - network
        belief_dict - {doctor:belief}
    """
    for node, belief in belief_dict.items():
        if node in G.nodes():
            G.node[node]['belief'] = belief

    G = gen.update_adoption_status(G, G.nodes(), threshold)
    return G