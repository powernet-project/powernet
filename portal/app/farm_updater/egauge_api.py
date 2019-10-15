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
        self.keys = ['L1 - VOLTAGE_C', 'L2 - VOLTAGE_A', 'POWER_CIRCUIT1', 'POWER_CIRCUIT1*', 'POWER_CIRCUIT2',
                     'POWER_CIRCUIT2*', 'SHED_POWER', 'CONTROL_FAN_POWER', 'CONTROL_FAN_POWER*',
                     'POWER_TEST_PEN', 'POWER_TEST_PEN*', 'ts', 'timestamp']

    # Function to get and format e-gauge data
    def get_egauge_data(self, request):
        power_values = dict.fromkeys(self.keys, None)
        root = ET.fromstring(request.text)
        timestamp = root.findtext("ts")

        if timestamp is not None:
            for r in root.findall('r'):
                for child in r:
                    for k in self.keys:
                        if r.get('n') == k:
                            power_values[k] = (int(child.text))

            power_values['ts'] = int(timestamp)

        else:
            print('No values from request')

        return power_values

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
        from app.models import FarmDevice, FarmData
        from app.models import DeviceType

        power_values = dict.fromkeys(self.keys, None)
        egauge_data = dict.fromkeys(self.keys_db, None)

        try:
            resp = requests.get(self.url, auth=HTTPDigestAuth(self.username, self.password))
            resp.raise_for_status()
            data_current = self.get_egauge_data(resp)
            egauge_data['raw'] = data_current
        except requests.exceptions.HTTPError as err:
            print(err)
            return None

        # Filtering by home_id and picking the first element in the list
        queryset = FarmDevice.objects.filter(type=DeviceType.EGAUGE)

        if queryset.count() == 0:
            print('No egauge device created. Please create one')
            return None

        # taking only the first Eguage -> Need to automate this in case there are more egauges
        data_queryset = FarmData.objects.filter(farm_device=queryset[0]).order_by('-id')

        # Checking if there's data stored already
        if not data_queryset:
            print('No previous Egauge data exists...creating first entry')
            return json.dumps(egauge_data)

        data_prev = json.loads(data_queryset[0].device_data)['raw']

        # Checking if timestamp is different than null
        if data_prev is None:
            print('Problem communicating with E-Gauge. No data collected')
            return None

        ts_delta = data_current['ts'] - data_prev['ts']

        if ts_delta == 0:
            print('time difference between samples need to be greater than zero')
            return None

        for k in self.keys:
            if k == 'ts':
                power_values['ts'] = data_current['ts']
            elif k == 'timestamp':
                power_values['timestamp'] = datetime.datetime.fromtimestamp(data_current['ts']).strftime(
                    '%Y-%m-%d %H:%M:%S')
            elif k == 'L1 - VOLTAGE_C' or k == 'L2 - VOLTAGE_A':
                power_values[k] = ((data_current[k] - data_prev[k]) / ts_delta) / 1000
            else:
                if k in data_prev:
                    power_values[k] = (data_current[k] - data_prev[k]) / ts_delta
                else:
                    data_prev[k] = 0

        egauge_data['processed'] = power_values
        return json.dumps(egauge_data)


def update_egauge_data():
    from app.models import FarmDevice, FarmData
    egauge_data = EgaugeInterface(url=settings.EGAUGE_URL, username=settings.EGAUGE_USER, password=settings.
                                  EGAUGE_PASSWORD).processing_egauge_data()

    if egauge_data is not None:
        try:
            farm_device = FarmDevice.objects.get(device_uid='46613')
            farmdata = FarmData(farm_device=farm_device)
            farmdata.device_data = egauge_data
            farmdata.save()
            print('saving...\n')

        except FarmDevice.DoesNotExist as e:
            print('Error update_egauge_data', e)