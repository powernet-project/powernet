import gridlabd_functions
import os


#Get state of charge of Battery object
SOC = gridlabd_functions.get('node1_batt','state_of_charge')
print(SOC['value'])

print(os.getenv("clock"))

#Write P_Out to battery object
gridlabd_functions.set('node1_batt_inv','P_Out',-1000)


