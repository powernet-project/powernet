import requests
from django.conf import settings


class SonnenApiInterface:

    def __init__(self, url=settings.SONNEN_URL):
        self.url = url
        self.serial = '67682'
        # self.serial2 = '67670'
        self.token = '5db92cf858eebce34af146974f49f4d40ec699b99372546c0af628fb48133f61'
        self.headers = {'Accept': 'application/vnd.sonnenbatterie.api.core.v1+json', 'Authorization': 'Bearer ' + self.token}

    def get_batteries_status_json(self):
        # This method does a request to sonnen api to get status
        status_endpoint = '/api/v1/status'

        try:
            resp = requests.get(self.url + self.serial + status_endpoint, headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            data['batt_id'] = self.serial
            return data

        except requests.exceptions.HTTPError as err:
            print('Error get_battery_status_json')
            return None

    def manual_mode_control(self, mode='charge', value='0'):
        control_endpoint = '/api/v1/setpoint/'
        # Checking if system is in off-grid mode
        voltage = self.get_batteries_status_json().get_status()['Uac']

        if voltage == 0:
            print('Battery is in off-grid mode... Cannot execute the command')
            return {}

        else:
            try:
                resp = requests.get(self.url + self.serial + control_endpoint + mode + '/' + value,
                                    headers=self.headers)
                resp.raise_for_status()

            except requests.exceptions.HTTPError as err:
                print(err)

            return resp.json()


# This method is used on scheduler.py to pull data in given periodicity
def update_battery_status():
    from app.models import FarmDevice

    sonnen_api = SonnenApiInterface()
    json = sonnen_api.get_batteries_status_json()
    print('json: ', json)
    if json is not None:
        try:
            farm_device = FarmDevice.objects.get(device_uid='67682')
            farm_device.device_data = json
            farm_device.save()
            print('saving...\n', farm_device)
        except FarmDevice.DoesNotExist as e:
            print('Error update_battery_status', e)
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
