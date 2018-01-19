import beaglebone_pru_adc as adc
import Adafruit_BBIO.GPIO as GPIO
import math
import time
import copy
import requests
import logging
from raven import Client
from datetime import datetime
from firebase import Firebase as fb

# Global variables
SENTRY_DSN = 'https://e3b3b7139bc64177b9694b836c1c5bd6:fbd8d4def9db41d0abe885a35f034118@sentry.io/230474'
client = Client(SENTRY_DSN)

class HardwareBBB:

    def __init__(self, gpio_map = None, N_SAMPLES = 100):
        self.CONVERTION = 1.8/4095.0
        self.CT10 = 10   # 10A/1V
        self.CT20 = 20   # 20A/1V
        self.REQUEST_TIMEOUT = 10
        self.FB_API_BASE_URL = 'https://fb-powernet.firebaseio.com/'
        self.PWRNET_API_BASE_URL = 'http://pwrnet-158117.appspot.com/api/v1/'
        self.SENTRY_DSN = 'https://e3b3b7139bc64177b9694b836c1c5bd6:fbd8d4def9db41d0abe885a35f034118@sentry.io/230474'
        logging.info('HardwareBBB class called')

        # Sentry setup for additional error reporting via 3rd party cloud service
        # self.client = Client(self.SENTRY_DSN)

        # Initializing GPIOs:
        self.appliance_lst = ["AC1", "SE1", "RF1" ,"CW1", "DW1"]

        self.N_SAMPLES = N_SAMPLES
        if gpio_map == None:
            self.gpio_map = {"CW1": "P8_9", "DW1": "P8_10", "AC1": "P8_15",
            "RF1": "P8_14", "SE1": "P8_11"}
        else:
            self.gpio_map = gpio_map

        for key in self.gpio_map:
            GPIO.setup(gpio_map[key], GPIO.OUT)
            GPIO.output(gpio_map[key], GPIO.HIGH)

    def analog_read(self, off_value):
        logging.info('Analog read called')
        capture = adc.Capture()
        capture.cap_delay = 50000
        capture.oscilloscope_init(adc.OFF_VALUES + off_value, self.N_SAMPLES)
        capture.start()

        while not capture.oscilloscope_is_complete():
            False  # This is a dumb condition just to keep the loop running

        capture.stop()
        capture.wait()
        capture.close()
        return capture.oscilloscope_data(self.N_SAMPLES)

    def relay_act(self, device, state):
        GPIO.output(self.gpio_map[device], GPIO.LOW if state == 'ON' else GPIO.HIGH)

    # Thread Producer_AI
    def producer_ai(self, format_ai, q_ai):
        logging.info('Producer AI called')
        while(True):
            dts = []  # date/time stamp for each start of analog read
            # AC id:5
            dts.append(str(datetime.now()))
            ai0 = self.analog_read(format_ai[0])
            # SE - Stove Exhaust id:12
            dts.append(str(datetime.now()))
            ai1 = self.analog_read(format_ai[1])
            # RF id:10
            dts.append(str(datetime.now()))
            ai2 = self.analog_read(format_ai[2])
            # CW id:13
            dts.append(str(datetime.now()))
            ai3 = self.analog_read(format_ai[3])
            # RA - 1
            dts.append(str(datetime.now()))
            ai4 = self.analog_read(format_ai[4])
            # RA - 2
            dts.append(str(datetime.now()))
            ai5 = self.analog_read(format_ai[5])
            # DW id:14
            dts.append(str(datetime.now()))
            ai6 = self.analog_read(format_ai[6])

            temp_ai = zip(ai0, ai1, ai2, ai3, ai4, ai5, ai6)
            temp_queue = [temp_ai, dts]

            # logger('Adding AI to the queue')

            try:
                q_ai.put(temp_queue, True, 2)

            except Exception as exc:
                logging.exception(exc)
                client.captureException()

            time.sleep(2)

    def RMS(self, data):
        # The size of sum_i is the size of the AIN ports
        sum_i = [0, 0, 0, 0, 0, 0, 0]
        for val in data:
            sum_i[0] += math.pow((val[0] * self.CONVERTION - 0.89), 2)
            sum_i[1] += math.pow((val[1] * self.CONVERTION - 0.89), 2)
            sum_i[2] += math.pow((val[2] * self.CONVERTION - 0.89), 2)
            sum_i[3] += math.pow((val[3] * self.CONVERTION - 0.89), 2)
            sum_i[4] += math.pow((val[4] * self.CONVERTION - 0.89), 2)
            sum_i[5] += math.pow((val[5] * self.CONVERTION - 0.89), 2)
            sum_i[6] += math.pow((val[6] * self.CONVERTION - 0.89), 2)

        rms_a0 = math.sqrt(sum_i[0] / self.N_SAMPLES) * self.CT10 * 2
        rms_a1 = math.sqrt(sum_i[1] / self.N_SAMPLES) * self.CT10 * 2
        rms_a2 = math.sqrt(sum_i[2] / self.N_SAMPLES) * self.CT10 * 2
        rms_a3 = math.sqrt(sum_i[3] / self.N_SAMPLES) * self.CT10 * 2
        rms_a4 = math.sqrt(sum_i[4] / self.N_SAMPLES) * self.CT20 * 2
        rms_a5 = math.sqrt(sum_i[5] / self.N_SAMPLES) * self.CT20 * 2
        rms_a6 = math.sqrt(sum_i[6] / self.N_SAMPLES) * self.CT10 * 2

        return [rms_a0, rms_a1, rms_a2, rms_a3, rms_a4, rms_a5, rms_a6]

    def consumer_ai(self, q_ai):
        logging.info('Consumer AI called')
        template = [
            {
                "sensor_id": 5,     # AC
                "samples": []
            }, {
                "sensor_id": 12,    # SE
                "samples": []
            }, {
                "sensor_id": 13,    # CW
                "samples": []
            }, {
                "sensor_id": 10,    # RF
                "samples": []
            },  {
                "sensor_id": 3,     # Range_1 leg
                "samples": []
            }, {
                "sensor_id": 4,     # Range_2 leg
                "samples": []
            }, {
                "sensor_id": 14,    # DW
                "samples": []
            }
        ]

        d_fb = copy.deepcopy(template)

        while True:
            if not q_ai.empty():
                try:
                    temp_cons = q_ai.get(True,2)
                    temp_ai = temp_cons[0]
                    temp_date = temp_cons[1]

                    i_rms = self.RMS(temp_ai[1:])

                    # Adding analog reads, sID and Date to lists for db upload
                    d_fb[0].get("samples").append({"RMS": i_rms[0], "date_time": temp_date[0]})
                    d_fb[1].get("samples").append({"RMS": i_rms[1], "date_time": temp_date[1]})
                    d_fb[2].get("samples").append({"RMS": i_rms[2], "date_time": temp_date[2]})
                    d_fb[3].get("samples").append({"RMS": i_rms[3], "date_time": temp_date[3]})
                    d_fb[4].get("samples").append({"RMS": i_rms[4], "date_time": temp_date[4]})
                    d_fb[5].get("samples").append({"RMS": i_rms[5], "date_time": temp_date[5]})
                    d_fb[6].get("samples").append({"RMS": i_rms[6], "date_time": temp_date[6]})

                    # Queue is done processing the element
                    q_ai.task_done()

                    if len(d_fb[1]["samples"]) == 10:
                        try:
                            # send the request to the powernet site instead of firebase
                            r_post_rms = requests.post(self.PWRNET_API_BASE_URL + "rms/", json={'devices_json': d_fb}, timeout=self.REQUEST_TIMEOUT)

                            if r_post_rms.status_code == 201:
                                # logger.info("Request was successful")
                                pass
                            else:
                                logging.exception("Request failed")
                                r_post_rms.raise_for_status()

                            d_fb[:]=[]
                            d_fb = None
                            d_fb = copy.deepcopy(template)

                        except Exception as exc:
                            logging.exception(exc)
                            client.captureException()

                            d_fb[:]=[]
                            d_fb = None
                            d_fb = copy.deepcopy(template)

                except Exception as exc:
                    logging.exception(exc)
                    client.captureException()

    def relay_th(self):
        """
            Relay Status
        """

        logging.info('Relay Thread called')

        app_orig_states = ["OFF", "OFF", "ON", "OFF", "OFF", "OFF"]
        app_new_status = ["OFF", "OFF", "ON", "OFF", "OFF", "OFF"]

        while True:
            try:
                dev_status = requests.get(self.PWRNET_API_BASE_URL + "device", timeout=self.REQUEST_TIMEOUT).json()["results"]

                status_AC1 = [v for v in dev_status if v['id']==5][0]['status']
                status_SE1 = [v for v in dev_status if v['id']==12][0]['status']
                status_RF1 = [v for v in dev_status if v['id']==10][0]['status']
                status_CW1 = [v for v in dev_status if v['id']==13][0]['status']
                status_DW1 = [v for v in dev_status if v['id']==14][0]['status']

                app_new_status = [status_AC1, status_SE1, status_RF1, status_CW1, status_DW1]

            except Exception as exc:
                logging.exception(exc)
                client.captureException()

            for index, (first, second) in enumerate(zip(app_orig_states, app_new_status)):
                if first != second:
                    self.relay_act(self.appliance_lst[index], second)
                    app_orig_states = copy.deepcopy(app_new_status)

            time.sleep(2)
