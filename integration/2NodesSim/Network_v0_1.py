"""Network Data
	v0.1 - July 2018
	Thomas Navidi

	This module contains the network object for the global controller algorithms
	Also contains ramp object
"""

import numpy as np
import networkx as nx
from scipy import sparse

class Network(object):
	""" Needs to be updated
	Inputs:
	Ybus - dense later converted to sparse real and imag parts
	root - index of root node
	battnodes - index of nodes with storage
	qmin, qmax, umin, umax, Vmin, Vmax
	Vtol - optional voltage tolerance for voltage soft constraints

	Attributes:
	Ybus with realYbus and imagYbus
	edgelist - list containing tuples of (from to) edges
	nodeNeighbor - dictionary with nodes as key and neighbors as values
	nodeEdge - dictionary with nodes as key and edge index as values
				order is same as neighbors
	nodeDirection = dictionary with direction of edges connected to each node
	battnodes - which nodes are assigned storage
	nbattInd - not boolean vector indicating battnodes
	root
	nrootInd - indicator vector of not rootInd
	qmin, qmax
	umin, umax
	Vmin2, Vmax2
	V2upBound/lowBound - boundary of voltage soft constraint penalty is lower than Vmin2/max2 by Vtol
	nodeElist0/1 - list of from/to nodes in order of edges
	"""

	def __init__(self, storagePen, solarPen, nodesPen, pDemandFull, rDemandFull, pricesFull, root, Ybus, startIdx=0, sNormFull=np.nan, Vmin=0.95, Vmax=1.05, Vtol=0, v_root=1.022, random=True, rampUAll={}):
		# create data arrays for real and reactive power demand and solar generation
		# can also randomly assign solar and storage
		# sNormFull should have maximumm value of 1 to represent a normalized solar curve to be scaled by the solarPen

		self.storagePen=storagePen
		self.solarPen=solarPen
		self.nodesPen=nodesPen
		self.rDemandFull=rDemandFull
		self.pricesFull=pricesFull
		self.root=root
		self.startIdx=startIdx # starting index of data in pDemandFull and others
		self.rampUAll=rampUAll

		if random==True:
			self.netDemandFull, sGenFull, self.battnodes, self.qmin, self.qmax, self.umin, self.umax = self.setStorageSolar(pDemandFull, sNormFull, storagePen, solarPen, nodesPen, root)
			self.makeNetwork(Ybus, root, self.battnodes, self.qmin, self.qmax, self.umin, self.umax, Vmin, Vmax, Vtol, v_root)
		else:
			self.battnodes=np.nan
			self.qmin=np.nan
			self.qmax=np.nan
			self.umin=np.nan
			self.umax=np.nan
			self.Vmin = Vmin
			self.Vmax = Vmax
			self.Vtol = Vtol
			self.v_root = v_root
			print('run Network.inputStorage to finish initialization')


	def inputStorage(self, Ybus, netDemandFull, battnodes, qmin, qmax, umin, umax):
		# Run when inputing your own configuration of storage and solar units

		self.netDemandFull=netDemandFull
		self.battnodes=battnodes
		self.qmin=qmin
		self.qmax=qmax
		self.umin=umin
		self.umax=umax
		
		self.makeNetwork(Ybus, self.root, battnodes, qmin, qmax, umin, umax, self.Vmin, self.Vmax, self.Vtol, self.v_root)


	def makeNetwork(self, Ybus, root, battnodes, qmin, qmax, umin, umax, Vmin, Vmax, Vtol, v_root):
		# matpower 123 case file actually has vmax/min 1.1/.9 and vroot = 1.044

		# make required network variables
		if sparse.issparse(Ybus):
			Ybus = sparse.csc_matrix.todense(Ybus)
		else:
			Ybus = Ybus.todense()

		self.realYbus = np.real(Ybus)
		self.imagYbus = np.imag(Ybus)
		self.realYbus = sparse.csr_matrix(self.realYbus)
		self.imagYbus = sparse.csr_matrix(self.imagYbus)

		self.Vmin2 = Vmin**2
		self.Vmax2 = Vmax**2
		self.V2upBound = (Vmax - Vtol)**2
		self.V2lowBound = (Vmin + Vtol)**2

		n = Ybus.shape[0]
		battInd = np.zeros(n)
		battInd[self.battnodes] = 1
		battInd = battInd == 1
		self.nbattInd = np.logical_not(battInd)
		# make sure root node is false in both
		self.nbattInd[root] = False

		self.root = root
		rootInd = np.zeros(n)
		rootInd[root] = 1
		rootInd = rootInd == 1
		self.nrootInd = np.logical_not(rootInd)

		A = Ybus
		A = A - np.diag(np.diag(A))
		A = A != 0
		G = nx.from_numpy_matrix(A)
		self.edgelist = G.edges()

		self.nodeElist0 = []
		self.nodeElist1 = []
		for e in self.edgelist:
			self.nodeElist0.append(e[0])
			self.nodeElist1.append(e[1])

		self.nodeEdge = {}
		self.nodeNeighbor = {}
		for node in range(n):
			edges = G.edges(node)
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


	def setStorageSolar(self, pDemandFull, sNormFull, storagePen, solarPen, nodesPen, rootIdx):
		"""
		Inputs: pDemandFull - full matrix of real power demanded (nodes X time)
			sNormFull - full matrix of normalized solar data to be scaled and added to power demanded
			storagePen, solarPen, nodesPen - storage, solar, nodes penetration percentages
			rootIdx - index of the root node in the network
		Outputs: netDemandFull - full matrix of real net load
			sGenFull - full matrix of solar generation for storage nodes
			nodesLoad - list of nodes that have non-zero load
			nodesStorage - list of storage nodes
			qmin, qmax, umin, umax
		"""
		# Pick storage nodes
		nodesLoad = np.nonzero(pDemandFull[:,0])[0]
		if pDemandFull[rootIdx,0] > 0:
			nodesLoad = np.delete(nodesLoad, np.argwhere(nodesLoad==rootIdx)) # remove substation node
		nodesStorage = np.random.choice(nodesLoad, int(np.rint(len(nodesLoad)*nodesPen)), replace=False )
		nodesStorage = np.sort(nodesStorage)

		# Assign solar
		loadSNodes = np.mean(pDemandFull[nodesStorage,:], 1)
		rawSolar = solarPen*sum(np.mean(pDemandFull, 1))
		rawStorage = storagePen*24*sum(np.mean(pDemandFull, 1))
		alphas = loadSNodes/sum(loadSNodes)
		netDemandFull = pDemandFull
		sGenFull = np.multiply(np.multiply(rawSolar,alphas),sNormFull)
		netDemandFull[nodesStorage,:] = netDemandFull[nodesStorage,:] - sGenFull

		# Assign storage
		qmax = np.multiply(rawStorage,alphas)
		qmin = np.zeros_like(qmax)
		umax = qmax/3 # it takes 3 hours to fully charge batteries
		umin = -umax

		return netDemandFull, sGenFull, nodesStorage, qmin, qmax, umin, umax

	def makeRampDict(self, rampDataAll, windPen, ramp_tolerance, pForecastFull):
		"""
		Make a dictionary of Ramp objects for each ramp
		Inputs: rampDataAll - matrix with ramps X (start/end time start/end power)
			windPen - wind penetration percent used to calculate ramp amount
			ramp_tolerance - percentage of ramp tolerance
			pForecastFull - full matrix of forecasted demands
		Outputs: rampUAll - dictionary with keys ramp start times and vals Ramp objects
		"""

		rampAmountAll = (rampDataAll[:,3] - rampDataAll[:,2])*windPen

		#print 'Maximum Ramp %: ', max(rampAmountAll)

		# Remove overlapping ramps
		idx = 0
		inds = np.ones(rampDataAll[:,0].shape, dtype=bool)
		for start in rampDataAll[:,0]:
			flag = np.logical_and(np.greater(start, rampDataAll[:,0]), np.less(start, rampDataAll[:,1])).any()
			if flag == True:
				inds[idx] = False # possibly remove self
			idx += 1
		rampDataAll = rampDataAll[inds,:]

		rampUAll = {}
		idx = 0
		for start, end in rampDataAll[:,[0,1]]:
			start = int(start)
			end = int(end)
			timesNew = np.arange(start, end)
			# ramp is linearly increasing to maximum value throughout duration
			U = rampAmountAll[idx]*np.sum(pForecastFull[:,start])*(np.arange(end-start)+1)/(end-start)

			toleranceNew = U*ramp_tolerance
			rampNew = Ramp(timesNew,U,toleranceNew)
			rampUAll[timesNew[0]] = rampNew
			idx += 1

		self.rampUAll = rampUAll
		return rampUAll

	def returnData(self, t_idx, t_period, ids='all'):
		if isinstance(ids, str):
			return self.netDemandFull[:,(t_idx+self.startIdx):(t_idx + t_period + self.startIdx)], \
			self.rDemandFull[:,(t_idx+self.startIdx):(t_idx + t_period + self.startIdx)], \
			self.pricesFull[:,(t_idx+self.startIdx):(t_idx + t_period + self.startIdx)]
		else:
			return self.netDemandFull[ids,(t_idx+self.startIdx):(t_idx + t_period + self.startIdx)], \
			self.rDemandFull[ids,(t_idx+self.startIdx):(t_idx + t_period + self.startIdx)], \
			self.pricesFull[:,(t_idx+self.startIdx):(t_idx + t_period + self.startIdx)]


class Ramp(object):
	"""
	Ramp object with data to characterize ramp
	Inputs: arrays of times, magnitude of ramp, and tolerance profiles
	Attributes:U - charge profile for ramp
			tolerance - allowed ramp deviation
			times - list of time indices for the ramp
	"""
	def __init__(self, rampTimes, rampMags, rampTolerances):
		self.times = rampTimes
		self.tolerance = rampTolerances
		self.mag = rampMags

def make_ramp_dict(rampDataAll, windPen, ramp_tolerance, pForecastFull):
	"""
	Make a dictionary of Ramp objects for each ramp
	Inputs: rampDataAll - matrix with ramps X (start/end time start/end power)
		windPen - wind penetration percent used to calculate ramp amount
		ramp_tolerance - percentage of ramp tolerance
		GCtime - time period of GC
		GCstepsTotal - total number of GC steps taken in simulation
		pForecastFull - full matrix of forecasted demands
	Outputs: rampUAll - dictionary with keys ramp start times and vals Ramp objects
	"""

	rampAmountAll = (rampDataAll[:,3] - rampDataAll[:,2])*windPen

	print 'Maximum Ramp %: ', max(rampAmountAll)

	# Remove overlapping ramps
	if rampDataAll.shape[0] > 1:
		idx = 0
		inds = np.ones(rampDataAll[:,0].shape, dtype=bool)
		for start in rampDataAll[:,0]:
			flag = np.logical_and(np.greater(start, rampDataAll[:,0]), np.less(start, rampDataAll[:,1])).any()
			if flag == True:
				inds[idx] = False # possibly remove self
			idx += 1
		rampDataAll = rampDataAll[inds,:]

		rampUAll = {}
		idx = 0
		for start, end in rampDataAll[:,[0,1]]:
			start = int(start)
			end = int(end)
			timesNew = np.arange(start, end)
			# ramp is linearly increasing to maximum value throughout duration
			U = rampAmountAll[idx]*np.sum(pForecastFull[:,start])*(np.arange(end-start)+1)/(end-start)

			toleranceNew = U*ramp_tolerance
			rampNew = Ramp(timesNew,U,toleranceNew)
			rampUAll[timesNew[0]] = rampNew
			idx += 1
	else:
		rampUAll = {}
		start = int(rampDataAll[0,0])
		end = int(rampDataAll[0,1])
		timesNew = np.arange(start, end)
		# ramp is linearly increasing to maximum value throughout duration
		U = np.array(rampAmountAll*np.sum(pForecastFull[:,start])*(np.arange(end-start)+1)/(end-start))
		U = U.flatten()
		toleranceNew = U*ramp_tolerance
		rampNew = Ramp(timesNew,U,toleranceNew)
		rampUAll[timesNew[0]] = rampNew

	return rampUAll

