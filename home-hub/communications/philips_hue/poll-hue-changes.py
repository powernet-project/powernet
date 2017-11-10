"""
    Setup a listener for Philips hue lightbulb changes
"""
from __future__ import print_function

__author__ = 'Jonathan G.'
__copyright__ = 'Stanford University'
__version__ = '0.1'
__email__ = 'jongon@stanford.edu'
__status__ = 'Prototype'

import time
import requests

HUE_IDS = ['1', '2', '3', '4', '5', '6']
HUE_API_KEY = 'q5B8MeIbazaKRZQ91UHqUBojNvLLh2IMH3B82C-f'
PHILPS_HUE_BRIDGE_URL = 'http://192.168.0.69/api/'
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
        Turn all the 6 BitsLab Philips Hue on to base
    """
    change_hue_to_base()

def turn_hue_off():
    """
        Turn all the 6 BitsLab Philips Hue to off
    """
    for hue_id in HUE_IDS:
        on_url = PHILPS_HUE_BRIDGE_URL + HUE_API_KEY + '/lights/' + hue_id + '/state'
        requests.put(url=on_url, data='{"on": false}')

def get_hue_lights_status():
    """
        Retrieve the statuses for hue lights in the BitsLab
    """
    req = requests.get(PHILPS_HUE_BRIDGE_URL + HUE_API_KEY + '/lights/')
    return req.json()

def query_for_updates(global_condition):
    """
        Query the powernet server for state change on the philips hue lights
    """
    req = requests.get(url=POLL_SERVER_URL)
    
    condition = req.json()['state']

    if global_condition != condition:
        if condition == 'ON':
            turn_hue_on()
        elif condition == 'OFF':
            turn_hue_off()
        elif condition == 'COORDINATED':
            change_hue_to_grid_support()
        elif condition == 'VIOLATION':
            change_hue_to_violation()
        elif condition == 'BASE':
            change_hue_to_base()
        else:
            pass  # Condition is unknown - either we just started or the server may be down

    return condition

def setup_polling_listener():
    """
        Setup HTTP long polling of our server for changes in home state, which
        we'll reflect in color changes in the Philips Hue
    """
    gc = 'UNKNOWN'
    while True:
        try:
            c = query_for_updates(gc)
            gc = c
        except Exception as exc:
            print(exc)
        time.sleep(2)


if __name__ == '__main__':
    try:
        setup_polling_listener()
    except Exception as exc:
        print(exc)
        setup_polling_listener()
