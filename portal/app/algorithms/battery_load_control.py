import json, datetime, numpy as np
from app.farm_updater import sonnen_api
from django.conf import settings


def batt_dispatch():
    from app.models import FarmDevice, FarmData, DeviceType

    try:
        egauge_device = FarmDevice.objects.get(device_uid=settings.EGAUGE_ID)
    except Exception as exc:
        print('Error: ', exc)
        return

    farmdata = FarmData.objects.filter(farm_device=egauge_device).order_by('-id')[0:3]
    batt_instance = sonnen_api.SonnenApiInterface()
    test_pen_power = []

    # Getting egauge info
    for data in farmdata:
        egauge_data = json.loads(data.device_data)
        test_pen_power.append(egauge_data['processed']['POWER_CIRCUIT1'] + egauge_data['processed']['POWER_CIRCUIT2'])

    avg_test_pen_power = np.average(np.asarray(test_pen_power))

    hour_day_utc = datetime.datetime.now().hour
    if hour_day_utc < 7:
        hour_day = hour_day_utc + 24 - 7
    else:
        hour_day = hour_day_utc - 7


    # getting batt soc
    sonnen_queryset = FarmDevice.objects.filter(type=DeviceType.SONNEN)
    for item in sonnen_queryset:
        batt = FarmData.objects.filter(farm_device=item).order_by('-id')[0]
        batt_serial = item.device_uid
        soc = batt.device_data['USOC']
        print('Battery Serial: ', batt_serial)

        if hour_day < 7:
            if soc < 90:
                batt_instance.manual_mode_control(serial=batt_serial, mode='charge', value='2000')
                print('Battery charging at 2kW...')

        elif hour_day < 18:
            batt_instance.manual_mode_control(serial=batt_serial, mode='charge', value='0')
            print('Battery in idle mode...')

        elif hour_day < 22:
            if avg_test_pen_power < -4000:
                if soc > 10:
                    batt_instance.manual_mode_control(serial=batt_serial, mode='discharge', value='4000')
                    print('Battery discharging at 4kW')

        else:
            batt_instance.manual_mode_control(serial=batt_serial, mode='charge', value='2000')
            print('Battery charging at 2kW...')
