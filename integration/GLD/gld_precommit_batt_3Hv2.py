import gridlabd_functions
import os
import rwText
import json
from HHoptimizer_funcDefs import *
from cvxpy import *


# Initializing variables
# set_P_out=-1000         # value to set P to (negative is charging, positive is discharging)
p_cc = 2000             # CC setpoint
soc_setpoint = 0.7      # Baterry SOC target

number_of_houses = range(4)[1:] # Houses with batt+solar: 1,3
batt_solar_houses = [1,3]
'''
houses_dict = {}
for i in number_of_houses:
    houses_dict[i]={}

#Get power and current of house meter
power_house_dict = []
power_house = []
current_house = []
#Get state of charge of Battery object
soc_read = []
#Get power and current of Battery inverter through meter
power_batt = []
current_batt = []
#Get power and current of solar inverter through meter
power_solar = []
current_solar = []
'''



sim_time = os.getenv("clock")
'''
# Can potentially use try/except to avoid these two loops. If the house doesnt have solar or storage either enter 0 or 'NA'
# Getting house power:
for i in number_of_houses:
    houses_dict[i]['HouseMeterRealPower'] =  float(gridlabd_functions.get('node1_meter_H'+str(i),'measured_real_power')['value'][1:-2])
    houses_dict[i]['HouseMeterReactivePower'] =  float(gridlabd_functions.get('node1_meter_H'+str(i),'measured_reactive_power')['value'][1:-4])
    houses_dict[i]['AgregatedMeterRealPower'] = houses_dict[i]['HouseMeterRealPower']
    houses_dict[i]['AgregatedMeterReactivePower'] = houses_dict[i]['HouseMeterReactivePower']
    houses_dict[i]['Timestep'] = sim_time


# Getting solar gen, soc, batt P and Q
for i in batt_solar_houses:
    houses_dict[i]['SolarRealPower'] = float(gridlabd_functions.get('node1_meter_S'+str(i),'measured_real_power')['value'][1:-2])
    houses_dict[i]['SolarReactivePower'] = float(gridlabd_functions.get('node1_meter_S'+str(i),'measured_reactive_power')['value'][1:-4])
    houses_dict[i]['soc'] = float(gridlabd_functions.get('node1_batt_H'+str(i),'state_of_charge')['value'][1:-3])
    houses_dict[i]['BatteryRealPower'] = float(gridlabd_functions.get('node1_meter_B'+str(i),'measured_real_power')['value'][1:-2])
    houses_dict[i]['BatteryReactivePower'] = float(gridlabd_functions.get('node1_meter_B'+str(i),'measured_reactive_power')['value'][1:-4])
    houses_dict[i]['AgregatedMeterRealPower'] = houses_dict[i]['AgregatedMeterRealPower']+houses_dict[i]['SolarRealPower']+houses_dict[i]['BatteryRealPower']
    houses_dict[i]['AgregatedMeterReactivePower'] = houses_dict[i]['HouseMeterReactivePower']+houses_dict[i]['SolarReactivePower']+houses_dict[i]['BatteryReactivePower']
'''
#Print out timestep and state of charge
#sim_time = os.getenv("clock")
#print sim_time

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
if sim_time[14:16] == "01":

    # Checking if the file exists
    try:
#        print 'Try BatteryReadRemove function...'
        u = 1000*BatteryReadRemove()
#        print 'File exists'
#        print 'u: ', u


        #with open('home_U.json','r') as file:
            #read and remove data

    # If file does not exist, run the optimization and create the file
    except Exception as exc:
#        print 'File does not exist...'
        prices = DataPreLoaded_Prices("pricesCurrent.csv",0)
        Q,U, boundsFlag = LC_Combined_No_Bounds_MultiHome(NLweight, prices, sellFactor, q0, LCscens, GCtime, umaxo, umino, qmaxo, qmino)
        U = -U
        #u = 1000*U[0][0]
        #houses_dict[1]['Battery_LC_U'] = u
#        print 'U: ', u
        u = BatteryProfiles(U, batt_solar_houses)
        #houses_dict[1]['Battery_LC_U'] = u[0]
        #houses_dict[3]['Battery_LC_U'] = u[1]


    gridlabd_functions.set('node1_batt_inv_H1','P_Out',u[0])
    gridlabd_functions.set('node1_batt_inv_H3','P_Out',u[1])

# Creating file with new data
#rwText.create_file_json('TestGLD.json', houses_dict)





###############################################
# Old Functions
'''
######## LC Controller House 1 #########
try:
    with open('home_U.json') as file:
        pass
except Exception as exc:
    NLweight = 100
    sellFactor = 1
    GCtime = 24          # Test for 1 but look into 24
    LCscens = 1
    q0 = 0.5
    umaxo = 0.3
    umino = -0.3
    qmaxo = 1.0
    qmino = 0.0
    prices = DataPreLoaded("pricesCurrent.csv",0)
    Q,U, boundsFlag = LC_Combined_No_Bounds_SingleHome(NLweight, prices, sellFactor, q0, LCscens, GCtime, umaxo, umino, qmaxo, qmino)
'''

# Reading from file
#lineList = rwText.read_file_json('TestGLD.json')
#data = json.loads(lineList[-1])
'''
soc_H1 = data['1']['soc']
soc_H3 = data['3']['soc']

if soc_H1 < 0.3:
    gridlabd_functions.set('node1_batt_inv_H1','P_Out',-2000)
else:
    gridlabd_functions.set('node1_batt_inv_H1','P_Out',300)

if soc_H3 < 0.6:
    gridlabd_functions.set('node1_batt_inv_H3','P_Out',-2000)
else:
    gridlabd_functions.set('node1_batt_inv_H3','P_Out',+500)

set_P_out = 0.099
'''

'''
if sim_time[14] != "4":
    set_P_out=1000
    gridlabd_functions.set('node1_batt_inv_H1','P_Out',set_P_out)  #Write P_Out to battery object
else:
    gridlabd_functions.set('node1_batt_inv_H1','P_Out',set_P_out)
# print "P_OUT:", set_P_out
'''
