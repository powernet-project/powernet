from test import *
from rwText import *

def main():
    NLweight = 100
    sellFactor = 1
    GCtime = 24          # Test for 1 but look into 24
    LCscens = 1
    q0 = 0.5
    batt_solar_houses = [1]
    Q_houses = {}
    U_houses = {}
    #umaxo = 0.41277343
    #umino = -0.41277343
    #qmaxo = 1.23832029
    #qmino = 0
    umaxo = 0.3
    umino = -0.3
    qmaxo = 1.0
    qmino = 0.0
    prices = DataPreLoaded("pricesCurrent.csv",0)

    #Q,U, boundsFlag = LC_Combined_No_Bounds_SingleHome(realS, NLweight, prices, sellFactor, q0, LCscens, GCtime, pre_pDemands, umaxo, umino, qmaxo, qmino):
    Q,U, boundsFlag = LC_Combined_No_Bounds_SingleHome(NLweight, prices, sellFactor, q0, LCscens, GCtime, umaxo, umino, qmaxo, qmino)
    for i in batt_solar_houses:
        Q_houses[i] = Q[[0]]
        U_houses[i] = U[[0]]

    create_file_json('home_U.json',U_houses)
    create_file_json('home_Q.json',Q_houses)
    
    print 'Q: ', Q
    print len(Q[0])
    print 'U: ', U
    print len(U[0])
    #print boundsFlag


if __name__ == '__main__':
    main()
