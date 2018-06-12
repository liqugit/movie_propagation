"""
General modules needed to calculate belief or update status 

Made by Hyojun Ada Lee October 17, 2016
"""
#global
import sys
import os
from operator import itemgetter
from itertools import combinations
from math import ceil

#from dateutil import parse

#Local
# src_dir = os.path.abspath(os.path.join(os.pardir, os.pardir, 'src'))
# sys.path[0] = src_dir

#############Functions#########################3
def limit_belief(belief_value):
    '''
    Limits the belief to between 0 and 1
    Input:
        belief_value - float 
    Output:
        belief_value - float in range [0, 1]
    '''
    if belief_value < 0.0:
        belief_value = 0.0
    elif belief_value > 1.0:
        belief_value = 1.0
    return belief_value

def update_adoption_status(G, phys_nodes, threshold):
    '''
    Updates teh adoption status on physicians based on the threshold parameter
    input:
        G - shift graph
        phys_nodes - list of node ids for the physicians
        threshold - the adoption threshold
    Output:
        G - shift graph
    '''
    for pnode in phys_nodes:
        #If the belief exceeds the threshold then the node becomes an adopter
        if G.node[pnode]['belief'] >= threshold:
            G.node[pnode]['status'] = 'Adopter'
        else:
            G.node[pnode]['status'] = 'NonAdopter'
    return G

def backfill_dates(dataset, end_date=None):
    '''
    Backfills missing datepoints in the adoption history, so that the generated 
    curve has the same plateaus as in the empirical dataset. i.e. if there are two
    points (0, 3), (2, 7) this function will backfill the dataset to be:
    (0,3), (1,3), (2,7) so that there isn't a false increas when plotted
    Input:
        dataset: list of paired points in order (day, number adopters)
    Output:
        new_data: list of paired points in order(day, number adopters)
    '''
    #First expand the dataset to where it currently is
    #Also remove duplicate points
    new_data = []
    for i in range(len(dataset)-1):
        pt_i, pt_j = dataset[i], dataset[i+1]
        date_dif = pt_j[0] - pt_i[0] -1
        #Do the appending process
        #If it equals zero, then we should append the point
        if date_dif == 0:
            new_data.append(pt_i)
        #If it is more than zero then append and go through the list
        elif date_dif > 0:
            new_data.append(pt_i)
            for temp_day in range(int(ceil(date_dif))):
                new_data.append([pt_i[0] + temp_day + 1, pt_i[1]])
    #Add the final point
    new_data.append(pt_j)
    #Now move it forward to where it should be
    if end_date:
        if new_data[-1][0] != end_date:
            diff = end_date - new_data[-1][0] 
            fin_date = new_data[-1][0]
            fin_value = new_data[-1][1]
            for i in range(int(ceil(diff))):
                new_data.append([fin_date + i + 1, fin_value])
    return new_data

def find_3team_weekends(G):
    """
    Find weekends with only 3 teams
    Input: 
        G: Doctor network graph
    Output: 
        T2_weekends: list of weekends with 3 teams
    """
    T3_weekends = []
    weekends_dic = {} #{order: [fel1, fel2]}
    #Get all the weekends shifts (or shifts that can be considered as weekends)
    for node in G.nodes():
            if G.node[node]['node_type'] == 'S':
                if G.node[node]['days'] == 2 and G.node[node]['team'] == 'T3':
                    T3_weekends.append(node)
    #print T3_weekends
    return T3_weekends