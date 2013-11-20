# BattingModel.py

'''
Estimate a hitter's true batting average, mui, (for the entire season) 
from the first month of data.


The batting average for hitter i is defined as his total number of hits, xi, divided by
the number of at bats, Ni

Statistical Model for batting:
xi | mui ~ Binomial(mui, Ni)
Ni = number of at bats (AB), xi = number of hits (H)
'''


import pymc
import numpy as np
import pandas as pd

# read in data
month = pd.read_csv('hw_11_data/laa_2011_april.txt',sep='\t')
month.sort(columns='Player',inplace=True) # sort for consistancy with final results

# data arrays
num_hits = month['H'] 
N = month['AB']
avg = num_hits / N.astype(float)


# priors on mu_i
alpha = 43.7846590909
beta = 127.919886364

x = np.empty(len(month.index),dtype=object)

#likelihoods
mu = np.empty(len(month.index),dtype=object)

for i in month.index:

    #priors
    mu[i] = pymc.Beta('mu_%i' % i,alpha,beta)

    #likelihoods
    x[i] = pymc.Binomial('x_%i' % i, n=N[i], p=mu[i], value=num_hits[i],observed=True)
