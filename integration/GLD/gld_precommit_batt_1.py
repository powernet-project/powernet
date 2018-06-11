import gridlabd_functions
import os

# Initializing variables
# set_P_out=-1000         # value to set P to (negative is charging, positive is discharging)
p_cc = 2000             # CC setpoint
soc_setpoint = 0.7      # Baterry SOC target

#Get state of charge of Battery object
soc_read = gridlabd_functions.get('node1_batt','state_of_charge')
soc = float(soc_read['value'][1:-3])

#Get power in the mains object
p_hApp_read = gridlabd_functions.get('meter1','measured_real_power')
p_hApp = float(p_hApp_read['value'][1:-2])


#Print out timestep and state of charge
sim_time = os.getenv("clock")
print soc
# print sim_time
print p_hApp

k = 20000                 # Controller gain
p_control = -(soc_setpoint - soc)*k
gridlabd_functions.set('node1_batt_inv','P_Out',p_control)  # Write p_control to battery


#batt_delta = -(p_cc - p_hApp)
#gridlabd_functions.set('node1_batt_inv','P_Out',batt_delta)  #Write P_Out to battery object





'''
if sim_time[14] != "4":
    set_P_out=1000
    gridlabd_functions.set('node1_batt_inv','P_Out',set_P_out)  #Write P_Out to battery object
else:
    gridlabd_functions.set('node1_batt_inv','P_Out',set_P_out)
# print "P_OUT:", set_P_out'''
