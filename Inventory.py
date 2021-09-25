"""
Created ........ Sun Nov 08 05:44:12 2015
Last modified .. Sat Nov 21 10:59:47 2015

@author: Caleb Andrade

AMS 553 (Fall 2015) final project.
Instructor: Jiaqiao Hu
Stony Brook University, NY

"Approximation algorithms applied to find a suboptimal
policy (s1, s2, S1, S2) for a two-dimensional Inventory
Control simulation"

Team: 

Tsz Ching Ng ....... tszching.ng@stonybrook.edu
Francisco Hawas .... francisco.hawas@stonybrook.edu
Yue Wang ........... francisyue8341@gmail.com
Caiwei Li .......... caiwei.li@stonybrook.edu
Yujian Liuyu ....... jian.liu.1@stonybrook.edu
Caleb Andrade ...... casernas@ams.sunysb.edu 
"""


#******************************************************************************
# HELPER FUNCTIONS FOR PLOTTING
#******************************************************************************

## import the following modules for plot capabilities
import pylab as pl
from matplotlib import collections  as mc
import matplotlib.pyplot as plt

def plotLines(lines1, lines2, color1, color2, xrang, yrang):
    """
    Plots segments of lines in the plane. Takes as arguments two lists
    'lines1', 'lines2' which consist of segments. The argument 'color1' 
    is the color selected for 'lines1', similarly for 'lines2'. The plot
    ranges are given by xrang and yrang. 
    """
    xaxis = [[(0, 0), (xrang[1], 0)]]
    lc1 = mc.LineCollection(lines1, linewidths = 1, color = color1)
    lc2 = mc.LineCollection(lines2, linewidths = 1, color = color2)
    lc3 = mc.LineCollection(xaxis, linewidths = 1, color = 'black')
    fig, ax = pl.subplots()
    plt.locator_params(nbins=10)
    ax.add_collection(lc3)
    ax.add_collection(lc2)
    ax.add_collection(lc1)
    ax.margins(0)
    ax.set_xlim(xrang)
    ax.set_ylim(yrang)
    fig.set_size_inches(10, 10)
    

def plotHist(histogram, order_arrivals, ss_policy):
    """
    Plots histogram.
    """
    ## initialize variables
    lines = []
    ymax = 0
    ymin = float('inf')
    low, top = ss_policy[0], ss_policy[1]
   
    ## loop through histogram's value
    for period in range(len(histogram) - 1):
        ## define the vertical values
        y1 = histogram[period]
        y2 = histogram[period + 1]
        ## keep track of greatest and minimal vertical values
        ysup = max(y1, y2)
        yinf = min(y1, y2)
        ## append to list line segments to plot
        lines.append([(period, y1), (period + 1, y1)])
        lines.append([(period + 1, y1), (period + 1, y2)])
        if order_arrivals[period] != 0:
            yinf = y1 - order_arrivals[period]
            lines.append([(period, y1), (period, yinf)])
        ## select best candidates for yrange
        if ysup > ymax:
            ymax = ysup
        if yinf < ymin:
            ymin = yinf
            
    ## append last line segment
    lines.append([(period + 1, y2), (period + 2, y2)])
    ## define plot's xrange and yrange
    xrang = [0, len(histogram)]
    yrang = [ymin - 0.1*abs(ymin), 1.1*ymax]
    ## create segments to draw policy's lower and upper limits
    low_lim = [(0, low), (len(histogram), low)]
    top_lim = [(0, top), (len(histogram), top)]
    plotLines(lines, [low_lim, top_lim], 'blue', 'red',  xrang, yrang)


#******************************************************************************
# INVENTORY CLASS
#******************************************************************************
__author__ = 'CalebAndrade'
class Inventory(object):
    """
    A class to model an inventory control problem with (s, S) policy.
    """
    def __init__(self, level, item_cost, backlog_cost, hold_cost, setup_cost,
                 lead_time, policy):
        """
        Initialize inventory state variables.
        """
        self.level = level
        self.initial_level = level ## records the initial level, never mutates
        self.in_stock = max(0, level)
        self.backlog = max(0, -level)
        self.place_order = 0 ## quantity of items ordered
        self.current_order = 0 ## number of items to arrive
        self.lead_time = lead_time
        self.order_delay = 0 ## periods after an order was placed
        self.ongoing_order = False ## is there an order going on?
        self.low = policy[0]
        self.top = policy[1]
        self.item_cost = item_cost
        self.backlog_cost = backlog_cost
        self.hold_cost = hold_cost
        self.setup_cost = setup_cost
        self.histogram = [level] ## inventory's level histogram
        self.order_arrivals = [self.place_order] ## records the orders arrivals
        self.backlog_hist = [self.backlog]
        self.cost_hist = [self.onePeriodCost()] ## inventory's cost histogram
        
                
    def __str__(self):
        """
        State variables as string.
        """
        info = '\nInventory level............ ' + str(self.level) + '\n'
        info += 'In-stock items............. ' + str(self.in_stock) + '\n'
        info += 'Backlogged items........... ' + str(self.backlog) + '\n'
        info += 'Place order................ ' + str(self.place_order) + '\n'
        info += 'Current order.............. ' + str(self.current_order) + '\n'
        info += 'Lead time.................. ' + str(self.lead_time) + '\n'
        info += 'Lead time passed........... ' + str(self.order_delay) + '\n'
        info += 'Policy (s, S).............. (' + str(self.low) + ', ' + str(self.top) + ')\n'
        info += 'Cost per item.............. $ ' + str(self.item_cost) + '\n'
        info += 'Backlog cost per item...... $ ' + str(self.backlog_cost) + '\n'
        info += 'Holding cost per item...... $ ' + str(self.hold_cost) + '\n'
        info += 'Set-up cost................ $ ' + str(self.setup_cost) + '\n'
        info += 'One period cost............ $ ' + str(self.onePeriodCost()) + '\n'        
        info += 'Average cost............... $ ' + str(self.averageCost()) + '\n'
        
        return info 
        
    
    def clone(self):
        """
        Returns an exact clone of self.
        """
        ## initialize inventory object
        clone = Inventory(self.level, self.item_cost, self.backlog_cost,
                          self.hold_cost, self.setup_cost, self.lead_time,
                          self.getPolicy())
        ## clone values from mutable variables in self
        clone.initial_level = self.initial_level
        clone.in_stock = self.in_stock
        clone.backlog = self.backlog
        clone.place_order = self.place_order
        clone.current_order = self.current_order
        clone.order_delay = self.order_delay
        clone.ongoing_order = self.ongoing_order
        clone.histogram = self.getLevelHistogram()
        clone.order_arrivals = self.getOrderArrivals()
        clone.backlog_hist = self.getBacklogHistogram()
        clone.cost_hist = self.getCostHistogram()
        
        return clone
        
        
    def onePeriodCost(self):
        """
        Returns the one-period cost.
        """
        ## costs associated with in stock and backlogged items
        cost = self.in_stock*self.hold_cost + self.backlog*self.backlog_cost
        ## if an order is placed, add the setup cost and cost per items
        ## this should only be added once, the day an order is placed
        if self.place_order != 0:
            cost += self.setup_cost + self.item_cost*(self.place_order)
        
        return cost
        
    
    def setPolicy(self, policy):
        """
        Sets a new policy.
        """
        if policy[0] < policy[1]:
            self.low = policy[0]
            self.top = policy[1]
        else:
            print "Warning: lower control value can't be greater than upper control value!"
    
    
    def onePeriodSim(self, demand):
        """
        Updates state after one period of simulation. 
        @co-author: Tsz Ching Ng.
        """
        # update inventory level, in-stock and backlog
        self.place_order = 0
        self.level -= demand
        self.backlog = max(0, -self.level)
        self.backlog_hist.append(self.backlog)
        self.order_arrivals.append(0) # order has not yet arrived
                    
        # has order arrived? reset order's variables
        if self.order_delay >= self.lead_time:
            self.level += self.current_order
            self.order_arrivals[-1] = self.current_order # order arrives
            self.current_order = 0
            self.order_delay = 0
            self.ongoing_order = False
 
        # place an order?
        if self.level < self.low and not self.ongoing_order:
            self.place_order = self.top - self.level
            self.current_order = self.place_order
            self.ongoing_order = True
        
        # update in-stock items
        self.in_stock = max(0, self.level)
        
        # record inventory level
        self.histogram.append(self.level)
        
        # update order delay time
        if self.ongoing_order:
            self.order_delay += 1
                    
        # update cost histogram
        self.cost_hist.append(self.onePeriodCost())
        
        
    def simulation(self, demands):
        """
        Runs simulation of inventory system extracting one demand per time
        period from the list 'demands'. 
        """
        for demand in demands:
            self.onePeriodSim(demand)
                        
    
    def averageCost(self):
        """
        Returns the average of costs recorded in 'self.hist_cost'.
        """
        return float(sum(self.cost_hist)) / len(self.cost_hist)
            
        
    def reset(self):
        """
        Resets inventory to initial state.
        """
        # reset mutable variables
        self.level = self.initial_level 
        self.in_stock = max(0, self.level)
        self.backlog = max(0, -self.level)
        self.place_order = 0 
        self.current_order = 0
        self.order_delay = 0 
        self.ongoing_order = False 
        self.histogram = [self.level] 
        self.cost_hist = [self.onePeriodCost()]  
        self.order_arrivals = [self.place_order] ## records the orders arrivals
        self.backlog_hist = [self.place_order]
        
    
    def plot(self):
        """
        Plots level histogram.
        """
        plotHist(self.histogram, self.order_arrivals, [self.low, self.top])
        
        
    def getLevelHistogram(self):
        """
        Gets level histogram as a list.
        """
        return list(self.histogram)
        
        
    def getBacklogHistogram(self):
        """
        Gets backlog histogram as a list.
        """
        return list(self.backlog_hist)
        
        
    def getCostHistogram(self):
        """
        Gets cost histogram as a list.
        """
        return list(self.cost_hist)
        
        
    def getPeriods(self):
        """
        Gets number of periods of simulation.
        """
        return len(self.histogram) - 1
        
    
    def getPolicy(self):
        """
        Get (s, S) policy.
        """
        return (self.low, self.top)
        
    def getOrderArrivals(self):
        """
        Get order_arrivals
        """
        return list(self.order_arrivals)

#******************************************************************************
# HELPER FUNCTIONS TO READ A TXT FILE WITH A MATRIX OF RANDOM NUMBERS
#******************************************************************************
def readFile(filetxt):
    """
    Reads a *.txt file containing a matrix of random numbers.
    """
    f = open(filetxt, 'r')
    data = []
    while True:
        numbers = []
        line = f.readline()
        if line != '':
            temp = ''
            for char in line:
                if char != ' ' and char != '\n':
                    temp += char
                else:
                    numbers.append(float(temp))
                    temp = ''
            data.append(numbers)
        else:
            break
    return data
    
#******************************************************************************
# EXAMPLES
#******************************************************************************
def main():
    """
    Testing examples.
    """
    import random
    
    # set the initial values for an inventory object
    level = 50
    item_cost = 20
    backlog_cost = 2
    holding_cost = 1
    setup_cost = 100
    lead_time = 0
    ss_policy = (12, 35)
    
    # create object
    inventory = Inventory(level, item_cost, backlog_cost, holding_cost, 
                          setup_cost, lead_time, ss_policy)
    
    print "\nInitial inventory: \n", inventory
    
    print "\n\n********************* EXAMPLE 1 ****************************** "
    demands = [2.1, 10.6, 19.6, 5.9, 11.8, 11.9, 2.1, 2.9, 1.2]
    # let's use the demands one at a time
    for demand in demands:
        print "\nIncoming demand: ", demand
        inventory.onePeriodSim(demand)
        print inventory
                
    #plot and reset
    inventory.plot()
    print "Average cost: ", inventory.averageCost()
    print inventory.histogram
    print inventory.order_arrivals
    
#    clone.plot()
#    print "Clone average cost: ", clone.averageCost()
#    print clone.histogram
#    
#    clone.simulation(demands)
#    clone.plot()
#    print "Clone average cost: ", clone.averageCost()
#    print clone.histogram
#    
#    
#    print "\n\n********************* EXAMPLE 2 ****************************** "
#    demands = [random.randrange(0, 50) for i in range(100)]
#    # simulate now using inventory's simulation method
#    inventory.reset()
#    inventory.simulation(demands)
#     # plot and reset  
#    inventory.plot()
#    print inventory
#    print "Average cost: ", inventory.averageCost()
#    inventory.reset()
#    
#    
#    print "\n\n********************* EXAMPLE 3 ****************************** "
#    demands = readFile('demand1.txt') # reading demands from a file
#    # simulate now using inventory's simulation method
#    inventory.reset()
#    inventory.simulation(demands[0])
#    # plot 
#    inventory.plot()
#    print inventory
#    print "Average cost: ", inventory.averageCost()
    
    

    
    

        
        
            
            
        
        
        
        