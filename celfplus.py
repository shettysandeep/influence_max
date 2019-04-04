#!usr/bin/python
# -*- coding: utf-8 -*-

# GREEDY CELF++ in Goyal et al (2011)
# Sandeep @ 11/24/2017

import os, sys
import time
import logging  # add logging parameters
import random
import itertools


def spread(*args):
    ''' Function that calculates the spread of a node
    
    #--------------------------
    Arguments:
    S: int or list (seed-set)

    Note: function called inside clef_pl2
    
    '''
    
    # FOR NOW JUST A RANDOM GENERATOR

    if isinstance(args[0], list):
        x = sum([random.uniform(0,1) for l in args[0]])
    else: 
        x = random.uniform(0,1)

    return x



def clef_pl2(V=10, k=2):
    
    ''' Function to implement the GREEDY CLEF++ algorithm by Goyal
    et al (2011) and returns a IM seed-set as a Python list.
    The code is based on the algorithm provided in Goyal et al (2011) on page:
    followed here are based on Exhibit X on page XX

    #-----------------------------
    Arguments: 
    V: Number of nodes
    k: |S| 

    #-----------------------------
    Implicit arguments:
    S: seed set (objective)
    Q: List of tuples. Collecting information.
    last_seed:
    cur_best: The best node in the current iteration
    u_mg1: Marginal gain in spread(S+{v})
    u_mg2: Marginal gain in spread(S + {prev_best})
    
    #-----------------------------
    Output:
    S: seed set
     
    '''
    
    # Initializing empty containers

    S = []      # Seed set
    Q = {}      # Dictionary  
    
    #-----------
    # Step 1: Setting up Q (dictionary)  
    
    cur_best = None  # Cannot be assigned 0 as it can be a node
    last_seed = None # same as above
    
    for v in range(V):

        u_mg1 = spread(v)
        u_prevbest = cur_best
        #print(u_prevbest)
        u_mg2 = spread([v,u_prevbest]) #make sure spread takes a list as argument
        u_flag = 0
        
        # Putting into a dictionary

        Q[v]= {'mgain':u_mg1,'prev_best':u_prevbest, 'mgain_prev':u_mg2}
        
        Qmax = max([Q[x]['mgain'] for x in Q.keys()])     

        for m,j in Q.items():
            if Q[m]['mgain']==Qmax:
                cur_best = m
                #print(cur_best)    
   
    #sys.exit()


    
    # since cannot sort a dictionary writing a function to get nodes with
    # highest mgain 

    def sorter(d, pos = 0):
        tmptup = sorted(d.items(), key=lambda x: x[1]['mgain'], reverse = True)
        return tmptup[pos][0]
    
    #print(sorter(Q,pos=0))
    #print(sorter(Q, pos =1))

    #sys.exit()

    # find the maximum among a list of u_mg1 and replace that in place of u_mg2
    
    print(cur_best, last_seed)

    #-----------
    # Step 2: Obtain the seed set by iterating through Q

    while(len(S) < k):
        
        u = sorter(Q,0)         # Take the first node in Q (largest)
        print(u)

        if u_flag == len(S):   # Is this the last element to be filled in S
            print("Here")
            S.append(u)
            del Q[u] 
            last_seed = u
            continue
        
        elif Q[u]['prev_best'] == last_seed:
            print(Q[u]['prev_best'])
            print(last_seed)
            print("Now here")
            Q[u]['mgain'] = Q[u]['mgain_prev'] # the advantage of CELF++
            
            u_flag = len(S)

        else:
            print("I am here")
            Q[u]['mgain'] = spread(S+[u]) - spread(S)
            Q[u]['prev_best'] = cur_best
            Q[u]['mgain_prev'] = spread(S+[Q[u]['prev_best']]+[u])-spread(S+[Q[u]['prev_best']]) 
            print(Q[u]['mgain_prev'])
            u_flag = len(S)
        
        #cur_best = k

        #Q2 = sorted(Q.items(), key=lambda x: x[1]['mgain'], reverse = True)
        #Q = dict(Q2)


    return S

print(clef_pl2(V=500,k=100))
