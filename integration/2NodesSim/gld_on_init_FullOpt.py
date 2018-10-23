import os
import gridlabd_functions
import random
import pandas
import pycurl
# import json
from StringIO import StringIO
# import for optimization function
import FullOpt
# Imports for DB
import pandas as pd
import mysql.connector
from datetime import datetime
import numpy as np
from sqlalchemy import create_engine
# Imports for comms with CC
import requests
import pickle
import time
import json

#initializing variables:
battInv = {'node_4':[2,3,5,6,7,8,10,11,12,14,17,18,21,22,24,25,26,27], 'node_12':[1,4,9,13,15,16,19,20,23]}
battery_GLD4 = []
for i in battInv['node_4']:
	battery_GLD4.append('Bat_inverter_'+str(i))
battery_GLD12 = []
for i in battInv['node_12']:
	battery_GLD12.append('Bat_inverter_'+str(i))


# Calling Full Optimization before simulation starts:

LC_U = FullOpt.SingleOpt()

LC_U4=np.squeeze(np.asarray(LC_U[0]))
LC_U12=np.squeeze(np.asarray(LC_U[1]))
bus_name = np.ones(len(LC_U4))
hour = np.arange(24)

df4 = pd.DataFrame({'bus_name': bus_name*4, 'power': LC_U4, 'hour': hour})
df12 = pd.DataFrame({'bus_name': bus_name*12, 'power': LC_U12, 'hour': hour})
df = df4.append(df12, ignore_index=True)

# writing data to db:
password = "tfPKrZ5lOSXAVf3Y"
user = "gridlabd"
hostname = "powernet-gridlabd-rt.cftqw2r7udps.us-east-1.rds.amazonaws.com"
database_name = "gridlabd"

#print "Writing to DB...."
engine = create_engine("mysql+mysqlconnector://"+user+":"+password+"@"+hostname+"/"+database_name)
df.to_sql('LC_outputs', con=engine, if_exists='replace', index=False)
#print 'written...'
# writing to battery:
uBatt4 = -df4['power'][0]/len(battInv['node_4'])*1000000
uBatt12 = -df12['power'][0]/len(battInv['node_12'])*1000000

for idx, b in enumerate(battery_GLD4):
	gridlabd_functions.set(b,'P_Out',uBatt4)
	print 'b: ', b
	print 'uBatt4: ', uBatt4

for idx, b in enumerate(battery_GLD12):
	gridlabd_functions.set(b,'P_Out',uBatt12)
	print 'b: ', b
	print 'uBatt12: ', uBatt12
