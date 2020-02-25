import requests
from app.models import EcobeeDevice
from rest_framework.decorators import api_view
from rest_framework.response import Response

ECOBEE_BASE_URL = 'https://api.ecobee.com/'
ECOBEE_API_KEY = 'AbziOl3GZDmJKrN4a6MbAIpYBbXR6tPb'
HEADERS = {'Content-Type': 'application/json;charset=UTF-8', 'Authorization': ''}


def refresh_ecobee_token(ecobee):
    url_base = 'https://api.ecobee.com/token?grant_type=refresh_token&refresh_token=' + ecobee.refresh_token
    url_client = '&client_id=' + ecobee.api_key
    HEADERS['Authorization'] = 'Bearer ' + ecobee.access_token

    try:
        r = requests.post(url_base + url_client, headers=HEADERS, timeout=10)
        # Saving Refresh token
        ecobee.refresh_token = r.json()['refresh_token']
        ecobee.access_token = r.json()['access_token']
        ecobee.save()
    except Exception as e:
        print('An exception happened refresh_token: ')
        print(e)


@api_view(['GET'])
def ecobee_data(request):
    ecobee = EcobeeDevice.objects.get(api_key=ECOBEE_API_KEY)
    HEADERS['Authorization'] = 'Bearer ' + ecobee.access_token
    payload = {'json': '{"selection":{"selectionType":"registered","selectionMatch":"","includeRuntime":"true","includeSettings":"true", "includeEvents": "true"}}'}
    url = 'https://api.ecobee.com/1/thermostat'

    try:
        r = requests.get(url, params=payload, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return Response(r.json()['thermostatList'][0])
        elif r.status_code == 500:
            # attempt to refresh the API TOKEN
            refresh_ecobee_token(ecobee)
            return Response({"error": "API Called failed " + str(r.status_code)})
    except Exception as e:
        print('An exception happened', e)
        return Response({"error": "API Called failed"})


@api_view(['POST'])
def ecobee_set_mode(request, mode):
    allowed_modes = ['heat', 'cool', 'auto', 'off']
    if mode not in allowed_modes:
        return Response({'error': 'invalid mode'})

    ecobee = EcobeeDevice.objects.get(api_key=ECOBEE_API_KEY)
    HEADERS['Authorization'] = 'Bearer ' + ecobee.access_token
    payload = {
        'selection': {
            'selectionType': 'registered',
            'selectionMatch': ''
        },
        'thermostat': {
            'settings': {'hvacMode': mode}
        }
    }
    url = "https://api.ecobee.com/1/thermostat?format=json"
    try:
        r = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        if r.status_code != requests.codes.ok:
            return Response({'error': 'could not set the mode, will attempt to refresh token, try again in 30 seconds'})

        return Response(r.json())
    except Exception as e:
        print('An exception happened while setting the hvac mode: ', e)
        return Response({'error': 'the set mode api call triggered an exception'})


@api_view(['POST'])
def ecobee_set_temperature(request, temp):
    ecobee = EcobeeDevice.objects.get(api_key=ECOBEE_API_KEY)
    HEADERS['Authorization'] = 'Bearer ' + ecobee.access_token
    payload = {
        "selection": {
            "selectionType": "registered",
            "selectionMatch": ""
        },
        "functions": [{"type": "setHold", "params": {"holdType": "nextTransition", "heatHoldTemp": temp, "coolHoldTemp": temp}}]
    }
    url = "https://api.ecobee.com/1/thermostat?format=json"
    try:
        r = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        if r.status_code != requests.codes.ok:
            return Response({'error': 'could not set the temperature, will attempt to refresh token, try again in 30 seconds'})

        return Response(r.json())
    except Exception as e:
        print('An exception happened while setting the hvac mode: ', e)
        return Response({'error': 'the set temperature api call triggered an exception'})
