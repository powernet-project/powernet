"""
Setup the Network interface - this communicates with our backend 
powernet REST API. Just a simple abstraction
"""
from __future__ import print_function

__author__ = 'Gustavo C. & Jonathan G. '
__copyright__ = 'Stanford University'
__version__ = '0.2'
__email__ = 'gcezar@stanford.edu, jongon@stanford.edu'
__status__ = 'Beta'

import json
import logging
import requests

logger = logging.getLogger('HOME_HUB_APPLICATION_LOGGER')

class NetworkInterface:
    def __init__(self, auth_token):
        self.request_timeout = 10
        self.headers = {'Authorization': 'Token ' + auth_token}
        self.pwrnet_base_url = 'https://pwrnet-158117.appspot.com/api/v1/'
        self.logger = logger

    def save_rms(self, json_data):
        r = requests.post(self.pwrnet_base_url + 'rms/', json=json_data, timeout=self.request_timeout, headers=self.headers)
        if r.status_code != 201:
            self.logger.error('Failed to save rms data')
            r.raise_for_status()

    def save_devices(self, json_data):
        r = requests.post(self.pwrnet_base_url + 'device/', json=json_data, timeout=self.request_timeout, headers=self.headers)
        if r.status_code != 201:
            self.logger.error('Failed to save device')
            return None
        return json.loads(r.text)['id']

    def get_device_status(self):
        r = requests.get(self.pwrnet_base_url + 'device/', timeout=self.request_timeout, headers=self.headers)
        return r.json()["results"]

    def get_battery_status(self, device_id):
        r = requests.get(self.pwrnet_base_url + 'device/' + device_id + '/', timeout=self.request_timeout, headers=self.headers)
        return r