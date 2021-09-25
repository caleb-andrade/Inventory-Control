# -*- coding: utf-8 -*-
"""
Created on ........ Fri Nov 20 06:27:58 2015
Last modified on .. Sat Nov 21 11:10:25 2015

@author: Caleb Andrade
"""
from gencorrdemand import genCorrDemand
from Inventory import Inventory
import time



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
        ## reset inventory?
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
    demands_list = [genCorrDemand(param[0], param[1], param[2], param[3]) for j in range(repeats)] 
    
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
        return 1.89
    
    return binarySearch(beta)
    
def binarySearch(beta):
    """
    Return the h-value from H_TABLE that corresponds to beta.
    """
    lo, hi = 0, (len(H_TABLE)-1)
    #print "length: ", hi
    while lo < hi-1:
        mid = (lo + hi) >> 1
        #print "\ninterva: ", lo, hi
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
    x = 1 - ((ni - n0)*delta**2 / ((variance*(h**2))))

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
    

def rankSelect1(inventory_a, policy, param, delta, beta, index):
    """
    Compute sample mean of cost value for an inventory, two different policies,
    select the best policy using a ranking and selection statistical procedure.
    
    Input: inventory, policy to evaluate, random demands parameters,
    delta and beta are the precision parameters, index: (0, inventory_a),
    (1, inventory_b).
    Output: best policy.
    """
    # initialize n0, and create two inventory copies for simulation
    n0 = 20
    system_i = inventory_a.clone()
    system_j = inventory_a.clone()
    system_j.setPolicy(policy)
    
    # generate a list of initial demands for n0 runs of simulation
    demands_list = [genCorrDemand(param[0], param[1], param[2], param[3]) for j in range(n0)] 
    
    # run initial n0 simulations
    avg1 = repSimulation(system_i, demands_list, n0, index) # use same index for comparison
    avg2 = repSimulation(system_j, demands_list, n0, index)
    
    # get initial averages and variances for the two policies
    [mean1, variance1] = statMeasures(avg1)
    [mean2, variance2] = statMeasures(avg2)
    
    # calculate how many more simulations to run    
    h = setPrecision(beta)
    
    n1 = max(n0 + 1, 1 + int(variance1*(h**2) / delta**2))
    n2 = max(n0 + 1, 1 + int(variance2*(h**2) / delta**2))
    
    # generate additional simulations
    demands_list = [genCorrDemand(param[0], param[1], param[2], param[3]) for j in range(max(n1, n2) - n0)] 
    
    avg1 = sum(repSimulation(system_i, demands_list, n1 - n0, index)) / (n1 - n0)
    avg2 = sum(repSimulation(system_j, demands_list, n2 - n0, index)) / (n2 - n0)
    
    # compute weights
    w1 = weight(n0, n1, delta, variance1, h)
    w2 = weight(n0, n2, delta, variance2, h)
    
    # compute sample means as a weighted average
    sample_mean1 = w1*mean1 + (1 - w1)*avg1
    sample_mean2 = w2*mean2 + (1 - w2)*avg2
    
    return [sample_mean1, sample_mean2], [inventory_a.getPolicy(), policy]
    
def rankSelect2(inventory_a, inventory_b, policy_a, policy_b, param, delta, beta):
    """
    Compute sample mean of cost value for an inventory, two different policies,
    select the best policy using a ranking and selection statistical procedure.
    
    Input: inventory, policy to evaluate, random demands parameters,
    delta and beta are the precision parameters.    
    Output: best policy.
    """
    # initialize n0, and create two inventory copies for simulation
    n0 = 20
    system_ia = inventory_a.clone()
    system_ib = inventory_b.clone()    
    system_ja = inventory_a.clone()
    system_jb = inventory_b.clone()
    
    system_ja.setPolicy(policy_a)
    system_jb.setPolicy(policy_b)    
    
    # generate a list of initial demands for n0 runs of simulation
    demands_list = [genCorrDemand(param[0], param[1], param[2], param[3]) for j in range(n0)] 
    
    # run initial n0 simulations
    avg1a = repSimulation(system_ia, demands_list, n0, 0) # use same index for comparison
    avg1b = repSimulation(system_ib, demands_list, n0, 1) # use same index for comparison
    avg2a = repSimulation(system_ja, demands_list, n0, 0)
    avg2b = repSimulation(system_jb, demands_list, n0, 1)
    
    avg1 = [avg1a[i] + avg1b[i] for i in range(len(avg1a))]  
    avg2 = [avg1a[i] + avg1b[i] for i in range(len(avg1a))] 
    
    # get initial averages and variances for the two policies
    [mean1, variance1] = statMeasures(avg1)
    [mean2, variance2] = statMeasures(avg2)
    
    # calculate how many more simulations to run    
    h = setPrecision(beta)
    
    n1 = max(n0 + 1, 1 + int(variance1*(h**2) / delta**2))
    n2 = max(n0 + 1, 1 + int(variance2*(h**2) / delta**2))
    
    # generate additional simulations
    demands_list = [genCorrDemand(param[0], param[1], param[2], param[3]) for j in range(max(n1,n2) - n0)] 
    
    avg1a = sum(repSimulation(system_ia, demands_list, n1 - n0, 0)) / (n1 - n0)
    avg1b = sum(repSimulation(system_ib, demands_list, n1 - n0, 1)) / (n1 - n0)
    avg2a = sum(repSimulation(system_ja, demands_list, n2 - n0, 0)) / (n2 - n0)
    avg2b = sum(repSimulation(system_jb, demands_list, n2 - n0, 1)) / (n2 - n0)
    
    # compute weights
    w1 = weight(n0, n1, delta, variance1, h)
    w2 = weight(n0, n2, delta, variance2, h)
    #print "w2: ", w2
    
    # compute sample means as a weighted average
    sample_mean1 = w1*mean1 + (1 - w1)*(avg1a+avg1b)
    sample_mean2 = w2*mean2 + (1 - w2)*(avg2a+avg2b)
    
    return [sample_mean1, sample_mean2],[inventory_a.getPolicy(),inventory_b.getPolicy(),policy_a,policy_b]


#******************************************************************************
# TESTING ZONE
#******************************************************************************

def main():
    """
    Testing.
    """
    inventory_a = Inventory(50, 3, 5, 1, 32, 0, (50, 100))
    inventory_b = Inventory(66, 2, 4, 1, 50, 0, (20, 34))
    
    param = (500, 0.12, 0.10, -0.8)
    
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
    print "\n********************** TESTING rankSelect1 **************************"
    tic = time.clock()
    result3 = rankSelect1(inventory_a, (10, 40), param, 1, 0.90, 0)
    toc = time.clock()
    print "sample means and policies: ", result3
    print "Running time: ", toc - tic
    
    tic = time.clock()
    result4 = rankSelect1(inventory_b, (20, 60), param, 1, 0.90, 1)
    toc = time.clock()
    print "sample means and policies: ", result4
    print "Running time: ", toc - tic
    
    print "\n********************** TESTING rankSelect2 **************************"
    tic = time.clock()
    result5 = rankSelect2(inventory_a, inventory_b, (10, 40), (20, 60), param, 1, 0.90)
    toc = time.clock()
    print "sample means and policies: ", result5
    print "Running time: ", toc - tic

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



    
    
    
