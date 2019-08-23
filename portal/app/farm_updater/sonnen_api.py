import requests
from django.conf import settings


class SonnenApiInterface:

    def __init__(self, url=settings.SONNEN_URL, token=settings.SONNEN_TOKEN):
        self.url = url
        self.token = token
        self.headers = {'Accept': 'application/vnd.sonnenbatterie.api.core.v1+json', 'Authorization': 'Bearer ' +
                                                                                                      self.token}
        self.status_endpoint = '/api/v1/status'
        self.control_endpoint = '/api/v1/setpoint/'

    def get_batteries_status_json(self, serial):
        # This method does a request to sonnen api to get status

        try:
            resp = requests.get(self.url + serial + self.status_endpoint, headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            data['batt_id'] = serial
            return data

        except requests.exceptions.HTTPError as err:
            print('Error get_battery_status_json: ', err)
            return None

    def manual_mode_control(self, serial, mode='charge', value='0'):

        # Checking if system is in off-grid mode
        voltage = self.get_batteries_status_json(serial)['Uac']

        if voltage == 0:
            print('Battery is in off-grid mode... Cannot execute the command')
            return None

        try:
            resp = requests.get(self.url + serial + self.control_endpoint + mode + '/' + value,
                                headers=self.headers)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.HTTPError as err:
            print(err)
            return {'Error: ', err}


# This method is used on scheduler.py to pull data in given periodicity
def update_battery_status():
    from app.models import FarmDevice, DeviceType, FarmData

    devices = FarmDevice.objects.filter(type=DeviceType.SONNEN)
    sonnen_api = SonnenApiInterface()

    for dev in devices:
        json_batt = sonnen_api.get_batteries_status_json(serial=dev.device_uid)
        if json_batt is not None:
            try:
                farm_device = FarmDevice.objects.get(device_uid=dev.device_uid)
                farmdata = FarmData(farm_device=farm_device)
                farmdata.device_data = json_batt
                farmdata.save()
                print('saving...\n', farmdata.device_data)
            except FarmDevice.DoesNotExist as e:
                print('Error update_battery_status for serial: ', dev.device_uid)
                print(e)
    return
