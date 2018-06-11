import gridlabd_functions
import os

# Initializing variables
# set_P_out=-1000         # value to set P to (negative is charging, positive is discharging)
p_cc = 2000             # CC setpoint
soc_setpoint = 0.7      # Baterry SOC target

number_of_houses = range(4)[1:] # Houses with batt+solar: 1,3
batt_solar_houses = [1,3]
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

# Getting house power:
for i in number_of_houses:
    #print 'TEST!!!!!!'
    #print gridlabd_functions.get('node1_meter_H'+str(i),'measured_real_power')['value'][1:-2]
    #a = gridlabd_functions.get('node1_meter_H'+str(i),'measured_real_power')
    #print float(a['value'][1:-2])

    #houses_dict[i]['HouseMeterRealPower'] =  gridlabd_functions.get('node1_meter_H'+str(i),'measured_real_power')
    #houses_dict[i]['HouseMeterReactivePower'] =  gridlabd_functions.get('node1_meter_H'+str(i),'measured_reactive_power')
    houses_dict[i]['HouseMeterRealPower'] =  float(gridlabd_functions.get('node1_meter_H'+str(i),'measured_real_power')['value'][1:-2])
    houses_dict[i]['HouseMeterReactivePower'] =  float(gridlabd_functions.get('node1_meter_H'+str(i),'measured_reactive_power')['value'][1:-4])

    #houses_dict[i]['HouseMeterCurrent'] =  gridlabd_functions.get('node1_meter_H'+str(i),'measured_current_1')['value']
    #power_house.append(gridlabd_functions.get('node1_meter_H'+str(i),'measured_power')['value'])
    #current_house.append(gridlabd_functions.get('node1_meter_H'+str(i),'measured_current_1')['value'])
#print 'power_house', power_house
#print 'current_house', current_house

# Getting soc
for i in batt_solar_houses:
    #houses_dict[i]['soc'] = gridlabd_functions.get('node1_batt_H'+str(i),'state_of_charge')
    #houses_dict[i]['BatteryRealPower'] = gridlabd_functions.get('node1_meter_B'+str(i),'measured_real_power')
    #houses_dict[i]['BatteryReactivePower'] = gridlabd_functions.get('node1_meter_B'+str(i),'measured_reactive_power')
    #houses_dict[i]['SolarRealPower'] = float(gridlabd_functions.get('node1_meter_S'+str(i),'measured_real_power')['value'][1:-2])
    #houses_dict[i]['SolarReactivePower'] = float(gridlabd_functions.get('node1_meter_S'+str(i),'measured_reactive_power')['value'][1:-4])
    houses_dict[i]['SolarRealPower'] = float(gridlabd_functions.get('node1_meter_S'+str(i),'measured_real_power')['value'][1:-2])
    houses_dict[i]['SolarReactivePower'] = float(gridlabd_functions.get('node1_meter_S'+str(i),'measured_reactive_power')['value'][1:-4])
    houses_dict[i]['soc'] = float(gridlabd_functions.get('node1_batt_H'+str(i),'state_of_charge')['value'][1:-3])
    houses_dict[i]['BatteryRealPower'] = float(gridlabd_functions.get('node1_meter_B'+str(i),'measured_real_power')['value'][1:-2])
    houses_dict[i]['BatteryReactivePower'] = float(gridlabd_functions.get('node1_meter_B'+str(i),'measured_reactive_power')['value'][1:-4])
    
    #houses_dict[i]['BatteryCurrent'] = gridlabd_functions.get('node1_meter_B'+str(i),'measured_current_1')['value']
    #houses_dict[i]['SolarCurrent'] = gridlabd_functions.get('node1_meter_S'+str(i),'measured_current_1')['value']
    #soc_read.append(gridlabd_functions.get('node1_batt_H'+str(i),'state_of_charge')['value'])
    #power_batt.append(gridlabd_functions.get('node1_meter_B'+str(i),'measured_power')['value'])
    #current_batt.append(gridlabd_functions.get('node1_meter_B'+str(i),'measured_current_1')['value'])
    #power_solar.append(gridlabd_functions.get('node1_meter_S'+str(i),'measured_power')['value'])
    #current_solar.append(gridlabd_functions.get('node1_meter_S'+str(i),'measured_current_1')['value'])

#print "soc_read: ", soc_read
#print "power_batt", power_batt
#print "current_batt", current_batt
#print "power_solar", power_solar
#print "current_solar", current_solar
#soc = float(soc_read['value'][1:-3])

print houses_dict
'''
# Getting solar
for i in batt_solar_houses:
    houses_dict[i]['soc'] = gridlabd_functions.get('node1_batt_H'+i,'state_of_charge')
    soc_read.append(gridlabd_functions.get('node1_batt','state_of_charge'))
print "soc_read: ", soc_read


#Get power in the mains object
p_hApp_read = gridlabd_functions.get('meter1','measured_real_power')
print "p_hApp_read: ", p_hApp_read
p_hApp = float(p_hApp_read['value'][1:-2])
'''

#Print out timestep and state of charge
sim_time = os.getenv("clock")
#print soc
# print sim_time
#print p_hApp

#k = 20000                 # Controller gain
#p_control = -(soc_setpoint - soc)*k
#gridlabd_functions.set('node1_batt_inv','P_Out',p_control)  # Write p_control to battery


#batt_delta = -(p_cc - p_hApp)
#gridlabd_functions.set('node1_batt_inv','P_Out',batt_delta)  #Write P_Out to battery object




set_P_out = 0.099

if sim_time[14] != "4":
    set_P_out=1000
    gridlabd_functions.set('node1_batt_inv_H1','P_Out',set_P_out)  #Write P_Out to battery object
else:
    gridlabd_functions.set('node1_batt_inv_H1','P_Out',set_P_out)
# print "P_OUT:", set_P_out
