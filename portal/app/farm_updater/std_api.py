import requests
from django.conf import settings


class StdApiInterface:
    """
    TODO:
    """

    LOGIN_ENDPOINT = '/api/login'
    DEVICE_ENDPOINT = '/api/device'

    def __init__(self, url=settings.SUN_TECH_DRIVE_URL, username=None, password=None):
        self.url = url
        self.cookie = None
        self.credentials = {'username': username, 'password': password}

    def login(self):
        session = requests.Session()
        session.post(self.url + self.LOGIN_ENDPOINT, data=self.credentials)
        self.cookie = session.cookies.get_dict()
        print(self.cookie)

    def get_devices_status(self):
        print('Getting devices')
        resp = requests.get(self.url + self.DEVICE_ENDPOINT, cookies=self.cookie)
        return resp.json()

    def get_single_device_status(self, dev_id):
        try:
            resp = requests.get(self.url + self.DEVICE_ENDPOINT + dev_id, cookies=self.cookie)
        except requests.exceptions.RequestException as exc:
            print(exc)

        return resp.json()

    def post_devices_command(self, dev_id, command='setpower', value='on'):
        try:
            resp = requests.post(self.url + '/api/command/' + dev_id + '?' + command + '=' + value, cookies=self.cookie)
        except requests.exceptions.RequestException as exc:
            print(exc)

        return resp

    def post_devices_command_all(self, command='setpower', value='on'):
        try:
            resp = requests.post(self.url + '/api/command' + '?' + command + '=' + value, cookies=self.cookie)
        except requests.exceptions.RequestException as exc:
            print(exc)

        return resp


def update_std_device_status():

    # TODO: will store this in the DB later
    username = settings.SUN_TECH_DRIVE_USERNAME
    password = settings.SUN_TECH_DRIVE_PASSWORD

    if username and password:
        try:
            std_api = StdApiInterface(url=settings.SUN_TECH_DRIVE_TEST_URL, username=settings.SUN_TECH_DRIVE_USERNAME,
                                      password=settings.SUN_TECH_DRIVE_PASSWORD)
            std_api.login()
            devices_from_std = std_api.get_devices_status()
            print(devices_from_std)

        except Exception as e:
            print('Error retrieving data from sun tech drive', e)
