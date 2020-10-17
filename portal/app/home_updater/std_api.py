import requests
from django.conf import settings


class StdApiInterface:

    LOGIN_ENDPOINT = '/api/login'
    DEVICE_ENDPOINT = '/api/device'

    def __init__(self, url=settings.SUN_TECH_DRIVE_URL, username=None, password=None):
        self.url = url
        self.cookie = None
        self.credentials = {'username': username, 'password': password}

    def login(self):
        session = requests.Session()
        session.post(self.url + self.LOGIN_ENDPOINT, data=self.credentials, verify=False)
        self.cookie = session.cookies.get_dict()

    def get_devices_status(self):
        print('Getting devices')
        try:
            resp = requests.get(self.url + self.DEVICE_ENDPOINT, cookies=self.cookie, verify=False)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as err:
            print('Error STD get_devices_status: ', err)
            return None

    def get_single_device_status(self, dev_id):
        try:
            resp = requests.get(self.url + self.DEVICE_ENDPOINT + '/' + dev_id, cookies=self.cookie, verify=False)
            print(resp.text)
            return resp.json()
        except requests.exceptions.RequestException as exc:
            print('Error STD get_single_device_status: ', exc)
            return None

    def post_devices_command(self, dev_id, command='setpower', value='on'):
        try:
            resp = requests.post(self.url + '/api/command/' + dev_id + '?' + command + '=' + value, cookies=self.cookie, verify=False)
            return resp
        except requests.exceptions.RequestException as exc:
            print('Error STD post_devices_command: ', exc)
            return None

    def post_devices_command_all(self, command='setpower', value='on'):
        try:
            resp = requests.post(self.url + '/api/command' + '?' + command + '=' + value, cookies=self.cookie, verify=False)
            return resp
        except requests.exceptions.RequestException as exc:
            print('Error STD post_devices_command_all: ', exc)
            return None


def update_std_device_status():
    from app.models import HomeDevice, DeviceType, HomeDeviceData

    username = settings.SUN_TECH_DRIVE_USERNAME
    password = settings.SUN_TECH_DRIVE_PASSWORD
    std_api = StdApiInterface(url=settings.SUN_TECH_DRIVE_TEST_URL, username=settings.SUN_TECH_DRIVE_USERNAME,
                              password=settings.SUN_TECH_DRIVE_PASSWORD)
    if username and password:
        try:
            std_api.login()
        except Exception as e:
            print('Error in sun tech drive log in', e)
            return

    devices = HomeDevice.objects.filter(type=DeviceType.PICO_BLENDER)
    for dev in devices:
        devices_from_std = std_api.get_devices_status()
        if devices_from_std is not None:
            try:
                home_device = HomeDevice.objects.get(device_uid=dev.device_uid)
                homedevicedata = HomeDeviceData(home_device=home_device)
                homedevicedata.device_data = devices_from_std
                homedevicedata.save()
            except HomeDevice.DoesNotExist as e:
                print('Error update_battery_status for serial: ', dev.device_uid)
                print(e)
