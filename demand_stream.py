# -*- coding: utf-8 -*-

#******************************************************************************
# SeedStream CLASS
#******************************************************************************

class SeedStream(object):
    """
    use to generate seeds for DemandStream
    """
    def __init__(self, seed_fct):
        self.seed_fct = seed_fct
        self.seed_list = []
        self.length = 0
        
    def GenerateSeeds(self, n):
        self.seed_list += [self.seed_fct() for _ in xrange(n)]
        self.length += n
        
    def __call__(self, i):
        if i < self.length:
            return self.seed_list[i]
        else:
            self.GenerateSeeds(i-self.length + 10)
            return self.seed_list[i]

#******************************************************************************
# DemandStream CLASS
#******************************************************************************
         
class DemandStream(object):
    """
    use to generate common demands
    """
    def __init__(self, demand_fct, seed_fct):
        """
        demand_fct : function takes a seed to generate a list of demand
        seed_fct : function to generate a seed
        """
        self.seed_fct = seed_fct
        self.seeds = SeedStream(self.seed_fct)
        self.demand_fct = demand_fct
        self.demand_list = []
        self.length = 0
        
    def GenerateDemands(self, n):
        self.demand_list += [self.demand_fct(self.seeds(self.length + i)) for i in range(n)]
        self.length += n
       
    def __call__(self, i):
        """
        call DemandStream(i) to get demand[i]
        """
        if i < self.length:
            return self.demand_list[i]
        else:
            self.GenerateDemands(i-self.length + 1)
            return self.demand_list[i]
           
#%%
#import numpy as np
#import gencorrdemand as gcd
#from demand_stream import *
#
##demand_fct = lambda i: gcd.genCorrDemand(365, 1, 2, 0.5, seed=i)
#demand_fct = lambda i: gcd.genCorrDemand(365, 1, 2, 0.5)
#seed_fct = lambda : np.random.RandomState().get_state()
#

# generate some demands
#demand_generator = DemandStream(demand_fct, seed_fct)
#data1 =  demand_generator(100)
#data2 =  demand_generator(100)

# generate different demands
#demand_generator = DemandStream(demand_fct, seed_fct)
#data3 =  demand_generator(100)
#data4 =  demand_generator(100)

#%%

#******************************************************************************
# demand generator with seeds
#******************************************************************************

import numpy as np
import math
from scipy.stats import norm

def genCorrDemand(num, lambda1, lambda2, rho, **options):
    """
    use arg "seed=" to input a seed from np.random.RandomState().get_state()
    
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
    
# uncomment one 'data' line and last three lines to test genCorrDemand
#data = genCorrDemand(10, 1, 2, 0.5)
#data = genCorrDemand(10, 1, 2, -0.5)
#data = genCorrDemand(50, 1, 2, 0.5)

#import matplotlib.pyplot as plt
#data_tuples = [(data[0][i], data[1][i]) for i in range(len(data[0]))]
#plt.plot(data_tuples)

# to use a common seed
#prng = np.random.RandomState()
#prng_state = prng.get_state()
#data1 = gcd.genCorrDemand(50, 1, 2, 0.5, seed=prng_state)
#data2 = gcd.genCorrDemand(50, 1, 2, 0.5, seed=prng_state)