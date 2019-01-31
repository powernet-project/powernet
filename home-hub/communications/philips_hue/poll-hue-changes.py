"""
    Setup a listener for Philips hue lightbulb changes
"""
from __future__ import print_function

__author__ = 'Jonathan G.'
__copyright__ = 'Stanford University'
__version__ = '0.1'
__email__ = 'jongon@stanford.edu'
__status__ = 'Prototype'

import os
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

def query_for_updates(global_condition, auth_token):
    """
        Query the powernet server for state change on the philips hue lights
    """
    req = requests.get(url=POLL_SERVER_URL, headers={'Authorization': 'Token ' + auth_token})
    
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

def setup_polling_listener(auth_token):
    """
        Setup HTTP long polling of our server for changes in home state, which
        we'll reflect in color changes in the Philips Hue
    """
    gc = 'UNKNOWN'
    while True:
        try:
            c = query_for_updates(gc, auth_token)
            gc = c
        except Exception as exc:
            print(exc)
            time.sleep(3)
        time.sleep(3)


if __name__ == '__main__':
    try:
        # Get the email and password for this HH's user from the env vars
        powernet_user_email = os.getenv('POWERNET_USER_EMAIL', None)
        powernet_user_password = os.getenv('POWERNET_USER_PASSWORD', None)
        
        if powernet_user_email is None:
            print('Missing the required login email address')
            print('Please set the POWERNET_USER_EMAIL environment variable and try again')
            exit()
        
        if powernet_user_password is None:
            print('Missing the required login password')
            print('Please set the POWERNET_USER_PASSWORD environment variable and try again')
            exit()
        
        # attempt to authenticate against our API
        form_payload = {'email': powernet_user_email, 'password': powernet_user_password}
        response = requests.post('https://pwrnet-158117.appspot.com/api/v1/powernet_user/auth/', data=form_payload)
        auth_token = response.json()['token']

        setup_polling_listener(auth_token)
    except Exception as exc:
        print(exc)
        time.sleep(3)
        setup_polling_listener(auth_token)
