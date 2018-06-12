 
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
#from dateutil import parse

#Local
src_dir = os.path.abspath(os.path.join(os.pardir, os.pardir, 'src'))
sys.path[0] = src_dir
import model.general as gen
import network.shift_graph_maker as sgm

#############Functions#########################3

def calculate_belief(agent_i, agent_j, shift_length, probability, dose, threshold, weight=1):
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
    for i in range(shift_length):
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
    
def contagion_belief_propagation_temporal_network(G, prob, dose, threshold):
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
    prj_start_date = sorted([G.node[n]['start_date'] for n in G.nodes() \
                                if G.node[n]['node_type']=='S'])[0]

    #Make the shift nodes dictionary (shift_order: node id)
    shift_nodes = [[G.node[n]['shift_order'], n] for n in G.nodes() if G.node[n]['node_type']=='S']
    shift_nodes.sort(key=itemgetter(0, 1))

    #print shift_nodes
    #print '---------------'

    #Get the phys node ids
    phys_node_ids = [n for n in G.nodes() if G.node[n]['node_type']=='D']

    #Doctor Adopters, node ids
    adopters = [n for n in phys_node_ids if G.node[n]['status'] == 'Adopter']

    #Adopter dictionary and their time points: {time:#of adopters}
    adopter_history = [[0, len(adopters)]]

    #print 'START---->'
    #Iterate through the shifts
    #for shift_order in sorted(shift_nodes.keys()):
    #Get the list of weekends with team 2 with same fellows
    T3_weekends = gen.find_3team_weekends(G)
    for shift_order, shift_id in shift_nodes:
        #Identify the shift node
        shift_node = G.node[shift_id]
    #     print ('Shift order', G.node[shift_id]['shift_order'])
    #     print ('Shift length', shift_node['days'])
        #Iterate through pairs of doctors
        #Any one shift node should only have two doctors, but this is generalized for the future
        doctor_ids = G.neighbors(shift_id)
        for doc1, doc2 in combinations(doctor_ids, 2):
            #Calculate the new belief values
            if shift_node['days'] == 2 and shift_id not in T3_weekends:
                shift_length = 1
            else:
                shift_length = shift_node['days']
            # before1, before2 = G.node[doc1]['belief'], G.node[doc2]['belief']
            b1, b2 = calculate_belief(G.node[doc1], G.node[doc2], shift_length, prob, dose,  threshold )
            # after1, after2 = G.node[doc1]['belief'], G.node[doc2]['belief']

            G.node[doc1]['belief'] = b1
            G.node[doc2]['belief'] = b2
            #Check to see who is an adopter
            G = gen.update_adoption_status(G, phys_node_ids, threshold)

        #Calculate the number of adopters
        adopters = [n for n in phys_node_ids if (G.node[n]['status'] == 'Adopter')]# and (G.node[n]['doc_type'] == 'A')]
        #Calculate the day, make it list at the midpoint of the shift
        day_count = (shift_node['start_date'] - prj_start_date).days + ceil(shift_node['days']/2)
        # print(shift_node['start_date'], day_count, len(adopters))
        adopter_history.append([day_count, len(adopters)])
    #get the end date
    final_numeric_day = (shift_node['start_date'] - prj_start_date).days + shift_node['days']
    #Backfill the missing days
    adopter_history = np.array(gen.backfill_dates(adopter_history, end_date = final_numeric_day))

    return adopter_history

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


def contagion_sequential_belief_propagation_projected_network(G, prob, dose, threshold, weight_type='none', weight_choice='none', time_limit=10000):
    """
    Objective: Random sequential belief updates of the projecte network, unweighted network
    Input: 
        G - NX graph of doctors, static
        prob - probability of infection
        dose - dosage of infection
        recovery - recovery
        threshold - threshold for being infected
        weight_type - 'none', shift', 'days', which attribute to use as weight
        weight_choice - 'none', neighbor', 'influence', how to use weight as 
    Output:
        adopter_list - list of adopters by day
    """
    adopters = [n for n in G.nodes() if G.node[n]['status'] == 'Adopter']
    adopter_history = [[0, len(adopters)]]
    #define the weight that will be used for the network
    G = calculate_weight(G, weight_type)
    try:
        init_node1, init_node2 = random.sample(adopters, 2) #choose random node to start
    except ValueError:
        init_node1, init_node2 = random.sample(G.nodes(),2)
    t = 1 
    w1, w2 = 1, 1
    while t < time_limit:
        #make list of neighbors, depending on the number of times they meet 'weight'
        w1 -= 1
        w2 -= 1
        if weight_choice == 'influence':
            if w1 == 0:
                next_node1 = choose_neighbor(G, init_node1, weight_choice) 
                w1 = G.edge[init_node1][next_node1]['weight']
            if w2  == 0:
                next_node2 = choose_neighbor(G, init_node2, weight_choice)
                w2 = G.edge[init_node2][next_node2]['weight']         
        else:
            #if we are not looking for influence size, we only care about which neighbor we choose
            next_node1 = choose_neighbor(G, init_node1, weight_choice)
            next_node2 = choose_neighbor(G, init_node2, weight_choice)
        #update belif for two teams
        b11,b12 = calculate_belief(G.node[init_node1], G.node[next_node1], 1, prob, dose, threshold)
        b21,b22 = calculate_belief(G.node[init_node2], G.node[next_node2], 1, prob, dose, threshold)
        G.node[init_node1]['belief'] = b11
        G.node[next_node1]['belief'] = b12
        G.node[init_node2]['belief'] = b21
        G.node[next_node2]['belief'] = b22

        #update adopter status
        G = gen.update_adoption_status(G, G.nodes(), threshold)
        adopters = [n for n in G.nodes() if G.node[n]['status']=='Adopter']
        adopter_history.append([t, len(adopters)])
        #change the nodes, calculating influence size
        #change the neighbor if the influence is over.  
        if w1 == 0:
            init_node1 = next_node1
        if w2 == 0:
            init_node2 = next_node2
        #one day passes
        t+=1
    adopter_history = gen.backfill_dates(adopter_history, end_date = time_limit)
    adopter_history = np.delete(np.array(adopter_history), (-1), axis=0)
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

def cumulative_adopters_over_time_projected_network_sequential_update(physician_sched_dict, belief_type, p, d, b, weight_type, weight_choice, time_limit=10000):
    """
    When the schedule is cut into months, get the cumulative adopters over time fo`r the projected network. 
    Random walk - when weighted random walk is weighed on number of shifts and the influence by number of days
    input:
        physcian_sched_dict: cut up sched. dictionary of dfs
        belieft_type: 'empirical' for the contagion model
        p, d, b - contagion model parameters
        weight - true or false
    output:
        entire_adopter_history: numpy array of cumulative adopters [days, adopters]
    """
    entire_adopter_history = np.empty([0,2],dtype=int)
    start_date = physician_sched_dict[0].Date.iloc[0]
    belief_dict = {}
    cumulative_adopters = [] #account for addional adopters
    for key in sorted(physician_sched_dict.keys()):
        #df for G
        df = physician_sched_dict[key]
        #start and end date 
        block_start_date = df['Date'].iloc[0] 
        block_end_date = df['Date'].iloc[-1]
        #set the time limit for iteration
        time_limit = (block_end_date - block_start_date).days + df['Days'].iloc[-1]
        add_up_date = (block_start_date-start_date).days
        #build G
        G = sgm.build_projected_network(df, belief_type, b)
        #update beliefs with exisitng 
        G = update_beliefs_for_existing_nodes(G, belief_dict, b)
        add_adopters = len([x for x in cumulative_adopters if x not in G.nodes()])
        G, adopter_history = contagion_sequential_belief_propagation_projected_network(G, p, d, b, weight_type, weight_choice, time_limit)
        
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