"""Global Controller Algorithms
	v0.1 - July 2018
	Thomas Navidi

	This module contains the algorithms for the global cloud controller

	Code needed updates:
	- StorageFlex functions have poorly named variables and lots of unwanted junk
	- Has hardcoded voltages for IEEE 123 bus case (substation voltage = 1.022)
	- many ramp characteristics hardcoded

	Feature needed updates:
	- For regulation signals Qireq needs to have both a max and min required SOC
	- Ubound optimization should consider all scenarios simutaneously not average

"""

import numpy as np
from cvxpy import *
import time

# from multiprocessing import Pool
import pathos.pools as pp
import itertools


class Global_Controller(object):
    """
    main controller object
    """

    def __init__(self, network, forecaster, GCtime, lookAheadTime, GCscens, sellFactor, V_weight, Vtol, ramp_weight):
        # network and forecaster are objects from the corresponding files
        # Set parameters
        """
        sellFactor = 1 # 0 means selling is not profitable
        V_weight = 10000 # tuning parameter for voltage penalties
        Vtol = .005 # tolerance bound on voltage penalties
        GCtime = 24 # run period of algorithm
        lookAheadTime = 24
        GCscens = 1 #Try just 1 scenario
        ramp_weight = 10000 # make large to prioritize ramp following
        """

        self.network = network
        self.forecaster = forecaster
        self.GCtime = GCtime
        self.lookAheadTime = lookAheadTime
        self.GCscens = GCscens
        self.sellFactor = sellFactor
        self.V_weight = V_weight
        self.Vtol = Vtol
        self.ramp_weight = ramp_weight

        self.t_idx = 0

        self.pool = pp.ProcessPool()

        self.rampSkips = []
        self.Ubounds_vio = []

    def StorageFlex_Out(self, network, sScenarios, pDemand, qDemand, prices, boundIndicator, scens, pool, V_weight):
        """
        Outer loop for the determining ramp flexibility controller. Takes average of all scenarios.
        Inputs: network - Network object
                prices - vector of prices for the times in pDemand
                sScenarios - dictionary of np matrix (storage nodes X time) as value and scen as key
                p/qDemand - forecast of p/q for all nodes
        Outputs: realS and imagS for all storage nodes
        """

        n, T = pDemand.shape
        nS = len(network.battnodes)
        nE = len(network.nodeElist0)
        Ubound_sum = np.matrix(np.zeros((nS, T)))
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
        sols = pool.map(self.StorageFlex_star,
                        itertools.izip(itertools.repeat(network), demandList, itertools.repeat(qDemand),
                                       itertools.repeat(prices), itertools.repeat(boundIndicator),
                                       itertools.repeat(V_weight)))

        # Unpack all information
        for i in range(scens):
            if sols[i][2] != "optimal":
                print 'OPF status is: ', sols[i][2]
            Ubound_sum += sols[i][0]
            rootV2_sum += sols[i][1]
            Wn_sum += sols[i][3]
            Wre_sum += sols[i][4]
            Wie_sum += sols[i][5]

        Ubound = Ubound_sum / scens
        rootV2 = rootV2_sum / scens
        Wn = Wn_sum / scens
        Wre = Wre_sum / scens
        Wie = Wie_sum / scens

        return Ubound, rootV2, Wn, Wre, Wie

    def StorageFlex_star(self, allargs):
        """Unpack all the arguments packed up for parallel processing"""
        return self.StorageFlex(*allargs)

    def StorageFlex(self, network, pDemand, qDemand, prices, boundIndicator, V_weight):
        """
        Determining ramp flexibility controller for cloud coordinator global control
        Inputs: network - Network object
                prices - vector of prices for the times in pDemand
                p/qDemand - np matrix (nodes X time) as values
        Outputs: realS, imagS, optimization status
        """

        n, T = pDemand.shape
        nE = len(network.edgelist)
        nS = len(network.battnodes)

        # print("dimensions of problem: ",n,T)

        umin = np.tile(network.umin, (1, T))
        umax = np.tile(network.umax, (1, T))
        rYbus = network.realYbus
        iYbus = network.imagYbus

        realS = Variable(n, T)
        imagS = Variable(n, T)
        Wre = Variable(nE, T)
        Wie = Variable(nE, T)
        Wn = Variable(n, T)

        U = Variable(nS, T)

        # Battery Constraints
        constraints = [U <= umax,
                       U >= umin
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
                               + rYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, iYbus[node, js]) * Wie[eidxs,
                                                                                                              :])
            constraints.append(imagS[node, :] == -iYbus[node, node] * Wn[node, :]
                               - iYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, rYbus[node, js]) * Wie[eidxs,
                                                                                                              :])

        # SDP constraint
        for e in range(nE):
            for t in range(T):
                constraints.append(quad_over_lin(Wre[e, t], Wn[network.nodeElist0[e], t])
                                   + quad_over_lin(Wie[e, t], Wn[network.nodeElist0[e], t]) - Wn[
                                       network.nodeElist1[e], t] <= 0)

            # annulus constraint
            # constraints.append( norm(vstack(Wre[e,t], Wie[e,t])) <= network.Vmax2 )

        # enforce substation voltage
        constraints.append(Wn[network.root, :] == 1.022 ** 2)  # as per 123 bus case file

        if boundIndicator == 0:  # take minimum storage as objective
            obj = Minimize(norm(U - umin, 'fro')
                           + V_weight * sum_entries(
                square(pos(Wn - network.V2upBound)) + square(pos(network.V2lowBound - Wn))))

            """ minimize the sum of all storage (does not work as a real bound for individual nodes)
            Usum = np.sum(umin,axis=0)
            obj = Minimize( norm(sum_entries(U, axis=0) - Usum,'fro')
                         + V_weight*sum_entries(square(pos(Wn - network.V2upBound)) + square(pos(network.V2lowBound - Wn))) )
            """
        else:  # take maximum storage as objective
            obj = Minimize(norm(U - umax, 'fro')
                           + V_weight * sum_entries(
                square(pos(Wn - network.V2upBound)) + square(pos(network.V2lowBound - Wn))))
            """
            Usum = np.sum(umax,axis=0)
            obj = Minimize( norm(sum_entries(U, axis=0) - Usum,'fro')
                         + V_weight*sum_entries(square(pos(Wn - network.V2upBound)) + square(pos(network.V2lowBound - Wn))) )
            """

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

        return U.value, Wn[network.root, :].value, prob.status, Wn.value, Wre.value, Wie.value

    def flexBounds(self, sScenarios, pForecast, rForecast, pricesCurrent, GCscens, V_weight):
        boundIndicator = 0  # for minimium bound
        Ubound_min, rootV2, Wn, Wre, Wie = self.StorageFlex_Out(self.network, sScenarios, pForecast, rForecast,
                                                                pricesCurrent, boundIndicator, GCscens, self.pool,
                                                                V_weight)
        boundIndicator = 1  # for maximum bounnd
        Ubound_max, rootV2, Wn, Wre, Wie = self.StorageFlex_Out(self.network, sScenarios, pForecast, rForecast,
                                                                pricesCurrent, boundIndicator, GCscens, self.pool,
                                                                V_weight)

        return Ubound_min, Ubound_max

    def buildRampRequirements(self, ramp_curr):
        # creates QiList, RstartList, RsignList

        # get variables from self for readability
        t_idx = self.t_idx
        GCtime = self.GCtime
        lookAheadTime = self.lookAheadTime
        qmax = self.network.qmax
        qmin = self.network.qmin
        umax = self.network.umax
        umin = self.network.umin
        rampUAll = self.network.rampUAll
        Ubound_min = self.Ubound_min
        Ubound_max = self.Ubound_max

        storageNum, T = Ubound_max.shape

        QiList = []
        RstartList = []
        RsignList = []

        for ramp_key in ramp_curr:
            rampObj = rampUAll[ramp_key]
            Rtimes = rampObj.times - t_idx
            if np.any(Rtimes >= (
                    GCtime + lookAheadTime)):  # if the last ramp extends past the look ahead horizon, ignore it
                continue
            # the optimization checks feasibility so we don't need to do it here
            U_ramp_test, UboundFlag = self.Distribute_Ramp(rampObj.mag, Ubound_max[:, Rtimes], Ubound_min[:, Rtimes],
                                                           qmax, qmin, umax, umin)
            if np.any(np.isnan(U_ramp_test)):
                print('ramp is infeasible at time', ramp_key)
                self.rampSkips.append(ramp_key)
                rampUAll.pop(ramp_key)
            else:
                Qtot = np.cumsum(U_ramp_test, axis=1)
                Qtot_max = np.amax(Qtot, axis=1)
                Qtot_min = np.amin(Qtot, axis=1)
                Qtot = np.where(np.absolute(Qtot_min) >= Qtot_max, Qtot_min, Qtot_max)
                # determining max and min required storage for each node across whole ramp
                Usign = (np.sign(Qtot) + 1) / 2
                Qireq = np.multiply(qmax, Usign) - Qtot
                QiList.append(Qireq)
                RstartList.append(Rtimes[0])
                Rsign = np.sign(rampObj.mag[0])  # -1 for negative and 1 for positive
                RsignList.append(Rsign)
        if QiList:  # if it is not empty
            QiList = np.hstack(QiList)
            RsignList = np.array(RsignList)
            RsignList = np.tile(RsignList, (storageNum, 1))
            RstartList = np.array(RstartList)
        else:
            print('no ramps in period')
            rampFlag = 0

        return QiList, RstartList, RsignList

    def Distribute_Ramp(self, Uramp, Ubound_max, Ubound_min, qmaxo, qmino, umax, umin, q0=np.nan):
        """
        distributes the ramp signal across the storage nodes
        inputs: Uramp - ramp amount, charging bounds determined from flexibility function, state of charge bounds
        Output: U_out storage charging schedule for ramp
        q0 = ramp prep state of charge
        """

        ramp_weight = 1000

        n, T = Ubound_max.shape
        Uramp = np.reshape(Uramp, (1, T))

        qmin = np.tile(qmino, (1, T + 1))
        qmax = np.tile(qmaxo, (1, T + 1))
        umin = np.tile(umin, (1, T))
        umax = np.tile(umax, (1, T))

        U = Variable(n, T)
        Q = Variable(n, T + 1)

        constraints = [Q[:, 1:T + 1] == Q[:, 0:T] + U,
                       U <= umax,
                       U >= umin,
                       Q <= qmax,
                       Q >= qmin
                       ]

        if not np.any(np.isnan(q0)):  # if there is a value for q0 use it
            if np.any(np.less(q0, qmino)):  # Correct for computational inaccuracies
                q0 += .00001
            elif np.any(np.greater(q0, qmaxo)):
                q0 += -.00001
            constraints.append(Q[:, 0] == q0)

        # constraints.append( sum_entries(U, axis=0) == Uramp ) #made into soft constraint
        # constraints.append( U <= Ubound_max )
        # constraints.append( U >= Ubound_min )

        # Nodes oppose each other too much in order to be close to middle
        # obj = Minimize( norm(U - (Ubound_min+Ubound_max)/2, 'fro') + norm(U, 1) )

        # Have penalty only when within alpha percent of the bounds
        alpha = .2
        tol = alpha * np.absolute(Ubound_max - Ubound_min)
        obj = Minimize(
            norm(pos(U - (Ubound_max - tol)) + pos((Ubound_min + tol) - U), 'fro') + norm(U, 1) + ramp_weight * norm(
                sum_entries(U, axis=0) - Uramp))

        prob = Problem(obj, constraints)

        prob.solve(solver=MOSEK)

        boundsFlag = np.nan

        if np.any(np.greater(U.value, Ubound_max - .0001)):
            print('U_dist Upper Bound violated')
            boundsFlag = 1
        if np.any(np.less(U.value, Ubound_min + .0001)):
            print('U_dist lower bound violated')
            boundsFlag = 1

        if prob.status != "optimal":
            print('Ramp distributing status is: ', prob.status)
            U_out = np.nan
        else:
            U_out = U.value

        return U_out, boundsFlag

    def RampPrep_NLFC_Out(self, network, sScenarios, pDemand, qDemand, q0, prices, sellFactor, scens, pool, V_weight,
                          ramp_weight, RstartList, QiList, RsignList):
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
        Q_sum = np.matrix(np.zeros((nS, T + 1)))

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
        sols = pool.map(self.RampPrep_NLFC_star,
                        itertools.izip(itertools.repeat(network), demandList, itertools.repeat(qDemand),
                                       itertools.repeat(q0), itertools.repeat(prices), itertools.repeat(sellFactor),
                                       itertools.repeat(V_weight),
                                       itertools.repeat(ramp_weight), itertools.repeat(RstartList),
                                       itertools.repeat(QiList), itertools.repeat(RsignList)))

        # Unpack all information
        for i in range(scens):
            if sols[i][2] != "optimal":
                print 'OPF status is: ', sols[i][2]
            realS_sum += sols[i][0]
            rootV2_sum += sols[i][1]
            Wn_sum += sols[i][3]
            Wre_sum += sols[i][4]
            Wie_sum += sols[i][5]
            Q_sum += sols[i][6]

        realS = realS_sum / scens
        rootV2 = rootV2_sum / scens
        Wn = Wn_sum / scens
        Wre = Wre_sum / scens
        Wie = Wie_sum / scens
        Q_sum = Q_sum / scens

        return realS, rootV2, Wn, Wre, Wie, Q_sum

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

    def RampPrep_NLFC_star(self, allargs):
        """Unpack all the arguments packed up for parallel processing"""
        return self.RampPrep_NLFC(*allargs)

    def RampPrep_NLFC(self, network, pDemand, qDemand, q0, prices, sellFactor, V_weight, ramp_weight, RstartList,
                      QiList, RsignList):
        """
        NLFC controller for cloud coordinator global control preparation for following ramps
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
                               + rYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, iYbus[node, js]) * Wie[eidxs,
                                                                                                              :])
            constraints.append(imagS[node, :] == -iYbus[node, node] * Wn[node, :]
                               - iYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, rYbus[node, js]) * Wie[eidxs,
                                                                                                              :])

        # SDP constraint
        for e in range(nE):
            for t in range(T):
                constraints.append(quad_over_lin(Wre[e, t], Wn[network.nodeElist0[e], t])
                                   + quad_over_lin(Wie[e, t], Wn[network.nodeElist0[e], t]) - Wn[
                                       network.nodeElist1[e], t] <= 0)

            # annulus constraint
            # constraints.append( norm(vstack(Wre[e,t], Wie[e,t])) <= network.Vmax2 )

        # enforce substation voltage = 1
        constraints.append(Wn[network.root, :] == 1.022 ** 2)  # as per 123 bus case file
        # constraints.append( Wn[network.root,:] == 1 )

        if sellFactor == 0:
            prices = np.tile(prices, (nS, 1))
            obj = Minimize(sum_entries(mul_elemwise(prices, neg(realS[network.battnodes, :])))  # cost min
                           + V_weight * sum_entries(
                square(pos(Wn - network.V2upBound)) + square(pos(network.V2lowBound - Wn)))  # voltage deviations
                           + ramp_weight * norm(max_elemwise(0, mul_elemwise(RsignList, (Q[:, RstartList] - QiList))),
                                                'fro'))  # ramp preparation
        else:
            obj = Minimize(sum_entries(mul_elemwise(prices, realS[0, :]))
                           + V_weight * sum_entries(
                square(pos(Wn - network.V2upBound)) + square(pos(network.V2lowBound - Wn)))
                           + ramp_weight * norm(max_elemwise(0, mul_elemwise(RsignList, (Q[:, RstartList] - QiList))),
                                                'fro'))

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

        return realS[network.battnodes, :].value, Wn[network.root,
                                                  :].value, prob.status, Wn.value, Wre.value, Wie.value, Q.value

    def GC_NLFC_Out(self, network, sScenarios, pDemand, qDemand, q0, prices, sellFactor, scens, pool, V_weight):
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
        sols = pool.map(self.GC_NLFC_star,
                        itertools.izip(itertools.repeat(network), demandList, itertools.repeat(qDemand),
                                       itertools.repeat(q0), itertools.repeat(prices), itertools.repeat(sellFactor),
                                       itertools.repeat(V_weight)))

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

    def GC_NLFC_star(self, allargs):
        """Unpack all the arguments packed up for parallel processing"""
        return self.GC_NLFC(*allargs)

    def GC_NLFC(self, network, pDemand, qDemand, q0, prices, sellFactor, V_weight):
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
                               + rYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, iYbus[node, js]) * Wie[eidxs,
                                                                                                              :])
            constraints.append(imagS[node, :] == -iYbus[node, node] * Wn[node, :]
                               - iYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, rYbus[node, js]) * Wie[eidxs,
                                                                                                              :])

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
        constraints.append(Wn[network.root, :] == 1.022 ** 2)  # as per 123 bus case file

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

    def NSC_Bounds_Out(self, network, pDemand, qDemand, Sload, pool, V_weight):
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
        sols = pool.map(self.NSC_Bounds_star,
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

    def NSC_Bounds_star(self, allargs):
        """Unpack all the arguments packed up for parallel processing"""
        return self.NSC_Bounds(*allargs)

    def NSC_Bounds(self, network, pDemand, qDemand, tNode, Sload, obj_sign, V_weight):
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
                               + rYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, iYbus[node, js]) * Wie[eidxs,
                                                                                                              :])
            constraints.append(imagS[node, :] == -iYbus[node, node] * Wn[node, :]
                               - iYbus[node, js] * Wre[eidxs, :] + mul_elemwise(direction, rYbus[node, js]) * Wie[eidxs,
                                                                                                              :])

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
        constraints.append(Wn[network.root, :] == 1.022 ** 2)  # as per 123 bus case file

        obj = Minimize(obj_sign * sum_entries(realS[network.battnodes[tNode], :]) + V_weight * sum_entries(
            square(pos(Wn - network.V2upBound)) + square(pos(network.V2lowBound - Wn))))

        prob = Problem(obj, constraints)

        # data = prob.get_problem_data(MOSEK)
        # data = []

        prob.solve(solver=MOSEK)

        return realS[network.battnodes[tNode], :].value, prob.status, Wn.value, Wre.value, Wie.value

    def runStep(self, q0, t_idx=np.nan):

        # get variables from self for readability
        if np.isnan(t_idx):
            t_idx = self.t_idx
        GCtime = self.GCtime
        lookAheadTime = self.lookAheadTime
        nodesStorage = self.network.battnodes
        GCscens = self.GCscens
        V_weight = self.V_weight
        rampUAll = self.network.rampUAll
        ramp_weight = self.ramp_weight
        sellFactor = self.sellFactor
        qmax = self.network.qmax

        # Get forecasts and scenarios
        pForecast = self.forecaster.netPredict(self.network.netDemandFull, t_idx, GCtime + lookAheadTime)
        rForecast = self.forecaster.rPredict(self.network.rDemandFull, t_idx, GCtime + lookAheadTime)
        if GCscens > 1:
            sScenarios = self.forecaster.scenarioGen(pForecast[nodesStorage, :], GCscens, nodesStorage)
        else:
            sScenarios = {}
            sScenarios[0] = pForecast[nodesStorage, :]

        # Get data from network
        netDemand, rDemand, pricesCurrent = self.network.returnData(t_idx, GCtime + lookAheadTime)

        storageNum = len(nodesStorage)

        ### Ramp algorithm stuff ###

        # Calculate storage flexibility bounds
        print('calculating storage flexibility bounds')
        self.Ubound_min, self.Ubound_max = self.flexBounds(sScenarios, pForecast, rForecast, pricesCurrent, GCscens,
                                                           V_weight)
        self.t_idx_bounds = t_idx  # save the time the bounds were made so they can be used again for the true ramp

        # Get the ramps during this time
        ramp_starts = np.sort(rampUAll.keys())
        ramp_curr = np.array(ramp_starts[ramp_starts <= (
                    t_idx + GCtime + lookAheadTime)])  # Consider ramps in both GC and lookahead time
        print('ramp times', ramp_curr)

        # If there are ramps, check if ramps are followable in the bounds and generate required Q
        print('Testing and Distributing ramps')
        rampFlag = 0
        Rtest_time = time.time()
        if ramp_curr.size > 0:  # if there are ramps in the current step
            rampFlag = 1
            QiList, RstartList, RsignList = self.buildRampRequirements(ramp_curr)
        else:
            print('no ramps in period')
            rampFlag = 0
            QiList = []
            RstartList = []
            RsignList = []

        # print('ramp test and dist comp time', time.time() - Rtest_time)

        ramp_starts = np.sort(rampUAll.keys())
        ramp_curr = np.array(ramp_starts[ramp_starts <= (t_idx + GCtime + lookAheadTime)])
        if ramp_curr.size == 0:  # if all the ramps were infeasible set flag to 0
            rampFlag = 0

        print('Obtaining net load for ramp preparation')
        if rampFlag == 1:  # only prepare nodes for ramps if there are ramps in current or look ahead time
            # Prepare storage for ramps
            realS, rootV2, Wn, Wre, Wie, Q_GC = self.RampPrep_NLFC_Out(self.network, sScenarios, pForecast, rForecast,
                                                                       q0, pricesCurrent, sellFactor, GCscens,
                                                                       self.pool, V_weight, ramp_weight, RstartList,
                                                                       QiList, RsignList)
            prep_err = np.mean(np.maximum(0, np.multiply(RsignList, (Q_GC[:, RstartList] - QiList))) / QiList, axis=0)
            # adjust ramp amounts after preparation step so that they are followable
            if np.any(prep_err > .1):  # 10% deviation
                print('prep error is, at time', prep_err, RstartList)
                prob_idx = []
                for err_i in range(len(prep_err)):  # find problematic ramp
                    if prep_err[:, err_i] < .1:
                        continue
                    else:
                        if RsignList[0, err_i] > 0:
                            Q_avail = np.sum(qmax) - np.sum(Q_GC[:, RstartList[err_i]])  # adjust ramp to be followable
                        else:
                            Q_avail = np.sum(Q_GC[:, RstartList[err_i]])
                        ramp_key = ramp_curr[err_i]
                        rampObj = rampUAll[ramp_key]
                        print('old ramp mag', np.sum(rampObj.mag))
                        rampMag = np.absolute(np.sum(rampObj.mag))
                        rampObj.mag = rampObj.mag * (Q_avail / rampMag)
                        print('new ramp mag', rampObj.mag)
                        self.rampSkips.append(ramp_key)
        else:
            print('No ramps so performing normal cost minimization')
            realS, rootV2, Wn, Wre, Wie = self.GC_NLFC_Out(self.network, sScenarios, pForecast, rForecast, q0,
                                                           pricesCurrent, sellFactor, GCscens, self.pool, V_weight)

        """
        print('Computing local load bounds')
        Lbounds_time = time.time()

        LowBounds, UpBounds, WnBounds, WreBounds, WieBounds = self.NSC_Bounds_Out(tnetwork, pForecast, rForecast, realS, pool, V_weight)

        print('Local load bounds comp time:', time.time() - Lbounds_time)
        """

        # determine how long to run LC before next GC run
        if rampFlag == 0:
            GC_nextTime = t_idx + GCtime
            ramp_next = np.nan
        elif ramp_curr[0] > t_idx + GCtime:
            GC_nextTime = t_idx + GCtime
            ramp_next = ramp_curr[0]
        else:
            GC_nextTime = ramp_curr[0]
            ramp_next = ramp_curr[0]
        LCtime = GC_nextTime - t_idx  # time until next GC run

        return realS, pricesCurrent, LCtime, rampFlag, RstartList, QiList, RsignList, ramp_next, self.Ubound_min, self.Ubound_max

    def disaggregateRampSignal(self, t_idx, q0, ramp_next):
        # After receiving a ramp signal, disaggregate the ramp accross the storage nodes

        # get variables from self
        rampUAll = self.network.rampUAll
        qmax = self.network.qmax
        qmin = self.network.qmin
        umax = self.network.umax
        umin = self.network.umin

        ramp_time = time.time()
        rampObj = rampUAll[ramp_next]
        Rtimes = rampObj.times - self.t_idx_bounds
        ramp_duration = Rtimes[-1] - Rtimes[0] + 1
        print('ramp duration', ramp_duration)
        print('ramp mag', np.sum(rampObj.mag))
        # the optimization checks feasibility so we don't need to do it here
        # print('q0: ', Qall[:,ramp_next])
        U_ramp_test, UboundFlag = self.Distribute_Ramp(rampObj.mag, self.Ubound_max[:, Rtimes],
                                                       self.Ubound_min[:, Rtimes], qmax, qmin, umax, umin, q0)
        if UboundFlag == 1:
            self.Ubounds_vio.append(ramp_next)
        if np.any(np.isnan(U_ramp_test)):
            print('True ramp is infeasible do not follow')
            ramp_duration = 0
            U_ramp_test = np.nan
        else:
            self.t_idx = t_idx + ramp_duration

        # remove ramp from dictionary of ramps
        rampUAll.pop(ramp_next)

        return U_ramp_test, ramp_duration, self.t_idx






