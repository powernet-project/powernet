from HHoptimizer_funcDefs import *
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
    for i in batt_solar_houses:
        Q_houses[i] = {}
        U_houses[i] = {}
    #umaxo = 0.41277343
    #umino = -0.41277343
    #qmaxo = 1.23832029
    #qmino = 0
    umaxo = 0.3
    umino = -0.3
    qmaxo = 1.0
    qmino = 0.0
    prices = DataPreLoaded_Prices("pricesCurrent.csv",0)

    #Q,U, boundsFlag = LC_Combined_No_Bounds_SingleHome(realS, NLweight, prices, sellFactor, q0, LCscens, GCtime, pre_pDemands, umaxo, umino, qmaxo, qmino):
    Q,U, boundsFlag = LC_Combined_No_Bounds_SingleHome(NLweight, prices, sellFactor, q0, LCscens, GCtime, umaxo, umino, qmaxo, qmino)
    Q_new = Q.tolist()[0]
    U_new = U.tolist()
    for i in batt_solar_houses:
        Q_houses[i]['soc'] = Q_new
        U_houses[i]['Battery'] = U_new


    print 'U_houses: ', U_houses
    #create_file_json('home_U.json',U_houses)
    #create_file_json('home_Q.json',Q_houses)

    print 'Q: ', Q_new
    print len(Q_new)
    print 'U: ', U_new
    print len(U_new)
    #print boundsFlag


##########################################################
'''
# Reading from file and deleting the element that is going to be used. Check first if the file exists, then the length of the array with U values. If len = 1 means this is the last element so needs to delete the file. If it's not 1, read and remove the element
    with open('home_U.json', 'r') as data_file:
        data = json.load(data_file)

    u_list = data['1']['Battery']
    #print 'u_list: ', u_list
    #print 'len u_list: ', len(u_list)

    # This is the value to actuate in the battery
    u = u_list[0]
    if len(u_list) == 1:
        print 'Need to delete the file...'

    # Removing the element that was read
    data['1']['Battery'] = u_list[1:-1]
    # Overwriting the file with new array (one less element)
    with open('home_U.json', 'w') as data_file:
        data = json.dump(data, data_file)
'''

if __name__ == '__main__':
    main()
