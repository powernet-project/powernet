"""
Setup the Hardware interface
"""
from __future__ import print_function

__author__ = 'Gustavo C. & Jonathan G. '
__copyright__ = 'Stanford University'
__version__ = '0.2'
__email__ = 'gcezar@stanford.edu, jongon@stanford.edu'
__status__ = 'Beta'

import math
import time
import copy
import json
import spidev
import logging
import sqlite3
import requests
import numpy as np
import RPi.GPIO as GPIO

from raven import Client
from sqlite3 import Error
from datetime import datetime
from google.cloud import pubsub_v1
from api_storage import StorageInterface
from api_network import NetworkInterface as api

# Global variables
SENTRY_DSN = 'https://e3b3b7139bc64177b9694b836c1c5bd6:fbd8d4def9db41d0abe885a35f034118@sentry.io/230474'
client = Client(SENTRY_DSN)

logger = logging.getLogger('HOME_HUB_APPLICATION_LOGGER')

class HardwareInterface:
    def __init__(self, house_id, gpio_map = None, N_SAMPLES = 100, auth_token = None):
        # initialize the logger
        self.logger = logger
        self.logger.info('HardwareRPi class called')
        
        # initialize the network api
        api(auth_token)
        
        # initialize our internal interface vars
        self.CONVERTION = 1.8/4095.0
        self.CT10 = 10   # 10A/1V
        self.CT20 = 20   # 20A/1V
        self.CT50 = 50   # 50A/1V
        self.CT100 = 100 # 100A/1V
        self.SENTRY_DSN = 'https://e3b3b7139bc64177b9694b836c1c5bd6:fbd8d4def9db41d0abe885a35f034118@sentry.io/230474'

        self.app_orig_states = ["OFF", "OFF", "OFF"]
        self.app_new_status = ["OFF", "OFF", "OFF"]
        
        # input_sources_statesDB GC -> 'api_appliance_name':[db_id,api_id]
        self.input_sources_statesDB = {'DW_GC': [3,40], 'RF_GC': [4,41], 'LT_GC':[5,42], 'MW_GC':[6,43],'WD1_GC':[7,44], 'WD2_GC': [8,45], 'Range1_GC':[9,46], 'Range2_GC':[10,47]}
        self.sourcesDBID = [self.input_sources_statesDB['DW_GC'][0],self.input_sources_statesDB['RF_GC'][0],self.input_sources_statesDB['LT_GC'][0],self.input_sources_statesDB['MW_GC'][0],self.input_sources_statesDB['WD1_GC'][0],self.input_sources_statesDB['WD2_GC'][0],self.input_sources_statesDB['Range1_GC'][0],self.input_sources_statesDB['Range2_GC'][0]]
        self.input_sources_measurements = []
        #self.appliance_lst = ["AC1", "SE1", "RF1", "CW1", "DW1", "WM1", "PW2"]
        self.appliance_lst = ["DW_GC", "RF_GC", "LT_GC", "MW_GC", "DR1_GC", "DR2_GC", "Range1_GC", "Range2_GC"]
        
        # Database variables:
        self.flag_db = 0
        self.prev = [-1,-1,-1,-1,-1,-1,-1,-1]
        self.dP = 0.3
        self.flag_state = 0

        # Creating home init variables:
        self.house_name = "HHLab"
        self.house_id = house_id                # This one changes depending on house number

        # Initializing GPIOs:
        GPIO.setmode(GPIO.BOARD)

        self.N_SAMPLES = N_SAMPLES
        self.adc_Vin = 3.3
        self.delay = 0.002

        gpio_map = [11,13,15,29,31,33,35,37]
        for i in gpio_map:
            GPIO.setup(i, GPIO.OUT)
            if i == 35:
                GPIO.output(i, GPIO.LOW)
            else:
                GPIO.output(i, GPIO.HIGH)

        # Initializing SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        self.spi.max_speed_hz=1000000

        # Initializing devices and DB (create DB if does not exist already):
        self.hh_devices_init(self.house_id, self.house_name)

        # Creating battery class:
        self.batt = StorageInterface(auth_token=auth_token)

        # Pubsub subscription:
        self.sub = 'HH' + str(self.house_id)

    
    def ConvertVolts(self, data,places):
        """
        Function to convert data to voltage level,
        rounded to specified number of decimal places.
        """
        volts = (data * self.adc_Vin) / float(1023)
        volts = np.around(volts, places)
        return volts

    
    def ReadChannel(self, channel):
        """
        Function to read SPI data from MCP3008 chip
        Channel must be an integer 0-7
        """
        n = 0
        data = np.zeros(self.N_SAMPLES)
      
        while(n < 100):
            adc = self.spi.xfer2([1, (8 + channel) << 4, 0])
            data[n]=((adc[1] & 3) << 8) + adc[2]
            n += 1
            time.sleep(self.delay)
        return self.ConvertVolts(data, 2)

    def producer_ai(self, q_ai):
        """
        Producer AI
        """
        self.logger.info('Producer AI called')
        while(True):
            dts = []  # date/time stamp for each start of analog read
            #DW
            dts.append(str(datetime.now()))
            ai0 = self.ReadChannel(0)
            #RF
            dts.append(str(datetime.now()))
            ai1 = self.ReadChannel(1)
            #LT
            dts.append(str(datetime.now()))
            ai2 = self.ReadChannel(2)
            #MW
            dts.append(str(datetime.now()))
            ai3 = self.ReadChannel(3)
            #WD1
            dts.append(str(datetime.now()))
            ai4 = self.ReadChannel(4)
            #WD2
            dts.append(str(datetime.now()))
            ai5 = self.ReadChannel(5)
            #Range1
            dts.append(str(datetime.now()))
            ai6 = self.ReadChannel(6)
            #Range2
            dts.append(str(datetime.now()))
            ai7 = self.ReadChannel(7)


            temp_ai = zip(ai0, ai1, ai2, ai3, ai4, ai5, ai6, ai7)
            temp_queue = [temp_ai, dts]

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

        # Computing RMS and converting to AMPS
        rms_a0 = math.sqrt(sum_i[0] / self.N_SAMPLES)*self.CT10
        rms_a1 = math.sqrt(sum_i[1] / self.N_SAMPLES)*self.CT10
        rms_a2 = math.sqrt(sum_i[2] / self.N_SAMPLES)*self.CT10
        rms_a3 = math.sqrt(sum_i[3] / self.N_SAMPLES)*self.CT10
        rms_a4 = math.sqrt(sum_i[4] / self.N_SAMPLES)*self.CT50
        rms_a5 = math.sqrt(sum_i[5] / self.N_SAMPLES)*self.CT50
        rms_a6 = math.sqrt(sum_i[6] / self.N_SAMPLES)*self.CT50
        rms_a7 = math.sqrt(sum_i[7] / self.N_SAMPLES)*self.CT50

        return [rms_a0, rms_a1, rms_a2, rms_a3, rms_a4, rms_a5, rms_a6, rms_a7]


    def dbWriteMeasurements(self, vals):
        try:
            conn = sqlite3.connect('homehubDB.db')
            c = conn.cursor()
            c.execute("INSERT INTO measurements (rms, currentdate, currenttime, source_id) VALUES ((?), (?), (?), (?))" , (vals[0], vals[1], vals[2], vals[3]))
        except sqlite3.IntegrityError:
            self.logger.error('error connecting to db')
        conn.commit()
        conn.close()


    def dbWriteStates(self, vals):
        try:
            conn = sqlite3.connect('homehubDB.db')
            c = conn.cursor()
            c.execute("INSERT INTO input_sources_state (state, currentdate, currenttime, source_id) VALUES ((?), (?), (?), (?))" , (vals[0], vals[1], vals[2], vals[3]))
        except sqlite3.IntegrityError:
            self.logger.error('error connecting to db')
        conn.commit()
        conn.close()


    def consumer_ai(self, q_ai):
        """
        Consumer AI
        """
        self.logger.info('Consumer AI called')
        template = [
            {
                "sensor_id": self.input_sources_measurements[1][0],
                "average": {},
                "samples": []
            }, {
                "sensor_id": self.input_sources_measurements[1][1],
                "average": {},
                "samples": []
            }, {
                "sensor_id": self.input_sources_measurements[1][2],
                "average": {},
                "samples": []
            }, {
                "sensor_id": self.input_sources_measurements[1][3],
                "average": {},
                "samples": []
            },  {
                "sensor_id": self.input_sources_measurements[1][4],
                "average": {},
                "samples": []
            }, {
                "sensor_id": self.input_sources_measurements[1][5],
                "average": {},
                "samples": []
            }, {
                "sensor_id": self.input_sources_measurements[1][6],
                "average": {},
                "samples": []
            }, {
                "sensor_id": self.input_sources_measurements[1][7],
                "average": {},
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
                        if i_rms[i] >= self.prev[i] + self.dP or i_rms[i] <= self.prev[i] - self.dP:
                            temp_db = [i_rms[i], temp_date[i].split()[0], temp_date[i].split()[1], i + 1]
                            try:
                                self.dbWriteMeasurements(temp_db)
                                self.flag_db = 1
                            except Exception as exc:
                                self.logger.exception(exc)
                                client.captureException()
                    if self.flag_db == 1:
                        self.prev = copy.deepcopy(i_rms)
                        self.flag_db = 0


                    # Adding analog reads, sID and Date to lists for db upload
                    d_fb[0].get("samples").append({"RMS": i_rms[0], "date_time": temp_date[0]})
                    d_fb[1].get("samples").append({"RMS": i_rms[1], "date_time": temp_date[1]})
                    d_fb[2].get("samples").append({"RMS": i_rms[2], "date_time": temp_date[2]})
                    d_fb[3].get("samples").append({"RMS": i_rms[3], "date_time": temp_date[3]})
                    d_fb[4].get("samples").append({"RMS": i_rms[4], "date_time": temp_date[4]})
                    d_fb[5].get("samples").append({"RMS": i_rms[5], "date_time": temp_date[5]})
                    d_fb[6].get("samples").append({"RMS": i_rms[6], "date_time": temp_date[6]})
                    d_fb[7].get("samples").append({"RMS": i_rms[7], "date_time": temp_date[7]})

                    # Queue is done processing the element
                    q_ai.task_done()

                    if len(d_fb[1]["samples"]) == 10:
                        # Computing average and adding to json for cloud
                        for i in range(len(d_fb)):
                            sm = self.sensor_mean(d_fb[i]['samples'])
                            dt = d_fb[i]['samples'][-1]['date_time']
                            d_fb[i]['average'] = {'RMS': sm, 'date_time': dt}
                            
                        try:
                            api.save_rms({'devices_json': d_fb, 'home': self.house_id})
                        except Exception as exc:
                            self.logger.exception(exc)
                            client.captureException()
                        finally:
                            d_fb[:]=[]
                            d_fb = None
                            d_fb = copy.deepcopy(template)

                except Exception as exc:
                    self.logger.exception(exc)
                    client.captureException()

    def sensor_mean(self, data):
        """
        Function to give average of samples sent to cloud -> used in consumer_ai
        """
        s = []
        for i in data:
            s.append(i['RMS'])
        return sum(s) / len(s)

    def devices_th(self):
        """
        Devices Status
        """
        self.logger.info('Device Thread called')
        # Google Pubsub -> To replace devices thread
        try:
            subscriber = pubsub_v1.SubscriberClient()
            subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
                project_id='pwrnet-158117',
                sub=self.sub,  # Set this to something appropriate.
            )
            subscriber.subscribe(subscription_name, callback=self.callback)
        except Exception as exc:
            self.logger.exception(exc)
            client.captureException()
            self.logger.error("Exception GCP: ", exc)

        while True:
            time.sleep(2)   # Delay between readings


    def devices_act(self, device, state):
        self.logger.info("device: ", device)
        self.logger.info("state: ", state)
        GPIO.output(self.input_sources_measurements[2][device-1], GPIO.LOW if state == 'ON' else GPIO.HIGH)

    def callback(self, message):
        dts = str(datetime.now())
        data = json.loads(message.data)
        self.logger.info('data: ', data)
        load_state = data['status']
        load_name = data['name']
        load_type = data['type']
        load_home = data['home']
        load_id = data['id']
        load_val = data['value']
        load_cPhi = data['cosphi']
        message.ack()

        if load_home == self.house_id:                                      # Chekcing whether the change is in the home we are interested in
            if load_type == 'SDF':                                          # Actuate in the relay controlled loads
                self.devices_act(int(load_name[-1]), load_state)
                # As of now just writing the relay devices states to db
                self.dbWriteStates([load_state, dts.split()[0], dts.split()[1], self.input_sources_measurements[1][int(load_name[-1])-1]])
            elif load_type == 'STORAGE':
                try:
                    # Comment the line below if no battery in range
                    self.batt.battery_act([load_state, "url", load_val, load_cPhi,load_id])     # Still needs to figure timing issue modbus
                except Exception as exc:
                    self.logger.exception(exc)
                    client.captureException()
            elif self.house_id == 1:
                idx = self.input_sources_measurements[0].index(int(load_id))
                self.devices_act(idx + 1, load_state)
                # As of now just writing the relay devices states to db
                self.dbWriteStates([load_state, dts.split()[0], dts.split()[1], self.input_sources_measurements[1][int(load_name[-1]) - 1]])

            else:                                                          
                self.logger.info("Other devices such as Z-Wave plugs")  # Actuate in any other load category



    def hh_devices_init(self, house_id, house_name):
        # dev_info = {"id": 48, "name": "Test_Dev", "type": "AIR_CONDITIONER", "status": "OFF", "value": 0, "cosphi": 1.0, "home": 2}
        # Getting all device information from cloud
        dev_status = api.get_device_status()
        home_devID = []
        name_devID = []
        type_devID = []
        print("dev_status", dev_status)
        for h in dev_status:
            if h['home'] == house_id:       # Checking if there is any device in house with house_id and include device id in list
                home_devID.append(h['id'])
                type_devID.append(h['type'])
                name_devID.append(h['name'])
        self.logger.info("homeDevID: ", home_devID)
        if home_devID:                      # If devices list is not empty (meaning that a house with devices is already created) dont create any dev
            try:                            # Check if DB exists in HH
                conn = sqlite3.connect('homehubDB.db')
                c = conn.cursor()
                lst_db = c.execute("SELECT * FROM 'input_sources'")  # HERE: If doesnt throw error need to check whether the number of rows in the list matches number of dev id. If different need to create additional ones based on the id's that are missing
            except Exception as exc:
                self.logger.error(exc)
                self.logger.exception(exc)
                client.captureException()
                self.create_table(conn)                  # Creating tables
                for d in range(len(home_devID)):    # Create rows for each dev in the home
                    vals=[type_devID[d],name_devID[d],home_devID[d]]
                    self.input_sources_insert(c,vals)
                conn.commit()
                conn.close()
                self.input_sources_measurements.append(home_devID)           # Adding device ID
                self.input_sources_measurements.append(range(len(home_devID)+1)[1:])    # Adding local DB ID
                if house_id == 1:
                    self.input_sources_measurements.append([33, 35, 37, 29, 31, 0, 0, 38]) # GPIO port -> fixed
                else: 
                    self.input_sources_measurements.append([37, 35, 33, 31, 29, 15, 13, 11]) # GPIO port -> fixed
                return
            # DB  table exists
            db_is = lst_db.fetchall()       # retireve all input_source table data
            self.logger.info(db_is)
            l_db_api_id = []
            l_db_prm_key = []
            if len(db_is):
                for i in db_is:
                    l_db_api_id.append(int(i[-1]))      # list with all api ids from db
                    l_db_prm_key.append(i[0])           # list with all primary keys from db
                diff_apidb = sorted(list(set(home_devID)-set(l_db_api_id)))     # Checking difference between get request and db (need to address difference between db and get as well)
                # diff_apidb.append(71)       # test case
                # diff_apidb.append(72)       # test case
                self.logger.info('diff_apidb: ', diff_apidb)
                if diff_apidb:
                    for i in diff_apidb:
                        vals = [type_devID[home_devID.index(i)], name_devID[home_devID.index(i)], i]
                        self.logger.info('vals: ', vals)
                        self.input_sources_insert(c, vals)
                        l_db_prm_key.append(c.lastrowid)
                    conn.commit()
                    conn.close()
                    self.input_sources_measurements.append(home_devID)           # Adding device ID
                    self.input_sources_measurements.append(l_db_prm_key)         # Adding local DB ID
                    if house_id == 1:
                        self.input_sources_measurements.append([33, 35, 37, 29, 31, 0, 0, 38]) # GPIO port -> fixed
                    else:    
                        self.input_sources_measurements.append([37, 35, 33, 31, 29, 15, 13, 11]) # GPIO port -> fixed    

        else:
            # If device list is empty means it needs to create new devices in the server and local db
            home_devID = self.create_devices(8)  # Create 8 devices -> there are 8 channels in the ADC and 8 relays
            if home_devID:
                conn = sqlite3.connect('homehubDB.db')
                c = conn.cursor()
                self.create_table(conn)                  # Creating tables
                for d in range(len(home_devID)):    # Create rows for each dev in the home
                    vals = [type_devID[d], name_devID[d], home_devID[d]]
                    self.input_sources_insert(c, vals)
                conn.commit()
                conn.close()
            else:
                self.logger.info('problem in creating devices. Check POST request')
                pass

        self.input_sources_measurements.append(home_devID)           # Adding device ID
        self.input_sources_measurements.append([1, 2, 3, 4, 5, 6, 7, 8])    # Adding local DB ID
        if house_id == 1:
            self.input_sources_measurements.append([33, 35, 37, 29, 31, 0, 0, 38]) # GPIO port -> fixed
        else: 
            self.input_sources_measurements.append([37, 35, 33, 31, 29, 15, 13, 11]) # GPIO port -> fixed

    def create_devices(self, number_of_devices, house_devstatus = 'ON'):
        device = { "status": None, "name": None, "type": None, "value": None, "home": None, "cosphi": None }
        devID = []
        for i in range(number_of_devices+1)[1:]:
            dev = copy.deepcopy(device)
            dev['name'] = self.house_name+str(self.house_id)+'_dev'+str(i)
            dev['home'] = self.house_id
            dev['status'] = house_devstatus
            dev['type'] = "SDF"
            dev['value'] = 0
            dev['cosphi'] = 1.0
            
            saved_device = api.save_devices(dev)
            if saved_device is not None:
                devID.append(saved_device)
            
        return devID


    def createDB(self):
        SQL_File_Name = 'table_schema.sql'
        TableSchema=""
        with open(SQL_File_Name, 'r') as SchemaFile:
            TableSchema=SchemaFile.read().replace('\n','')

        """ create a database connection to a SQLite database """
        try:
            conn = sqlite3.connect('homehubDB.db')
            c = conn.cursor()
            c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='input_sources'")
            if c.fetchone()[0]==0:
                sqlite3.complete_statement(TableSchema)
                c.executescript(TableSchema)
        except Error as e:
            self.logger.exception(e)
            client.captureException()
            self.logger.error(e)
        finally:
            c.close()
            conn.close()

    def create_table(self, conn):
        SQL_File_Name = 'create_table_sql.sql'
        TableSchema=""
        with open(SQL_File_Name, 'r') as SchemaFile:
            TableSchema=SchemaFile.read().replace('\n','')
        try:
            c = conn.cursor()
            sqlite3.complete_statement(TableSchema)
            c.executescript(TableSchema)
        except Error as e:
            self.logger.error(e)

    def input_sources_insert(self,c,vals):
        c.execute("INSERT INTO input_sources (type, name, api_id) VALUES ((?), (?), (?))" , (vals[0], vals[1], vals[2]))
