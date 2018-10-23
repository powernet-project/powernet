import pickle
from case_123 import *
from combined_cost_min import *
from data_processing_cost_min import *
from multiprocessing.dummy import Pool


def run_gc(p_forecast, r_forecast, q_zero):
    """ main
        v0.1 - July 2018
        Thomas Navidi

        How to run powernet algorithm modules
    """
    import numpy as np
    import argparse
    from scipy.io import loadmat
    import time
    from algorithms import *
    from network import *
    from forecaster import *

    parser = argparse.ArgumentParser(description='Simulate Control')
    parser.add_argument('--seed', default=0, help='random seed')
    parser.add_argument('--storagePen', default=2, help='storage penetration percentage')
    parser.add_argument('--solarPen', default=3, help='solar penetration percentage')
    #parser.add_argument('--V_weight', default=500, help='voltage soft constraint weight')
    FLAGS, unparsed = parser.parse_known_args()
    #print('running with arguments: ({})'.format(FLAGS))
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
    network_data = np.load('network_data.npz')
    loadMod = 1
    presampleIdx = 168 # first week as presample data
    startIdx = presampleIdx + 1 # starting index for the load dataset
    DataDict = loadmat('loadData123Ag.mat')
    pDemandFull = loadMod*np.matrix(DataDict['pDemand'])
    rDemandFull = loadMod*np.matrix(DataDict['rDemand'])
    DataDict = loadmat('PyLoadData.mat')
    sNormFull = np.matrix(DataDict['sNorm'])
    # Load Residual Means and Covariance Dictionaries
    ResidualDict = loadmat('ResidualData123.mat')
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
    rampDict = loadmat('rampDataAll.mat')
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
    #print('all ramp times', np.sort(rampUAll.keys()))

    # initialize forecaster and network
    forecast_error = .1
    forecaster = Forecaster(forecast_error, pMeans, pCovs)

    # Random = True
    network = Network(storagePen, solarPen, nodesPen, pDemandFull, rDemandFull, pricesFull, root, Ybus, startIdx, sNormFull, Vmin=0.95, Vmax=1.05, Vtol=0, v_root=1.022, random=True, rampUAll=rampUAll)

    # Random = False

    # hardcoding battery information
    battnodes = np.array([4, 10], dtype=int)
    qmin = np.reshape(np.matrix([0, 0]), (2,1))
    qmax = np.reshape(np.matrix([0.126, 0.063]), (2,1))
    umin = -qmax/3
    umax = qmax/3
    # 123 bus case 1 day Pecan Street 1 minute data
    startIdx = 0
    battnode_data = np.genfromtxt('agg_load_123_raw.csv', delimiter=',').T
    battnode_data[0,0] = 1235.22
    pdat = np.zeros((2,24))
    for i in range(24):
        pdat[:,i] = np.mean(battnode_data[:,i*60:(i+1)*60], axis=1)
    rdat = pdat*np.tan(np.arccos(.9))
    network_data = np.genfromtxt('network123_case_load.csv', delimiter=',')
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
    #print('all ramp times', np.sort(rampUAll.keys()))

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

    # print('MY OG Q0')
    # print(q0)
    # print(np.matrix(np.zeros(qmax.shape)))

    if q_zero:
        q_zero = np.matrix(q_zero)
        q_zero = q_zero.T
        q0 = q_zero

    # Initialize values to save
    Qall = np.matrix(np.zeros((storageNum,GCtime*GCstepsTotal+1)))
    Uall = np.matrix(np.zeros((storageNum,GCtime*GCstepsTotal)))


    ### Run Global Controller ###
    print('Running time:', t_idx)
    realS, pricesCurrent, LCtime, rampFlag, RstartList, QiList, RsignList, ramp_next, ubound_min, ubound_max = GC.runStep(q0, t_idx)

    # print('THESE ARE MY RESULTS!')
    # print(realS)
    # print(pricesCurrent)
    # print(LCtime)
    # print(rampFlag)
    # print(RstartList)
    # print(QiList)
    # print(RsignList)
    # print(ramp_next)

    result = {
        'realS': pickle.dumps(realS, protocol=0),
        'pricesCurrent': pickle.dumps(pricesCurrent, protocol=0),
        'LCtime': LCtime,
        'rampFlag': rampFlag,
        'RstartList': pickle.dumps(RstartList, protocol=0),
        'QiList': pickle.dumps(QiList, protocol=0),
        'RsignList': pickle.dumps(RsignList, protocol=0),
        'ramp_next': ramp_next,
        'uboundMin': pickle.dumps(ubound_min, protocol=0),
        'uboundMax': pickle.dumps(ubound_max, protocol=0)
    }

    return result

    #     pickled_value = pickle.dumps(realS, protocol=0)
    #
    #     #print 'WTF:', pickle.loads(pickled_value)
    #
    #     return pickled_value








# # Main file for integrated cost min
# import pickle
# from data_processing_cost_min import *
# from combined_cost_min import *
# from multiprocessing.dummy import Pool
# from case_123 import *
#
#
# def run_gc(p_forecast, r_forecast, q_zero):
#     # run this for testing purposes
#     # This part is all one time initialization
#     import time
#     import argparse
#     from scipy.io import loadmat
#
#
#
#     Allstart = time.time()
#     Prepstart = time.time()
#
#     parser = argparse.ArgumentParser(description='Simulate Control')
#     parser.add_argument('--seed', default=0, help='random seed')
#     parser.add_argument('--storagePen', default=2, help='storage penetration percentage')
#     parser.add_argument('--solarPen', default=3, help='solar penetration percentage')
#     # parser.add_argument('--V_weight', default=500, help='voltage soft constraint weight')
#     FLAGS, unparsed = parser.parse_known_args()
#
#     #print 'running with arguments: ({})'.format(FLAGS)
#
#     storagePen = float(FLAGS.storagePen) / 10
#     solarPen = float(FLAGS.solarPen) / 10
#     seed = int(FLAGS.seed)
#     # V_weight = float(FLAGS.V_weight)
#
#     np.random.seed(seed)  # set random seed
#
#     # Set parameters
#     sellFactor = 1  # 0 means selling is not profitable
#     V_weight = 1000
#     Vtol = .005
#     GCtime = 2
#     GCstepsTotal = 1  # 30 = 30 days when GCtime = 24 hours
#     lookAheadTime = 0
#     LCscens = 1
#     NLweight = 400  # Try NLweight = price approximately 400
#     GCscens = 1  # Try just 1 scenario...
#     nodesPen = max(solarPen, storagePen)  # .11 gets 3 nodes # percentage of load nodes in network with storage/solar
#     # print 'seed ', seed
#     # print 'nodesPen: ', nodesPen
#     # print 'storage and solar pen:', storagePen, solarPen
#
#     # Load Network and load data
#     Vmin = .95
#     Vmax = 1.05
#
#     loadMod = 1
#     rootIdx = 0
#     ppc = case123()
#     Ybus = GetYbus(ppc)
#     presampleIdx = 168  # first week as presample data
#     startIdx = presampleIdx + 1  # starting index for the load dataset
#     DataDict = loadmat('loadData123Ag.mat')
#     pDemandFull = loadMod * np.matrix(DataDict['pDemand'])
#     rDemandFull = loadMod * np.matrix(DataDict['rDemand'])
#     DataDict = loadmat('PyLoadData.mat')
#     sNormFull = np.matrix(DataDict['sNorm'])
#     # Assign Storage/Solar
#     netDemandFull, sGenFull, nodesLode, nodesStorage, qmin, qmax, umin, umax = setStorageSolar(pDemandFull, sNormFull,
#                                                                                                storagePen, solarPen,
#                                                                                                nodesPen, rootIdx)
#     #q0 = np.matrix(np.zeros(qmax.shape))  # set initial q0 to be 0
#
#     q_zero = np.matrix(q_zero)
#     q_zero = q_zero.T
#     q0 = q_zero
#
#     # Load Global Forecast for all nodes
#     ForecastDict = loadmat('ForecastData123.mat')
#     pForecastFull1 = loadMod * np.matrix(ForecastDict['pForecastAll1'])
#     rForecastFull1 = loadMod * np.matrix(ForecastDict['rForecastAll1'])
#     pForecastFull2 = loadMod * np.matrix(ForecastDict['pForecastAll2'])
#     rForecastFull2 = loadMod * np.matrix(ForecastDict['rForecastAll2'])
#
#     # Add solar part
#     pForecastFull1[nodesStorage, :] = pForecastFull1[nodesStorage, :] - sGenFull
#     pForecastFull2[nodesStorage, :] = pForecastFull2[nodesStorage, :] - sGenFull
#
#     # Load Residual Means and Covariance Dictionaries
#     ResidualDict = loadmat('ResidualData123.mat')
#     pMeans = ResidualDict['pMeans'][0, 0]
#     pCovs = ResidualDict['pCovs'][0, 0]
#     for i in nodesStorage:
#         pMeans['b' + str(i + 1)] = pMeans['b' + str(i + 1)].flatten()
#     # End comment here
#
#     # Print information
#     #print 'load Mod: ', loadMod
#     nodesNum, timeTotal = pDemandFull.shape
#     #print 'Number of Nodes:', nodesNum, '\n', 'Total Timesteps:', GCtime * GCstepsTotal
#     #print 'Selling Factor: ', sellFactor
#
#     # Load Prices
#     prices = np.matrix(np.hstack((250 * np.ones((1, 16)), 350 * np.ones((1, 5)), 250 * np.ones((1, 3)))))
#     prices = np.tile(prices, (1, timeTotal / 24))
#
#     # Bulid network
#     tnetwork = Network(Ybus, rootIdx, nodesStorage, qmin, qmax, umin, umax, Vmin, Vmax, Vtol)
#
#     Prepend = time.time()
#     #print "Prep comp time: ", Prepend - Prepstart
#
#     # Initialize results arrays
#     ARBtotal = 0
#     allVoltage = np.zeros((nodesNum, GCtime * GCstepsTotal))
#     Qall = np.zeros((len(nodesStorage), GCtime * GCstepsTotal))
#     Uall = np.zeros((len(nodesStorage), GCtime * GCstepsTotal))
#
#     pool = Pool()
#
#     # This loop repeats daily
#     for GCiter in range(GCstepsTotal):
#         #print '\nIteration #: ', GCiter
#         # Get forecasts and prices for current run
#
#         if GCiter % 2:
#             pForecast = pForecastFull2[:, (GCiter * GCtime + startIdx):((GCiter + 1) * GCtime + lookAheadTime + startIdx)]
#             rForecast = rForecastFull2[:, (GCiter * GCtime + startIdx):((GCiter + 1) * GCtime + lookAheadTime + startIdx)]
#         else:
#             pForecast = pForecastFull1[:, (GCiter * GCtime + startIdx):((GCiter + 1) * GCtime + lookAheadTime + startIdx)]
#             rForecast = rForecastFull1[:, (GCiter * GCtime + startIdx):((GCiter + 1) * GCtime + lookAheadTime + startIdx)]
#
#         pricesCurrent = prices[:, (GCiter * GCtime + startIdx):((GCiter + 1) * GCtime + lookAheadTime + startIdx)]
#
#         # Give LC real data to make scenarios with since we have no local forecasts
#         netDemand = netDemandFull[:, (GCiter * GCtime + startIdx):((GCiter + 1) * GCtime + lookAheadTime + startIdx)]
#         rDemand = rDemandFull[:, (GCiter * GCtime + startIdx):((GCiter + 1) * GCtime + lookAheadTime + startIdx)]
#
#         """
#         Q, U, runVoltage, LowBounds, UpBounds, netLoad, boundsFlag, WnNLFC, WreNLFC, WieNLFC, WnBounds, WreBounds, WieBounds = NSC_Out_All(
#             tnetwork, pricesCurrent, sellFactor, netDemand, rDemand, q0, pForecast, rForecast, pMeans, pCovs, GCscens, LCscens, GCtime, NLweight, ppc, pool, V_weight)
#         """
#
#         pDemand = netDemand
#
#         # nodesStorage = tnetwork.battnodes
#
#         # Get scenarios for storage nodes for current run
#         sScenarios = ScenarioGenGC(nodesStorage, pForecast[nodesStorage, :], pMeans, pCovs, GCscens)
#
#         # Run GC outer loop
#         OPFstart = time.time()
#
#         ### RESETTING P & R FORECAST
#         pForecast[nodesStorage, :] = np.array(p_forecast)
#         rForecast[nodesStorage, :] = np.array(r_forecast)
#
#         realS, rootV2, WnNLFC, WreNLFC, WieNLFC = GC_NLFC_Out(tnetwork, sScenarios, pForecast, rForecast, q0,
#                                                               pricesCurrent, sellFactor, GCscens, pool, V_weight)
#
#         OPFend = time.time()
#         #print "GC comp time: ", OPFend - OPFstart
#
#         # Calculate Bounds
#         """
#         OPFstart = time.time()
#
#         LowBounds, UpBounds, WnBounds, WreBounds, WieBounds = NSC_Bounds_Out(tnetwork, pForecast, rForecast, realS, pool, V_weight)
#
#         OPFend = time.time()
#         print "Bounds comp time: ", OPFend - OPFstart
#         """
#
#         # Run LCs
#         LCstart = time.time()
#
#         Q, U, boundsFlag = LC_Combined_No_Bounds(realS, NLweight, pricesCurrent, sellFactor, q0, LCscens, GCtime,
#                                                  pDemand[nodesStorage, :], tnetwork.umax, tnetwork.umin, tnetwork.qmax,
#                                                  tnetwork.qmin, nodesStorage, pMeans, pCovs)
#
#         LCend = time.time()
#         #print "LC comp time: ", LCend - LCstart
#
#         PFstart = time.time()
#
#         """
#         #Simulate results using PF
#         runVoltage = PF_Sim(ppc, GCtime, pDemand, rDemand, nodesStorage, U, rootV2)
#
#         PFend = time.time()
#         print "PF simulation time: ", PFend - PFstart
#         """
#
#         # Update q0
#         q0 = Q[:, -1]
#
#         # Save results
#         # allVoltage[:,GCiter*GCtime:(GCiter+1)*GCtime] = runVoltage
#         Qall[:, GCiter * GCtime:(GCiter + 1) * GCtime] = Q[:, 0:-1]
#         Uall[:, GCiter * GCtime:(GCiter + 1) * GCtime] = U
#
#         # Calculate arbitrage profits
#         #ARBtotal += pricesCurrent[:, 0:GCtime] * np.sum(U, 0).T
#
#     #Allend = time.time()
#     #AllTime = Allend - Allstart
#     #print "Total time: ", AllTime
#     #print 'ARBtotal', ARBtotal
#     #print realS.shape
#
#     pickled_value = pickle.dumps(realS, protocol=0)
#
#     #print 'WTF:', pickle.loads(pickled_value)
#
#     return pickled_value
#
#
#
#
#
#
