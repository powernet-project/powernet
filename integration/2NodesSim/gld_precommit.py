import gridlabd_functions
import os
import pandas as pd
import mysql.connector
from datetime import datetime
import numpy as np
from sqlalchemy import create_engine

# Global Variables
sim_time = os.getenv("clock")
#print 'on_precommit called'
time_sim = sim_time

# Initializing variables
battInv = {'node_4':[2,3,5,6,7,8,10,11,12,14,17,18,21,22,24,25,26,27], 'node_12':[1,4,9,13,15,16,19,20,23]}
battery_GLD4 = []
for i in battInv['node_4']:
	battery_GLD4.append('Bat_inverter_'+str(i))
battery_GLD12 = []
for i in battInv['node_12']:
	battery_GLD12.append('Bat_inverter_'+str(i))

# sim_time string: "2015-07-01 14:58:30 EDT"
#                   01234567890123456789
if(int(sim_time[14:16]) == 59):
	hour = int(sim_time[11:13])+1
	print 'hour: ', hour
	if(hour < 24):
		mydb = mysql.connector.connect(host='powernet-gridlabd-rt.cftqw2r7udps.us-east-1.rds.amazonaws.com',user='gridlabd',port='3306',passwd='tfPKrZ5lOSXAVf3Y',database='gridlabd')
		query = 'SELECT * FROM LC_outputs WHERE hour = %(hour)s'
		df = pd.read_sql(query, con=mydb, params={'hour': hour})
		# setting battery inverter nodes 4:
		uBatt4 = -df['power'][0]/len(battInv['node_4'])*1000000
		for idx, b in enumerate(battery_GLD4):
			gridlabd_functions.set(b,'P_Out',uBatt4)
			print 'b: ', b
			print 'uBatt4PC: ', uBatt4

		# setting battery inverter nodes 4:
		uBatt12 = -df['power'][1]/len(battInv['node_12'])*1000000
		for idx, b in enumerate(battery_GLD12):
			gridlabd_functions.set(b,'P_Out',uBatt12)
			print 'b: ', b
			print 'uBatt12PC: ', uBatt12
