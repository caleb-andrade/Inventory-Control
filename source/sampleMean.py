"""
Created on ........ Fri Nov 20 06:27:58 2015
Last modified on .. Sat Nov 21 11:10:25 2015

@author: Caleb Andrade
"""
from gencorrdemand import genCorrDemand as gcd
from Inventory import Inventory
import time
import numpy as np


def repSimulation(inventory, demands_list, repeats, index):
    """
    Perform 'repeats' runs of an inventory's simulation 
    with a specified list of demands and repeats.
    
    Input: inventory, list of demands, repeats, index of inventory.
    Output: a list with average costs of every run.
    """
    avg = []
    temp_inventory = inventory.clone()
    
    for rep in range(repeats):
        temp_inventory.simulation(demands_list[rep][index]) 
        avg.append(temp_inventory.averageCost())
        temp_inventory.reset()
    
    return avg


def simultaneousRuns(inventory_a, inventory_b, repeats, param, joint = False):
    """
    Run simulation 'repeats' times simultaneously for two inventories.
    
    Input: two inventories, repeats, set of parameters for the randomly 
    generated demands, objective function will be joint? or not.
    Output: average and variance for the simulations of each inventory.
    """
    # generate a list of demands
    demands_list = [gcd(param[0], param[1], param[2], param[3]) for j in range(repeats)] 
    
    # repeat simulations and save average costs in a list for each inventory
    avg1 = repSimulation(inventory_a, demands_list, repeats, 0)
    avg2 = repSimulation(inventory_b, demands_list, repeats, 1)
           
    if joint:
        average = (sum(avg1) + sum(avg2)) / repeats
        variance = [(average - (avg1[i] + avg2[i]))**2 for i in range(repeats)]

        return [average, None], [sum(variance) / (repeats - 1), None]
        
    else:
        [average1, variance1] = statMeasures(avg1)
        [average2, variance2] = statMeasures(avg2)
        
        return [average1, average2], [variance1, variance2]
 

def setPrecision(beta):
    """
    Look in TABLE the h value for given parameters.
    
    Input: precision, initial number of repeats, table of values.
    Output: h.
    """
    # set for n0 = 20
    if beta == 0.90:
        return 1.9
    
    return binarySearch(beta)
    

def genSeeds(n):
    """
    Generate a set of n seeds for random number generation.
    
    Input: number of seeds.
    Output: list of seeds.
    """
    seeds = []
    for i in range(n):
        prng = np.random.RandomState()
        seeds.append(prng.get_state())
    
    return seeds

    
def binarySearch(beta):
    """
    Return the h-value from H_TABLE that corresponds to beta.
    @author: Caiwei Li
    """
    lo, hi = 0, (len(H_TABLE)-1)
    while lo < hi-1:
        mid = (lo + hi) >> 1
        k = H_TABLE[mid][0]
        if k == beta:
            return H_TABLE[mid][1]
        elif k < beta:
            lo = mid # search upper subarray
        else:
            hi = mid # search lower subarray

    if lo < hi:
        if abs(H_TABLE[lo][0]-beta) > abs(H_TABLE[hi][0]-beta):
            return H_TABLE[hi][1]
        else:
            return H_TABLE[lo][1]
    else:
        return H_TABLE[lo][1]
    
    
def weight(n0, ni, delta, variance, h):
    """
    Compute the weights for the averages used in ranking selection.
    
    Input: initial iterations, additional iterations, precision, variance, h.
    Ouput: weight wi.
    """
    x = 1 - ((ni - n0)*delta**2 / variance*(h**2))

    return ( 1 + ( 1 - ( x*float(ni) / n0) )**0.5 )*float(n0) / ni
    

def statMeasures(values):
    """
    Compute the mean and variance of a list of values.
    
    Input: list of values.
    Output: variance.
    """
    average = sum(values) / len(values)
    variance = [(average - values[i])**2 for i in range(len(values))]
    
    return average, sum(variance) / (len(values) - 1)
    

def sampleMean1(inventory_a, param, delta, beta, index, rank, seeds = []):
    """
    Compute sample mean of cost value for an inventory as a weighted average
    of averages, following the statistical method for ranking and selection.
    
    Input: inventory, random demands' parameters, delta and beta are the 
    precision parameteres, index: (0, inventory_a) and (1, inventory_b).
    Rank is a boolean variable to activate or deactivate ranking and selection.
    As an option, seeds is a list of seeds for random number generation.
    Output: sample mean of current inventory.
    """
    n0 = 20
    system_a = inventory_a.clone()
    ## if no seeds are specified, generate seeds    
    if seeds == []:
        no_seeds = True # no seeds were specified
        seeds = genSeeds(n0)
    else:
        no_seeds = False
   
    ## generate a list of initial demands. Compute average and variance for n0 replications.
    demands_list = [gcd(param[0], param[1], param[2], param[3], seed=seeds[j]) for j in range(n0)] 
    avg1, variance = statMeasures(repSimulation(system_a, demands_list, n0, index))
    
    ## if no ranking and selection
    if not rank:
        print "No ranking and selection"
        return avg1, seeds
    
    ## calculate how many more simulations to run    
    h = setPrecision(beta)
    n1 = max(n0 + 1, 1 + int(variance*(h**2) / delta**2))
    
    ## generate additional batch of seeds
    if no_seeds:
        more_seeds = genSeeds(n1 - n0) 
    elif len(seeds) < n1: ## if seeds were specified but are not enough
        more_seeds = genSeeds(n1 - len(seeds))
    else:
        more_seeds = []
    seeds += more_seeds
    
    # generate additional demands. Compute average for n1 - n0 replications
    demands_list = [gcd(param[0], param[1], param[2], param[3], seed=seeds[n0 + j]) for j in range(n1 - n0)] 
    
    avg2 = sum(repSimulation(system_a, demands_list, n1 - n0, index)) / (n1 - n0)
    
    # compute weights and weighted average of sample mean
    w = weight(n0, n1, delta, variance, h)
    sample_mean = w*avg1 + (1 - w)*avg2
    
    return sample_mean, seeds
    

def sampleMean2(inventory_a, inventory_b, param, delta, beta, rank, seeds = []):
    """
    Compute sample mean of cost value for the sum of two inventories as a
    weighted average, following the statistical method for ranking and selection.
    
    Input: inventories, random demands' parameters, delta and beta are the 
    precision parameters, index: (0, inventory_a) and (1, inventory_b).
    Rank is a boolean variable to activate or deactivate ranking and selection.
    As an option, seeds is a list of seeds for random number generation.
    Output: sample mean of current inventory.
    """
    n0 = 20
    system_a = inventory_a.clone()
    system_b = inventory_b.clone()
    
    ## if no seeds are specified, generate seeds    
    if seeds == []:
        no_seeds = True # no seeds were specified
        seeds = genSeeds(n0)
    else:
        no_seeds = False
   
    ## generate a list of initial demands. Compute average and variance for n0 replications.
    demands_list = [gcd(param[0], param[1], param[2], param[3], seed=seeds[j]) for j in range(n0)] 
    avg1a = repSimulation(system_a, demands_list, n0, 0) 
    avg1b = repSimulation(system_b, demands_list, n0, 1)         
    
    avg1 = [avg1a[i] + avg1b[i] for i in range(len(avg1a))]  
    mean1, variance = statMeasures(avg1)
    
    ## if no ranking and selection
    if not rank:
        print "No ranking and selection"
        return mean1, seeds
        
    ## calculate how many more simulations to run    
    h = setPrecision(beta)
    n1 = max(n0 + 1, 1 + int(variance*(h**2) / delta**2))
   
    ## generate additional batch of seeds
    if no_seeds:
        more_seeds = genSeeds(n1 - n0) 
    elif len(seeds) < n1: ## if seeds were specified but are not enough
        more_seeds = genSeeds(n1 - len(seeds))
    else:
        more_seeds = []
    seeds += more_seeds
    
    # generate additional demands. Compute average for n1 - n0 replications
    demands_list = [gcd(param[0], param[1], param[2], param[3], seed=seeds[n0 + j]) for j in range(n1 - n0)] 
    
    avg2a = repSimulation(system_a, demands_list, n1 - n0, 0) 
    avg2b = repSimulation(system_b, demands_list, n1 - n0, 1)         
    
    avg2 = [avg2a[i] + avg2b[i] for i in range(len(avg2a))]  
    mean2 = sum(avg2) / len(avg2)
    
    # compute weights and weighted average of sample mean
    w = weight(n0, n1, delta, variance, h)
    sample_mean = w*mean1+ (1 - w)*mean2
    
    return sample_mean, seeds
    

H_TABLE =[[0.5272, 0.1], [0.5544, 0.2], [0.5812, 0.3], [0.6077, 0.4],
          [0.6337, 0.5], [0.6591, 0.6], [0.6837, 0.7], [0.7075, 0.8], [0.7304, 0.9],
          [0.7523, 1.0], [0.7732, 1.1], [0.793, 1.2], [0.8117, 1.3], [0.8293, 1.4],
          [0.8457, 1.5], [0.8611, 1.6], [0.8753, 1.7], [0.8884, 1.8], [0.9004, 1.9],
          [0.9115, 2.0], [0.9215, 2.1], [0.9307, 2.2], [0.9389, 2.3], [0.9464, 2.4],
          [0.953, 2.5], [0.959, 2.6], [0.9643, 2.7], [0.969, 2.8], [0.9732, 2.9],
          [0.9768, 3.0], [0.98, 3.1], [0.9828, 3.2], [0.9853, 3.3], [0.9874, 3.4],
          [0.9893, 3.5], [0.9909, 3.6], [0.9923, 3.7], [0.9934, 3.8], [0.9944, 3.9],
          [0.9953, 4.0], [0.996, 4.1], [0.9967, 4.2], [0.9972, 4.3], [0.9976, 4.4],
          [0.998, 4.5], [0.9983, 4.6], [0.9986, 4.7], [0.9988, 4.8], [0.999, 4.9],
          [0.9992, 5.0], [0.9993, 5.1]]
          
#******************************************************************************
# TESTING ZONE
#******************************************************************************

def main():
    """
    Testing.
    """
    inventory_a = Inventory(60, 1, 10, 1, 10, 0, (50, 100))
    inventory_b = Inventory(70, 1, 10, 1, 10, 0, (20, 34))
    
    param = (60, 0.10, 0.12, 0)
    
#    print "\n********************* TESTING simultaneous runs *************************"
#    tic = time.clock()
#    result1 = simultaneousRuns(inventory_a, inventory_b, 20, param, True)
#    toc = time.clock()
#    print "\nJoint result: ", result1
#    print "\nRunning time: ", toc-tic
#    
#    tic = time.clock()
#    result2 = simultaneousRuns(inventory_a, inventory_b, 20, param, False)
#    toc = time.clock()
#    print "\nDisjoint result: ", result2
#    print "\nRunning time: ", toc-tic
#    
    print "\n********************** TESTING sampleMean1 **************************"
    tic = time.clock()
    result3 = sampleMean1(inventory_a, param, 1, 0.90, 0)
    toc = time.clock()
    print "\nSample mean: ", result3[0]
    print "Number of seeds: ", len(result3[1])
    print "Running time: ", toc - tic
    
    tic = time.clock()
    result4 = sampleMean1(inventory_b, param, 1, 0.90, 1)
    toc = time.clock()
    print "\nSample mean: ", result4[0]
    print "Number of seeds: ", len(result4[1])
    print "Running time: ", toc - tic
    
    print "\n********************** TESTING sampleMean2 **************************"
    tic = time.clock()
    result5 = sampleMean2(inventory_a, inventory_b, param, 1, 0.90)
    toc = time.clock()
    print "Sample mean: ", result5[0]
    print "Number of seeds: ", len(result5[1])
    print "Running time: ", toc - tic
    
    tic = time.clock()
    result6 = sampleMean2(inventory_a, inventory_b, param, 1, 0.90, result5[1])
    toc = time.clock()
    print "\nSample mean: ", result6[0]
    print "Number of seeds: ", len(result6[1])
    print "Running time: ", toc - tic
    





    
    
    
