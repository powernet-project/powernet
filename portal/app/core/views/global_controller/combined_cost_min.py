"""
Python Module for NSC cost minimization controller

Dependencies:
	numpy
	cvxpy
	mosek
	pypower
	multiprocessing
	itertools
"""

import numpy as np
from cvxpy import *
from pypower.api import runpf, ppoption
import time
from multiprocessing import Pool
import itertools


def ScenarioGenGC(battnodes, pForecast, pMeans, pCovs, scens):
    """
    Inputs: battnodes - nodes with storage
        pForecast - real power forecast for only storage nodes
        pMeans/Covs - dictionaries of real power mean vector and covariance matrices
                        keys are 'b node#' values are arrays
        scens - number of scenarios to generate
    Outputs: sScenarios - dictionary with keys scens and vals (nS X time)
    """
    nS, T = pForecast.shape
    sScenarios = {}
    for j in range(scens):
        counter = 0
        tmpArray = np.zeros((nS, T))
        for i in battnodes:
            resi = np.random.multivariate_normal(pMeans['b' + str(i + 1)], pCovs['b' + str(i + 1)])
            tmpArray[counter, :] = pForecast[counter, :] + resi[0:T]
            counter += 1
        sScenarios[j] = tmpArray

    return sScenarios


def ScenarioGen(battnodes, pForecast, pMeans, pCovs, scens):
    """
    Inputs: battnodes - nodes with storage
        pForecast - real power forecast for only storage nodes
        pMeans/Covs - dictionaries of real power mean vector and covariance matrices
                        keys are 'b node#' values are arrays
        scens - number of scenarios to generate
    Outputs: sScenarios - dictionary with keys scens and vals (nS X time)
    """
    nS, T = pForecast.shape
    sScenarios = {}
    for j in range(scens):
        counter = 0
        tmpArray = np.zeros((nS, T))
        for i in battnodes:
            resi = np.random.multivariate_normal(pMeans['b' + str(i + 1)], pCovs['b' + str(i + 1)])
            tmpArray[counter, :] = pForecast[counter, :] + resi[0:T]
            counter += 1
        sScenarios[j] = tmpArray

    return sScenarios


def GC_NLFC_Out(network, sScenarios, pDemand, qDemand, q0, prices, sellFactor, scens, pool, V_weight):
    """
    Outer loop for the NLFC controller. Takes average of all scenarios.
    Inputs: network - Network object
            prices - vector of prices for the times in pDemand
            sScenarios - dictionary of np matrix (storage nodes X time) as value and scen as key
            p/qDemand - forecast of p/q for all nodes
            q0 - initial state of charge vector length number of storage nodes
    Outputs: realS and imagS for all storage nodes
    """

    n, T = pDemand.shape
    nS = len(network.battnodes)
    nE = len(network.nodeElist0)
    realS_sum = np.matrix(np.zeros((nS, T)))
    rootV2_sum = np.matrix(np.zeros((1, T)))
    Wn_sum = np.matrix(np.zeros((n, T)))
    Wre_sum = np.matrix(np.zeros((nE, T)))
    Wie_sum = np.matrix(np.zeros((nE, T)))

    ## Compute in parallel
    # Gather all scenarios data into a list
    demandList = []
    for i in range(scens):
        combDemand = pDemand
        combDemand[network.battnodes, :] = sScenarios[i]
        demandList.append(combDemand)

    # Make parallel pool
    # if __name__== "__main__":
    # print('start parallel pool')
    # pool = Pool()
    print 'Computing in pool'
    sols = pool.map(GC_NLFC_star, itertools.izip(itertools.repeat(network), demandList, itertools.repeat(qDemand),
                                                 itertools.repeat(q0), itertools.repeat(prices),
                                                 itertools.repeat(sellFactor), itertools.repeat(V_weight)))

    # Unpack all information
    for i in range(scens):
        if sols[i][2] != "optimal":
            print 'OPF status is: ', sols[i][2]
        realS_sum += sols[i][0]
        rootV2_sum += sols[i][1]
        Wn_sum += sols[i][3]
        Wre_sum += sols[i][4]
        Wie_sum += sols[i][5]

    realS = realS_sum / scens
    rootV2 = rootV2_sum / scens
    Wn = Wn_sum / scens
    Wre = Wre_sum / scens
    Wie = Wie_sum / scens

    return realS, rootV2, Wn, Wre, Wie

    """
    #Sequential code
    for i in range(scens):
        combDemand = pDemand
        combDemand[network.battnodes,:] = sScenarios[i]
        realS_new, imagS_new, rootV2_new, status, cost = GC_NLFC(network, combDemand, qDemand, q0, prices)
        realS_sum = realS_sum + realS_new
        rootV2_sum = rootV2_sum + rootV2_new
        if status != "optimal":
            print('status is: ', status)
    """


def GC_NLFC_star(allargs):
    """Unpack all the arguments packed up for parallel processing"""
    return GC_NLFC(*allargs)


def GC_NLFC(network, pDemand, qDemand, q0, prices, sellFactor, V_weight):
    """
    NLFC controller for cloud coordinator global control
    Inputs: network - Network object
            prices - vector of prices for the times in pDemand
            p/qDemand - np matrix (nodes X time) as values
            q0 - initial state of charge vector length number of storage nodes
    Outputs: realS, imagS, optimization status
    """

    n, T = pDemand.shape
    nE = len(network.edgelist)
    nS = len(network.battnodes)

    # print("dimensions of problem: ",n,T)

    if np.any(np.less(q0, network.qmin)):  # Correct for computational inaccuracies
        q0 += .00001
        print 'q0 too low'
    elif np.any(np.greater(q0, network.qmax)):
        q0 += -.00001
        print 'q0 too high'

    umin = np.tile(network.umin, (1, T))
    umax = np.tile(network.umax, (1, T))
    qmax = np.tile(network.qmax, (1, T + 1))
    qmin = np.tile(network.qmin, (1, T + 1))
    rYbus = network.realYbus
    iYbus = network.imagYbus

    realS = Variable(n, T)
    imagS = Variable(n, T)
    Wre = Variable(nE, T)
    Wie = Variable(nE, T)
    Wn = Variable(n, T)

    U = Variable(nS, T)
    Q = Variable(nS, T + 1)

    # Battery Constraints
    constraints = [Q[:, 0] == q0,
                   Q[:, 1:T + 1] == Q[:, 0:T] + U,
                   U <= umax,
                   U >= umin,
                   Q <= qmax,
                   Q >= qmin
                   ]

    # Demand and battery action constraints
    constraints.append(realS[network.nbattInd, :] == -pDemand[network.nbattInd, :])
    constraints.append(realS[network.battnodes, :] == -U - pDemand[network.battnodes, :])
    constraints.append(imagS[network.nrootInd, :] == -qDemand[network.nrootInd, :])

    # Voltage Constraints
    # constraints.append( Wn <= network.Vmax2 )
    # constraints.append( Wn >= network.Vmin2 )

    # Power Flow constraints
    for node in range(n):
        eidxs = network.nodeEdge[node]
        js = network.nodeNeighbor[node]
        direction = network.nodeDirection[node]
        constraints.append(realS[node, :] == rYbus[node, node] * Wn[node, :]
                           + rYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, iYbus[node, js]) * Wie[eidxs, :])
        constraints.append(imagS[node, :] == -iYbus[node, node] * Wn[node, :]
                           - iYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, rYbus[node, js]) * Wie[eidxs, :])

    # SDP constraint
    for e in range(nE):
        for t in range(T):
            constraints.append(quad_over_lin(Wre[e, t], Wn[network.nodeElist0[e], t])
                               + quad_over_lin(Wie[e, t], Wn[network.nodeElist0[e], t]) - Wn[
                                   network.nodeElist1[e], t] <= 0)

        # annulus constraint
        # constraints.append( norm(vstack(Wre[e,t], Wie[e,t])) <= network.Vmax2 )

    # enforce substation voltage = 1
    # constraints.append( Wn[network.root,:] == 1 )

    if sellFactor == 0:
        prices = np.tile(prices, (nS, 1))
        obj = Minimize(sum_entries(mul_elemwise(prices, neg(realS[network.battnodes, :])))
                       + V_weight * sum_entries(
            square(pos(Wn - network.V2upBound)) + square(pos(network.V2lowBound - Wn))))
    else:
        obj = Minimize(sum_entries(mul_elemwise(prices, realS[0, :]))
                       + V_weight * sum_entries(
            square(pos(Wn - network.V2upBound)) + square(pos(network.V2lowBound - Wn))))
    if sellFactor == 2:
        constraints.append(realS[0, :] >= 0)  # substation cannot sell
    if sellFactor == 3:
        constraints.append(realS[network.battnodes, :] <= 0)  # nodes cannot sell

    prob = Problem(obj, constraints)

    # data = prob.get_problem_data(MOSEK)
    # data = []

    prob.solve(solver=MOSEK)

    """
    Solvers: ECOS - failed
    CVXOPT - memory usage intractable
    MOSEK - works well but is commercial
    GUROBI - commercial
    SCS - far from optimal
    """

    return realS[network.battnodes, :].value, Wn[network.root, :].value, prob.status, Wn.value, Wre.value, Wie.value


def LC_Combined(LowBounds, UpBounds, realS, NLweight, prices, sellFactor, q0, LCscens, GCtime, pre_pDemands, umaxo,
                umino, qmaxo, qmino, battnodes, pMeans, pCovs):
    """
    NLFC Local controller
    Inputs: realS - real net power from GC for only storage notes
    q0 - initial state of charge
    LCscens - number of local scenarios
    GCtime - time between GC steps
    pre_pDemands - previous time real power of storage nodes used for local forecasts
    umaxo, umino, qmaxo, qmino
    Outputs: Qfinal, Ufinal
    """

    nS, T = LowBounds.shape
    Qfinal = np.matrix(np.zeros((nS, GCtime + 1)))
    Ufinal = np.matrix(np.zeros((nS, GCtime)))
    boundsFlag = np.zeros((1, GCtime))
    Qfinal[:, 0] = q0[:, 0]

    for t in range(GCtime):
        # Resize parameters to match new time
        umin = np.tile(umino, (1, T - t))
        umax = np.tile(umaxo, (1, T - t))
        qmax = np.tile(qmaxo, (1, T - t + 1))
        qmin = np.tile(qmino, (1, T - t + 1))
        pricesCurrent = np.tile(prices[:, t:], (nS, LCscens))
        LowBoundsCurr = LowBounds[:, t:]
        UpBoundsCurr = UpBounds[:, t:]

        # generate local forecasts
        # LCforecast = forecaster then LCforecasts = scenario gen from forecast
        LCforecasts = ScenarioGen(battnodes, pre_pDemands[:, t:], pMeans, pCovs, LCscens)

        # initialize variables
        Y = Variable(nS, (T - t) * LCscens)
        U = Variable(nS, T - t)
        Q = Variable(nS, T - t + 1)

        # Battery Constraints
        constraints = [Q[:, 0] == q0,
                       Q[:, 1:T - t + 1] == Q[:, 0:T - t] + U,
                       U <= umax,
                       U >= umin,
                       Q <= qmax,
                       Q >= qmin
                       ]

        for i in range(LCscens):
            # Demand and battery action constraints
            constraints.append(Y[:, (i * (T - t)):((i + 1) * (T - t))] == -LCforecasts[i] - U)

            # Bounds Constraints
            constraints.append(Y[:, (i * (T - t)):((i + 1) * (T - t))] >= LowBoundsCurr)
            constraints.append(Y[:, (i * (T - t)):((i + 1) * (T - t))] <= UpBoundsCurr)

        if sellFactor == 0:
            obj = Minimize(sum_entries(mul_elemwise(pricesCurrent, neg(Y))) + NLweight * norm(
                Y - np.tile(realS[:, t:], (1, LCscens)), 'fro'))
        else:
            obj = Minimize(
                sum_entries(mul_elemwise(pricesCurrent, -Y)) + NLweight * norm(Y - np.tile(realS[:, t:], (1, LCscens)),
                                                                               'fro'))
        if sellFactor == 3:
            constraints.append(Y <= 0)  # nodes cannot sell

        prob = Problem(obj, constraints)

        # data = prob.get_problem_data(MOSEK)
        # data = []

        prob.solve(solver=MOSEK)

        # Store values
        if prob.status != "optimal":
            print 'LC status is: ', prob.status
        Qfinal[:, t + 1] = Q[:, 1].value
        q0 = Q[:, 1].value
        if np.any(np.less(q0, qmino)):  # Correct for computational inaccuracies
            q0 += .00001
        elif np.any(np.greater(q0, qmaxo)):
            q0 += -.00001
        Ufinal[:, t] = U[:, 0].value
        LowBoundsRep = np.tile(LowBoundsCurr, (1, LCscens))
        UpBoundsRep = np.tile(UpBoundsCurr, (1, LCscens))

        if np.any(np.greater(Y.value, UpBoundsRep - .0001)):
            print 'LC Upper Bound Reached'
            boundsFlag[:, t] = 1
        if np.any(np.less(Y.value, LowBoundsRep + .0001)):
            print 'LC Lower Bound Reached'
            boundsFlag[:, t] = 1

    return Qfinal, Ufinal, boundsFlag


def LC_Combined_No_Bounds(realS, NLweight, prices, sellFactor, q0, LCscens, GCtime, pre_pDemands, umaxo, umino, qmaxo,
                          qmino, battnodes, pMeans, pCovs):
    """
    NLFC Local controller
    Inputs: realS - real net power from GC for only storage notes
    NLWeight - net load following weight in objective
    sellFactor - 1 for selling 0 for selling not profitable
    q0 - initial state of charge
    LCscens - number of local scenarios
    GCtime - time between GC steps
    pre_pDemands - previous time real power of storage nodes used for local forecasts or dictionary of scenarios
    umaxo, umino, qmaxo, qmino
    Outputs: Qfinal, Ufinal
    """

    nS, T = realS.shape
    Qfinal = np.matrix(np.zeros((nS, GCtime + 1)))
    Ufinal = np.matrix(np.zeros((nS, GCtime)))
    boundsFlag = np.zeros((1, GCtime))
    Qfinal[:, 0] = q0[:, 0]

    for t in range(GCtime):
        # Resize parameters to match new time
        umin = np.tile(umino, (1, T - t))
        umax = np.tile(umaxo, (1, T - t))
        qmax = np.tile(qmaxo, (1, T - t + 1))
        qmin = np.tile(qmino, (1, T - t + 1))
        pricesCurrent = np.tile(prices[:, t:], (nS, LCscens))

        # generate local forecasts
        # LCforecast = forecaster then LCforecasts = scenario gen from forecast
        if pre_pDemands is dict:
            LCforecasts = pre_pDemands
        else:
            LCforecasts = ScenarioGen(battnodes, pre_pDemands[:, t:], pMeans, pCovs, LCscens)

        # initialize variables
        Y = Variable(nS, (T - t) * LCscens)
        U = Variable(nS, T - t)
        Q = Variable(nS, T - t + 1)

        # Battery Constraints
        constraints = [Q[:, 0] == q0,
                       Q[:, 1:T - t + 1] == Q[:, 0:T - t] + U,
                       U <= umax,
                       U >= umin,
                       Q <= qmax,
                       Q >= qmin
                       ]

        for i in range(LCscens):
            # Demand and battery action constraints
            constraints.append(Y[:, (i * (T - t)):((i + 1) * (T - t))] == -LCforecasts[i] - U)

        if sellFactor == 0:
            obj = Minimize(sum_entries(mul_elemwise(pricesCurrent, neg(Y))) + NLweight * norm(
                Y - np.tile(realS[:, t:], (1, LCscens)), 'fro'))
        else:
            obj = Minimize(
                sum_entries(mul_elemwise(pricesCurrent, -Y)) + NLweight * norm(Y - np.tile(realS[:, t:], (1, LCscens)),
                                                                               'fro'))
        if sellFactor == 3:
            constraints.append(Y <= 0)  # nodes cannot sell

        prob = Problem(obj, constraints)

        # data = prob.get_problem_data(MOSEK)
        # data = []

        prob.solve(solver=MOSEK)

        # Store values
        if prob.status != "optimal":
            print 'LC status is: ', prob.status
        Qfinal[:, t + 1] = Q[:, 1].value
        q0 = Q[:, 1].value
        if np.any(np.less(q0, qmino)):  # Correct for computational inaccuracies
            q0 += .00001
        elif np.any(np.greater(q0, qmaxo)):
            q0 += -.00001
        Ufinal[:, t] = U[:, 0].value

    return Qfinal, Ufinal, boundsFlag


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
    runVoltage = np.zeros((nodesNum, GCtime))
    for t in range(GCtime):
        pLoad = pDemand[:, t]
        pLoad[nodesStorage] = pLoad[nodesStorage] + U[:, t]
        rLoad = rDemand[:, t]
        rootVoltage = np.sqrt(rootV2[:, t])
        ppc['bus'][:, 2] = pLoad.flatten()
        ppc['bus'][:, 3] = rLoad.flatten()
        # ppc['bus'][rootIdx,7] = rootVoltage # Doesnt actually set PF root voltage

        # for surpressing runpf output
        ppopt = ppoption(VERBOSE=0, OUT_ALL=0)
        ppc_out = runpf(ppc, ppopt)

        rootVdiff = rootVoltage - 1
        runVoltage[:, t] = ppc_out[0]['bus'][:, 7] + rootVdiff

    return runVoltage


def NSC_Bounds_Out(network, pDemand, qDemand, Sload, pool, V_weight):
    """
    Outer loop for running NSC Bounds in parallel
    Inputs: network - Network object
            p/qDemand - np matrix (nodes X time) as values
            tNode - target node for finding bounds, in range 0:NS
            Sload - net load for other storage nodes
            obj_sign - + for minimize, - for maximize
    Outputs: LowBounds, UpBounds
    """
    n, T = pDemand.shape
    nS = len(network.battnodes)
    UpBounds = np.matrix(np.zeros((nS, T)))
    LowBounds = np.matrix(np.zeros((nS, T)))
    WnDict = {}
    WreDict = {}
    WieDict = {}

    ## Compute in parallel
    # Gather all data into lists
    tNodes = []
    obj_sign = []
    for i in range(nS):
        tNodes.append(i)
        obj_sign.append(1)
    for i in range(nS):
        tNodes.append(i)
        obj_sign.append(-1)

    # Make parallel pool
    # if __name__== "__main__":
    # print('start parallel pool')
    # pool = Pool()
    print 'Computing in pool'
    sols = pool.map(NSC_Bounds_star,
                    itertools.izip(itertools.repeat(network), itertools.repeat(pDemand), itertools.repeat(qDemand),
                                   tNodes, itertools.repeat(Sload), obj_sign, itertools.repeat(V_weight)))

    # Unpack all information
    for i in range(nS):
        LowBounds[i, :] = sols[i][0]
        if sols[i][1] != "optimal":
            print 'OPF status is: ', sols[i][1]
        WnDict[i] = sols[i][2]
        WreDict[i] = sols[i][3]
        WieDict[i] = sols[i][4]
    for i in range(nS):
        UpBounds[i, :] = sols[i + nS][0]
        if sols[i + nS][1] != "optimal":
            print 'OPF status is: ', sols[i + nS][1]
        WnDict[i + nS] = sols[i + nS][2]
        WreDict[i + nS] = sols[i + nS][3]
        WieDict[i + nS] = sols[i + nS][4]

    return LowBounds, UpBounds, WnDict, WreDict, WieDict


def NSC_Bounds_star(allargs):
    """Unpack all the arguments packed up for parallel processing"""
    return NSC_Bounds(*allargs)


def NSC_Bounds(network, pDemand, qDemand, tNode, Sload, obj_sign, V_weight):
    """
    NSC bound calculator for cloud coordinator global control
    Inputs: network - Network object
            p/qDemand - np matrix (nodes X time) as values
            tNode - target node for finding bounds, in range 0:NS
            Sload - net load for other storage nodes
            obj_sign - + for minimize, - for maximize
    Outputs: realS, optimization status
    """

    n, T = pDemand.shape
    nE = len(network.edgelist)
    nS = len(network.battnodes)

    # print("dimensions of problem: ",n,T)

    rYbus = network.realYbus
    iYbus = network.imagYbus

    realS = Variable(n, T)
    imagS = Variable(n, T)
    Wre = Variable(nE, T)
    Wie = Variable(nE, T)
    Wn = Variable(n, T)

    battnodes = network.battnodes
    battnodes = battnodes[np.arange(nS) != tNode]  # Remove the target node from list of nodes
    Sload = Sload[np.arange(nS) != tNode, :]  # Remove target node from list of net loads

    # Constraints
    constraints = []

    # Demand and battery action constraints
    constraints.append(realS[network.nbattInd, :] == -pDemand[network.nbattInd, :])
    constraints.append(realS[battnodes, :] == Sload)
    constraints.append(imagS[network.nrootInd, :] == -qDemand[network.nrootInd, :])

    # Voltage Constraints
    # constraints.append( Wn <= network.Vmax2 )
    # constraints.append( Wn >= network.Vmin2 )

    # Power Flow constraints
    for node in range(n):
        eidxs = network.nodeEdge[node]
        js = network.nodeNeighbor[node]
        direction = network.nodeDirection[node]
        constraints.append(realS[node, :] == rYbus[node, node] * Wn[node, :]
                           + rYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, iYbus[node, js]) * Wie[eidxs, :])
        constraints.append(imagS[node, :] == -iYbus[node, node] * Wn[node, :]
                           - iYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, rYbus[node, js]) * Wie[eidxs, :])

    # SDP constraint
    for e in range(nE):
        for t in range(T):
            constraints.append(quad_over_lin(Wre[e, t], Wn[network.nodeElist0[e], t])
                               + quad_over_lin(Wie[e, t], Wn[network.nodeElist0[e], t]) - Wn[
                                   network.nodeElist1[e], t] <= 0)

        # annulus constraint
        # constraints.append( norm(vstack(Wre[e,t], Wie[e,t])) <= network.Vmax2 )

    # enforce substation voltage = 1
    # constraints.append( Wn[network.root,:] == 1 )

    obj = Minimize(obj_sign * sum_entries(realS[network.battnodes[tNode], :]) + V_weight * sum_entries(
        square(pos(Wn - network.V2upBound)) + square(pos(network.V2lowBound - Wn))))

    prob = Problem(obj, constraints)

    # data = prob.get_problem_data(MOSEK)
    # data = []

    prob.solve(solver=MOSEK)

    return realS[network.battnodes[tNode], :].value, prob.status, Wn.value, Wre.value, Wie.value


def NSC_Out_All(tnetwork, pricesCurrent, sellFactor, pDemand, rDemand, q0, pForecast, rForecast, pMeans, pCovs, GCscens,
                LCscens, GCtime, NLweight, ppc, pool, V_weight):
    nodesStorage = tnetwork.battnodes

    # Get scenarios for storage nodes for current run
    sScenarios = ScenarioGenGC(nodesStorage, pForecast[nodesStorage, :], pMeans, pCovs, GCscens)

    # Run GC outer loop
    OPFstart = time.time()

    realS, rootV2, WnNLFC, WreNLFC, WieNLFC = GC_NLFC_Out(tnetwork, sScenarios, pForecast, rForecast, q0, pricesCurrent,
                                                          sellFactor, GCscens, pool, V_weight)

    OPFend = time.time()
    print "GC comp time: ", OPFend - OPFstart

    # Calculate Bounds
    OPFstart = time.time()

    LowBounds, UpBounds, WnBounds, WreBounds, WieBounds = NSC_Bounds_Out(tnetwork, pForecast, rForecast, realS, pool,
                                                                         V_weight)

    OPFend = time.time()
    print "Bounds comp time: ", OPFend - OPFstart

    # Run LCs
    LCstart = time.time()

    Q, U, boundsFlag = LC_Combined(LowBounds, UpBounds, realS, NLweight, pricesCurrent, sellFactor, q0, LCscens, GCtime,
                                   pDemand[nodesStorage, :], tnetwork.umax, tnetwork.umin, tnetwork.qmax, tnetwork.qmin,
                                   nodesStorage, pMeans, pCovs)

    LCend = time.time()
    print "LC comp time: ", LCend - LCstart

    PFstart = time.time()

    # Simulate results using PF
    runVoltage = PF_Sim(ppc, GCtime, pDemand, rDemand, nodesStorage, U, rootV2)

    PFend = time.time()
    print "PF simulation time: ", PFend - PFstart

    return Q, U, runVoltage, LowBounds, UpBounds, realS, boundsFlag, WnNLFC, WreNLFC, WieNLFC, WnBounds, WreBounds, WieBounds

# """
# Python Module for NSC cost minimization controller
#
# Dependencies:
#     numpy
#     cvxpy
#     mosek
#     pypower
#     multiprocessing
#     itertools
# """
#
# import numpy as np
# from cvxpy import *
# from pypower.api import runpf, ppoption
# import time
# from multiprocessing import Pool
# import itertools
#
#
# def ScenarioGenGC(battnodes, pForecast, pMeans, pCovs, scens):
#     """
#     Inputs: battnodes - nodes with storage
#         pForecast - real power forecast for only storage nodes
#         pMeans/Covs - dictionaries of real power mean vector and covariance matrices
#                         keys are 'b node#' values are arrays
#         scens - number of scenarios to generate
#     Outputs: sScenarios - dictionary with keys scens and vals (nS X time)
#     """
#     nS, T = pForecast.shape
#     sScenarios = {}
#     for j in range(scens):
#         counter = 0
#         tmpArray = np.zeros((nS, T))
#         for i in battnodes:
#             resi = np.random.multivariate_normal(pMeans['b' + str(i + 1)], pCovs['b' + str(i + 1)])
#             tmpArray[counter, :] = pForecast[counter, :] + resi[0:T]
#             counter += 1
#         sScenarios[j] = tmpArray
#
#     return sScenarios
#
#
# def ScenarioGen(battnodes, pForecast, pMeans, pCovs, scens):
#     """
#     Inputs: battnodes - nodes with storage
#         pForecast - real power forecast for only storage nodes
#         pMeans/Covs - dictionaries of real power mean vector and covariance matrices
#                         keys are 'b node#' values are arrays
#         scens - number of scenarios to generate
#     Outputs: sScenarios - dictionary with keys scens and vals (nS X time)
#     """
#     nS, T = pForecast.shape
#     sScenarios = {}
#     for j in range(scens):
#         counter = 0
#         tmpArray = np.zeros((nS, T))
#         for i in battnodes:
#             resi = np.random.multivariate_normal(pMeans['b' + str(i + 1)], pCovs['b' + str(i + 1)])
#             tmpArray[counter, :] = pForecast[counter, :] + resi[0:T]
#             counter += 1
#         sScenarios[j] = tmpArray
#
#     return sScenarios
#
#
# def GC_NLFC_Out(network, sScenarios, pDemand, qDemand, q0, prices, sellFactor, scens, pool, V_weight):
#     """
#     Outer loop for the NLFC controller. Takes average of all scenarios.
#     Inputs: network - Network object
#             prices - vector of prices for the times in pDemand
#             sScenarios - dictionary of np matrix (storage nodes X time) as value and scen as key
#             p/qDemand - forecast of p/q for all nodes
#             q0 - initial state of charge vector length number of storage nodes
#     Outputs: realS and imagS for all storage nodes
#     """
#
#     n, T = pDemand.shape
#     nS = len(network.battnodes)
#     nE = len(network.nodeElist0)
#     realS_sum = np.matrix(np.zeros((nS, T)))
#     rootV2_sum = np.matrix(np.zeros((1, T)))
#     Wn_sum = np.matrix(np.zeros((n, T)))
#     Wre_sum = np.matrix(np.zeros((nE, T)))
#     Wie_sum = np.matrix(np.zeros((nE, T)))
#
#     ## Compute in parallel
#     # Gather all scenarios data into a list
#     demandList = []
#     for i in range(scens):
#         combDemand = pDemand
#         combDemand[network.battnodes, :] = sScenarios[i]
#         demandList.append(combDemand)
#
#     # Make parallel pool
#     # if __name__== "__main__":
#     # print('start parallel pool')
#     # pool = Pool()
#     print 'Computing in pool'
#     sols = pool.map(GC_NLFC_star, itertools.izip(itertools.repeat(network), demandList, itertools.repeat(qDemand),
#                                                  itertools.repeat(q0), itertools.repeat(prices),
#                                                  itertools.repeat(sellFactor), itertools.repeat(V_weight)))
#
#     # Unpack all information
#     for i in range(scens):
#         if sols[i][2] != "optimal":
#             print 'OPF status is: ', sols[i][2]
#         realS_sum += sols[i][0]
#         rootV2_sum += sols[i][1]
#         Wn_sum += sols[i][3]
#         Wre_sum += sols[i][4]
#         Wie_sum += sols[i][5]
#
#     realS = realS_sum / scens
#     rootV2 = rootV2_sum / scens
#     Wn = Wn_sum / scens
#     Wre = Wre_sum / scens
#     Wie = Wie_sum / scens
#
#     return realS, rootV2, Wn, Wre, Wie
#
#     """
#     #Sequential code
#     for i in range(scens):
#         combDemand = pDemand
#         combDemand[network.battnodes,:] = sScenarios[i]
#         realS_new, imagS_new, rootV2_new, status, cost = GC_NLFC(network, combDemand, qDemand, q0, prices)
#         realS_sum = realS_sum + realS_new
#         rootV2_sum = rootV2_sum + rootV2_new
#         if status != "optimal":
#             print('status is: ', status)
#     """
#
#
# def GC_NLFC_star(allargs):
#     """Unpack all the arguments packed up for parallel processing"""
#     return GC_NLFC(*allargs)
#
#
# def GC_NLFC(network, pDemand, qDemand, q0, prices, sellFactor, V_weight):
#     """
#     NLFC controller for cloud coordinator global control
#     Inputs: network - Network object
#             prices - vector of prices for the times in pDemand
#             p/qDemand - np matrix (nodes X time) as values
#             q0 - initial state of charge vector length number of storage nodes
#     Outputs: realS, imagS, optimization status
#     """
#
#     n, T = pDemand.shape
#     nE = len(network.edgelist)
#     nS = len(network.battnodes)
#
#     # print("dimensions of problem: ",n,T)
#
#     if np.any(np.less(q0, network.qmin)):  # Correct for computational inaccuracies
#         q0 += .00001
#         print 'q0 too low'
#     elif np.any(np.greater(q0, network.qmax)):
#         q0 += -.00001
#         print 'q0 too high'
#
#     umin = np.tile(network.umin, (1, T))
#     umax = np.tile(network.umax, (1, T))
#     qmax = np.tile(network.qmax, (1, T + 1))
#     qmin = np.tile(network.qmin, (1, T + 1))
#     rYbus = network.realYbus
#     iYbus = network.imagYbus
#
#     realS = Variable(n, T)
#     imagS = Variable(n, T)
#     Wre = Variable(nE, T)
#     Wie = Variable(nE, T)
#     Wn = Variable(n, T)
#
#     U = Variable(nS, T)
#     Q = Variable(nS, T + 1)
#
#     # Battery Constraints
#     constraints = [Q[:, 0] == q0,
#                    Q[:, 1:T + 1] == Q[:, 0:T] + U,
#                    U <= umax,
#                    U >= umin,
#                    Q <= qmax,
#                    Q >= qmin
#                    ]
#
#     # Demand and battery action constraints
#     constraints.append(realS[network.nbattInd, :] == -pDemand[network.nbattInd, :])
#     constraints.append(realS[network.battnodes, :] == -U - pDemand[network.battnodes, :])
#     constraints.append(imagS[network.nrootInd, :] == -qDemand[network.nrootInd, :])
#
#     # Voltage Constraints
#     # constraints.append( Wn <= network.Vmax2 )
#     # constraints.append( Wn >= network.Vmin2 )
#
#     # Power Flow constraints
#     for node in range(n):
#         eidxs = network.nodeEdge[node]
#         js = network.nodeNeighbor[node]
#         direction = network.nodeDirection[node]
#         constraints.append(realS[node, :] == rYbus[node, node] * Wn[node, :]
#                            + rYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, iYbus[node, js]) * Wie[eidxs, :])
#         constraints.append(imagS[node, :] == -iYbus[node, node] * Wn[node, :]
#                            - iYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, rYbus[node, js]) * Wie[eidxs, :])
#
#     # SDP constraint
#     for e in range(nE):
#         for t in range(T):
#             constraints.append(quad_over_lin(Wre[e, t], Wn[network.nodeElist0[e], t])
#                                + quad_over_lin(Wie[e, t], Wn[network.nodeElist0[e], t]) - Wn[
#                                    network.nodeElist1[e], t] <= 0)
#
#             # annulus constraint
#             # constraints.append( norm(vstack(Wre[e,t], Wie[e,t])) <= network.Vmax2 )
#
#     # enforce substation voltage = 1
#     # constraints.append( Wn[network.root,:] == 1 )
#
#     if sellFactor == 0:
#         prices = np.tile(prices, (nS, 1))
#         obj = Minimize(sum_entries(mul_elemwise(prices, neg(realS[network.battnodes, :])))
#                        + V_weight * sum_entries(
#             square(pos(Wn - network.V2upBound)) + square(pos(network.V2lowBound - Wn))))
#     else:
#         obj = Minimize(sum_entries(mul_elemwise(prices, realS[0, :]))
#                        + V_weight * sum_entries(
#             square(pos(Wn - network.V2upBound)) + square(pos(network.V2lowBound - Wn))))
#     if sellFactor == 2:
#         constraints.append(realS[0, :] >= 0)  # substation cannot sell
#     if sellFactor == 3:
#         constraints.append(realS[network.battnodes, :] <= 0)  # nodes cannot sell
#
#     prob = Problem(obj, constraints)
#
#     # data = prob.get_problem_data(MOSEK)
#     # data = []
#
#     prob.solve(solver=MOSEK)
#
#     """
#     Solvers: ECOS - failed
#     CVXOPT - memory usage intractable
#     MOSEK - works well but is commercial
#     GUROBI - commercial
#     SCS - far from optimal
#     """
#
#     return realS[network.battnodes, :].value, Wn[network.root, :].value, prob.status, Wn.value, Wre.value, Wie.value
#
#
# def LC_Combined(LowBounds, UpBounds, realS, NLweight, prices, sellFactor, q0, LCscens, GCtime, pre_pDemands, umaxo,
#                 umino, qmaxo, qmino, battnodes, pMeans, pCovs):
#     """
#     NLFC Local controller
#     Inputs: realS - real net power from GC for only storage notes
#     q0 - initial state of charge
#     LCscens - number of local scenarios
#     GCtime - time between GC steps
#     pre_pDemands - previous time real power of storage nodes used for local forecasts
#     umaxo, umino, qmaxo, qmino
#     Outputs: Qfinal, Ufinal
#     """
#
#     nS, T = LowBounds.shape
#     Qfinal = np.matrix(np.zeros((nS, GCtime + 1)))
#     Ufinal = np.matrix(np.zeros((nS, GCtime)))
#     boundsFlag = np.zeros((1, GCtime))
#     Qfinal[:, 0] = q0[:, 0]
#
#     for t in range(GCtime):
#         # Resize parameters to match new time
#         umin = np.tile(umino, (1, T - t))
#         umax = np.tile(umaxo, (1, T - t))
#         qmax = np.tile(qmaxo, (1, T - t + 1))
#         qmin = np.tile(qmino, (1, T - t + 1))
#         pricesCurrent = np.tile(prices[:, t:], (nS, LCscens))
#         LowBoundsCurr = LowBounds[:, t:]
#         UpBoundsCurr = UpBounds[:, t:]
#
#         # generate local forecasts
#         # LCforecast = forecaster then LCforecasts = scenario gen from forecast
#         LCforecasts = ScenarioGen(battnodes, pre_pDemands[:, t:], pMeans, pCovs, LCscens)
#
#         # initialize variables
#         Y = Variable(nS, (T - t) * LCscens)
#         U = Variable(nS, T - t)
#         Q = Variable(nS, T - t + 1)
#
#         # Battery Constraints
#         constraints = [Q[:, 0] == q0,
#                        Q[:, 1:T - t + 1] == Q[:, 0:T - t] + U,
#                        U <= umax,
#                        U >= umin,
#                        Q <= qmax,
#                        Q >= qmin
#                        ]
#
#         for i in range(LCscens):
#             # Demand and battery action constraints
#             constraints.append(Y[:, (i * (T - t)):((i + 1) * (T - t))] == -LCforecasts[i] - U)
#
#             # Bounds Constraints
#             constraints.append(Y[:, (i * (T - t)):((i + 1) * (T - t))] >= LowBoundsCurr)
#             constraints.append(Y[:, (i * (T - t)):((i + 1) * (T - t))] <= UpBoundsCurr)
#
#         if sellFactor == 0:
#             obj = Minimize(sum_entries(mul_elemwise(pricesCurrent, neg(Y))) + NLweight * norm(
#                 Y - np.tile(realS[:, t:], (1, LCscens)), 'fro'))
#         else:
#             obj = Minimize(
#                 sum_entries(mul_elemwise(pricesCurrent, -Y)) + NLweight * norm(Y - np.tile(realS[:, t:], (1, LCscens)),
#                                                                                'fro'))
#         if sellFactor == 3:
#             constraints.append(Y <= 0)  # nodes cannot sell
#
#         prob = Problem(obj, constraints)
#
#         # data = prob.get_problem_data(MOSEK)
#         # data = []
#
#         prob.solve(solver=MOSEK)
#
#         # Store values
#         if prob.status != "optimal":
#             print 'LC status is: ', prob.status
#         Qfinal[:, t + 1] = Q[:, 1].value
#         q0 = Q[:, 1].value
#         if np.any(np.less(q0, qmino)):  # Correct for computational inaccuracies
#             q0 += .00001
#         elif np.any(np.greater(q0, qmaxo)):
#             q0 += -.00001
#         Ufinal[:, t] = U[:, 0].value
#         LowBoundsRep = np.tile(LowBoundsCurr, (1, LCscens))
#         UpBoundsRep = np.tile(UpBoundsCurr, (1, LCscens))
#
#         if np.any(np.greater(Y.value, UpBoundsRep - .0001)):
#             print 'LC Upper Bound Reached'
#             boundsFlag[:, t] = 1
#         if np.any(np.less(Y.value, LowBoundsRep + .0001)):
#             print 'LC Lower Bound Reached'
#             boundsFlag[:, t] = 1
#
#     return Qfinal, Ufinal, boundsFlag
#
#
# def LC_Combined_No_Bounds(realS, NLweight, prices, sellFactor, q0, LCscens, GCtime, pre_pDemands, umaxo, umino, qmaxo,
#                           qmino, battnodes, pMeans, pCovs):
#     """
#     NLFC Local controller
#     Inputs: realS - real net power from GC for only storage notes
#     NLWeight - net load following weight in objective
#     sellFactor - 1 for selling 0 for selling not profitable
#     q0 - initial state of charge
#     LCscens - number of local scenarios
#     GCtime - time between GC steps
#     pre_pDemands - previous time real power of storage nodes used for local forecasts or dictionary of scenarios
#     umaxo, umino, qmaxo, qmino
#     Outputs: Qfinal, Ufinal
#     """
#
#     nS, T = realS.shape
#     Qfinal = np.matrix(np.zeros((nS, GCtime + 1)))
#     Ufinal = np.matrix(np.zeros((nS, GCtime)))
#     boundsFlag = np.zeros((1, GCtime))
#     Qfinal[:, 0] = q0[:, 0]
#
#     for t in range(GCtime):
#         # Resize parameters to match new time
#         umin = np.tile(umino, (1, T - t))
#         umax = np.tile(umaxo, (1, T - t))
#         qmax = np.tile(qmaxo, (1, T - t + 1))
#         qmin = np.tile(qmino, (1, T - t + 1))
#         pricesCurrent = np.tile(prices[:, t:], (nS, LCscens))
#
#         # generate local forecasts
#         # LCforecast = forecaster then LCforecasts = scenario gen from forecast
#         if pre_pDemands is dict:
#             LCforecasts = pre_pDemands
#         else:
#             LCforecasts = ScenarioGen(battnodes, pre_pDemands[:, t:], pMeans, pCovs, LCscens)
#
#         # initialize variables
#         Y = Variable(nS, (T - t) * LCscens)
#         U = Variable(nS, T - t)
#         Q = Variable(nS, T - t + 1)
#
#         # Battery Constraints
#         constraints = [Q[:, 0] == q0,
#                        Q[:, 1:T - t + 1] == Q[:, 0:T - t] + U,
#                        U <= umax,
#                        U >= umin,
#                        Q <= qmax,
#                        Q >= qmin
#                        ]
#
#         for i in range(LCscens):
#             # Demand and battery action constraints
#             constraints.append(Y[:, (i * (T - t)):((i + 1) * (T - t))] == -LCforecasts[i] - U)
#
#         if sellFactor == 0:
#             obj = Minimize(sum_entries(mul_elemwise(pricesCurrent, neg(Y))) + NLweight * norm(
#                 Y - np.tile(realS[:, t:], (1, LCscens)), 'fro'))
#         else:
#             obj = Minimize(
#                 sum_entries(mul_elemwise(pricesCurrent, -Y)) + NLweight * norm(Y - np.tile(realS[:, t:], (1, LCscens)),
#                                                                                'fro'))
#         if sellFactor == 3:
#             constraints.append(Y <= 0)  # nodes cannot sell
#
#         prob = Problem(obj, constraints)
#
#         # data = prob.get_problem_data(MOSEK)
#         # data = []
#
#         prob.solve(solver=MOSEK)
#
#         # Store values
#         if prob.status != "optimal":
#             print 'LC status is: ', prob.status
#         Qfinal[:, t + 1] = Q[:, 1].value
#         q0 = Q[:, 1].value
#         if np.any(np.less(q0, qmino)):  # Correct for computational inaccuracies
#             q0 += .00001
#         elif np.any(np.greater(q0, qmaxo)):
#             q0 += -.00001
#         Ufinal[:, t] = U[:, 0].value
#
#     return Qfinal, Ufinal, boundsFlag
#
#
# def PF_Sim(ppc, GCtime, pDemand, rDemand, nodesStorage, U, rootV2):
#     """
#     Uses PyPower to calculate PF to simulate node voltages after storage control
#     Inputs: ppc - PyPower case dictionary
#         GCtime - number of time steps between GC runs
#         pDemand/rDemand - true values of real and reactive power demanded
#         nodesStorage - list of storage nodes indexes
#         U - storage control action
#         rootV2 - voltage of the substation node
#     Outputs: runVoltage - (buses X time) array of voltages
#     """
#     nodesNum, T = pDemand.shape
#     runVoltage = np.zeros((nodesNum, GCtime))
#     for t in range(GCtime):
#         pLoad = pDemand[:, t]
#         pLoad[nodesStorage] = pLoad[nodesStorage] + U[:, t]
#         rLoad = rDemand[:, t]
#         rootVoltage = np.sqrt(rootV2[:, t])
#         ppc['bus'][:, 2] = pLoad.flatten()
#         ppc['bus'][:, 3] = rLoad.flatten()
#         # ppc['bus'][rootIdx,7] = rootVoltage # Doesnt actually set PF root voltage
#
#         # for surpressing runpf output
#         ppopt = ppoption(VERBOSE=0, OUT_ALL=0)
#         ppc_out = runpf(ppc, ppopt)
#
#         rootVdiff = rootVoltage - 1
#         runVoltage[:, t] = ppc_out[0]['bus'][:, 7] + rootVdiff
#
#     return runVoltage
#
#
# def NSC_Bounds_Out(network, pDemand, qDemand, Sload, pool, V_weight):
#     """
#     Outer loop for running NSC Bounds in parallel
#     Inputs: network - Network object
#             p/qDemand - np matrix (nodes X time) as values
#             tNode - target node for finding bounds, in range 0:NS
#             Sload - net load for other storage nodes
#             obj_sign - + for minimize, - for maximize
#     Outputs: LowBounds, UpBounds
#     """
#     n, T = pDemand.shape
#     nS = len(network.battnodes)
#     UpBounds = np.matrix(np.zeros((nS, T)))
#     LowBounds = np.matrix(np.zeros((nS, T)))
#     WnDict = {}
#     WreDict = {}
#     WieDict = {}
#
#     ## Compute in parallel
#     # Gather all data into lists
#     tNodes = []
#     obj_sign = []
#     for i in range(nS):
#         tNodes.append(i)
#         obj_sign.append(1)
#     for i in range(nS):
#         tNodes.append(i)
#         obj_sign.append(-1)
#
#     # Make parallel pool
#     # if __name__== "__main__":
#     # print('start parallel pool')
#     # pool = Pool()
#     print 'Computing in pool'
#     sols = pool.map(NSC_Bounds_star,
#                     itertools.izip(itertools.repeat(network), itertools.repeat(pDemand), itertools.repeat(qDemand),
#                                    tNodes, itertools.repeat(Sload), obj_sign, itertools.repeat(V_weight)))
#
#     # Unpack all information
#     for i in range(nS):
#         LowBounds[i, :] = sols[i][0]
#         if sols[i][1] != "optimal":
#             print 'OPF status is: ', sols[i][1]
#         WnDict[i] = sols[i][2]
#         WreDict[i] = sols[i][3]
#         WieDict[i] = sols[i][4]
#     for i in range(nS):
#         UpBounds[i, :] = sols[i + nS][0]
#         if sols[i + nS][1] != "optimal":
#             print 'OPF status is: ', sols[i + nS][1]
#         WnDict[i + nS] = sols[i + nS][2]
#         WreDict[i + nS] = sols[i + nS][3]
#         WieDict[i + nS] = sols[i + nS][4]
#
#     return LowBounds, UpBounds, WnDict, WreDict, WieDict
#
#
# def NSC_Bounds_star(allargs):
#     """Unpack all the arguments packed up for parallel processing"""
#     return NSC_Bounds(*allargs)
#
#
# def NSC_Bounds(network, pDemand, qDemand, tNode, Sload, obj_sign, V_weight):
#     """
#     NSC bound calculator for cloud coordinator global control
#     Inputs: network - Network object
#             p/qDemand - np matrix (nodes X time) as values
#             tNode - target node for finding bounds, in range 0:NS
#             Sload - net load for other storage nodes
#             obj_sign - + for minimize, - for maximize
#     Outputs: realS, optimization status
#     """
#
#     n, T = pDemand.shape
#     nE = len(network.edgelist)
#     nS = len(network.battnodes)
#
#     # print("dimensions of problem: ",n,T)
#
#     rYbus = network.realYbus
#     iYbus = network.imagYbus
#
#     realS = Variable(n, T)
#     imagS = Variable(n, T)
#     Wre = Variable(nE, T)
#     Wie = Variable(nE, T)
#     Wn = Variable(n, T)
#
#     battnodes = network.battnodes
#     battnodes = battnodes[np.arange(nS) != tNode]  # Remove the target node from list of nodes
#     Sload = Sload[np.arange(nS) != tNode, :]  # Remove target node from list of net loads
#
#     # Constraints
#     constraints = []
#
#     # Demand and battery action constraints
#     constraints.append(realS[network.nbattInd, :] == -pDemand[network.nbattInd, :])
#     constraints.append(realS[battnodes, :] == Sload)
#     constraints.append(imagS[network.nrootInd, :] == -qDemand[network.nrootInd, :])
#
#     # Voltage Constraints
#     # constraints.append( Wn <= network.Vmax2 )
#     # constraints.append( Wn >= network.Vmin2 )
#
#     # Power Flow constraints
#     for node in range(n):
#         eidxs = network.nodeEdge[node]
#         js = network.nodeNeighbor[node]
#         direction = network.nodeDirection[node]
#         constraints.append(realS[node, :] == rYbus[node, node] * Wn[node, :]
#                            + rYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, iYbus[node, js]) * Wie[eidxs, :])
#         constraints.append(imagS[node, :] == -iYbus[node, node] * Wn[node, :]
#                            - iYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, rYbus[node, js]) * Wie[eidxs, :])
#
#     # SDP constraint
#     for e in range(nE):
#         for t in range(T):
#             constraints.append(quad_over_lin(Wre[e, t], Wn[network.nodeElist0[e], t])
#                                + quad_over_lin(Wie[e, t], Wn[network.nodeElist0[e], t]) - Wn[
#                                    network.nodeElist1[e], t] <= 0)
#
#             # annulus constraint
#             # constraints.append( norm(vstack(Wre[e,t], Wie[e,t])) <= network.Vmax2 )
#
#     # enforce substation voltage = 1
#     # constraints.append( Wn[network.root,:] == 1 )
#
#     obj = Minimize(obj_sign * sum_entries(realS[network.battnodes[tNode], :]) + V_weight * sum_entries(
#         square(pos(Wn - network.V2upBound)) + square(pos(network.V2lowBound - Wn))))
#
#     prob = Problem(obj, constraints)
#
#     # data = prob.get_problem_data(MOSEK)
#     # data = []
#
#     prob.solve(solver=MOSEK)
#
#     return realS[network.battnodes[tNode], :].value, prob.status, Wn.value, Wre.value, Wie.value
#
#
# def NSC_Out_All(tnetwork, pricesCurrent, sellFactor, pDemand, rDemand, q0, pForecast, rForecast, pMeans, pCovs, GCscens,
#                 LCscens, GCtime, NLweight, ppc, pool, V_weight):
#     nodesStorage = tnetwork.battnodes
#
#     # Get scenarios for storage nodes for current run
#     sScenarios = ScenarioGenGC(nodesStorage, pForecast[nodesStorage, :], pMeans, pCovs, GCscens)
#
#     # Run GC outer loop
#     OPFstart = time.time()
#
#     realS, rootV2, WnNLFC, WreNLFC, WieNLFC = GC_NLFC_Out(tnetwork, sScenarios, pForecast, rForecast, q0, pricesCurrent,
#                                                           sellFactor, GCscens, pool, V_weight)
#
#     OPFend = time.time()
#     print "GC comp time: ", OPFend - OPFstart
#
#     # Calculate Bounds
#     OPFstart = time.time()
#
#     LowBounds, UpBounds, WnBounds, WreBounds, WieBounds = NSC_Bounds_Out(tnetwork, pForecast, rForecast, realS, pool,
#                                                                          V_weight)
#
#     OPFend = time.time()
#     print "Bounds comp time: ", OPFend - OPFstart
#
#     # Run LCs
#     LCstart = time.time()
#
#     Q, U, boundsFlag = LC_Combined(LowBounds, UpBounds, realS, NLweight, pricesCurrent, sellFactor, q0, LCscens, GCtime,
#                                    pDemand[nodesStorage, :], tnetwork.umax, tnetwork.umin, tnetwork.qmax, tnetwork.qmin,
#                                    nodesStorage, pMeans, pCovs)
#
#     LCend = time.time()
#     print "LC comp time: ", LCend - LCstart
#
#     PFstart = time.time()
#
#     # Simulate results using PF
#     runVoltage = PF_Sim(ppc, GCtime, pDemand, rDemand, nodesStorage, U, rootV2)
#
#     PFend = time.time()
#     print "PF simulation time: ", PFend - PFstart
#
#     return Q, U, runVoltage, LowBounds, UpBounds, realS, boundsFlag, WnNLFC, WreNLFC, WieNLFC, WnBounds, WreBounds, WieBounds
