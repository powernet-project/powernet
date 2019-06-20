import requests


def _get_batteries_status_json():
    # This method does a request to sonnen api to get status
    serial1 = '67682'
    # serial2 = '67670'
    token = '5db92cf858eebce34af146974f49f4d40ec699b99372546c0af628fb48133f61'
    url_ini = 'https://core-api.sonnenbatterie.de/proxy/'
    headers = { 'Accept': 'application/vnd.sonnenbatterie.api.core.v1+json','Authorization': 'Bearer '+token,}
    status_endpoint = '/api/v1/status'

    try:
        resp = requests.get(url_ini + serial1 + status_endpoint, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        data['batt_id'] = serial1
        return data

    except requests.exceptions.HTTPError as err:
        print('Error get_battery_status_json')
        return None


# This method is used on scheduler.py to pull data in given periodicity
def update_battery_status():
    from app.models import FarmDevice
    json = _get_batteries_status_json()
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
