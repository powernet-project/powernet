# Main Demo Function
"""
	Demos Optimal Cost Min functionality

	Dependencies:
		scipy
		numpy

	Inputs:

	Outputs:


"""

import numpy as np
from scipy.io import loadmat
from DemoMod import *
import json


def mainDemo(solarAlphas, storageAlphas, control):
	np.random.seed(0) # Do not randomize anything

	# Set Constant Parameters
	transLimitDay = 1 # day that the transformer limit takes place
	transLimit = 9 # kW limit on transformer
	transLimitTime = np.arange(6,11) # times of the day it takes place
	GCstepsTotal = 2 # Total number of simulation days
	Vmin = .95 # max and min voltage
	Vmax = 1.05
	# Load Prices TOU
	prices = np.matrix(np.hstack((.25*np.ones((1,16)) , .35*np.ones((1,5)), .25*np.ones((1,3)))))
	prices = np.tile(prices, (1,GCstepsTotal+2))
	
	GCtime = 24
	lookAheadTime = 48
	Vbuff = .005

	# Load Network and PF case data
	rootIdx = 0
	ppc = DemoCase7()

	# Load Data
	presampleIdx = 72*0-1; # make -1 to start at 0
	startIdx = presampleIdx + 1 # starting index for the load dataset
	DataDict = loadmat('DemoData.mat')
	pDemandFull = np.matrix(DataDict['pDemand'])
	rDemandFull = np.matrix(DataDict['rDemand'])
	solarReg = np.matrix(DataDict['solarReg'])
	Ybus = GetYbus(ppc)
	# Switch transformer and commercial building demand
	pDemandFull[2,:] = pDemandFull[1,:]
	rDemandFull[2,:] = rDemandFull[1,:]
	pDemandFull[1,:] = pDemandFull[1,:] - pDemandFull[1,:]
	rDemandFull[1,:] = rDemandFull[1,:] - rDemandFull[1,:]
	nodesNum, timeTotal = pDemandFull.shape

	# Load Prices TOU
	prices = np.matrix(np.hstack((.25*np.ones((1,16)) , .35*np.ones((1,5)), .25*np.ones((1,3)))))
	prices = np.tile(prices, (1,timeTotal/24))

	# Assign Storage/Solar
	sGenFull, nodesLoad, nodesStorage, qmin, qmax, umin, umax = DemoAssignStorageSolar(solarReg, solarAlphas, storageAlphas)
	netDemandFull = np.zeros(pDemandFull.shape) + pDemandFull
	netDemandFull[nodesStorage,:] = pDemandFull[nodesStorage,:] - sGenFull
	q0 = np.zeros(qmax.shape) #set initial q0 to be 0

	# Bulid network
	tnetwork = Network(Ybus, rootIdx, nodesStorage, qmin, qmax, umin, umax, Vmin+Vbuff, Vmax-Vbuff)

	## Start of optimization loop GC then PF simulator

	# Initialize results arrays
	ARBtotal = 0
	ARBeach = np.zeros((1,5))
	allVoltage = np.zeros((nodesNum,GCtime*GCstepsTotal))
	OPFVoltage = np.zeros((nodesNum,GCtime*GCstepsTotal))
	Qall = np.zeros((len(nodesStorage),GCtime*GCstepsTotal))
	Uall = np.zeros((len(nodesStorage),GCtime*GCstepsTotal))
	netPowerAll = np.zeros((7,GCtime*GCstepsTotal))
	"""
	rankCheckAll = np.zeros((1,GCtime*GCstepsTotal))
	annulusMinCheckAll = np.zeros((1,GCtime*GCstepsTotal))
	annulusMaxCheckAll = np.zeros((1,GCtime*GCstepsTotal))
	"""

	for GCiter in range(GCstepsTotal):

		#Get prices for current run
		pricesCurrent = prices[:,(GCiter*GCtime+startIdx):((GCiter+1)*GCtime+lookAheadTime+startIdx)]

		#Get real data
		netDemand = netDemandFull[:,(GCiter*GCtime+startIdx):((GCiter+1)*GCtime+lookAheadTime+startIdx)]
		rDemand = rDemandFull[:,(GCiter*GCtime+startIdx):((GCiter+1)*GCtime+lookAheadTime+startIdx)]

		# PFSOC Controller
		if control:
			if GCiter == transLimitDay:
				transLimitTime = transLimitTime
			else:
				transLimitTime = 0
			pForecast, rForecast = Forecaster(netDemand, rDemand)
			Q, U, runVoltage, allV2, Wre, Wie, S0 = PFSOC_Out_All(tnetwork, pricesCurrent, pForecast, rForecast, q0, GCtime, ppc, transLimitTime, transLimit)

			# check rank and annulus condition satisfaction
			"""
			rankCheck, annulusMinCheck, annulusMaxCheck = CheckAnnulusRank(allV2, Wre, Wie, tnetwork, GCtime)
			rankCheckAll[:,GCiter*GCtime:(GCiter+1)*GCtime] = rankCheck
			annulusMinCheckAll[:,GCiter*GCtime:(GCiter+1)*GCtime] = annulusMinCheck
			annulusMaxCheckAll[:,GCiter*GCtime:(GCiter+1)*GCtime] = annulusMaxCheck
			"""

			#Update q0
			q0 = Q[:,GCtime]
			OPFVoltage[:,GCiter*GCtime:(GCiter+1)*GCtime] = np.sqrt(allV2[:,0:GCtime])

		else:
			# Make U charge during solar and discharge based on prices disregarding the network
			Usingle = np.hstack((np.zeros((1,7)) , np.ones((1,9))*3/9., -np.ones((1,5))*3/5., np.zeros((1,3))))
			U = np.matrix(umax*np.tile(Usingle, (5,1)))
			Q = np.cumsum(U, axis=1)

			rootV2 = np.matrix(np.ones((1,GCtime))) # no control over root voltage for first run
			runVoltage, S0 = PF_Sim(ppc, GCtime, netDemand, rDemand, nodesStorage, U, rootV2)
			maxV = np.max(runVoltage,axis=0)
			minV = np.amin(runVoltage,axis=0)
			maxmin = np.vstack((maxV,minV))
			rootV2 = 2 - np.mean(maxmin,0)
			rootV2 = np.matrix(np.square(rootV2))
			runVoltage, S0 = PF_Sim(ppc, GCtime, netDemand, rDemand, nodesStorage, U, rootV2)

		#Save results
		allVoltage[:,GCiter*GCtime:(GCiter+1)*GCtime] = runVoltage
		Qall[:,GCiter*GCtime:(GCiter+1)*GCtime] = Q[:,0:GCtime]
		Uall[:,GCiter*GCtime:(GCiter+1)*GCtime] = U[:,0:GCtime]
		netPowerAll[0,GCiter*GCtime:(GCiter+1)*GCtime] = S0[:,0:GCtime] # substation
		netPowerAll[2:,GCiter*GCtime:(GCiter+1)*GCtime] = netDemand[2:,0:GCtime] + U[:,0:GCtime] # commercial building and houses
		netPowerAll[1,GCiter*GCtime:(GCiter+1)*GCtime] = np.sum(netDemand[3:,0:GCtime] + U[1:,0:GCtime],0) #transformer is sum of houses

		#Calculate arbitrage profits
		ARBeach += pricesCurrent[:,0:GCtime]*U[:,0:GCtime].T
		ARBtotal += pricesCurrent[:,0:GCtime]*np.sum(U[:,0:GCtime],0).T

	# Calculate results
	vio_times, vio_plus_sum, vio_min_sum, vio_when = Violation_Process(allVoltage, Vmin, Vmax)
	chargeTotal = np.sum(np.abs(Uall),axis=1)
	cyclesNum = chargeTotal/qmax.flatten()/2
	#print 'Number of Battery Cycles: ', cyclesNum

	return -ARBeach, netPowerAll, sGenFull[:,0:GCtime*GCstepsTotal], Uall, Qall, allVoltage

if __name__ == '__main__':
	# Set default input parameters
	control = 1 # whether or not to use control
	solarAlphas = np.array([9, 3, 3, 3, 3,]) # 9kW commercial 3kW residential solar installations
	storageAlphas = np.array([3*14, 14, 14, 14, 14]) # 14kWh per tesla powerwall
	ARBeach, netPowerAll, solarAll, Uall, Qall, voltageAll = mainDemo(solarAlphas, storageAlphas, control)

	import matplotlib.pyplot as plt
	# print 'Arbitrage Profit per Node: ', ARBeach
	# print 'Arbitrage transposed: ', ARBeach.T
	# print 'Arbitrage to list: ', ARBeach.tolist()
	# print 'Arbitrage to list after being transposed: ', ARBeach.T.tolist()
	# print 'Arbitrage serialized: ', json.dumps(ARBeach.tolist())
	# print 'Arbitrage transposed serialized: ', json.dumps(ARBeach.T.tolist())
	
	# print 'Net Power All: ', netPowerAll.T
	
	# print 'Solar All: ', solarAll.T
	# print 'Q All: ', Qall.T
	# print 'U All: ', Uall.T
	# print 'Voltage All: ', voltageAll.T

	#print json.dumps(voltageAll.T.tolist())

	plt.figure(0)
	plt.plot(netPowerAll.T)
	plt.title('Net Power for Each Node')
	plt.figure(1)
	plt.plot(solarAll.T)
	plt.title('Solar Generation for Each Node')
	plt.figure(2)
	plt.plot(Qall.T)
	plt.title('State of Charge for Each Node')
	plt.figure(3)
	plt.plot(Uall.T)
	plt.title('Charging Action for Each Node')
	plt.figure(4)
	plt.plot(voltageAll.T)
	plt.title('Voltage for Each Node')
	plt.show()



