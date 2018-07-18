
import gridlabd_functions
import os
import rwText
import json
from HHoptimizer_funcDefs import *
from cvxpy import *



sim_time = os.getenv("clock")
#print 'on_precommit called'
print 'sim_time: ', sim_time
# Initializing variables
# set_P_out=-1000         # value to set P to (negative is charging, positive is discharging)
p_cc = 2000             # CC setpoint
soc_setpoint = 0.7      # Baterry SOC target

number_of_houses = 14
houses_list = range(number_of_houses+1)[1:] # Houses with batt+solar: 1,3
batt_solar_houses = range(number_of_houses+1)[1:] # Houses with batt+solar: 1,3
house_GLD = []
battery_GLD = []
for i in houses_list:
    house_GLD.append('GLD_000'+str(i))
    battery_GLD.append('Bat_inverter_'+str(i))


######## LC Controller House 1 #########
NLweight = 100
sellFactor = 1
GCtime = 24          # Test for 1 but look into 24
LCscens = 1
q0 = 0.5
#q0 = houses_dict[1]['soc']
umaxo = 0.3
umino = -0.3
qmaxo = 1.0
qmino = 0.0
# sim_time string: "2015-07-01 14:58:30 EDT"
#                   01234567890123456789
if sim_time[14:19] == "01:00":
#if sim_time[15:19] == "5:00":
#if sim_time[15] == "1":

    # Checking if the file exists
    try:
        u = BatteryReadRemove(batt_solar_houses)
        #print 'File exists'
        #print 'u: ', u


        #with open('home_U.json','r') as file:
            #read and remove data

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
