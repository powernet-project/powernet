import requests
from django.conf import settings
import datetime
from xml.etree import ElementTree as ET
from requests.auth import HTTPDigestAuth
import json


class EgaugeInterface():

    def __init__(self, url=None, username=None, password=None, 
        device_uid = None, t_sample=5):
        # Initializing credentials
        self.url = url
        self.username = username
        self.password = password
        self.device_uid = device_uid

        # Initializing parameters
        self.t_sample = t_sample
        self.keys_db = ['raw', 'processed']
        self.keys = ['L1_Voltage', 'L2_Voltage', 'POWER-P', 'POWER_SUBPANEL-P',
                     # Living Rooms
                     'FURNACE-P', 'LIGHT-P', 'LIGHT1-P', 'LIGHT2-P', 'LIVING_ROOM_1-P', 'LIVING_ROOM_2-P', 'LIVING-ROOM-P',
                     # Bedrooms
                     'BEDROOM-P', 'BEDROOM_1-P', 'BEDROOM_2-P',
                     # Kitchen
                     'KITCHEN-P', 'KITCHEN_A-P', 'KITCHEN_B-P', 'KITCHEN_PLUGS-P', 'MICROWAVE-P', 'OVEN-P', 'REFRIGERATOR-P',
                     # Laundry
                     'DISHWASHER-P', 'DRYER-P', 'LAUNDRY-P',
                     # Others
                     'AC-P', 'EV-P', 'GARAGE-P', 'SOLAR-P', 'SUBPANEL_A-P', 'SUBPANEL_B-P', 'POWER_SUBPANEL-P',
                     'PLUGS_APPLIANCE1-P', 'PLUGS_APPLIANCE2-P', 'PLUGS_APPLIANCE3-P', 'PLUGS_APPLIANCE-P',
                     'ATTIC-P', 'BATHROOM-P', 'OFFICE-P', 'WATER-HEATER-P',
                     # New fields (not listed in subcircuit names spreadsheet)
                     'WASHER-P', 'WASHER_A-P', 'DRYER_A-P', 'DRYER_B-P', 'RANGE-P', 'AIRCONDITIONING-P', 'STOVE-P', 'EVSE-P',
                     # Additional
                     'ts', 'timestamp']

    # Function to get and format e-gauge data
    def get_egauge_data(self, request):
        power_values = dict.fromkeys(self.keys, None)
        root = ET.fromstring(request.text)
        timestamp = root.findtext("ts")

        if timestamp is not None:
            for r in root.findall('r'):
                for child in r:
                    s = r.get('n')
                    if s.find("-") == -1: 
                        continue
                    name = s[s.index("-") + 1:]
                    if name == 'L1_Voltage' or name == 'L2_Voltage' or name.endswith("-P"):
                        if name in power_values:
                            power_values[name] = (int(child.text))

            power_values['ts'] = int(timestamp)

        else:
            print('No values from request for egauge device %s' % self.device_uid)
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
        from app.models import HomeDevice, HomeDeviceData, Home, DeviceType

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

        # Check whether the eguage device exists
        if HomeDevice.objects.filter(
            type=DeviceType.EGAUGE, 
            device_uid=self.device_uid).count() == 0:
            print('No egauge device %s created. Please create one' % self.device_uid)
            return None

        # Filtering by device_uid and picking the first element in the list
        queryset = HomeDevice.objects.filter(
            type=DeviceType.EGAUGE, device_uid=self.device_uid)

        # taking only the first Eguage -> Need to automate this in case there are more egauges
        data_queryset = HomeDeviceData.objects.filter(home_device=queryset[0]).order_by('-id')

        # Checking if there's data stored already
        if not data_queryset:
            print('No previous Egauge data for device %s exists...creating first entry' 
                % self.device_uid)
            return json.dumps(egauge_data)

        data_prev = json.loads(data_queryset[0].device_data)['raw']

        # Checking if timestamp is different than null
        if data_prev is None:
            print('Problem communicating with E-Gauge. \
                No data collected for egauge device %s' % self.device_uid)
            return None

        ts_delta = data_current['ts'] - data_prev['ts']

        if ts_delta == 0:
            print('time difference between samples need to be greater than zero \
                for egauge device %s' % self.device_uid)
            return None

        for k in self.keys:
            if k == 'ts':
                power_values['ts'] = data_current['ts']
            elif k == 'timestamp':
                power_values['timestamp'] = datetime.datetime.fromtimestamp(
                    data_current['ts']).strftime('%Y-%m-%d %H:%M:%S')
            elif k == 'L1_Voltage' or k == 'L2_Voltage':
                if data_prev[k] is not None and data_current[k] is not None:
                    power_values[k] = ((data_current[k] - data_prev[k]) / ts_delta) / 1000
            else:
                if data_prev[k] is not None and data_current[k] is not None:
                    power_values[k] = (data_current[k] - data_prev[k]) / ts_delta

        egauge_data['processed'] = power_values
        return json.dumps(egauge_data)


def update_egauge_data():
    from app.models import HomeDevice, HomeDeviceData, DeviceType

    devices = HomeDevice.objects.filter(type=DeviceType.EGAUGE)
    for dev in devices:
        uid = dev.device_uid
        url = 'https://egauge%s.egaug.es/cgi-bin/egauge' % uid
        egauge_data = EgaugeInterface(
            url=url, 
            username=settings.EGAUGE_USER, 
            password=settings.EGAUGE_PASSWORD,
            device_uid=uid).processing_egauge_data()

        if egauge_data is not None:
            home_device = HomeDevice.objects.get(device_uid=uid)
            homedevicedata = HomeDeviceData(home_device=home_device)
            homedevicedata.device_data = egauge_data
            homedevicedata.save()
            print('saving for eguage device %s...\n' % uid)