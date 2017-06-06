"""
Python Module for powernet algorithms

Working Version #1

Dependencies:
	numpy
	cvxpy
	networkx
	mosek
"""

import numpy as np
from cvxpy import *
import networkx as nx

class Network(object):
	"""
	Inputs:
	Ybus
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
		self.Ybus = np.matrix(Ybus)
		self.realYbus = np.real(Ybus)
		self.imagYbus = np.imag(Ybus)
		self.battnodes = battnodes
		
		self.qmin = qmin
		self.qmax = qmax
		self.umin = umin
		self.umax = umax		
		self.Vmin2 = Vmin**2
		self.Vmax2 = Vmax**2

		n = self.Ybus.shape[0]
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

		A = self.Ybus
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


def GC_DSC(network, pDemand, qDemand, q0, prices):
	"""
	DSC controller for cloud coordinator global control
	Inputs: network - Network object
			prices - vector of prices for the times in pDemand
			p/qDemand - dictionary with scenarios 0:scens as keys and matrix (nodes X time) as values
			q0 - initial state of charge vector length number of storage nodes
	Outputs: Q, U, optimization status, cvx data
	"""
	
	n, T = pDemand[0].shape
	scens = len(pDemand)
	nE = len(network.edgelist)
	nS = len(network.battnodes)

	print("dimensions of problem: ",n,T,scens)

	umin = np.tile(network.umin, (1,T))
	umax = np.tile(network.umax, (1,T))
	qmax = np.tile(network.qmax, (1,T+1))
	qmin = np.tile(network.qmin, (1,T+1))
	rYbus = network.realYbus
	iYbus = network.imagYbus
	
	realS = {}
	imagS = {}
	Wre = {}
	Wie = {}
	Wn = {}
	for i in range(scens):
		realS[i] = Variable(n,T)
		imagS[i] = Variable(n,T)
		Wre[i] = Variable(nE,T)
		Wie[i] = Variable(nE,T)
		Wn[i] = Variable(n,T)

	U = Variable(nS,T)
	Q = Variable(nS,T+1)
	S0 = Variable(scens,T)

	# Battery Constraints
	constraints = [Q[:,0] == q0,
				Q[:,1:T+1] == Q[:,0:T] + U,
				U <= umax,
				U >= umin,
				Q <= qmax,
				Q >= qmin
				]

	for i in range(scens):
	
		# Demand and battery action constraints
		constraints.append( realS[i][network.nbattInd,:] == -pDemand[i][network.nbattInd,:] )
		constraints.append( realS[i][network.battnodes,:] == -U - pDemand[i][network.battnodes,:] )
		constraints.append( imagS[i][network.nrootInd,:] == -qDemand[i][network.nrootInd,:] )

		# Voltage Constraints
		constraints.append( Wn[i] <= network.Vmax2 )
		constraints.append( Wn[i] >= network.Vmin2 )

		#Placeholder for objective
		constraints.append( realS[i][0,:] == S0[i,:] )

		# Power Flow constraints
		for node in range(n):			
			eidxs = network.nodeEdge[node]
			js = network.nodeNeighbor[node]
			direction = network.nodeDirection[node]
			constraints.append( realS[i][node,:] == rYbus[node,node]*Wn[i][node,:] 
								+ rYbus[node,js]*Wre[i][eidxs,:] + mul_elemwise(direction, iYbus[node,js])*Wie[i][eidxs,:] )
			constraints.append( imagS[i][node,:] == -iYbus[node,node]*Wn[i][node,:] 
							- iYbus[node,js]*Wre[i][eidxs,:] + mul_elemwise(direction, rYbus[node,js])*Wie[i][eidxs,:] )

		# SDP constraint
		for e in range(nE):
			for t in range(T):
				constraints.append( quad_over_lin(Wre[i][e,t], Wn[i][network.nodeElist0[e],t]) 
					+ quad_over_lin(Wie[i][e,t], Wn[i][network.nodeElist0[e],t]) - Wn[i][network.nodeElist1[e],t] <= 0 )

				# annulus constraint
				constraints.append( norm(vstack(Wre[i][e,t], Wie[i][e,t])) <= network.Vmax2 )

		# enforce substation voltage = 1
		#constraints.append( Wn[i][network.root,:] == 1 )

	obj = Minimize( sum(mul_elemwise(prices, sum_entries(S0, 0)))/scens )

	prob = Problem(obj, constraints)

	#data = prob.get_problem_data(MOSEK)
	#data = []

	prob.solve(solver = MOSEK, verbose=True)

	return Q.value, U.value, prob.status, prob.value