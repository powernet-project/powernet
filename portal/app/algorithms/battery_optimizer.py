import json, datetime, numpy as np
import pandas as pd
from app.farm_updater import sonnen_api
from django.conf import settings

def batt_opt():
    from app.models import FarmDevice, FarmData, DeviceType

    ### Dynamic inputs
    try:
        egauge_device = FarmDevice.objects.get(device_uid=settings.EGAUGE_ID)
        blender_device = FarmDevice.objects.get(device_uid='100000')
    except Exception as exc:
        print('Error: ', exc)
        return

    start_date = datetime.datetime.today()-datetime.timedelta(days=3)
    end_date = datetime.datetime.today()
    power_data = FarmData.objects.filter(farm_device=egauge_device, timestamp__range=[start_date, end_date]).order_by('timestamp')
    solar_data = FarmData.objects.filter(farm_device=blender_device, timestamp__range=[start_date, end_date]).order_by(
        'timestamp')
    # batt_instance = sonnen_api.SonnenApiInterface()
    test_pen_power = []
    blender_solar_power = []

    # Getting egauge info
    for data in power_data:
        egauge_data = json.loads(data.device_data)
        test_pen_power.append([egauge_data['processed']['POWER_CIRCUIT1'] + egauge_data['processed']['POWER_CIRCUIT2'], data.timestamp])
        # print('Egauge_data: ',test_pen_power)
    egauge_pd = pd.DataFrame(test_pen_power, columns=['Power','Time'])
    egauge_pd.set_index('Time', inplace=True)
    load_data = egauge_pd['Power'].resample('15min').mean()

    # Getting solar power info
    for data in solar_data:
        blender_data = data.device_data
        # print(blender_data[0]['pv_power'])
        blender_solar_power.append([blender_data[0]['pv_power'], data.timestamp])
    blender_pd = pd.DataFrame(blender_solar_power, columns=['PV_Power','Time'])
    blender_pd.set_index('Time', inplace=True)
    solar_data = blender_pd['PV_Power'].resample('15min').mean()

    # Getting the last value from solar_data - which corresponds to most recent date/time - to get the frequency
    f_on = blender_data[0]['frq']

    # Getting sonnen USOC
    sonnen_queryset = FarmDevice.objects.filter(type=DeviceType.SONNEN)
    soc_current = []
    for item in sonnen_queryset:
        batt = FarmData.objects.filter(farm_device=item).order_by('-id')[0]
        batt_serial = item.device_uid
        try:
            soc_current.append(batt.device_data['USOC'])
        except Exception as exc:
            print('Battery exception: ', exc)
            soc_current.append(0)
    # Get the smallest soc between the two batteries.
    soc_min = np.min(np.asarray(soc_current))

    # Getting current datetime
    hour = int(datetime.datetime.today().hour)
    minute = int(datetime.datetime.today().minute)
    time_current = hour*4 + int(minute/15)



