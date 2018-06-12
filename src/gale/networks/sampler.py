'''
File: sampler.py
Author: Adam Pah
Description:
Sampling methods on a graph
'''

def node_sampler(G, p):
    '''
    Node samples from a network at a given percentage, (p)
    Nodes are picked at random, links between picked nodes are returned
    as a graph
    '''
    import random
    import networkx as nx
    
    fixed_nodes = random.sample(G.nodes(), int(p * len(G)))
    H = G.subgraph(fixed_nodes)
    return H

def link_sampler(G, p):
    '''
    Link samples from a network at a given percentage, (p)
    '''
    import random
    import networkx as nx
    
    chosen_links = random.sample(G.edges(), int(p * len(G.edges())))
    H = nx.Graph()
    H.add_edges_from(chosen_links)
    return H

def fixed_effect_sampler(G, p, f):
    '''
    Fixed effect sampling, p percentage nodes have f max 
    links chosen at random
    '''
    import random
    import networkx as nx

    #Different from node_sampler, we get all the links for a node
    fixed_nodes = random.sample(G.nodes(), int(p * len(G)))
    #Start the graph
    H = nx.Graph()
    for n in fixed_nodes:
        num_edges = len(G.edges(n))
        if num_edges>f:
            H.add_edges_from(random.sample(G.edges(n), f))
        else:
            H.add_edges_from(G.edges(n))
    return H
