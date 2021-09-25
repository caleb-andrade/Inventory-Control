# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 15:12:36 2015

@author: Caleb Andrade
"""

from Inventory import Inventory
from math import exp
from sampleMean import sampleMean2
import random
import time
from gencorrdemand import genCorrDemand as gcd
from matplotlib import pyplot as plt


def nextPolicy(policy):
    """
    Generate a random neighboring policy, within an offset of +/- 5 units.
    
    Input: policy.
    Output: neighboring policy.
    """
    low = policy[0] + random.randint(-5, 5)
    top = policy[1] + random.randint(-5, 5)
    if low > top:
        return top, low
    return low, top 
    

def simAnnealing2(inventory_a, inventory_b, temperature, mkv_long, cooling_factor, repeats, index, param):
    """
    Simulated Annealing with Ranking and Selection implementation to 
    select best policy (s, S) for an inventory control system.
    
    Input: inventory,  number of iterations, temperature, inventory's index,
    parameters for randomly generated demands.
    Output: best policy.
    """
    ## initialize variables
    histogram = []
    accept = False
    k = 0
    
    ## create a copy of inventory, initialize best and current mean and seeds
    system_a = inventory_a.clone()
    system_b = inventory_b.clone()
    
    best_mean, best_seeds = sampleMean2(system_a, system_b, param, 1, 0.9, False, [])  
    mean, seeds = best_mean, best_seeds          
        
    ## start simulation main loop
    while k < repeats: # stopping condition!
        count = 0
        # markov chain loop, before decreasing temperature
        while count < mkv_long:
            ## propose next policy, create new inventory with it
            next_policy_a = nextPolicy(system_a.getPolicy())
            next_policy_b = nextPolicy(system_b.getPolicy())
            next_system_a = system_a.clone()
            next_system_b = system_b.clone()
            next_system_a.setPolicy(next_policy_a)            
            next_system_b.setPolicy(next_policy_b)
            
            ## compute sample mean of next inventory
            next_mean, next_seeds = sampleMean2(next_system_a, next_system_b, param, 1, 0.9, False, seeds)            
            # determine if next policy is accepted
            if next_mean <= mean:
                accept = True
                if next_mean <= best_mean:
                    best_mean = next_mean
                    best_policy_a = next_policy_a
                    best_policy_b = next_policy_b
            else:
                prob = 1 / exp((next_mean - mean) / temperature)
                if random.random() <= prob:
                    accept = True
            
            if accept:
                print "Iteration: ", k
                ## set new policy and record cost value
                system_a.setPolicy(next_policy_a)
                system_b.setPolicy(next_policy_b)
                system_a.reset()
                system_b.reset()
                histogram.append(next_mean)
                mean = next_mean
                seeds = next_seeds
            k += 1 # update iteration
            count += 1 # update markov chain length
            accept = False
        temperature = cooling_factor*temperature # update temperature
    
    return best_mean, best_policy_a, best_policy_b, histogram


"""
SARS SIMULATION FOR TWO JOINT INVENTORIES WITH NEGATIVE CORRELATED DEMANDS
"""
def main(repeats):
    """
    Testing.
    """
    param = (120, 0.12, 0.10, -0.8)
    
    inventory_a = Inventory(50, 3, 5, 1, 32, 0, (50, 100))
    inventory_b = Inventory(50, 3, 20, 1, 5, 0, (50, 100))
    
    tic = time.clock()
    ##simAnnealing2(inventory_a, inventory_b, temperature, mkv_long, cooling_factor, repeats, index, param):
    result = simAnnealing2(inventory_a, inventory_b, 10, 50, 0.5, repeats, 0, param)
    toc = time.clock()
    
    print "\nSARS WITH NO RANKING AND SELECTION, JOINT INVENTORIES"
    print "\nInventory_a + Inventory_b best objective function cost: ", result[0]
    print "Best policy_a: ", result[1]
    print "Best policy_b: ", result[2]
    
    print "Running time: ", toc-tic    
    print "Histogram: "
    plt.plot(result[3])
    
    inventory_a.setPolicy(result[1])
    demands = gcd(param[0], param[1], param[2], param[3])
    inventory_a.simulation(demands[0])
    inventory_a.plot()
    
    inventory_b.setPolicy(result[2])
    demands = gcd(param[0], param[1], param[2], param[3])
    inventory_b.simulation(demands[1])
    inventory_b.plot()
    plt.show()
 
# uncomment next lines to run simulation, one at a time.

# 100 iterations      
#main(100)

# 150 iterations
#main(150)

# 200 iterations
#main(200)

       
    