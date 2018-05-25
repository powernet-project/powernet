import numpy as np
from cvxpy import *
from pypower.api import runpf, ppoption
import time
from multiprocessing import Pool
import itertools
import csv

# Ideally won't need this function -> all the data should come from CC
def DataPreLoaded(csv_file,houseNumber):
    reader = csv.reader(open(csv_file, 'rUb'), dialect=csv.excel_tab,delimiter=',')
    #reader = csv.reader(open("ScenarioGen_N.csv", 'rUb'), dialect=csv.excel_tab,delimiter=',')
    scen = list(reader)
    homeForecast = [] # next 48 hours forecast
    for r in scen[houseNumber]:
        homeForecast.append(float(r))
    return homeForecast


def LC_Combined_No_Bounds_SingleHome(NLweight, prices, sellFactor, q0, LCscens, GCtime, umaxo, umino, qmaxo, qmino):
    Qfinal = np.zeros((1,GCtime+1))     # Variable to hold state of charge of the house
    Ufinal = np.zeros((1,GCtime+1))     # Variable to hold batery charging power of the house
    boundsFlag = np.zeros((1,GCtime))
    Qfinal[:,0] = q0                    # Intializing battery state of charge

    # New variables -> pre-computed
    nS = 1      # # of houses -> first house
    T = 48      # Time horizon 24hrs, 48hrs etc -> This should be same as realS # of columns

    # Ideally won't need this function -> all the data should come from CC
    #homeForecast = DataPreLoaded("ScenarioGen1_Last.csv",0)
    realS = DataPreLoaded("realS1.csv",0)   # net power profile to be followed by the home

    # This loops through the 24hrs of the global controller updates -> calculating all 24hrs at a time
    for t in range(GCtime):

        umin = np.tile(umino, (1,T-t))
        umax = np.tile(umaxo, (1,T-t))
        qmax = np.tile(qmaxo, (1,T-t+1))
        qmin = np.tile(qmino, (1,T-t+1))
        #pricesCurrent = np.tile(prices[:,t:], LCscens)
        pricesCurrent = np.tile(prices[t:],(nS,LCscens))
        # Ideally won't need this function -> all the data should come from CC
        homeForecast = DataPreLoaded("ScenarioGen1.csv",t*26)
        LCforecasts = homeForecast


		# initialize variables
        Y = Variable(nS,(T-t)*LCscens)
        U = Variable(nS,T-t)
        Q = Variable(nS,T-t+1)

		# Battery Constraints
        constraints = [Q[0] == q0,
					Q[1:T-t+1] == Q[0:T-t] + U,
					U <= umax,
					U >= umin,
					Q <= qmax,
					Q >= qmin
					]

        for i in range(LCscens):
            # Demand and battery action constraints
            constraints.append( Y[(i*(T-t)):((i+1)*(T-t))] == -LCforecasts[i] - U )
            print "LCforecast[i]: ", LCforecasts[i]

        if sellFactor == 0:
            obj = Minimize( sum_entries(mul_elemwise(pricesCurrent, neg(Y))) + NLweight*norm(Y - np.tile(realS[t:], (1,LCscens)), 'fro') )
        else:
			obj = Minimize( sum_entries(mul_elemwise(pricesCurrent, -Y)) + NLweight*norm(Y - np.tile(realS[t:], (1,LCscens)), 'fro') )

        if sellFactor == 3:
			constraints.append( Y <= 0) # nodes cannot sell

        prob = Problem(obj, constraints)
        prob.solve(solver = MOSEK)
        if prob.status != "optimal":
			print 'LC status is: ', prob.status
        Qfinal[:,t+1] = Q[:,1].value
        q0 = Q[:,1].value
        if np.any(np.less(q0, qmino)): # Correct for computational inaccuracies
			q0 += .00001
        elif np.any(np.greater(q0, qmaxo)):
			q0 += -.00001
        Ufinal[:,t] = U[:,0].value

    return Qfinal, Ufinal, boundsFlag
