
import numpy as np
import argparse
from scipy.io import loadmat
import time

from GC_algs_v0_1 import *
from LC_algs_v0_1 import *
from Network_v0_1 import *
from Forecaster_v0_1 import *

def SingleOpt():
	parser = argparse.ArgumentParser(description='Simulate Control')
	parser.add_argument('--seed', default=0, help='random seed')
	parser.add_argument('--storagePen', default=2, help='storage penetration percentage')
	parser.add_argument('--solarPen', default=3, help='solar penetration percentage')
	#parser.add_argument('--V_weight', default=500, help='voltage soft constraint weight')
	FLAGS, unparsed = parser.parse_known_args()
	print 'running with arguments: ({})'.format(FLAGS)
	storagePen = float(FLAGS.storagePen)/10
	solarPen = float(FLAGS.solarPen)/10
	seed = int(FLAGS.seed)

	np.random.seed(seed) # set random seed

	#Initialize simulation parameters
	nodesPen = np.maximum(solarPen,storagePen)
	GCtime = 24
	lookAheadTime = 24
	GCstepsTotal = 30
	sellFactor = 1
	GCscens = 1
	LCscens = 1
	V_weight = 10000 # tuning parameter for voltage penalties
	Vtol = .005 # tolerance bound on voltage penalties
	ramp_weight = 100000 # make large to prioritize ramp following
	NLweight = 4000 # make 10X price when there are no bounds

	# For 1 day pecan street data
	GCtime = 12
	lookAheadTime = 12
	GCstepsTotal = 2


	# Load Data
	# IEEE 123 bus case PG&E data
	network_data = np.load('data/network_data.npz')
	loadMod = 1
	presampleIdx = 168; # first week as presample data
	startIdx = presampleIdx + 1 # starting index for the load dataset
	DataDict = loadmat('data/loadData123Ag.mat')
	pDemandFull = loadMod*np.matrix(DataDict['pDemand'])
	rDemandFull = loadMod*np.matrix(DataDict['rDemand'])
	DataDict = loadmat('data/PyLoadData.mat')
	sNormFull = np.matrix(DataDict['sNorm'])
	# Load Residual Means and Covariance Dictionaries
	ResidualDict = loadmat('data/ResidualData123.mat')
	pMeans = ResidualDict['pMeans'][0,0]
	pCovs = ResidualDict['pCovs'][0,0]

	# Load network
	root = 0
	ppc = network_data['ppc'][()]
	Ybus = network_data['Ybus'][()]

	# Load Prices
	prices = np.matrix(np.hstack((250*np.ones((1,16)) , 350*np.ones((1,5)), 250*np.ones((1,3)))))
	prices = np.tile(prices, (1,GCtime*GCstepsTotal/24))
	pricesFull = prices

	# Load Ramps
	windPen = .3 # 30% of electricity comes from wind used to calculate ramp amounts
	ramp_tolerance = 0 # 5% of ramp amount tolerance on ramp works better with 0 tolerance
	rampDict = loadmat('data/rampDataAll.mat')
	rampUpData = rampDict['true_Uramp'] # dimensions are ramps X (start/end time start/end power)
	rampUpData = rampUpData[1:,:] # remove first ramp since it occurs too early at time 2
	rampDownData = rampDict['true_Dramp']
	rampDownData[:,[2,3]] = rampDownData[:,[3,2]] # swap down ramp amounts to make negative
	rampDataAll = np.vstack((rampUpData, rampDownData))
	rOrder = np.argsort(rampDataAll[:,0])
	rampsNumTotal = len(rOrder)
	rampDataAll = rampDataAll[rOrder,:]
	rampDataAll[:,[0,1]] = rampDataAll[:,[0,1]] - 1 # subtract 1 for matlab indexing

	# Make dictionary of ramps using whole network for scale
	rampUAll = make_ramp_dict(rampDataAll, windPen, ramp_tolerance, pDemandFull)
	ramp_starts = np.sort(rampUAll.keys())
	ramp_curr = np.array(ramp_starts[ramp_starts >= (720)]) # remove ramps after 720 hours
	for ramp_key in ramp_curr:
		rampUAll.pop(ramp_key)
	print('all ramp times', np.sort(rampUAll.keys()))

	# initialize forecaster and network
	forecast_error = .1
	forecaster = Forecaster(forecast_error, pMeans, pCovs)

	# Random = True
	network = Network(storagePen, solarPen, nodesPen, pDemandFull, rDemandFull, pricesFull, root, Ybus, startIdx, sNormFull, Vmin=0.95, Vmax=1.05, Vtol=0, v_root=1.022, random=True, rampUAll=rampUAll)

	# Random = False

	# hardcoding battery information
	battnodes = np.array([4, 10], dtype=int)
	qmin = np.reshape(np.matrix([0, 0]), (2,1))
	qmax = np.reshape(np.matrix([0.126, 0.063]), (2,1))	# 7kWh x 18batt = 126kWh / 7kWh x 9batt = 63kWh
	umin = -qmax/3
	umax = qmax/3
	# 123 bus case 1 day Pecan Street 1 minute data
	startIdx = 0
	battnode_data = np.genfromtxt('data/agg_load_123_raw.csv', delimiter=',').T
	battnode_data[0,0] = 1235.22
	pdat = np.zeros((2,24))
	for i in range(24):
		pdat[:,i] = np.mean(battnode_data[:,i*60:(i+1)*60], axis=1)
	rdat = pdat*np.tan(np.arccos(.9))
	network_data = np.genfromtxt('data/network123_case_load.csv', delimiter=',')
	network_data[0,0] = 0
	pDemandFull = np.tile(np.reshape(network_data[:,0], (123,1)), (1,24))
	rDemandFull = np.tile(np.reshape(network_data[:,1], (123,1)), (1,24))
	pDemandFull[battnodes,:] = pdat/1000000 # convert to MW
	rDemandFull[battnodes,:] = rdat/1000000
	netDemandFull = np.matrix(pDemandFull)
	rDemandFull = np.matrix(rDemandFull)
	rampDataAll = np.matrix(rampDataAll[0,:]) # use only first ramp for 24 hours of data
	for i in battnodes: #Make 0 for no forecaster
		pMeans['b'+str(i+1)] = np.zeros(pMeans['b'+str(i+1)].shape)
		pCovs['b'+str(i+1)] = np.zeros(pCovs['b'+str(i+1)].shape)

	# Make dictionary of ramps using only battnodes for scale
	windPen = 6 # make 1 to account for only using battnodes instead of whole network
	rampUAll = make_ramp_dict(rampDataAll, windPen, ramp_tolerance, pDemandFull[battnodes,:])
	ramp_starts = np.sort(rampUAll.keys())
	ramp_curr = np.array(ramp_starts[ramp_starts >= (720)]) # remove ramps after 720 hours
	for ramp_key in ramp_curr:
		rampUAll.pop(ramp_key)
	print('all ramp times', np.sort(rampUAll.keys()))

	rampUAll_orig = rampUAll.copy()

	network = Network(storagePen, solarPen, nodesPen, pDemandFull, rDemandFull, pricesFull, root, Ybus, startIdx, Vmin=0.95, Vmax=1.05, Vtol=0, v_root=1.022, random=False, rampUAll=rampUAll)
	network.inputStorage(Ybus, netDemandFull, battnodes, qmin, qmax, umin, umax)
	# End Random = False


	#get network information
	nodesStorage = network.battnodes
	storageNum = len(nodesStorage)
	qmin = network.qmin
	qmax = network.qmax

	#reformat data for network
	for i in nodesStorage:
		pMeans['b'+str(i+1)] = pMeans['b'+str(i+1)].flatten()

	# initialize controllers
	t_idx = 0 # set controller t_idx to something non zero after this if wanted
	GC = Global_Controller(network, forecaster, GCtime, lookAheadTime, GCscens, sellFactor, V_weight, Vtol, ramp_weight)
	q0 = np.matrix(np.zeros(qmax.shape)) #set initial q0 to be 0
	#q0 = np.matrix(np.ones(qmax.shape)*0.5) #set initial q0 to be 0.5
	LCs = Local_Controllers(network, forecaster, GCtime+lookAheadTime, LCscens, NLweight, sellFactor, ramp_weight, nodesStorage, q0)

	# Initialize values to save
	Qall = np.matrix(np.zeros((storageNum,GCtime*GCstepsTotal+1)))
	Uall = np.matrix(np.zeros((storageNum,GCtime*GCstepsTotal)))


	#while t_idx < GCtime*GCstepsTotal:

	### Run Global Controller ###
	print('Running time:', t_idx)
	realS, pricesCurrent, LCtime, rampFlag, RstartList, QiList, RsignList, ramp_next = GC.runStep(q0, t_idx)
	print 'realS: ', realS
	print 'pricesCurrent: ', pricesCurrent
	print 'LCtime: ', LCtime
	print 'rampFlag: ', rampFlag
	print 'RstartList: ', RstartList
	print 'QiList: ', QiList
	print 'RsignList: ', RsignList
	print 'Pdemand: ', pdat/1000000


	### Run Local Controllers ###
	# run several time periods at once should be switched to sequentially
	print('running local controllers')
	Uall[:,t_idx:(t_idx+LCtime)], Qall[:,(t_idx+1):(t_idx+LCtime+1)], t_idx_new = LCs.runPeriod(t_idx, realS, pricesCurrent, LCtime, rampFlag, RstartList, QiList, RsignList)
	t_idx_old = t_idx
	t_idx = t_idx_new
	print 'after LC time', t_idx

	# get latest state of charge before splitting ramp
	q0 = np.reshape(Qall[:,t_idx], (storageNum,1))

	print "LATEST SOC, Q0: ", q0

	if np.any(np.less(q0, qmin)): # Correct for computational inaccuracies
		q0 += .00001
		print('q0 too low')
	elif np.any(np.greater(q0, qmax)):
		q0 += -.00001
		print('q0 too high')

	### Split Ramp Signal ###
	# split signal is sent directly to storage units to follow without running LC MPC optimization
	# Added t_idx_old as a function variable
	if rampFlag == 1:
		print('splitting ramp signal')
		U_ramp_test, ramp_duration, t_idx_new = GC.disaggregateRampSignal(t_idx, q0, ramp_next, t_idx_old)
		# U_ramp_test is the battery charging action during a ramp
		Uall[:,t_idx:(t_idx+ramp_duration)] = U_ramp_test
		Qall[:,(t_idx+1):(t_idx+ramp_duration+1)] = np.reshape(Qall[:,t_idx], (storageNum,1)) + np.cumsum(U_ramp_test,axis=1)
		t_idx = t_idx_new

		############
		print "U_ramp_test shape: ", U_ramp_test.shape
		print "U_ramp_test: ", U_ramp_test
		print "Uall shape: ", Uall.shape
		print "Uall: ", Uall
		############

		############
		print 'Qall: ', Qall
		############

		# get latest state of charge before running global controller
		q0 = np.reshape(Qall[:,t_idx], (storageNum,1))
		if np.any(np.less(q0, qmin)): # Correct for computational inaccuracies
			q0 += .00001
			print('q0 too low')
		elif np.any(np.greater(q0, qmax)):
			q0 += -.00001
			print('q0 too high')

		print 'q0 to GC: ', q0

	print 'after ramp time', t_idx

	if (t_idx%100) < 20:
		# Save Data
		np.savez('ramp_1day-2',Qall=Qall,Uall=Uall,t_idx=t_idx, Ubounds_vio=GC.Ubounds_vio, rampSkips=GC.rampSkips, rampUAll=rampUAll_orig)
		print('SAVED')
	#np.savetxt("Uall.csv", Uall, delimiter=",")


	#print Uall
	#print Qall
	# Save Data
	#np.savez('ramp_1day-2',Qall=Qall,Uall=Uall,t_idx=t_idx, Ubounds_vio=GC.Ubounds_vio, rampSkips=GC.rampSkips, rampUAll=rampUAll_orig)
	#print('SAVED')

	return Uall
