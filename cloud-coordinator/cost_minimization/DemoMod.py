"""
Python Module for NLFC cost minimization Demo

Dependencies:
	numpy
	cvxpy
	mosek
	pypower
	networkx
	scipy
"""
#from IPython import embed

import numpy as np
from cvxpy import *
from pypower.api import runpf, ppoption, makeYbus
import networkx as nx
from scipy import sparse

def PFSOC(network, pDemand, qDemand, q0, prices, transLimitTime, transLimit):
	"""
	PFSOC controller for benchmark
	Inputs: network - Network object
			prices - vector of prices for the times in pDemand
			p/qDemand - np matrix (nodes X time) as values
			q0 - initial state of charge vector length number of storage nodes
	Outputs: Q, U, root voltage squared, optimization status
	"""
	
	n, T = pDemand.shape
	nE = len(network.edgelist)
	nS = len(network.battnodes)

	#print("dimensions of problem: ",n,T)

	umin = np.tile(network.umin, (1,T))
	umax = np.tile(network.umax, (1,T))
	qmax = np.tile(network.qmax, (1,T+1))
	qmin = np.tile(network.qmin, (1,T+1))
	rYbus = network.realYbus
	iYbus = network.imagYbus
	
	realS = Variable(n,T)
	imagS = Variable(n,T)
	Wre = Variable(nE,T)
	Wie = Variable(nE,T)
	Wn = Variable(n,T)

	U = Variable(nS,T)
	Q = Variable(nS,T+1)

	# Battery Constraints
	constraints = [Q[:,0] == q0,
				Q[:,1:T+1] == Q[:,0:T] + U,
				U <= umax,
				U >= umin,
				Q <= qmax,
				Q >= qmin
				]
	
	# Demand and battery action constraints
	constraints.append( realS[network.nbattInd,:] == -pDemand[network.nbattInd,:] )
	constraints.append( realS[network.battnodes,:] == -U - pDemand[network.battnodes,:] )
	constraints.append( imagS[network.nrootInd,:] == -qDemand[network.nrootInd,:] )

	# Voltage Constraints
	constraints.append( Wn <= network.Vmax2 )
	constraints.append( Wn >= network.Vmin2 )

	# Transformer limit constraint
	if np.sum(transLimitTime) > 0:
		#print 'transformer constraint active', transLimitTime
		constraints.append( sum_entries(realS[3:,transLimitTime],1) >= -transLimit )

	# Power Flow constraints
	for node in range(n):			
		eidxs = network.nodeEdge[node]
		js = network.nodeNeighbor[node]
		direction = network.nodeDirection[node]
		constraints.append( realS[node,:] == rYbus[node,node]*Wn[node,:] 
							+ rYbus[node,js]*Wre[eidxs,:] + mul_elemwise(direction, iYbus[node,js])*Wie[eidxs,:] )
		constraints.append( imagS[node,:] == -iYbus[node,node]*Wn[node,:] 
						- iYbus[node,js]*Wre[eidxs,:] + mul_elemwise(direction, rYbus[node,js])*Wie[eidxs,:] )

	# SDP constraint
	for e in range(nE):
		for t in range(T):
			constraints.append( quad_over_lin(Wre[e,t], Wn[network.nodeElist0[e],t]) 
				+ quad_over_lin(Wie[e,t], Wn[network.nodeElist0[e],t]) - Wn[network.nodeElist1[e],t] <= 0 )

			# annulus constraint
			#constraints.append( norm(vstack(Wre[e,t], Wie[e,t])) <= network.Vmax2 )

	# enforce substation voltage = 1
	#constraints.append( Wn[network.root,:] == 1 )

	obj = Minimize( sum_entries(mul_elemwise(prices, realS[0,:])) )

	prob = Problem(obj, constraints)

	#data = prob.get_problem_data(MOSEK)
	#data = []

	prob.solve(solver = MOSEK)

	"""
	Solvers: ECOS - failed
	CVXOPT - memory usage intractable
	MOSEK - works well but is commercial
	GUROBI - commercial
	SCS - far from optimal
	"""

	return Q.value, U.value, Wn[network.root,:].value, Wn.value, Wre.value, Wie.value, prob.status

def PF_Sim(ppc, GCtime, pDemand, rDemand, nodesStorage, U, rootV2):
	"""
	Uses PyPower to calculate PF to simulate node voltages after storage control
	Inputs: ppc - PyPower case dictionary
		GCtime - number of time steps between GC runs
		pDemand/rDemand - true values of real and reactive power demanded
		nodesStorage - list of storage nodes indexes
		U - storage control action
		rootV2 - voltage of the substation node
	Outputs: runVoltage - (buses X time) array of voltages
	"""
	nodesNum, T = pDemand.shape
	runVoltage = np.zeros((nodesNum,GCtime))
	S0 = np.zeros((1,GCtime))
	for t in range(GCtime):
		pLoad = pDemand[:,t]
		pLoad[nodesStorage] = pLoad[nodesStorage] + U[:,t]
		rLoad = rDemand[:,t]
		rootVoltage = np.sqrt(rootV2[:,t])
		ppc['bus'][:,2] = pLoad.flatten()
		ppc['bus'][:,3] = rLoad.flatten()
		#ppc['bus'][rootIdx,7] = rootVoltage # Doesnt actually set PF root voltage
		
		#sys.stdout = tempfile.TemporaryFile() # for surpressing runpf output
		ppopt = ppoption(VERBOSE = 0, OUT_ALL = 0)
		ppc_out = runpf(ppc, ppopt)
		#sys.stdout.close()
		#sys.stdout = sys.__stdout__

		rootVdiff = rootVoltage - 1
		runVoltage[:,t] = ppc_out[0]['bus'][:,7] + rootVdiff
		S0[:,t] = ppc_out[0]['gen'][0,1]

	return runVoltage, S0

def PFSOC_Out_All(tnetwork, pricesCurrent, pDemand, rDemand, q0, GCtime, ppc, transLimitTime, transLimit):

	nodesStorage = tnetwork.battnodes

	#Run GC outer loop

	Q, U, rootV2, allV2, Wre, Wie, status = PFSOC(tnetwork, pDemand, rDemand, q0, pricesCurrent, transLimitTime, transLimit)
	if status != 'optimal':
		print 'OPF Status is: ', status

	#Simulate results using PF
	runVoltage , S0= PF_Sim(ppc, GCtime, pDemand, rDemand, nodesStorage, U, rootV2)

	return Q, U, runVoltage, allV2, Wre, Wie, S0


def DemoCase7():

    ## PYPOWER Case Format : Version 2
    ppc = {'version': '2'}

    ##-----  Power Flow Data  -----##
    ## system KVA base
    ppc['baseMVA'] = 1

    ## bus data
    # bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin
    ppc['bus'] = np.array([
        [0, 3, 30, 14.5296631, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [1, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [2, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [3, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [4, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [5, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [6, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
    ])

    ## generator data
    # bus Pg Qg Qmax Qmin Vg mBase status Pmax Pmin Pc1 Pc2 Qc1min Qc1max Qc2min Qc2max ramp_agc ramp_10 ramp_30 ramp_q apf
    ppc['gen'] = np.array([
        [0, 30, 12, 300, -300, 1, 1, 1, 250, -250, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ])

    ## branch data
    # fbus tbus r x b rateA rateB rateC ratio angle status angmin angmax
    ppc['branch'] = np.array([
        [0, 1, 0.00169811011, 0.00529757905, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [0, 2, 0.00443248701, 0.000603189693, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [1, 3, 0.000301594847, 0.000603189693, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [1, 5, 0.000603189693, 0.000203248701, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [3, 4, 0.00140307168, 0.000301594847, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [5, 6, 0.00100295366, 0.000299940992, 0, 250, 250, 250, 0, 0, 1, -360, 360],
    ])

    ##-----  OPF Data  -----##
    ## generator cost data
    # 1 startup shutdown n x1 y1 ... xn yn
    # 2 startup shutdown n c(n-1) ... c0
    ppc['gencost'] = np.array([
        [2, 0, 0, 2, 15, 0],
    ])

    return ppc

class Network(object):
	"""
	Inputs:
	Ybus - dense
	root - index of root node
	battnodes - index of nodes with storage
	qmin, qmax, umin, umax, Vmin, Vmax

	Attributes:
	Ybus with realYbus and imagYbus
	edgelist - list containing tuples of (from to) edges
	nodeNeighbor - dictionary with nodes as key and neighbors as values
	nodeEdge - dictionary with nodes as key and edge index as values
				order is same as neighbors
	nodeDirection = dictionary with direction of edges connected to each node
	battnodes - which nodes are assigned storage
	battInd - boolean vector indicating battnodes
	nbattInd - not battInd
	root
	rootInd - indicator vector of the root node
	nrootInd - not rootInd
	nodeIter - list of nodes to iterate over not including root
	G - networkx graph
	qmin, qmax
	umin, umax
	Vmin2, Vmax2
	nodeElist0/1 - list of from/to nodes in order of edges
	"""

	def __init__(self, Ybus, root, battnodes, qmin, qmax, umin, umax, Vmin, Vmax):

		Ybus = sparse.csc_matrix.todense(Ybus)
		self.realYbus = np.real(Ybus)
		self.imagYbus = np.imag(Ybus)
		self.realYbus = sparse.csr_matrix(self.realYbus)
		self.imagYbus = sparse.csr_matrix(self.imagYbus)
		self.battnodes = battnodes
		
		self.qmin = np.matrix(qmin)
		self.qmax = np.matrix(qmax)
		self.umin = np.matrix(umin)
		self.umax = np.matrix(umax)		
		self.Vmin2 = Vmin**2
		self.Vmax2 = Vmax**2

		n = Ybus.shape[0]
		self.battInd = np.zeros(n)
		self.battInd[self.battnodes] = 1
		self.battInd = self.battInd == 1
		self.nbattInd = np.logical_not(self.battInd)
		# make sure root node is false in both
		self.nbattInd[root] = False

		self.root = root
		self.rootInd = np.zeros(n)
		self.rootInd[root] = 1
		self.rootInd = self.rootInd == 1
		self.nrootInd = np.logical_not(self.rootInd)
		self.nodeIter = range(n)
		del self.nodeIter[root]

		A = Ybus
		A = A - np.diag(np.diag(A))
		A = A != 0
		self.G = nx.from_numpy_matrix(A)
		self.edgelist = self.G.edges()

		self.nodeElist0 = []
		self.nodeElist1 = []
		for e in self.edgelist:
			self.nodeElist0.append(e[0])
			self.nodeElist1.append(e[1])

		self.nodeEdge = {}
		self.nodeNeighbor = {}
		for node in range(n):
			edges = self.G.edges(node)
			edges2 = []
			for tup in edges:
				edges2.append((tup[1], tup[0]))
			self.nodeEdge[node] = []
			self.nodeNeighbor[node] = []
			enumlist = enumerate(self.edgelist)
			for i,x in enumlist:
				if x in edges:
					self.nodeEdge[node].append(i)
					if x[0] == node:
						self.nodeNeighbor[node].append(x[1])
					else:
						self.nodeNeighbor[node].append(x[0])
				elif x in edges2:
					self.nodeEdge[node].append(i)
					if x[0] == node:
						self.nodeNeighbor[node].append(x[1])
					else:
						self.nodeNeighbor[node].append(x[0])

		self.nodeDirection = {}
		for node in range(n):
			direction = self.nodeNeighbor[node] > np.tile(node,len(self.nodeNeighbor[node]))
			direction = np.matrix(direction)
			self.nodeDirection[node] = direction*2 - 1

def DemoAssignStorageSolar(solarReg, solarAlphas, storageAlphas):
	"""
	Assigns storage and solar for purposes of the demo using values from the interface
	Inputs:
		solarReg - time series for each storage node of regularized solar between 0 and 1 for peak value
		solar/storageAlphas - kW of peak capacity solar / kWh of battery (1 building, 4 houses)
	Outputs: sGenFull - full matrix of solar generation for storage nodes
		nodesLoad - list of nodes that have non-zero load
		nodesStorage - list of storage nodes
		qmin, qmax, umin, umax
	"""

	nodesStorage = np.arange(5) + 2
	nodesLoad = nodesStorage
	sGenFull = np.matrix(np.tile(np.reshape(solarAlphas,(5,1)),(1,solarReg.shape[1]))*np.array(solarReg))
	qmin = np.zeros((5,1))
	qmax = np.reshape(storageAlphas,(5,1)) # 14kWh per tesla powerwall
	umax = qmax/3.0
	umin = -umax
	return sGenFull, nodesLoad, nodesStorage, qmin, qmax, umin, umax

def Violation_Process(allVoltage, Vmin, Vmax):
	vGreater = (allVoltage-Vmax).clip(min=0)
	vLess = (Vmin-allVoltage).clip(min=0)
	vio_plus_sum = np.sum(vGreater, axis=1) # bus# X sum of all over voltage violations
	vio_min_sum = np.sum(vLess, axis=1) # bus# X sum of all under voltage violations

	vio_plus_max = np.max(vGreater)
	vio_min_max = np.max(vLess)

	vio_timesbig = (vGreater + vLess) > 0
	vio_times = np.sum(vio_timesbig, axis=1) # bus# X number of times there are violations

	#print 'Maximum over voltage violation: ', vio_plus_max
	#print 'Maximium under voltage violation: ', vio_min_max
	vioTotal = np.sum(vio_min_sum+vio_plus_sum)
	#print 'Sum of all voltage violations magnitude: ', vioTotal
	viosNum = sum(vio_times)
	#print 'Number of voltage violations: ', viosNum
	if viosNum == 0:
		vioAve = 0
	else:
		vioAve = vioTotal/viosNum
	#print 'Average voltage violation magnitude: ', vioAve

	vio_when = np.sum(vio_timesbig, axis=0)

	return vio_times, vio_plus_sum, vio_min_sum, vio_when

def CheckAnnulusRank(Wn, Wre, Wie, network, GCtime):
	edgesNum, T = Wre.shape
	rankCheck = np.zeros((1,GCtime))
	annulusMinCheck = np.zeros((1,GCtime))
	annulusMaxCheck = np.zeros((1,GCtime))
	for t in range(GCtime):
		W = np.zeros((2,2),dtype=np.complex_)
		rank_sum = 0
		annulusMin_sum = 0
		annulusMax_sum = 0
		for e in range(edgesNum):
			W[0,0] = Wn[network.nodeElist0[e],t]
			W[0,1] = Wre[e,t] + 1j*Wie[e,t]
			W[1,0] = Wre[e,t] - 1j*Wie[e,t]
			W[1,1] = Wn[network.nodeElist1[e],t]
			s = np.linalg.svd(W, compute_uv=False)
			s = np.abs(s)
			rank_sum += max(s)/sum(s)
			annulusMin_sum += np.max((network.Vmin2 - np.abs(W[0,1]), 0))/network.Vmin2
			annulusMax_sum += np.max((-network.Vmax2 + np.abs(W[0,1]), 0))/network.Vmax2

		rankCheck[0,t] = rank_sum/edgesNum
		annulusMinCheck[0,t] = 1 - annulusMin_sum/edgesNum
		annulusMaxCheck[0,t] = 1 - annulusMax_sum/edgesNum

	return rankCheck, annulusMinCheck, annulusMaxCheck

def GetYbus(ppc):
	Ybus, j1, j2 = makeYbus(ppc['baseMVA'], ppc['bus'], ppc['branch'])

	return Ybus

def Forecaster(netDemand, rDemand):
	"""
	Make fake forecasts
	"""
	mu = np.hstack(((np.arange(15)+1)/100.0, .2*np.ones(72-15)))*3
	cov = mu/3
	mod = np.random.normal(np.tile(mu, (7,1)), cov)
	sign = np.random.randint(0,1)*2 - 1
	mod = sign*mod
	pForecast = np.array(netDemand) + mod
	rForecast = np.array(rDemand) + mod

	return np.matrix(pForecast), np.matrix(rForecast)

