from pymongo import MongoClient
from datetime import datetime
import RPi.GPIO as GPIO
import math
import time
import copy
import requests
import logging
from logging.handlers import RotatingFileHandler
from raven import Client
import spidev
import numpy as np
import sqlite3


class HardwareRPi:
    def __init__(self, gpio_map = None, N_SAMPLES = 100, adc_Vin = 5.11):
        self.CONVERTION = 1.8/4095.0
        self.CT10 = 10   # 10A/1V
        self.CT20 = 20   # 20A/1V
        self.REQUEST_TIMEOUT = 10
        self.PWRNET_API_BASE_URL = 'http://pwrnet-158117.appspot.com/api/v1/'
        self.SENTRY_DSN = 'https://e3b3b7139bc64177b9694b836c1c5bd6:fbd8d4def9db41d0abe885a35f034118@sentry.io/230474'
        self.app_orig_states = ["OFF", "OFF", "ON", "OFF", "OFF", "OFF","OFF"] # Battery not included
        self.app_new_status = ["OFF", "OFF", "ON", "OFF", "OFF", "OFF", "OFF"]  # Battery not included

        # Initializing GPIOs:
        GPIO.setmode(GPIO.BOARD)
        # Dictionary with db states id:
        # Format: {'appliance_name': ['local_DB_id', 'pwrnet_appspot_id'], ...}
        self.input_sources_statesDB = {'AC1': [3,22], 'SE1': [4,23], 'RF1':[6,25], 'DW1':[7,28],'WM1':[8,29], 'CW1': [9,24], 'PW2':[10,25]}
        self.sourcesDBID = [self.input_sources_statesDB['AC1'][0],self.input_sources_statesDB['SE1'][0],self.input_sources_statesDB['RF1'][0],self.input_sources_statesDB['CW1'][0],self.input_sources_statesDB['DW1'][0],self.input_sources_statesDB['WM1'][0],self.input_sources_statesDB['PW2'][0]]
        self.appliance_lst = ["AC1", "SE1", "RF1", "CW1", "DW1", "WM1"]

        self.N_SAMPLES = N_SAMPLES
        self.adc_Vin = adc_Vin
        self.delay = 0.002

        # delta in power to save in db
        self.dP = 0.3
        self.flag_db = 0
        self.flag_state = 0


        # Initializing SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        self.spi.max_speed_hz=1000000


    def ConvertVolts(self, data,places):
      volts = (data * self.adc_Vin) / float(1023)
      volts = np.around(volts,places)
      return volts

    # Function to read SPI data from MCP3008 chip
    # Channel must be an integer 0-7


    def ReadChannel(self, channel):
      n = 0
      data = np.zeros(self.N_SAMPLES)
      #print datetime.now()
      while (n<100):
          adc = self.spi.xfer2([1,(8+channel)<<4,0])
          data[n]=((adc[1]&3) << 8) + adc[2]
          n+=1
          time.sleep(self.delay)

      return self.ConvertVolts(data,2)

    def RMS(self, data):
      """
          Current RMS calculation for consumer_ai
      """
      # The size of sum_i is the size of the AIN ports
      sum_i = [0, 0, 0, 0, 0, 0, 0, 0]
      for val in data:
          sum_i[0] += math.pow((val[0]), 2)
          sum_i[1] += math.pow((val[1]), 2)
          sum_i[2] += math.pow((val[2]), 2)
          sum_i[3] += math.pow((val[3]), 2)
          sum_i[4] += math.pow((val[4]), 2)
          sum_i[5] += math.pow((val[5]), 2)
          sum_i[6] += math.pow((val[6]), 2)
          sum_i[7] += math.pow((val[7]), 2)

      # NEED TO INCLUDE CONVERSION FROM CT
      rms_a0 = math.sqrt(sum_i[0] / self.N_SAMPLES)
      rms_a1 = math.sqrt(sum_i[1] / self.N_SAMPLES)
      rms_a2 = math.sqrt(sum_i[2] / self.N_SAMPLES)
      rms_a3 = math.sqrt(sum_i[3] / self.N_SAMPLES)
      rms_a4 = math.sqrt(sum_i[4] / self.N_SAMPLES)
      rms_a5 = math.sqrt(sum_i[5] / self.N_SAMPLES)
      rms_a6 = math.sqrt(sum_i[6] / self.N_SAMPLES)
      rms_a7 = math.sqrt(sum_i[7] / self.N_SAMPLES)

      return [rms_a0, rms_a1, rms_a2, rms_a3, rms_a4, rms_a5, rms_a6, rms_a7]


    def dbWriteMeasurements(self, vals):
      try:
          #print 'connecting'
          conn = sqlite3.connect('homehubDB.db')
          c = conn.cursor()
          #print vals
          c.execute("INSERT INTO measurements (rms, currentdate, currenttime, source_id) VALUES ((?), (?), (?), (?))" , (vals[0], vals[1], vals[2], vals[3]))
      except sqlite3.IntegrityError:
          print 'error connecting to db'
          #print('ERROR: ID already exists in PRIMARY KEY column {}'.format(id_column))
      conn.commit()
      conn.close()


    def dbWriteStates(self, vals):
      try:
          #print 'connecting'
          conn = sqlite3.connect('homehubDB.db')
          c = conn.cursor()
          #print vals
          c.execute("INSERT INTO input_sources_state (state, currentdate, currenttime, source_id) VALUES ((?), (?), (?), (?))" , (vals[0], vals[1], vals[2], vals[3]))
          #print 'State written...'
          #print 'Vals: ', vals
      except sqlite3.IntegrityError:
          print 'error connecting to db'
          #print('ERROR: ID already exists in PRIMARY KEY column {}'.format(id_column))
      conn.commit()
      conn.close()



          #c.execute("""INSERT INTO measurements (rms,
            #  currentdate, currenttime, source_id) VALUES((?), (?),
             # (?), (?))""", (data[3], str(datetime.today()).split()[0], str(datetime.today()).split()[1], 1 ))
          #conn.commit()
          #conn.close()



if __name__ == '__main__':
    test = HardwareRPi()

    status_PW2 = "OFF"
    power_PW2 = 0.0
    cosphi_PW2 = 1.0

    #prev = [-1,-1,-1,-1,-1,-1,-1,-1]
    while True:
        '''

        dts = []  # date/time stamp for each start of analog read
        #AC id:5
        dts.append(str(datetime.now()))
        ai0 = test.ReadChannel(0)
        #SE - Stove Exhaust id:12
        dts.append(str(datetime.now()))
        ai1 = test.ReadChannel(1)
        #RF id:10
        dts.append(str(datetime.now()))
        ai2 = test.ReadChannel(2)
        #CW id:13
        dts.append(str(datetime.now()))
        ai3 = test.ReadChannel(3)
        #RA - 1
        dts.append(str(datetime.now()))
        ai4 = test.ReadChannel(4)
        #RA - 2
        dts.append(str(datetime.now()))
        ai5 = test.ReadChannel(5)
        #DW id:14
        dts.append(str(datetime.now()))
        ai6 = test.ReadChannel(6)

        dts.append(str(datetime.now()))
        ai7 = test.ReadChannel(7)

        temp_ai = zip(ai0, ai1, ai2, ai3, ai4, ai5, ai6, ai7)
        temp_queue = [temp_ai, dts]
        #print temp_ai[0]

        data = test.RMS(temp_ai)
        # i+1 is foreign key for db
        for i in range(len(data)):
            if data[i] >= prev[i]+test.dP or data[i] <= prev[i]-test.dP:
                temp = [data[i], dts[i].split()[0], dts[i].split()[1], i+1]
                try:
                    test.dbWriteMeasurements(temp)
                    test.flag_db = 1
                except Exception as exc:
                    #self.logger.exception(exc)
                    #client.captureException()
                    pass

        if test.flag_db == 1:
            prev = copy.deepcopy(data)
            test.flag_db = 0
        '''


        # date/time stamp for device status


        dev_status = requests.get(test.PWRNET_API_BASE_URL + "device", timeout=test.REQUEST_TIMEOUT).json()["results"]
        dts = str(datetime.now())
        status_AC1 = [v for v in dev_status if v['id']==test.input_sources_statesDB['AC1'][1]][0]['status']
        status_SE1 = [v for v in dev_status if v['id']==test.input_sources_statesDB['SE1'][1]][0]['status']
        status_RF1 = [v for v in dev_status if v['id']==test.input_sources_statesDB['RF1'][1]][0]['status']
        status_CW1 = [v for v in dev_status if v['id']==test.input_sources_statesDB['CW1'][1]][0]['status']
        status_DW1 = [v for v in dev_status if v['id']==test.input_sources_statesDB['DW1'][1]][0]['status']
        status_WM1 = [v for v in dev_status if v['id']==test.input_sources_statesDB['WM1'][1]][0]['status']
        # Battery
        status_PW2 = [v for v in dev_status if v['id']==test.input_sources_statesDB['PW2'][1]][0]['status']
        power_PW2 = [v for v in dev_status if v['id']==test.input_sources_statesDB['PW2'][1]][0]['value']
        cosphi_PW2 = [v for v in dev_status if v['id']==test.input_sources_statesDB['PW2'][1]][0]['cosphi']

        test.app_new_status = [status_AC1, status_SE1, status_RF1, status_CW1, status_DW1, status_WM1]

        for i in range(len(test.app_new_status)):
            if test.app_new_status[i] != test.app_orig_states[i]:
                temp_db = [test.app_new_status[i], dts.split()[0], dts.split()[1], test.sourcesDBID[i]]
                try:
                    # devices_act(test.appliance_lst[i], test.app_new_status[i])
                    test.dbWriteStates(temp_db)
                    test.flag_state = 1
                    #print 'try flag: ', test.flag_state
                except Exception as exc:
                    test.logger.exception(exc)
                    client.captureException()
        if test.flag_state == 1:
            #print 'app_orig_states: ', test.app_orig_states
            test.app_orig_states = copy.deepcopy(test.app_new_status)
            #print 'app_orig_states_new: ', test.app_orig_states
            test.flag_state = 0



        time.sleep(2)






'''


sen1 = db.sensor1
sen1_data = {'RMS': random.random(), 'Datetime:': datetime.now(), }

result = sen1.insert(sen1_data)
print result
'''





'''
# Pseudocode
# data format: [rms, state, datetime, flag]
flag = 0
flag_saved = 0

while:
    if upload not successful:
        if flag_saved == 0:
            save [xt, datetime, 1]
            flag_saved = 1
    elif x_t >= x_t-1+dx or x_t <= x_t-1-dx:
        save [xt, datetime, 0]
        flag_saved = 0
    else:
        flag_saved = 0
'''
