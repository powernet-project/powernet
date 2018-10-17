
# Uncomment these two lines if using BBB
#import beaglebone_pru_adc as adc
#import Adafruit_BBIO.GPIO as GPIO
import RPi.GPIO as GPIO
import math
import time
import copy
import requests
import logging
from logging.handlers import RotatingFileHandler
#import StorageClass
from raven import Client
from datetime import datetime
import spidev
import numpy as np
import sqlite3
#from main import logger


# Global variables
SENTRY_DSN = 'https://e3b3b7139bc64177b9694b836c1c5bd6:fbd8d4def9db41d0abe885a35f034118@sentry.io/230474'
client = Client(SENTRY_DSN)
#battery_fct = StorageClass.Storage(timeBatt=5)

class HardwareRPi:
    def __init__(self, gpio_map = None, N_SAMPLES = 100):
        self.CONVERTION = 1.8/4095.0
        self.CT10 = 10   # 10A/1V
        self.CT20 = 20   # 20A/1V
        self.CT100 = 100 # 100A/1V
        self.REQUEST_TIMEOUT = 10
        self.PWRNET_API_BASE_URL = 'http://pwrnet-158117.appspot.com/api/v1/'
        self.SENTRY_DSN = 'https://e3b3b7139bc64177b9694b836c1c5bd6:fbd8d4def9db41d0abe885a35f034118@sentry.io/230474'
        #self.app_orig_states = ["OFF", "OFF", "ON", "OFF", "OFF", "OFF"] # Battery not included
        #self.app_new_status = ["OFF", "OFF", "ON", "OFF", "OFF", "OFF"]  # Battery not included
        #self.appliance_lst = ["AC1", "SE1", "RF1", "CW1", "DW1"]

        #################### DONE
        # self.app_orig_states = ["OFF", "OFF", "ON", "OFF", "OFF", "OFF","OFF"] # Battery included
        # self.app_new_status = ["OFF", "OFF", "ON", "OFF", "OFF", "OFF", "OFF"]  # Battery included
        self.app_orig_states = ["OFF", "OFF", "OFF"]
        self.app_new_status = ["OFF", "OFF", "OFF"]
        ####################

        # input_sources_statesDB TEST
        #self.input_sources_statesDB = {'AC1': [3,22], 'SE1': [4,23], 'RF1':[6,25], 'DW1':[7,28],'WM1':[8,29], 'CW1': [9,24], 'PW2':[10,25]}

        #################### DONE
        # input_sources_statesDB LAB
        self.input_sources_statesDB = {'DW_GC': [3,40], 'RF_GC': [4,41], 'LT_GC':[6,42], 'MW_GC':[7,43],'DR1_GC':[8,44], 'DR2_GC': [9,45], 'Range1_GC':[10,46], 'Range2_GC':[11,47]}
        self.sourcesDBID = [self.input_sources_statesDB['DW_GC'][0],self.input_sources_statesDB['RF_GC'][0],self.input_sources_statesDB['LT_GC'][0],self.input_sources_statesDB['MW_GC'][0],self.input_sources_statesDB['DR1_GC'][0],self.input_sources_statesDB['DR2_GC'][0],self.input_sources_statesDB['Range1_GC'][0],self.input_sources_statesDB['Range2_GC'][0]]
        # self.input_sources_statesDB = {'Fan_SLAC_H2': [14,37], 'Lights_SLAC_H2': [15,38], 'Computer_SLAC_H2':[16,39]}
        # self.sourcesDBID = [self.input_sources_statesDB['Fan_SLAC_H2'][0],self.input_sources_statesDB['Lights_SLAC_H2'][0],self.input_sources_statesDB['Computer_SLAC_H2'][0]]
        ####################

        #################### DONE
        #self.appliance_lst = ["AC1", "SE1", "RF1", "CW1", "DW1", "WM1", "PW2"]
        self.appliance_lst = ["DW_GC", "RF_GC", "LT_GC", "MW_GC", "DR1_GC", "DR2_GC", "Range1_GC", "Range2_GC"]
        ####################


        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.handler = RotatingFileHandler('my_log.log', maxBytes=2000, backupCount=10)
        self.logger.addHandler(self.handler)

        self.logger.info('HardwareRPi class called')

        # Database:
        self.flag_db = 0
        self.prev = [-1,-1,-1,-1,-1,-1,-1,-1]
        self.dP = 0.3
        self.flag_state = 0

        # Initializing GPIOs:
        GPIO.setmode(GPIO.BOARD)


        self.N_SAMPLES = N_SAMPLES
        self.adc_Vin = 3.3
        self.delay = 0.002

        if gpio_map == None:
            #################### DONE
            # self.gpio_map = {"CW1": 29, "DW1": 31, "AC1": 33,
            # "RF1": 35, "SE1": 37, "WM1": 38}
            self.gpio_map = {"Fan_SLAC_H2": 29, "Lights_SLAC_H2": 31, "Computer_SLAC_H2": 33}
            ####################
        else:
            self.gpio_map = gpio_map

        for key in self.gpio_map:
            GPIO.setup(gpio_map[key], GPIO.OUT)
            if gpio_map[key] == 35:
                GPIO.output(gpio_map[key], GPIO.LOW)
            else:
                GPIO.output(gpio_map[key], GPIO.HIGH)

        # Initializing SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        self.spi.max_speed_hz=1000000


    # Function to convert data to voltage level,
    # rounded to specified number of decimal places.
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

    def producer_ai(self, q_ai):
        """
            Producer AI
        """

        self.logger.info('Producer AI called')
        while(True):
            dts = []  # date/time stamp for each start of analog read
            #SE - Stove Exhaust id:12
            dts.append(str(datetime.now()))
            ai0 = self.ReadChannel(0)
            #AC id:5
            dts.append(str(datetime.now()))
            ai1 = self.ReadChannel(1)
            #RF id:10
            dts.append(str(datetime.now()))
            ai2 = self.ReadChannel(2)
            #CW id:13
            dts.append(str(datetime.now()))
            ai3 = self.ReadChannel(3)
            #BATT: phase 1 (black)
            dts.append(str(datetime.now()))
            ai4 = self.ReadChannel(4)
            #Solar: phase 1 (black)
            dts.append(str(datetime.now()))
            ai5 = self.ReadChannel(5)
            #MAINS: phase 1 (red)
            dts.append(str(datetime.now()))
            ai6 = self.ReadChannel(6)
            #MAINS: phase 2 (black)
            dts.append(str(datetime.now()))
            ai7 = self.ReadChannel(7)


            temp_ai = zip(ai0, ai1, ai2, ai3, ai4, ai5, ai6, ai7)
            temp_queue = [temp_ai, dts]

            # logger('Adding AI to the queue')

            try:
                q_ai.put(temp_queue, True, 2)

            except Exception as exc:
                self.logger.exception(exc)
                client.captureException()

            time.sleep(2)

    def RMS(self, data):
        """
            Current RMS calculation for consumer_ai
        """
        # The size of sum_i is the size of the AIN ports
        sum_i = [0, 0, 0, 0, 0, 0, 0, 0]
        for val in data:
            sum_i[0] += math.pow((val[0]-self.adc_Vin/2), 2)
            #sum_i[0] += math.pow((x-1.6 for x in val[0]), 2)
            sum_i[1] += math.pow((val[1]-self.adc_Vin/2), 2)
            sum_i[2] += math.pow((val[2]-self.adc_Vin/2), 2)
            sum_i[3] += math.pow((val[3]-self.adc_Vin/2), 2)
            sum_i[4] += math.pow((val[4]-self.adc_Vin/2), 2)
            sum_i[5] += math.pow((val[5]-self.adc_Vin/2), 2)
            sum_i[6] += math.pow((val[6]-self.adc_Vin/2), 2)
            sum_i[7] += math.pow((val[7]-self.adc_Vin/2), 2)

        # NEED TO INCLUDE CONVERSION FROM CT
        rms_a0 = math.sqrt(sum_i[0] / self.N_SAMPLES)*self.CT10
        rms_a1 = math.sqrt(sum_i[1] / self.N_SAMPLES)*self.CT10
        rms_a2 = math.sqrt(sum_i[2] / self.N_SAMPLES)*self.CT10
        rms_a3 = math.sqrt(sum_i[3] / self.N_SAMPLES)*self.CT10
        rms_a4 = math.sqrt(sum_i[4] / self.N_SAMPLES)*self.CT100
        rms_a5 = math.sqrt(sum_i[5] / self.N_SAMPLES)*self.CT100
        rms_a6 = math.sqrt(sum_i[6] / self.N_SAMPLES)*self.CT100
        rms_a7 = math.sqrt(sum_i[7] / self.N_SAMPLES)*self.CT100

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


    def consumer_ai(self, q_ai):
        """
            Consumer AI
        """
        self.logger.info('Consumer AI called')
        template = [
            {
                "sensor_id": self.input_sources_statesDB['SE1'][1], #SE
                "samples": []
            }, {
                "sensor_id": self.input_sources_statesDB['AC1'][1], #AC
                "samples": []
            }, {
                "sensor_id": self.input_sources_statesDB['RF1'][1], #CW
                "samples": []
            }, {
                "sensor_id": self.input_sources_statesDB['CW1'][1], #RF
                "samples": []
            },  {
                "sensor_id": self.input_sources_statesDB['PW2'][1], # Battery phase 1
                "samples": []
            }, {
                "sensor_id": self.input_sources_statesDB['PV'][1], # Solar phase 1
                "samples": []
            }, {
                "sensor_id": self.input_sources_statesDB['Mains1'][1], #MAINS phase 1 -> Red
                "samples": []
            }, {
                "sensor_id": self.input_sources_statesDB['Mains2'][1], #MAINS phase 2 -> Black
                "samples": []
            }
        ]

        d_fb = copy.deepcopy(template)

        while(True):
            if not q_ai.empty():
                try:
                    temp_cons = q_ai.get(True,2)
                    temp_ai = temp_cons[0]
                    temp_date = temp_cons[1]
                    i_rms = self.RMS(temp_ai)

                    # Writing data to db:
                    for i in range(len(i_rms)):
                        if i_rms[i] >= self.prev[i]+self.dP or i_rms[i] <= self.prev[i]-self.dP:
                            temp_db = [i_rms[i], temp_date[i].split()[0], temp_date[i].split()[1], i+1]
                            try:
                                self.dbWriteMeasurements(temp_db)
                                self.flag_db = 1
                                #print 'try flag: ', self.flag_db
                            except Exception as exc:
                                self.logger.exception(exc)
                                client.captureException()
                    if self.flag_db == 1:
                        self.prev = copy.deepcopy(i_rms)
                        self.flag_db = 0


                    # Adding analog reads, sID and Date to lists for db upload
                    d_fb[0].get("samples").append({"RMS": i_rms[0], "date_time": temp_date[0]}) #SE1
                    d_fb[1].get("samples").append({"RMS": i_rms[1], "date_time": temp_date[1]}) #AC1
                    d_fb[2].get("samples").append({"RMS": i_rms[2], "date_time": temp_date[2]}) #RF1
                    d_fb[3].get("samples").append({"RMS": i_rms[3], "date_time": temp_date[3]}) #CW1
                    d_fb[4].get("samples").append({"RMS": i_rms[4], "date_time": temp_date[4]}) #PW2
                    d_fb[5].get("samples").append({"RMS": i_rms[5], "date_time": temp_date[5]}) #PV
                    d_fb[6].get("samples").append({"RMS": i_rms[6], "date_time": temp_date[6]}) #Mains1 - Red
                    d_fb[7].get("samples").append({"RMS": i_rms[7], "date_time": temp_date[7]}) #Mains2 - Black

                    # Queue is done processing the element
                    q_ai.task_done()
                    #print "length: ", len(d_fb[1]["samples"])
                    if len(d_fb[1]["samples"]) == 10:
                        try:
                            # send the request to the powernet site instead of firebase
                            r_post_rms = requests.post(self.PWRNET_API_BASE_URL + "rms/", json={'devices_json': d_fb}, timeout=self.REQUEST_TIMEOUT)

                            if r_post_rms.status_code == 201:
                                #self.logger.info("Request was successful")
                                pass
                            else:
                                self.logger.exception("Request failed")
                                r_post_rms.raise_for_status()

                            d_fb[:]=[]
                            d_fb = None
                            d_fb = copy.deepcopy(template)

                        except Exception as exc:
                            self.logger.exception(exc)
                            client.captureException()

                            d_fb[:]=[]
                            d_fb = None
                            d_fb = copy.deepcopy(template)

                except Exception as exc:
                    self.logger.exception(exc)
                    client.captureException()

    def devices_th(self, q_batt):
        """
            Devices Status
        """
        self.logger.info('Device Thread called')

        #app_orig_states = ["OFF", "OFF", "ON", "OFF", "OFF", "OFF"] # Battery not included
        #app_new_status = ["OFF", "OFF", "ON", "OFF", "OFF", "OFF"]  # Battery not included

        ################### DONE
        # status_PW2 = "OFF"
        # power_PW2 = 0.0
        # cosphi_PW2 = 1.0
        ###################

        while True:
            try:
                dev_status = requests.get(self.PWRNET_API_BASE_URL + "device", timeout=self.REQUEST_TIMEOUT).json()["results"]
                dts = str(datetime.now())
                ################### DONE
                # status_AC1 = [v for v in dev_status if v['id']==self.input_sources_statesDB['AC1'][1]][0]['status']
                # status_SE1 = [v for v in dev_status if v['id']==self.input_sources_statesDB['SE1'][1]][0]['status']
                # status_RF1 = [v for v in dev_status if v['id']==self.input_sources_statesDB['RF1'][1]][0]['status']
                # status_CW1 = [v for v in dev_status if v['id']==self.input_sources_statesDB['CW1'][1]][0]['status']
                # status_DW1 = [v for v in dev_status if v['id']==self.input_sources_statesDB['DW1'][1]][0]['status']
                # status_WM1 = [v for v in dev_status if v['id']==self.input_sources_statesDB['WM1'][1]][0]['status']
                # # Battery
                # status_PW2 = [v for v in dev_status if v['id']==self.input_sources_statesDB['PW2'][1]][0]['status']
                # power_PW2 = [v for v in dev_status if v['id']==self.input_sources_statesDB['PW2'][1]][0]['value']
                # cosphi_PW2 = [v for v in dev_status if v['id']==self.input_sources_statesDB['PW2'][1]][0]['cosphi']

                status_Fan = [v for v in dev_status if v['id']==self.input_sources_statesDB['Fan_SLAC_H2'][1]][0]['status']
                status_Lights = [v for v in dev_status if v['id']==self.input_sources_statesDB['Lights_SLAC_H2'][1]][0]['status']
                status_Computer = [v for v in dev_status if v['id']==self.input_sources_statesDB['Computer_SLAC_H2'][1]][0]['status']
                ###################

                ################### DONE
                # self.app_new_status = [status_AC1, status_SE1, status_RF1, status_CW1, status_DW1, status_WM1, status_PW2]
                self.app_new_status = [status_Fan, status_Lights, status_Computer]
                print 'Devices new status: ', self.app_new_status
                ###################
                #print 'app_new_status: ', self.app_new_status
                #print 'battery status: ', status_PW2

                for i in range(len(self.app_new_status)):
                    if self.app_new_status[i] != self.app_orig_states[i]:
                        temp_db = [self.app_new_status[i], dts.split()[0], dts.split()[1], self.sourcesDBID[i]]
                        ###################
                        # try:
                        #     if self.appliance_lst[i] == 'PW2':
                        #         temp_q_batt = [status_PW2, "url", power_PW2, cosphi_PW2]
                        #         #print 'q_batt: ', temp_q_batt
                        #         try:
                        #             q_batt.put(temp_q_batt)
                        #             #print 'Success q_batt put'
                        #         except Exception as exc:
                        #             self.logger.exception(exc)
                        #             client.captureException()
                        #     else:
                        #         self.devices_act(self.appliance_lst[i], self.app_new_status[i])
                        try:
                            self.devices_act(self.appliance_lst[i], self.app_new_status[i])
                        ###################

                            ################### DONE
                            #self.dbWriteStates(temp_db)
                            self.flag_state = 1
                            ###################

                            #print 'try flag: ', self.flag_state
                        except Exception as exc:
                            self.logger.exception(exc)
                            client.captureException()
                if self.flag_state == 1:
                    #print 'app_orig_states: ', self.app_orig_states
                    self.app_orig_states = copy.deepcopy(self.app_new_status)
                    #print 'app_orig_states_new: ', self.app_orig_states
                    self.flag_state = 0

            except Exception as exc:
                self.logger.exception(exc)
                client.captureException()

            time.sleep(2)   # Delay between readings


    def devices_act(self, device, state):
        GPIO.output(self.gpio_map[device], GPIO.LOW if state == 'ON' else GPIO.HIGH)
