import requests
from django.conf import settings


class SonnenApiInterface:

    def __init__(self, url=settings.SONNEN_URL, token=settings.SONNEN_TOKEN):
        self.url = url
        self.token = token
        self.headers = {'Accept': 'application/vnd.sonnenbatterie.api.core.v1+json', 'Authorization': 'Bearer ' +
                                                                                                      self.token}

    def get_batteries_status_json(self, serial):
        # This method does a request to sonnen api to get status
        status_endpoint = '/api/v1/status'

        try:
            resp = requests.get(self.url + serial + status_endpoint, headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            data['batt_id'] = serial
            return data

        except requests.exceptions.HTTPError as err:
            print('Error get_battery_status_json')
            return None

    def manual_mode_control(self, serial, mode='charge', value='0'):
        control_endpoint = '/api/v1/setpoint/'
        # Checking if system is in off-grid mode
        voltage = self.get_batteries_status_json().get_status()['Uac']

        if voltage == 0:
            print('Battery is in off-grid mode... Cannot execute the command')
            return {}

        else:
            try:
                resp = requests.get(self.url + serial + control_endpoint + mode + '/' + value,
                                    headers=self.headers)
                resp.raise_for_status()

            except requests.exceptions.HTTPError as err:
                print(err)

            return resp.json()


# This method is used on scheduler.py to pull data in given periodicity
def update_battery_status():
    from app.models import FarmDevice
    serial_batt1 = settings.SONNEN_BATT1
    serial_batt2 = settings.SONNEN_BATT2

    sonnen_api = SonnenApiInterface()
    json_batt1 = sonnen_api.get_batteries_status_json(serial=serial_batt1)
    json_batt2 = sonnen_api.get_batteries_status_json(serial=serial_batt2)
    print('json: ', json_batt1)
    print('json: ', json_batt2)

    if json_batt1 is not None:
        try:
            farm_device = FarmDevice.objects.get(device_uid=serial_batt1)
            farm_device.device_data = json_batt1
            farm_device.save()
            print('saving...\n', farm_device)
        except FarmDevice.DoesNotExist as e:
            print('Error update_battery1_status', e)
            pass

    if json_batt2 is not None:
        try:
            farm_device2 = FarmDevice.objects.get(device_uid=serial_batt2)
            farm_device2.device_data = json_batt2
            farm_device2.save()
            print('saving...\n', farm_device2)
        except FarmDevice.DoesNotExist as e:
            print('Error update_battery2_status', e)
            pass


# This method is used to control whether battery is charging or discharging at a given rate
def set_battery_action(mode='charge', value='0'):
    sonnen_api = SonnenApiInterface()
    control = sonnen_api.manual_mode_control(mode, value)
    print('control: ', control)
    if int(control['ResponseCode']) != 0:
        print('Error submitting request to sonnen server: ', control)
    else:
        return control
