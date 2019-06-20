import requests
from django.conf import settings
import datetime
from xml.etree import ElementTree as ET
from requests.auth import HTTPDigestAuth
import time
import json

class EgaugeInterface():

    def __init__(self, url=None, username=None, password=None, t_sample=5):
        # Initializing credentials
        self.url = url
        self.username = username
        self.password = password

        # Initializing parameters
        self.t_sample = t_sample
        self.keys = ['L1 Voltage', 'L2 Voltage', 'Power Circuit 1', 'Power Circuit 1*', 'Power Circuit 2',
                     'Power Circuit 2*', 'Power Circuit 1 neutral', 'Shed Power', 'Control Fan Power',
                     'Control Fan Power*', 'ts']

    # Function to get and format e-gauge data
    def get_egauge_data(self, request):
        power_values = dict.fromkeys(self.keys, None)
        root = ET.fromstring(request.text)
        timestamp = root.findtext("ts")

        if timestamp != None:
            for r in root.findall('r'):
                for child in r:
                    if r.get('n') == 'L1 Voltage':
                        power_values['L1 Voltage'] = (int(child.text))
                    elif r.get('n') == 'L2 Voltage':
                        power_values['L2 Voltage'] = (int(child.text))
                    elif r.get('n') == 'Power Circuit 1':
                        power_values['Power Circuit 1'] = (int(child.text))
                    elif r.get('n') == 'Power Circuit 1*':
                        power_values['Power Circuit 1*'] = (int(child.text))
                    elif r.get('n') == 'Power Circuit 2':
                        power_values['Power Circuit 2'] = (int(child.text))
                    elif r.get('n') == 'Power Circuit 2*':
                        power_values['Power Circuit 2*'] = (int(child.text))
                    elif r.get('n') == 'Power Circuit 1 neutral':
                        power_values['Power Circuit 1 neutral'] = (int(child.text))
                    elif r.get('n') == 'Shed Power':
                        power_values['Shed Power'] = (int(child.text))
                    elif r.get('n') == 'Control Fan Power':
                        power_values['Control Fan Power'] = (int(child.text))
                    elif r.get('n') == 'Control Fan Power*':
                        power_values['Control Fan Power*'] = (int(child.text))

            power_values['ts'] = int(timestamp)

        else:
            print('No values from request')

        return power_values

    # Function to process data from e-gauge and convert to useful power values
    def processing_egauge_data(self):
        power_values = dict.fromkeys(self.keys, None)
        try:
            resp = requests.get(self.url, auth=HTTPDigestAuth(self.username, self.password))
            resp.raise_for_status()
            data_ini = self.get_egauge_data(resp)

        except requests.exceptions.HTTPError as err:
            print(err)
            return json.dumps(power_values)

        time.sleep(self.t_sample)

        try:
            resp = requests.get(self.url, auth=HTTPDigestAuth(self.username, self.password))
            resp.raise_for_status()
            data_end = self.get_egauge_data(resp)

        except requests.exceptions.HTTPError as err:
            print(err)
            return json.dumps(power_values)

        ts_delta = data_end['ts'] - data_ini['ts']
        try:
            int(ts_delta)
            power_values['ts'] = datetime.datetime.fromtimestamp(int(data_end['ts'])).strftime('%Y-%m-%d %H:%M:%S')
            power_values['L1 Voltage'] = ((data_end['L1 Voltage'] - data_ini['L1 Voltage']) / ts_delta) / 1000
            power_values['L2 Voltage'] = ((data_end['L2 Voltage'] - data_ini['L2 Voltage']) / ts_delta) / 1000
            power_values['Power Circuit 1'] = (data_end['Power Circuit 1'] - data_ini['Power Circuit 1']) / ts_delta
            power_values['Power Circuit 1*'] = (data_end['Power Circuit 1*'] - data_ini['Power Circuit 1*']) / ts_delta
            power_values['Power Circuit 2'] = (data_end['Power Circuit 2'] - data_ini['Power Circuit 2']) / ts_delta
            power_values['Power Circuit 2*'] = (data_end['Power Circuit 2*'] - data_ini['Power Circuit 2*']) / ts_delta
            power_values['Power Circuit 1 neutral'] = (data_end['Power Circuit 1 neutral'] - data_ini[
                'Power Circuit 1 neutral']) / ts_delta
            power_values['Shed Power'] = (data_end['Shed Power'] - data_ini['Shed Power']) / ts_delta
            power_values['Control Fan Power'] = (data_end['Control Fan Power'] - data_ini[
                'Control Fan Power']) / ts_delta
            power_values['Control Fan Power*'] = (data_end['Control Fan Power*'] - data_ini[
                'Control Fan Power*']) / ts_delta

            json_dict = json.dumps(power_values)
            return json.dumps(power_values)

        except Exception as e:
            print('Error retrieving data from E-Gauge API', e)
            return None

def update_egauge_data():
    from app.models import FarmDevice
    try:
        egauge_data = EgaugeInterface(url=settings.EGAUGE_URL, username=settings.EGAUGE_USER, password=settings.EGAUGE_PASSWORD).processing_egauge_data()
        print('egauge data: ', egauge_data)

    except Exception as e:
        print('Error retireving data from egauge api')


    if egauge_data is not None:
        try:
            farm_device = FarmDevice.objects.get(device_uid='46613')
            farm_device.device_data = egauge_data
            farm_device.save()
            print('saving...\n', farm_device)

        except FarmDevice.DoesNotExist as e:
            print('Error update_egauge_data', e)
            pass

