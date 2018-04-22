"""
Python module for Data Pre processing
Dependencies:
    numpy
    networkx
    scipy
"""

import numpy as np
import networkx as nx
from scipy import sparse
# import matplotlib.pyplot as plt
from pypower.api import makeYbus


def case47():
    if np.version.version == '1.12.1':
        datatype = float
    else:
        datatype = float

    ## PYPOWER Case Format : Version 2
    ppc = {'version': '2'}

    ##-----  Power Flow Data  -----##
    ## system MVA base
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
        [7, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [8, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [9, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [10, 1, 0.67, 0.32449581, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [11, 1, 0.45, 0.217944947, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [12, 1, 0.89, 0.431046673, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [13, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [14, 1, 0.07, 0.0339025473, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [15, 1, 0.67, 0.32449581, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [16, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [17, 1, 0.45, 0.217944947, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [18, 1, 2.23, 1.08003829, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [19, 1, 0.45, 0.217944947, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [20, 1, 0.2, 0.096864421, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [21, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [22, 1, 0.13, 0.0629618736, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [23, 1, 0.13, 0.0629618736, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [24, 1, 0.2, 0.096864421, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [25, 1, 0.07, 0.0339025473, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [26, 1, 0.13, 0.0629618736, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [27, 1, 0.27, 0.130766968, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [28, 1, 0.2, 0.096864421, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [29, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [30, 1, 0.27, 0.130766968, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [31, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [32, 1, 0.45, 0.217944947, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [33, 1, 1.34, 0.64899162, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [34, 1, 0.13, 0.0629618736, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [35, 1, 0.67, 0.32449581, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [36, 1, 0.13, 0.0629618736, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [37, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [38, 1, 0.45, 0.217944947, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [39, 1, 0.2, 0.096864421, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [40, 1, 0.45, 0.217944947, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
        [41, 1, 0, 0, 0, 0, 1, 1, 0, 12.35, 1, 1.05, 0.95],
    ], dtype=datatype)

    ## generator data
    # bus Pg Qg Qmax Qmin Vg mBase status Pmax Pmin Pc1 Pc2 Qc1min Qc1max Qc2min Qc2max ramp_agc ramp_10 ramp_30 ramp_q apf
    ppc['gen'] = np.array([
        [0, 30, 12, 300, -300, 1, 1, 1, 250, -250, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ], dtype=datatype)

    ## branch data
    # fbus tbus r x b rateA rateB rateC ratio angle status angmin angmax
    ppc['branch'] = np.array([
        [0, 1, 0.00169811011, 0.00529757905, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [1, 2, 0.000203248701, 0.000603189693, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [2, 3, 0.000301594847, 0.000603189693, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [2, 12, 0.000603189693, 0.000203248701, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [2, 13, 0.00140307168, 0.000301594847, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [3, 16, 0.00220295366, 0.000399940992, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [3, 4, 0.000701535839, 0.00119982298, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [4, 20, 0.000399940992, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [4, 5, 9.83461457e-05, 0.000203248701, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [5, 21, 0.00110147683, 0.000399940992, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [5, 6, 0.000203248701, 0.000301594847, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [6, 26, 0.000498287138, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [6, 7, 9.83461457e-05, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [7, 34, 0.000301594847, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [7, 33, 0.00159976397, 0.000301594847, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [7, 35, 0.000701535839, 0.000203248701, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [7, 29, 0.000498287138, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [7, 8, 0.000203248701, 0.000203248701, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [8, 9, 9.83461457e-05, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [8, 36, 0.00100313069, 0.000301594847, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [9, 10, 0.000701535839, 0.000498287138, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [9, 40, 0.00150141782, 0.000799881985, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [10, 41, 0.000203248701, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [10, 11, 0.000498287138, 0.000301594847, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [13, 15, 0.000301594847, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [13, 14, 0.000701535839, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [16, 17, 0.000799881985, 0.000603189693, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [16, 19, 0.00140307168, 0.000301594847, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [17, 18, 0.00129816912, 0.000301594847, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [21, 25, 0.000301594847, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [21, 22, 0.000701535839, 0.000203248701, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [22, 23, 0.000701535839, 0.000203248701, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [23, 24, 0.000399940992, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [26, 27, 0.000301594847, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [27, 28, 0.000203248701, 6.55640971e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [29, 30, 0.000498287138, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [29, 31, 0.000498287138, 0.000301594847, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [29, 32, 0.000701535839, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [36, 37, 0.000399940992, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [37, 38, 0.000399940992, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [37, 39, 0.000399940992, 9.83461457e-05, 0, 250, 250, 250, 0, 0, 1, -360, 360],
    ], dtype=datatype)

    ##-----  OPF Data  -----##
    ## generator cost data
    # 1 startup shutdown n x1 y1 ... xn yn
    # 2 startup shutdown n c(n-1) ... c0
    ppc['gencost'] = np.array([
        [2, 0, 0, 2, 15, 0],
    ], dtype=datatype)

    return ppc


class Network(object):
    """
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

    def __init__(self, Ybus, root, battnodes, qmin, qmax, umin, umax, Vmin, Vmax, Vtol=0):
        Ybus = sparse.csc_matrix.todense(Ybus)
        self.realYbus = np.real(Ybus)
        self.imagYbus = np.imag(Ybus)
        self.realYbus = sparse.csr_matrix(self.realYbus)
        self.imagYbus = sparse.csr_matrix(self.imagYbus)
        self.battnodes = battnodes

        self.qmin = qmin
        self.qmax = qmax
        self.umin = umin
        self.umax = umax
        self.Vmin2 = Vmin ** 2
        self.Vmax2 = Vmax ** 2
        self.V2upBound = (Vmax - Vtol) ** 2
        self.V2lowBound = (Vmin + Vtol) ** 2

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
            for i, x in enumlist:
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
            direction = self.nodeNeighbor[node] > np.tile(node, len(self.nodeNeighbor[node]))
            direction = np.matrix(direction)
            self.nodeDirection[node] = direction * 2 - 1


def setStorageSolar(pDemandFull, sNormFull, storagePen, solarPen, nodesPen, rootIdx):
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
    nodesLoad = np.nonzero(pDemandFull[:, 0])[0]
    if pDemandFull[rootIdx, 0] > 0:
        nodesLoad = np.delete(nodesLoad, np.argwhere(nodesLoad == rootIdx))  # remove substation node
    nodesStorage = np.random.choice(nodesLoad, int(np.rint(len(nodesLoad) * nodesPen)), replace=False)
    nodesStorage = np.sort(nodesStorage)

    # Assign solar
    loadSNodes = np.mean(pDemandFull[nodesStorage, :], 1)
    rawSolar = solarPen * sum(np.mean(pDemandFull, 1))
    rawStorage = storagePen * 24 * sum(np.mean(pDemandFull, 1))
    alphas = loadSNodes / sum(loadSNodes)
    netDemandFull = pDemandFull
    sGenFull = np.multiply(np.multiply(rawSolar, alphas), sNormFull)
    netDemandFull[nodesStorage, :] = netDemandFull[nodesStorage, :] - sGenFull

    # Assign storage
    qmax = np.multiply(rawStorage, alphas)
    qmin = np.zeros_like(qmax)
    umax = qmax / 3  # it takes 3 hours to fully charge batteries
    umin = -umax

    return netDemandFull, sGenFull, nodesLoad, nodesStorage, qmin, qmax, umin, umax


def Violation_Process(allVoltage, Vmin, Vmax):
    vGreater = (allVoltage - Vmax).clip(min=0)
    vLess = (Vmin - allVoltage).clip(min=0)
    vio_plus_sum = np.sum(vGreater, axis=1)  # bus# X sum of all over voltage violations
    vio_min_sum = np.sum(vLess, axis=1)  # bus# X sum of all under voltage violations

    vio_plus_max = np.max(vGreater)
    vio_min_max = np.max(vLess)

    vio_timesbig = (vGreater + vLess) > 0
    vio_times = np.sum(vio_timesbig, axis=1)  # bus# X number of times there are violations

    print 'Maximum over voltage violation: ', vio_plus_max
    print 'Maximium under voltage violation: ', vio_min_max
    vioTotal = np.sum(vio_min_sum + vio_plus_sum)
    print 'Sum of all voltage violations magnitude: ', vioTotal
    viosNum = sum(vio_times)
    print 'Number of voltage violations: ', viosNum
    vioAve = vioTotal / viosNum
    print 'Average voltage violation magnitude: ', vioAve

    vio_when = np.sum(vio_timesbig, axis=0)

    return vio_times, vio_plus_sum, vio_min_sum, vio_when


def CheckAnnulusRank(Wn, Wre, Wie, network, GCtime):
    edgesNum, T = Wre.shape
    rankCheck = np.zeros((1, GCtime))
    annulusMinCheck = np.zeros((1, GCtime))
    annulusMaxCheck = np.zeros((1, GCtime))
    for t in range(GCtime):
        W = np.zeros((2, 2), dtype=np.complex_)
        rank_sum = 0
        annulusMin_sum = 0
        annulusMax_sum = 0
        for e in range(edgesNum):
            W[0, 0] = Wn[network.nodeElist0[e], t]
            W[0, 1] = Wre[e, t] + 1j * Wie[e, t]
            W[1, 0] = Wre[e, t] - 1j * Wie[e, t]
            W[1, 1] = Wn[network.nodeElist1[e], t]
            s = np.linalg.svd(W, compute_uv=False)
            s = np.abs(s)
            rank_sum += max(s) / sum(s)
            annulusMin_sum += np.max((network.Vmin2 - np.abs(W[0, 1]), 0)) / network.Vmin2
            annulusMax_sum += np.max((-network.Vmax2 + np.abs(W[0, 1]), 0)) / network.Vmax2

        rankCheck[0, t] = rank_sum / edgesNum
        annulusMinCheck[0, t] = 1 - annulusMin_sum / edgesNum
        annulusMaxCheck[0, t] = 1 - annulusMax_sum / edgesNum

    return rankCheck, annulusMinCheck, annulusMaxCheck


def GetYbus(ppc):
    Ybus, j1, j2 = makeYbus(ppc['baseMVA'], ppc['bus'], ppc['branch'])

    return Ybus


def Forecaster(netDemand, rDemand):
    """
    Make fake forecasts
    """
    mu = np.hstack(((np.arange(15) + 1) / 100.0, .2 * np.ones(72 - 15))) * np.mean(netDemand) / 2
    cov = np.abs(mu) / 3
    mod = np.random.normal(np.tile(mu, (netDemand.shape[0], 1)), cov)
    sign = np.random.randint(2) * 2 - 1
    mod = sign * mod
    pForecast = np.array(netDemand) + mod[:, 0:netDemand.shape[1]]
    rForecast = np.array(rDemand) + mod[:, 0:netDemand.shape[1]]

    return np.matrix(pForecast), np.matrix(rForecast)
