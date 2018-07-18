import numpy as np
from cvxpy import *
from pypower.api import runpf, ppoption
import time
from multiprocessing import Pool
import itertools
import csv
import rwText
import json
import os

# Ideally won't need this function -> all the data should come from CC
# HouseNumber is the file line that is being selected - houses with battery should start from 0 to n
def DataPreLoaded_NetPower(csv_file,houseNumber):
    reader = csv.reader(open(csv_file, 'rUb'), dialect=csv.excel_tab,delimiter=',')
    #reader = csv.reader(open("ScenarioGen_N.csv", 'rUb'), dialect=csv.excel_tab,delimiter=',')
    scen = list(reader)
    netPowerProfile = [] # next 48 hours forecast
    for i in houseNumber:
        temp = [float(d) for d in scen[i]]
        netPowerProfile.append(temp)

    #for idx,elem in enumerate(scen):
    #    if idx =
    #    netPowerProfile.append(float(elem))

    return netPowerProfile

def DataPreLoaded_Forecast(csv_file,houseNumber):
    reader = csv.reader(open(csv_file, 'rUb'), dialect=csv.excel_tab,delimiter=',')
    #reader = csv.reader(open("ScenarioGen_N.csv", 'rUb'), dialect=csv.excel_tab,delimiter=',')
    scen = list(reader)
    homeForecast = [] # next 48 hours forecast
    for i in houseNumber:
        temp = [float(d) for d in scen[i]]
        homeForecast.append(temp)
    return homeForecast

def DataPreLoaded_Prices(csv_file,houseNumber):
    reader = csv.reader(open(csv_file, 'rUb'), dialect=csv.excel_tab,delimiter=',')
    #reader = csv.reader(open("ScenarioGen_N.csv", 'rUb'), dialect=csv.excel_tab,delimiter=',')
    scen = list(reader)
    prices = [] # next 48 hours forecast
    for r in scen[houseNumber]:
        prices.append(float(r))
    return prices


def BatteryProfiles(U, batt_solar_houses):
    '''
    U_houses = {}               # Creating battery house profile
    for i in batt_solar_houses:
        U_houses[i] = {}

    U_new = U.tolist()[0]   # converting numpy array (output from LC_Combined_No_Bounds_SingleHome) to list for json. This is for one house
    for i in batt_solar_houses:
        U_houses[i]['Battery'] = U_new[1:-1]
    rwText.create_file_json('home_U.json',U_houses)
    '''
    U_new = U.tolist()   # converting numpy array (output from LC_Combined_No_Bounds_SingleHome) to list for json.
    #print 'U_new: ', U_new

    # FIX: DICTIONARY DOES NOT PRESERVE ORDER. FIX WHERE U_HOUSES AND U_BATT INTERSECT!!!!!!

    U_houses = {}               # Creating battery house profile
    u_batt = []
    for idx,i in enumerate(batt_solar_houses):
        U_houses[i] = {}
        u_batt.append(U_new[idx][0])
        U_houses[i]['Battery'] = U_new[idx][1:-1]

    #print 'U_houses: ', U_houses
    rwText.create_file_json('homes_U.json',U_houses)
    #print 'Battery Profile: u_batt = ', u_batt
    return u_batt


def BatteryReadRemove(batt_solar_houses):
    '''
    try:
        with open('homes_U.json', 'r') as data_file:
            data = json.load(data_file)
            print 'data: ', data
    except IOError as e:
        return
    '''
    with open('homes_U.json', 'r') as data_file:
        data = json.load(data_file)
        #print 'data: ', data

    dict_keys = data.keys()

    # Value to actuate in the battery
    try:
        u_batt = []
        #print 'Length battery: ', len(data[dict_keys[0]]['Battery'])
        for i in batt_solar_houses:
            #print 'i: ', i
            #print 'unatt_i: ', data[str(i)]['Battery'][0]
            u_batt.append(data[str(i)]['Battery'][0])
            data[str(i)]['Battery'] = data[str(i)]['Battery'][1:-1]

        if len(data[dict_keys[0]]['Battery']) == 1:
            os.remove('homes_U.json')
            #print 'file deleted...'
        else:
            with open('homes_U.json', 'w') as data_file:
                data = json.dump(data, data_file)

    except Exception as exc:
        print exc

    '''
    with open('homes_U.json', 'w') as data_file:
        data = json.dump(data, data_file)

    try:
        # Overwriting the file with new array (one less element)
        with open('homes_U.json', 'w') as data_file:
            data = json.dump(data, data_file)

    except IOError as e:
        print 'Unable to open write file'
        return
    '''

    print 'BatteryReadRemove: u_batt = ', u_batt
    return u_batt


def LC_Combined_No_Bounds_SingleHome(NLweight, prices, sellFactor, q0, LCscens, GCtime, umaxo, umino, qmaxo, qmino):
    # New variables -> pre-computed
    #house_numbers = np.array([0,2])
    house_numbers = np.array([0])
    nS = house_numbers.size      # # of houses
    T = 48      # Time horizon 24hrs, 48hrs etc -> This should be same as realS # of columns

    Qfinal = np.zeros((nS,GCtime+1))     # Variable to hold state of charge of the house
    Ufinal = np.zeros((nS,GCtime+1))     # Variable to hold batery charging power of the house
    boundsFlag = np.zeros((1,GCtime))
    Qfinal[:,0] = q0                    # Intializing battery state of charge

    # Ideally won't need this function -> all the data should come from CC
    #homeForecast = DataPreLoaded("ScenarioGen1_Last.csv",0) The 0 here means we are taking the first home
    realS = DataPreLoaded_NetPower("realS1.csv",house_numbers)[0]   # net power profile to be followed by the home

    # This loops through the 24hrs of the global controller updates -> calculating all 24hrs at a time
    for t in range(GCtime):

        umin = np.tile(umino, (1,T-t))
        umax = np.tile(umaxo, (1,T-t))
        qmax = np.tile(qmaxo, (1,T-t+1))
        qmin = np.tile(qmino, (1,T-t+1))
        #pricesCurrent = np.tile(prices[:,t:], LCscens) -> LCscens means how many scenarios we are leveraging for the optimization
        pricesCurrent = np.tile(prices[t:],(nS,LCscens))
        # Ideally won't need this function -> all the data should come from CC
        homeForecast = DataPreLoaded_Forecast("ScenarioGen1.csv",t*26+house_numbers)
        LCforecasts = homeForecast
        #print 'LCforecasts: ', LCforecasts[0]
        #print 't: ', t


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
            constraints.append( Y[(i*(T-t)):((i+1)*(T-t))] == -LCforecasts[0][i] - U )
            #print "LCforecast[i]: ", LCforecasts[i]

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


def LC_Combined_No_Bounds_MultiHome(NLweight, prices, sellFactor, q0, LCscens, GCtime, umax, umin, qmax, qmin, number_of_houses):
    # New variables -> pre-computed
    house_numbers = np.arange(number_of_houses+1)[1:]
    #house_numbers = np.array([0])
    nS = house_numbers.size      # # of houses
    T = 48      # Time horizon 24hrs, 48hrs etc -> This should be same as realS # of columns
    umaxo = []
    umino = []
    qmaxo = []
    qmino = []
    for i in house_numbers:
        umaxo.append([umax])
        umino.append([umin])
        qmaxo.append([qmax])
        qmino.append([qmin])

    umaxo = np.asarray(umaxo)
    umino = np.asarray(umino)
    qmaxo = np.asarray(qmaxo)
    qmino = np.asarray(qmino)

    Qfinal = np.matrix(np.zeros((nS,GCtime+1)))     # Variable to hold state of charge of the house
    Ufinal = np.matrix(np.zeros((nS,GCtime+1)))     # Variable to hold batery charging power of the house
    boundsFlag = np.zeros((1,GCtime))
    Qfinal[:,0] = q0                    # Intializing battery state of charge

    # Ideally won't need this function -> all the data should come from CC
    #homeForecast = DataPreLoaded("ScenarioGen1_Last.csv",0) The 0 here means we are taking the first home
    realS_list = DataPreLoaded_NetPower("realS1.csv",house_numbers)   # net power profile to be followed by the home
    realS = np.asarray(realS_list)
    #print 'realS: ', realS

    # This loops through the 24hrs of the global controller updates -> calculating all 24hrs at a time
    for t in range(GCtime):

        umin = np.tile(umino, (1,T-t))
        umax = np.tile(umaxo, (1,T-t))
        qmax = np.tile(qmaxo, (1,T-t+1))
        qmin = np.tile(qmino, (1,T-t+1))
        #pricesCurrent = np.tile(prices[:,t:], LCscens) -> LCscens means how many scenarios we are leveraging for the optimization
        pricesCurrent = np.tile(prices[t:],(nS,LCscens))
        # Ideally won't need this function -> all the data should come from CC
        homeForecast = DataPreLoaded_Forecast("ScenarioGen1.csv",t*26+house_numbers)
        LCforecasts = np.asarray(homeForecast)

        #print 'LCforecasts: ', LCforecasts
        #print 't: ', t


		# initialize variables
        Y = Variable(nS,(T-t)*LCscens)
        U = Variable(nS,T-t)
        Q = Variable(nS,T-t+1)

		# Battery Constraints
        constraints = [Q[:,0] == q0,
					Q[:,1:T-t+1] == Q[:,0:T-t] + U,
					U <= umax,
					U >= umin,
					Q <= qmax,
					Q >= qmin
					]

        for i in range(LCscens):
            # Demand and battery action constraints
            constraints.append( Y[:,(i*(T-t)):((i+1)*(T-t))] == -LCforecasts - U )

        if sellFactor == 0:
            obj = Minimize( sum_entries(mul_elemwise(pricesCurrent, neg(Y))) + NLweight*norm(Y - np.tile(realS[:,t:], (1,LCscens)), 'fro') )
        else:
			obj = Minimize( sum_entries(mul_elemwise(pricesCurrent, -Y)) + NLweight*norm(Y - np.tile(realS[:, t:], (1,LCscens)), 'fro') )

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
