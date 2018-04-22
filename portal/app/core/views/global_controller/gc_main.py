# Main file for integrated cost min
from data_processing_cost_min import *
from combined_cost_min import *
from multiprocessing import Pool


def run_gc():
    # run this for testing purposes
    # This part is all one time initialization
    import argparse
    from scipy.io import loadmat
    import time

    Allstart = time.time()
    Prepstart = time.time()

    parser = argparse.ArgumentParser(description='Simulate Control')
    parser.add_argument('--seed', default=0, help='random seed')
    parser.add_argument('--storagePen', default=2, help='storage penetration percentage')
    parser.add_argument('--solarPen', default=3, help='solar penetration percentage')
    # parser.add_argument('--V_weight', default=500, help='voltage soft constraint weight')
    FLAGS, unparsed = parser.parse_known_args()
    print 'running with arguments: ({})'.format(FLAGS)
    storagePen = float(FLAGS.storagePen) / 10
    solarPen = float(FLAGS.solarPen) / 10
    seed = int(FLAGS.seed)
    # V_weight = float(FLAGS.V_weight)

    np.random.seed(seed)  # set random seed

    # Set parameters
    sellFactor = 1  # 0 means selling is not profitable
    V_weight = 1000
    Vtol = .005
    GCtime = 24
    GCstepsTotal = 2  # 30 = 30 days when GCtime = 24 hours
    lookAheadTime = 24
    LCscens = 1
    NLweight = 400  # Try NLweight = price approximately 400
    GCscens = 1  # Try just 1 scenario...
    nodesPen = max(solarPen, storagePen)  # .11 gets 3 nodes # percentage of load nodes in network with storage/solar
    print 'seed ', seed
    print 'nodesPen: ', nodesPen
    print 'storage and solar pen:', storagePen, solarPen

    # Load Network and load data
    Vmin = .95
    Vmax = 1.05

    # Case 123 start comment here
    from case_123 import *

    loadMod = 1
    rootIdx = 0
    ppc = case123()
    Ybus = GetYbus(ppc)
    presampleIdx = 168;  # first week as presample data
    startIdx = presampleIdx + 1  # starting index for the load dataset
    DataDict = loadmat('loadData123Ag.mat')
    pDemandFull = loadMod * np.matrix(DataDict['pDemand'])
    rDemandFull = loadMod * np.matrix(DataDict['rDemand'])
    DataDict = loadmat('PyLoadData.mat')
    sNormFull = np.matrix(DataDict['sNorm'])
    # Assign Storage/Solar
    netDemandFull, sGenFull, nodesLode, nodesStorage, qmin, qmax, umin, umax = setStorageSolar(pDemandFull, sNormFull,
                                                                                               storagePen, solarPen,
                                                                                               nodesPen, rootIdx)
    q0 = np.matrix(np.zeros(qmax.shape))  # set initial q0 to be 0
    print 'Number of storage nodes: ', len(nodesStorage), nodesStorage
    # Load Global Forecast for all nodes
    ForecastDict = loadmat('ForecastData123.mat')
    pForecastFull1 = loadMod * np.matrix(ForecastDict['pForecastAll1'])
    rForecastFull1 = loadMod * np.matrix(ForecastDict['rForecastAll1'])
    pForecastFull2 = loadMod * np.matrix(ForecastDict['pForecastAll2'])
    rForecastFull2 = loadMod * np.matrix(ForecastDict['rForecastAll2'])
    # Add solar part
    pForecastFull1[nodesStorage, :] = pForecastFull1[nodesStorage, :] - sGenFull
    pForecastFull2[nodesStorage, :] = pForecastFull2[nodesStorage, :] - sGenFull
    # Load Residual Means and Covariance Dictionaries
    ResidualDict = loadmat('ResidualData123.mat')
    pMeans = ResidualDict['pMeans'][0, 0]
    pCovs = ResidualDict['pCovs'][0, 0]
    for i in nodesStorage:
        pMeans['b' + str(i + 1)] = pMeans['b' + str(i + 1)].flatten()
    # End comment here

    # Print information
    print 'load Mod: ', loadMod
    nodesNum, timeTotal = pDemandFull.shape
    print 'Number of Nodes:', nodesNum, '\n', 'Total Timesteps:', GCtime * GCstepsTotal
    print 'Selling Factor: ', sellFactor

    # Load Prices
    prices = np.matrix(np.hstack((250 * np.ones((1, 16)), 350 * np.ones((1, 5)), 250 * np.ones((1, 3)))))
    prices = np.tile(prices, (1, timeTotal / 24))

    # Bulid network
    tnetwork = Network(Ybus, rootIdx, nodesStorage, qmin, qmax, umin, umax, Vmin, Vmax, Vtol)

    Prepend = time.time()
    print "Prep comp time: ", Prepend - Prepstart

    # Initialize results arrays
    ARBtotal = 0
    allVoltage = np.zeros((nodesNum, GCtime * GCstepsTotal))
    Qall = np.zeros((len(nodesStorage), GCtime * GCstepsTotal))
    Uall = np.zeros((len(nodesStorage), GCtime * GCstepsTotal))

    # Make parallel pool
    print 'Number of GC scenarios:', GCscens
    PPstart = time.time()
    print "Making parallel pool"
    pool = Pool()
    print 'Number of Workers: ', pool._processes
    PPend = time.time()
    print 'Parallel Pool comp time: ', PPend - PPstart

    # This loop repeats daily
    for GCiter in range(GCstepsTotal):
        print '\nIteration #: ', GCiter
        if GCiter == 1:
            break

        # Get forecasts and prices for current run

        if GCiter % 2:
            pForecast = pForecastFull2[:,
                        (GCiter * GCtime + startIdx):((GCiter + 1) * GCtime + lookAheadTime + startIdx)]
            rForecast = rForecastFull2[:,
                        (GCiter * GCtime + startIdx):((GCiter + 1) * GCtime + lookAheadTime + startIdx)]
        else:
            pForecast = pForecastFull1[:,
                        (GCiter * GCtime + startIdx):((GCiter + 1) * GCtime + lookAheadTime + startIdx)]
            rForecast = rForecastFull1[:,
                        (GCiter * GCtime + startIdx):((GCiter + 1) * GCtime + lookAheadTime + startIdx)]

        pricesCurrent = prices[:, (GCiter * GCtime + startIdx):((GCiter + 1) * GCtime + lookAheadTime + startIdx)]

        # Give LC real data to make scenarios with since we have no local forecasts
        netDemand = netDemandFull[:, (GCiter * GCtime + startIdx):((GCiter + 1) * GCtime + lookAheadTime + startIdx)]
        rDemand = rDemandFull[:, (GCiter * GCtime + startIdx):((GCiter + 1) * GCtime + lookAheadTime + startIdx)]

        """
        Q, U, runVoltage, LowBounds, UpBounds, netLoad, boundsFlag, WnNLFC, WreNLFC, WieNLFC, WnBounds, WreBounds, WieBounds = NSC_Out_All(
            tnetwork, pricesCurrent, sellFactor, netDemand, rDemand, q0, pForecast, rForecast, pMeans, pCovs, GCscens, LCscens, GCtime, NLweight, ppc, pool, V_weight)
        """

        pDemand = netDemand

        # nodesStorage = tnetwork.battnodes

        # Get scenarios for storage nodes for current run
        sScenarios = ScenarioGenGC(nodesStorage, pForecast[nodesStorage, :], pMeans, pCovs, GCscens)

        # Run GC outer loop
        OPFstart = time.time()

        realS, rootV2, WnNLFC, WreNLFC, WieNLFC = GC_NLFC_Out(tnetwork, sScenarios, pForecast, rForecast, q0,
                                                              pricesCurrent, sellFactor, GCscens, pool, V_weight)

        OPFend = time.time()
        print "GC comp time: ", OPFend - OPFstart

        # Calculate Bounds
        """
        OPFstart = time.time()

        LowBounds, UpBounds, WnBounds, WreBounds, WieBounds = NSC_Bounds_Out(tnetwork, pForecast, rForecast, realS, pool, V_weight)

        OPFend = time.time()
        print "Bounds comp time: ", OPFend - OPFstart
        """

        # Run LCs
        LCstart = time.time()

        Q, U, boundsFlag = LC_Combined_No_Bounds(realS, NLweight, pricesCurrent, sellFactor, q0, LCscens, GCtime,
                                                 pDemand[nodesStorage, :], tnetwork.umax, tnetwork.umin, tnetwork.qmax,
                                                 tnetwork.qmin, nodesStorage, pMeans, pCovs)

        LCend = time.time()
        print "LC comp time: ", LCend - LCstart

        PFstart = time.time()

        """
        #Simulate results using PF
        runVoltage = PF_Sim(ppc, GCtime, pDemand, rDemand, nodesStorage, U, rootV2)

        PFend = time.time()
        print "PF simulation time: ", PFend - PFstart
        """

        # Update q0
        q0 = Q[:, -1]

        # Save results
        # allVoltage[:,GCiter*GCtime:(GCiter+1)*GCtime] = runVoltage
        Qall[:, GCiter * GCtime:(GCiter + 1) * GCtime] = Q[:, 0:-1]
        Uall[:, GCiter * GCtime:(GCiter + 1) * GCtime] = U

        # Calculate arbitrage profits
        ARBtotal += pricesCurrent[:, 0:GCtime] * np.sum(U, 0).T

    Allend = time.time()
    AllTime = Allend - Allstart
    print "Total time: ", AllTime
    print 'ARBtotal', ARBtotal

    return ARBtotal






