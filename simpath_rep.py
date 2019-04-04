# !usr/env/python
# -*-encoding: utf-8 -*-

# Simpath by Goyal et al 
# Sandeep @ 11/27/17
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


import os, sys
import logging
import networkx as nx
from networkx.algorithms import approximation


# 1) Get a directed graph for play
# G goes into the Simpath algorithm 4

G = nx.DiGraph()  

G.add_weighted_edges_from([(1,2,0.5),
    (1,3,0.75),(6,1,0.25),(1,9,0.2),(7,1,0.75),(2,3,0.25),(5,2,0.15),(2,8,0.15)])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#2) Function simpath-spread

def simpath_spread(S, tol, U):
    ''' Algorithm 1 
        Input: List of nodes, pruning coefficient, subgraph induced by certain
        nodes
        Output: Spread of S (spread_S) in the main graph G as well as the
        spread calculated in a subgraph induced by a collection of nodes
        (spread_Wv). See algorithm 4
    '''
    
    spread_S = 0      
    spread_Wv = 0 

    W1 = [v for v in G.nodes() if v not in S]  # V - S
    VminU = [v for v in G.nodes() if v not in U]       # V - U


    if isinstance(U,list):
    
        for s in S:
            
            W1.append(s)                            # V - S + s
            W = G.subgraph(W1)                      # creating a subgraph

            # V-v where 'v' belongs to U (see algorithm 4 that calls this function
            # with two different U's (1. U = V-C & In-neighbors(each c in C), 2. U
            # is list of promising nodes. 

            VminU.append(s)                         # V - U + s
            U = G.subgraph(VminU)

            spread_S = spread_S + backtrack(s, tol, W, U=None)[0]
            spread_Wv = spread_Wv + backtrack(s, tol, W, U=None)[1]
    
    else:
        
        for s in S:
            W1.append(S)    
            spread_S, spread_Wv = spread_S + backtrack(s, tol, W, U) 

    return (spread_S, spread_Wv)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# 3) Function Backtrack

def backtrack(u, tol, W, U=None):

    ''' Algorithm 2  - called "backtrack" in the paper.
    This function shift backwards by a node and then calls the forward
    algorithm to add nodes on a live path. It systematically travels
    the different paths.  
    '''

    D = {}
    Q = [u]      # adding to u to Q (list)
    D[u] = []    # Dictionary: {node: {visited neighbors}}
    spd = 1      # initial value of spread
    pp = 1       # intial pp simple path weight
    
    while Q:     # is not None:

        Q,D,spd,pp,spdW_v = forward(Q,D,spd,pp,tol,W,U)
        #print(Q)
        #print(D)
        
        if Q :
            u = Q[-1]        # make this as the last node from forward so that it can be forwarded
            Q.remove(u)      # remove the old u; this can make Q empty
        
            if len(Q) >= 2:
                v = Q[-1]        # second last from Q 
        
                try: 
                    w1= W.edge[u][v]['weight']
                    pp = pp+ (pp/(w1))  # (u, v): 
                except: 
                    pass

        if u in D:
            del D[u]
                
    return (spd, spdW_v)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#4) Function Forward

def forward(Q,D,spd,pp,tol,W,U=None):

    ''' Algorithm 3 - called "forward" in the paper. This subroutine enumerates
    all the active nodes on a given path starting from a specific node.  
    '''

    x = Q.pop() #Q[-1] #                    # keeping this as a list; extract last element
    D[x] = [] 
    nout_x = W.successors(x)    # list of immediate successor of x in graph W
    
    while nout_x: # is not None:
        
        for succ in nout_x:
            if (succ not in Q) and (succ not in D[x]) and (succ in W.nodes()):

                wght = W.edge[x][succ]['weight'] # assuming in data 'weight'
                if pp*wght < tol:
                
                    D[x] = D[x] + [succ] # keeping track of outneighbors
        
                else:
                    Q = Q + [succ]
                    pp = pp*wght 
                    spd = spd + pp
                    D[x] = D[x] + [succ]
            
            # See Algorithm 4 (kicks in for Vertex cover)

                if U:
                    for v in U:
                        if v not in Q:
                            spdW_v = spdW_v + pp

            else:
                continue
        
        # Take the last element from above and look for its successors to go
        # depth-first into enumerating the path 
                   
        x = Q[-1]       
        nout_x = W.successors(x)

    return (Q,D,spd,pp,spdW_v)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# 5) Assembly of SIMPATH with CELF

def simpath(G, tol, l=10, k=2):
    
    ''' Algorithm 4 in paper Assembly of the Simpath algorithm
    Input: 
    G(V,E): Networkx Directed Graph Object
    tol: pruning coefficient
    l: length of potential seed nodes
    k: length of seed set

    Output: Set of seed (S)
    '''
    
    #*****************************************
    # Setting up steps [1-8] of Simpath algorithm    
    #*****************************************

    G1 = G.to_undirected()
    C = approximation.min_weighted_vertex_cover(G1)  # list of vertices
    
    V = G.nodes()

    u1 = [v for v in V if v not in C]    # Nodes in V - C 

    celfq = []
    tup_c={}

    for c in C:                              # line 2
        N_in = G.neighbors(c)                # Neighbors of C
        U = [v for v in u1 if v in N_in]     # U = {(V-C)& N(c)}
             
        spd_u, spdW_v = simpath_spread(c, tol, U=U)   # spread(u) on Graph of nodes: V-v = V
                                                         # will give both spread in G as well
                                                         # as G-S+u simultaneously 

        tup_c[c] = spdW_v                   # Adding to dictionary for sorting                                    
        celfq.append(u)                     # Appending to CELF queue
         
    for w in u1:                            # line 6
         noutv = G.successors(w)            # Out-neighbors of w
         spdv = 1

         for nou in noutv:
             wgt = (G.edge[w][noutv]['weight'])
             spdv = spdv + (wgt*tup_c[nou])  # Theorem 2

         tup_c[w] = spdv
         celfq.append(w)                     # Appending to CELF queue
         
    #*****************************************
    # Steps [9-14] - CELF 
    #*****************************************

    S = []
    spd = 0
    
    def sorter(d, pos = l):
        
        ''' Returns a list of top-l keys from a Dictionary sorted (desc) on values '''

        tmtup = sorted(d.items(), key = lambda x: x[1], reverse = True)
        tmtup = tmtup[:pos]                         # top-l nodes sorted on spread
        tmtupl = [x for x,y in tmtup.items()]
        return tmtupl
    
    u_flag = 0                              # tracking iteration
    while len(S) < k:                       # line 10
        lu = sorter(tup_c)
        lu1 = [(la,u_flag)for la in lu]
        
        spdV_x = {}   # New dictionary
        
        for ul in lu1:
            ul_x = [v for v in V if v != ul]        # V - x; want to keep V intact.

            spd,spdV_xS = simpath_spread(S, tol, U = ul_x)      
            

        for index,x,y in enumerate(lu):
            if y == u_flag-1:                 # checking if x part of the previous iteration
                S = S + [x]                 
                spd = spd + spd
                celfq.remove(x)             # remove u
                break
            
            V_S = [v for v in V if v not in S]

            spreadV_Sx, skip = backtrack(x,tol,V_s,U=None)

            spreadSplusx = spreadV_Sx + spreadV_xS    

            marg_gain_x = spreadSplux - spd
            
            u_flag += 1   # next iteration

            celfq.insert(index,x)

    return S

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


def main():
     
    #print(simpath_spread(S=[1,2,3,9],tol=0.05,U=None))          
    print(simpath(G,tol=0.05,l=10,k=2))

if __name__ == "__main__" :
    main()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


