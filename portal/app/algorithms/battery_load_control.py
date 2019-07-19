import json, datetime
import numpy as np
from app.farm_updater import sonnen_api


def batt_dispatch():
    from app.models import FarmDevice, FarmData, DeviceType

    egauge_device = FarmDevice.objects.get(device_uid='46613')
    sonnen_queryset = FarmDevice.objects.filter(type=DeviceType.SONNEN)
    farmdata = FarmData.objects.filter(farm_device=egauge_device).order_by('-id')[0:3]
    test_pen_power = []

    # Getting egauge info
    for data in farmdata:
        test_pen_power.append(json.loads(data.device_data)["processed"]["POWER_CIRCUIT1"]+json.loads(data.device_data)["processed"]["POWER_CIRCUIT2"])

    avg_test_pen_power = np.average(np.asarray(test_pen_power))

    # getting batt soc
    batt1 = FarmData.objects.filter(farm_device=sonnen_queryset[0]).order_by('-id')[0]
    batt_serial1 = sonnen_queryset[0].device_uid
    batt2 = FarmData.objects.filter(farm_device=sonnen_queryset[1]).order_by('-id')[0]
    batt_serial2 = sonnen_queryset[1].device_uid

    soc_batt1 = batt1.device_data['USOC']
    soc_batt2 = batt2.device_data['USOC']

    hour_day = datetime.datetime.now().hour
    if hour_day < 7:
        if soc_batt1 < 10:
            sonnen_api.SonnenApiInterface().manual_mode_control(serial=batt_serial1, mode='charge', value='2000')
        if soc_batt2 < 10:
            sonnen_api.SonnenApiInterface().manual_mode_control(serial=batt_serial2, mode='charge', value='2000')
        print('Battery charging at 2kW...')

    elif hour_day < 18:
        sonnen_api.SonnenApiInterface().manual_mode_control(serial=batt_serial1, mode='charge', value='0')
        sonnen_api.SonnenApiInterface().manual_mode_control(serial=batt_serial2, mode='charge', value='0')
        print('Battery in idle mode...')

    elif hour_day < 21:
        if avg_test_pen_power > 10000:
            if soc_batt1 > 10 and soc_batt2 > 10:
                sonnen_api.SonnenApiInterface().manual_mode_control(serial=batt_serial1, mode='discharge', value='4000')
                sonnen_api.SonnenApiInterface().manual_mode_control(serial=batt_serial2, mode='discharge', value='4000')
                print('Battery discharging at 4kW')

    else:
        sonnen_api.SonnenApiInterface().manual_mode_control(serial=batt_serial1, mode='charge', value='2000')
        sonnen_api.SonnenApiInterface().manual_mode_control(serial=batt_serial2, mode='charge', value='2000')
        print('Battery charging at 2kW...')