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

HUE_IDS = ['1', '2', '3', '4', '5', '6']
HUE_API_KEY = 'q5B8MeIbazaKRZQ91UHqUBojNvLLh2IMH3B82C-f'
# FIXME: this should become .69 after our static IP setup works
PHILPS_HUE_BRIDGE_URL = 'http://192.168.0.100/api/'
POLL_SERVER_URL = 'https://pwrnet-158117.appspot.com/api/v1/hue_states/1'

def change_hue_to_violation():
    """
        Change the Philips Hue in the home to show that a violation occurred - RED
    """
    for hue_id in HUE_IDS:
        on_url = PHILPS_HUE_BRIDGE_URL + HUE_API_KEY + '/lights/' + hue_id + '/state'
        requests.put(url=on_url, data='{"on": true, "sat": 255, "bri": 255, "hue": 0}')

def change_hue_to_base():
    """
        Change the Philips Hue in the home to show normal day-to-day - YELLOWISH WHITE
    """
    for hue_id in HUE_IDS:
        on_url = PHILPS_HUE_BRIDGE_URL + HUE_API_KEY + '/lights/' + hue_id + '/state'
        requests.put(url=on_url, data='{"on": true, "sat": 121, "bri": 254, "hue": 8597}')

def change_hue_to_grid_support():
    """
        Change the Philips Hue in the home to show that the home is supporting the grid - GREEN
    """
    for hue_id in HUE_IDS:
        on_url = PHILPS_HUE_BRIDGE_URL + HUE_API_KEY + '/lights/' + hue_id + '/state'
        requests.put(url=on_url, data='{"on": true, "sat": 254, "bri": 254, "hue": 25500}')

def turn_hue_on():
    """
        The all the 6 BitsLab Philips Hue on to base
    """
    change_hue_to_base()

def turn_hue_off():
    """
        The all the 6 BitsLab Philips Hue to off
    """
    for hue_id in HUE_IDS:
        on_url = PHILPS_HUE_BRIDGE_URL + HUE_API_KEY + '/lights/' + hue_id + '/state'
        requests.put(url=on_url, data='{"on": false}')

def get_hue_lights_status():
    """
        Retrieve the statuses for hue lights in the BitsLab
    """
    req = requests.get(PHILPS_HUE_BRIDGE_URL + HUE_API_KEY + '/lights/')
    print(req.json())

def query_for_updates():
    """
        Query the powernet server for state change on the philips hue lights
    """
    req = requests.get(url=POLL_SERVER_URL)
    print(req.json())
    if condtion ==


def setup_polling_listener():
    """
        Setup HTTP long polling of our server for changes in home state, which
        we'll reflect in color changes in the Philips Hue
    """
    while True:
        query_for_updates()    
        #change_hue_to_grid_support()
        #get_hue_lights_status()


if __name__ == '__main__':
    setup_polling_listener()