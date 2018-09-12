
import gridlabd_functions
import os
import rwText
import json
from HHoptimizer_funcDefs import *
from cvxpy import *
import pickle
import numpy as np
import requests
import time
import random


######## Global Variables ###########
sim_time = os.getenv("clock")
#print 'on_precommit called'
time_sim = sim_time
# Initializing variables
# set_P_out=-1000         # value to set P to (negative is charging, positive is discharging)
p_cc = 2000             # CC setpoint
soc_setpoint = 0.7      # Baterry SOC target

#number_of_houses = 14
number_of_houses = 2    # assuming one big battery per node
houses_list = range(number_of_houses+1)[1:] # Houses with batt+solar: 1,3
batt_solar_houses = range(number_of_houses+1)[1:] # Houses with batt+solar: 1,3
house_GLD = []
battery_GLD = []

for i in houses_list:
    house_GLD.append('GLD_000'+str(i))
    battery_GLD.append('Bat_inverter_'+str(i))

# LC Controller House 1
NLweight = 100
sellFactor = 1
#GCtime = 24          # Test for 1 but look into 24
GCtime = 2
LCscens = 1
q0 = 0.5
#q0 = houses_dict[1]['soc']
umaxo = 0.7
umino = -0.7
qmaxo = 1.0
qmino = 0.0

nodes_List = [4,12]
batteryNode4 = [1,2,3,4,5]
PowerNode_dict = {}
for i in range(len(nodes_List)):
    PowerNode_dict[nodes_List[i]]={}
socNode_dict = {}
for i in range(len(nodes_List)):
    socNode_dict[nodes_List[i]]={}
powerFile = 'PowerNode.json'
battFile = 'batt.json'

PWRNET_API_BASE_URL = 'http://pwrnet-158117.appspot.com/api/v1/'

##########################################

# sim_time string: "2015-07-01 14:58:30 EDT"
#                   01234567890123456789

# Collecting data every 14 minutes - minutes: 14, 28, 42 and 56
#if int(sim_time[14:16]) % 14 == 0 and int(sim_time[14:16]) != 0 and int(sim_time[17:18]) == 0:
if int(sim_time[15:16]) == 5 and int(sim_time[17:18]) == 0:
    print 'OUTER Loop...'
    # Getting power at node level
    for i in nodes_List:
        PowerNode_dict[i]['pPowerNode'] = float(gridlabd_functions.get('meter_'+str(i),'measured_real_power')['value'][1:-2])  + random.uniform(-50,50)
        PowerNode_dict[i]['rPowerNode'] = float(gridlabd_functions.get('meter_'+str(i),'measured_reactive_power')['value'][1:-4]) + random.uniform(-50,50)

    # Getting soc at node level - need to call only when sending info to CC
    # Only need to get one SOC per node
    PowerNode_dict[4]['SOC'] = float(gridlabd_functions.get('Battery_1','state_of_charge')['value'][1:-3]) # This is node 4
    PowerNode_dict[12]['SOC'] = float(gridlabd_functions.get('Battery_2','state_of_charge')['value'][1:-3]) # This is node 12
    # Saving data to json
    rwText.create_file_json(powerFile, PowerNode_dict)

    # Setting up CC communication every 8hrs
    if int(time_sim[11:13]) != 0 and int(time_sim[11:13]) % 2 == 0 and int(sim_time[15:16]) == 5:
        print 'CC...'
        n_hoursCC = 2
        dataList = rwText.read_file_json(powerFile) # list of json string -> each item is PowerNode_dict json element
        print 'Len dataList: ', len(dataList)
        #if len(dataList) > 4*n_hoursCC-1:
        if len(dataList) > 5*n_hoursCC-1:
            pPower4_temp = []
            rPower4_temp = []
            pPower12_temp = []
            rPower12_temp = []
            pPower = []
            rPower = []
            pPower4_avg = []
            rPower4_avg = []
            pPower12_avg = []
            rPower12_avg = []

            for i in range(len(dataList)):
                temp = json.loads(dataList[i])
                pPower4_temp.append(temp['4']['pPowerNode'])
                pPower12_temp.append(temp['12']['pPowerNode'])
                rPower4_temp.append(temp['4']['rPowerNode'])
                rPower12_temp.append(temp['12']['rPowerNode'])

            #for i in range(len(dataList)/4):
            for i in range(n_hoursCC):
                pPower4_avg.append(np.mean(pPower4_temp[4*i:4*i+3]))
                rPower4_avg.append(np.mean(rPower4_temp[4*i:4*i+3]))
                pPower12_avg.append(np.mean(pPower12_temp[4*i:4*i+3]))
                rPower12_avg.append(np.mean(rPower12_temp[4*i:4*i+3]))

            pPower = [pPower4_avg, pPower12_avg]    # Real Power forecast baseed on the previous 8hrs
            rPower = [rPower4_avg, rPower12_avg]    # Reactive Power forecast baseed on the previous 8hrs
            #pForecast_pickle = pickle.dumps(pPower, protocol=0)
            #rForecast_pickle = pickle.dumps(rPower, protocol=0)
            print 'DONE WITH POWER PROCESSING!'
            soc4 = float(gridlabd_functions.get('Battery_1','state_of_charge')['value'][1:-3]) # This is node 4
            soc12 = float(gridlabd_functions.get('Battery_2','state_of_charge')['value'][1:-3]) # This is node 12
            soc = [soc4, soc12]
            print 'soc: ', soc
            #soc = np.array(soc)                    # Latest SOC from batteries
            #soc_pickle = pickle.dumps(soc, protocol=0)

            os.remove(powerFile)

            r = requests.post(PWRNET_API_BASE_URL+'run_gc/', json={'pForecast':pPower, 'rForecast':rPower,'q0':soc},timeout=20)
            response_json = r.json()
            print response_json
            task_id = response_json['task_id']
            i=0
            time.sleep(10)

            while(i<40):
                g = requests.get(PWRNET_API_BASE_URL+'gc_results/?task_id='+task_id)
                if g.status_code == 200:
                    break
                i=i+1
                time.sleep(5)

            response_json = g.json()

            try:
                array_json = json.loads(response_json['result'])
                numpy_array = pickle.loads(array_json)
                print numpy_array

            except:
                print 'A Key error was generated from trying to deserialize the numpy array'
                numpy_array = pickle.loads(str(response_json['result']))

            # Removing battery file:
            try:
                os.remove(battFile)
                print 'battery file removed'
            except:
                print 'No battery file'

            realS = numpy_array

            # writing value for next hour:
            print 'Optimization statrting...'
            #prices = DataPreLoaded_Prices("pricesCurrent.csv",0)
            prices = [250, 250]

            # Testing if homeforecast file exists -> Need tot alk to Thomas
            try:
                temp1 = []
                with open('homeForecast.csv', 'r') as File:
                    reader = csv.reader(File)
                    for row in reader:
                        temp1.append(row)
                temp1[0][0] = float(temp1[0][0])
                temp1[0][1] = float(temp1[0][1])
                temp1[1][0] = float(temp1[1][0])
                temp1[1][1] = float(temp1[1][1])

                homeForecast = csv.reader(open('homeForecast.csv', 'rUb'), dialect=csv.excel_tab,delimiter=',')
            except:
                homeForecast = [[0.7,0.8],[0.8,0.8]]    # Fixing value -> need to change



            Q,U, boundsFlag = LC_Combined_No_Bounds_MultiHome_IEEE(NLweight, prices, sellFactor, soc4, LCscens, GCtime, umaxo, umino, qmaxo, qmino, number_of_houses, realS, homeForecast)
            U = -U
            print 'Optimization result: ', U

            # write homeForecast with U values
            # Write code!!!!!!!!!

        # read values of power and perform average
        # read values of soc
        # send power and soc to cloud to compute next steps
        # wait for answer for realS from the cloud
        # overwrite previous realS file
        # run LC controller and set new values for Q and U for the next 8+24 hours

    elif time_sim[14:16] == '05' and int(sim_time[17:18]) == 0:
        print 'BATTERY'



        '''
        # Checking if the file exists
        try:
            u = BatteryReadRemove(batt_solar_houses)
        # If file does not exist, run the optimization and create the file
        except Exception as exc:
            prices = DataPreLoaded_Prices("pricesCurrent.csv",0)
            Q,U, boundsFlag = LC_Combined_No_Bounds_MultiHome(NLweight, prices, sellFactor, q0, LCscens, GCtime, umaxo, umino, qmaxo, qmino, number_of_houses)
            U = -U
            #print 'U: ', U
            #u = 1000*U[0][0]
            #houses_dict[1]['Battery_LC_U'] = u
            u = BatteryProfiles(U, batt_solar_houses)
            #print 'Battery Profile: ', u


        #print 'GLD set u: ', u
        for idx, b in enumerate(battery_GLD):
            #val = 1000*u[idx]
            #gridlabd_functions.set(b,'P_Out',u[idx])
            gridlabd_functions.set(b,'P_Out',10000*u[idx])
            #print 'House number: ', b
            #print 'Power value: ', u[idx]
    #gridlabd_functions.set('node1_batt_inv_H1','P_Out',u[0])
    #gridlabd_functions.set('node1_batt_inv_H3','P_Out',u[1])
    '''
