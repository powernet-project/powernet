import requests
from django.conf import settings
import datetime
from xml.etree import ElementTree as ET
from requests.auth import HTTPDigestAuth
import json


class EgaugeInterface():

    def __init__(self, url=None, username=None, password=None, t_sample=5):
        # Initializing credentials
        self.url = url
        self.username = username
        self.password = password

        # Initializing parameters
        self.t_sample = t_sample
        self.keys_db = ['raw', 'processed']
        self.keys = ['L1 Voltage', 'L2 Voltage', 'Power Circuit 1', 'Power Circuit 1*', 'Power Circuit 2',
                     'Power Circuit 2*', 'Power Circuit 1 neutral', 'Shed Power', 'Control Fan Power',
                     'Control Fan Power*', 'ts']

    # Function to get and format e-gauge data
    def get_egauge_data(self, request):
        power_values = dict.fromkeys(self.keys, None)
        root = ET.fromstring(request.text)
        timestamp = root.findtext("ts")

        if timestamp is not None:
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

    def delete_eguage_db_entries(self):
        from app.models import FarmDevice
        from app.models import DeviceType

        FarmDevice.objects.filter(type=DeviceType.EGAUGE).delete()

    def request_egauge_data(self):
        try:
            resp = requests.get(self.url, auth=HTTPDigestAuth(self.username, self.password))
            resp.raise_for_status()
            return self.get_egauge_data(resp)

        except requests.exceptions.HTTPError as err:
            print(err)
            return None

    # Function to process data from e-gauge and convert to useful power values
    def processing_egauge_data(self):
        from app.models import FarmDevice
        from app.models import DeviceType

        # self.delete_eguage_db_entries()
        power_values = dict.fromkeys(self.keys, None)
        egauge_data = dict.fromkeys(self.keys_db, None)

        try:
            resp = requests.get(self.url, auth=HTTPDigestAuth(self.username, self.password))
            resp.raise_for_status()
            data_current = self.get_egauge_data(resp)
            egauge_data['raw'] = data_current
        except requests.exceptions.HTTPError as err:
            print(err)
            return json.dumps(egauge_data)

        queryset = FarmDevice.objects.filter(type=DeviceType.EGAUGE).order_by('-id')[0].device_data
        if queryset is None:
            print('Error, no egauge data in DB...')
            return json.dumps(egauge_data)

        data_prev = json.loads(queryset)['raw']

        ts_delta = data_current['ts'] - data_prev['ts']

        power_values['ts'] = data_current['ts']
        power_values['timestamp'] = datetime.datetime.fromtimestamp(int(data_current['ts'])
                                                                    ).strftime('%Y-%m-%d %H:%M:%S')
        power_values['L1 Voltage'] = ((data_current['L1 Voltage'] - data_prev['L1 Voltage']) / ts_delta) / 1000
        power_values['L2 Voltage'] = ((data_current['L2 Voltage'] - data_prev['L2 Voltage']) / ts_delta) / 1000
        power_values['Power Circuit 1'] = (data_current['Power Circuit 1'] - data_prev['Power Circuit 1']) / ts_delta
        power_values['Power Circuit 1*'] = (data_current['Power Circuit 1*'] - data_prev['Power Circuit 1*']) / ts_delta
        power_values['Power Circuit 2'] = (data_current['Power Circuit 2'] - data_prev['Power Circuit 2']) / ts_delta
        power_values['Power Circuit 2*'] = (data_current['Power Circuit 2*'] - data_prev['Power Circuit 2*']) / ts_delta
        power_values['Power Circuit 1 neutral'] = (data_current['Power Circuit 1 neutral'] - data_prev[
            'Power Circuit 1 neutral']) / ts_delta
        power_values['Shed Power'] = (data_current['Shed Power'] - data_prev['Shed Power']) / ts_delta
        power_values['Control Fan Power'] = (data_current['Control Fan Power'] - data_prev[
            'Control Fan Power']) / ts_delta
        power_values['Control Fan Power*'] = (data_current['Control Fan Power*'] - data_prev[
            'Control Fan Power*']) / ts_delta

        egauge_data['processed'] = power_values
        return json.dumps(egauge_data)


def update_egauge_data():
    from app.models import FarmDevice
    egauge_data = EgaugeInterface(url=settings.EGAUGE_URL, username=settings.EGAUGE_USER, password=settings.
                                  EGAUGE_PASSWORD).processing_egauge_data()

    if egauge_data is not None:
        try:
            farm_device = FarmDevice.objects.get(device_uid='46613')
            farm_device.device_data = egauge_data
            farm_device.save()
            print('saving...\n', farm_device.device_data)

        except FarmDevice.DoesNotExist as e:
            print('Error update_egauge_data', e)