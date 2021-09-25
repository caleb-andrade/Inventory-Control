"""
@author: Francisco Hawas
@contribution: Tze Ching 
"""
import numpy as np
import math
from scipy.stats import norm

def genCorrDemand(num, lambda1, lambda2, rho, **options):
    """
    Returns two lists of size 'num' with random generated numbers:
    'demand1' and 'demand2', that belong to two correlated
    random variates.
    """
    
    prng = np.random.RandomState()
    
    if options.has_key("seed"):
        prng.set_state(options.get("seed"))
            
    mean = [0, 0]
    matrix = np.matrix([[1,rho],[rho,1]])
    dlam1 = -1 / lambda1
    dlam2 = -1 / lambda2
    data = prng.multivariate_normal(mean, matrix, num)
    demand1 = []
    demand2 = []
    for idx in range(num):
        demand1.append(dlam1*math.log(norm.cdf(data[idx][0])))
        demand2.append(dlam2*math.log(norm.cdf(data[idx][1])))
    
    return demand1, demand2
    
def main():
    """
    Testing.
    """
    #data = genCorrDemand(10, 0.12, 0.10, 0.5)
    #data = genCorrDemand(10, 0.12, 0.10, -0.5)
    #data = genCorrDemand(50, 0.12, 0.10, 0.5)
    data = genCorrDemand(50, 0.12, 0.10, -0.5)
    
    import matplotlib.pyplot as plt
    data_tuples = [(data[0][i], data[1][i]) for i in range(len(data[0]))]
    plt.plot(data_tuples)
    
    seeds = []    
    
    for i in range(10):
        ## to use a common seed
        prng = np.random.RandomState()
        prng_state = prng.get_state()
        seeds.append(prng_state)
        
    for prng_state in seeds:
        #print prng_state
        data1 = genCorrDemand(50, 1, 2, 0.5, seed=prng_state)
        data2 = genCorrDemand(50, 1, 2, 0.5, seed=prng_state)
        
        print data1[0][0]
        print data2[0][0]
