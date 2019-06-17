from app.api.v1 import CsrfExemptAuth
from rest_framework.decorators import action
from rest_framework.response import Response
from app.models import FarmDevice, Home, Device
from rest_framework import (viewsets, serializers, status)
from rest_framework.authentication import TokenAuthentication
import requests

# This method does a request to sonnen api to get status
def _get_batteries_status_json():
    serial1 = '67682'
    # serial2 = '67670'
    token = '5db92cf858eebce34af146974f49f4d40ec699b99372546c0af628fb48133f61'
    url_ini = 'https://core-api.sonnenbatterie.de/proxy/'
    headers = { 'Accept': 'application/vnd.sonnenbatterie.api.core.v1+json','Authorization': 'Bearer '+self.token,}
    status_endpoint = '/api/v1/status'

    try:
        resp = requests.get(url_ini + serial1 + status_endpoint, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        data['batt_id'] = serial1
        return data

    except requests.exceptions.HTTPError as err:
        return None


# This method is used on scheduler.py to pull data in given periodicity
def update_battery_status():
    json = _get_batteries_status_json()
    if json is not None:
        try:
            farmdevice = FarmDevice()
            farmdevice = FarmDevice.objects.get(device_uid = '67682')
            farmdevice.update(device_data = json)
            print('saving...\n', farmdevice)
        except:
            pass
            
        
