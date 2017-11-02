"""
    Setup a listener for Philips hue lightbulb changes
"""
__author__ = 'Jonathan G.'
__copyright__ = 'Stanford University'
__version__ = '0.1'
__email__ = 'jongon@stanford.edu'
__status__ = 'Prototype'

from __future__ import print_function

import time
import requests

HUE_IDS = ['1','2','3','4','5','6']
HUE_API_KEY = 'q5B8MeIbazaKRZQ91UHqUBojNvLLh2IMH3B82C-f'
PHILPS_HUE_BRIDGE_URL = 'http://192.168.0.100/api/' # FIXME: this should become .69 after our static IP setup works
POLL_SERVER_URL = 'https://pwrnet-158117.appspot.com/api/v1/philips_hue/' # retrieve the requested updates

# TODO: process the requested updates


def change_hue_to_violation():
    for hue_id in HUE_IDS:
        on_url = PHILPS_HUE_BRIDGE_URL + HUE_API_KEY + '/lights/' + hue_id + '/state'
        r = requests.put(url=on_url, data='{"on": true, "sat": 255, "bri": 255, "hue": 0}')

def change_hue_to_base():
    for hue_id in HUE_IDS:
        on_url = PHILPS_HUE_BRIDGE_URL + HUE_API_KEY + '/lights/' + hue_id + '/state'
        r = requests.put(url=on_url, data='{"on": true, "sat": 121, "bri": 254, "hue": 8597}')

def change_hue_to_grid_support():
    for hue_id in HUE_IDS:
        on_url = PHILPS_HUE_BRIDGE_URL + HUE_API_KEY + '/lights/' + hue_id + '/state'
        r = requests.put(url=on_url, data='{"on": true, "sat": 254, "bri": 254, "hue": 25500}')

def turn_hue_on():
    change_hue_to_base()
        

def turn_hue_off():
    for hue_id in HUE_IDS:
        on_url = PHILPS_HUE_BRIDGE_URL + HUE_API_KEY + '/lights/' + hue_id + '/state'
        r = requests.put(url=on_url, data='{"on": false}')

def get_hue_lights_status():
    r = requests.get(PHILPS_HUE_BRIDGE_URL + HUE_API_KEY + '/lights/')
    print(r.json())


if __name__ == '__main__':
    change_hue_to_grid_support()
    get_hue_lights_status()

