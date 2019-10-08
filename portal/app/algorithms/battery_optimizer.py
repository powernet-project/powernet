import json, datetime, numpy as np
import pandas as pd
from app.farm_updater import sonnen_api
from django.conf import settings
import time







def trainForecaster(data_p, n_samples, fname):
    # train models

    data_p = data_p.reshape((data_p.size, 1))

    # for training
    training_data = data_p[0:n_samples]

    # print('training data', training_data)

    training_mean = np.mean(training_data)
    print('mean', training_mean)

    forecaster = Forecaster(my_order=(3, 0, 3), my_seasonal_order=(3, 0, 3, 24), pos=False)
    forecaster.train(training_data, model_name='p')
    forecaster_params = forecaster.model_params_p

    np.savez('forecast_models/' + fname + str(n_samples) + '.npz', forecaster_params=forecaster_params,
             training_mean=training_mean)
    print('SAVED forecaster params at', 'forecast_models/' + fname + str(n_samples) + '.npz')

    return forecaster, training_mean

def prepareSolarForecaster(n_samples, training_data=None):
    if training_data is not None:
        # train SARIMA forecaster
        print('no solar forecaster data found, so training new forecaster')
        forecaster_s, training_mean_s = trainForecaster(training_data, n_samples, 'SARIMA_SolarModel_params')
        forecaster_s.input_training_mean(training_mean_s, model_name='s')
    else:
        # load SARIMA forecaster
        print('Loading solar forecaster parameters from',
              'forecast_models/SARIMA_SolarModel_params' + str(n_samples) + '.npz')
        model_data = np.load('forecast_models/SARIMA_SolarModel_params' + str(n_samples) + '.npz')
        forecaster_params = model_data['forecaster_params']
        training_mean_s = model_data['training_mean']
        forecaster_s = Forecaster(my_order=(3, 0, 3), my_seasonal_order=(3, 0, 3, 24), pos=False)
        model_fitted_p = forecaster_params
        forecaster_s.loadModels(model_params_p=model_fitted_p)
        forecaster_s.input_training_mean(training_mean_s, model_name='s')

    return forecaster_s

def dynamicData(d_name, solar_data):
    from app.models import FarmDevice, FarmData, DeviceType

    # this data should changed and input each time

    # load simulation power data
    power = np.loadtxt(d_name)
    power = power.reshape((1, len(power)))

    # s_name will be solar_data
    solar_full = solar_data.to_numpy()


    #####################
    # Collecting solar data
    start_date = datetime.datetime.today() - datetime.timedelta(days=3)
    end_date = datetime.datetime.today()
    solar_data = FarmData.objects.filter(farm_device=blender_device, timestamp__range=[start_date, end_date]).order_by(
        'timestamp')
    blender_solar_power = []

    # Getting solar power info
    for data in solar_data:
        blender_data = data.device_data
        # print(blender_data[0]['pv_power'])
        blender_solar_power.append([blender_data[0]['pv_power'], data.timestamp])
    blender_pd = pd.DataFrame(blender_solar_power, columns=['PV_Power', 'Time'])
    blender_pd.set_index('Time', inplace=True)
    solar_data = blender_pd['PV_Power'].resample('15min').mean()
    solar_data.fillna(0, inplace=True)
    solar_full = solar_data.to_numpy()

    # Getting the last value from solar_data - which corresponds to most recent date/time - to get the frequency
    f_on = blender_data[0]['frq']

    # Power data: all zeros as we are assuming there are no other significant loads besides the fans
    power = np.zeros(len(solar_full))





    # Where in the dataset are we starting the simulation
    # for a standard run, the dataset should consist of at least 3 days of historical data (4 * 24 * 3 points)
    # This is so the forecaster can use the historical data to make a prediction
    # when training the forecaster, the dataset should be at least 7 days of history so start_idx = 4 * 24 * 7 points
    start_idx = 4 * 24 * 3

    # keep track of night to improve solar forecast. (ex. night time from 6am to 8pm in July)
    # data can be found at https://www.timeanddate.com/sun/usa/palo-alto
    sun_start = 6 * 4  # number of 15 minute intervals after midnight that the sun rises
    sun_stop = 19 * 4
    # creating the solar mask
    night_mask = np.hstack((np.zeros(sun_start, dtype=int), np.ones(sun_stop - sun_start, dtype=int),
                            np.zeros(4 * 4, dtype=int)))
    night_mask_full = np.tile(night_mask, 31)

    # approximate start and end times of the fans to improve predictions
    f_start = 7 * 4
    f_end = 20 * 4

    f_on = 0

    # initial battery charge in kWh
    Q0 = 0.1

    # last peak power consumption in billing period
    Pmax0 = 1.5

    # current time (number of 15 minute intervals past midnight)
    time_curr = 0

    return power, solar_full, start_idx, f_start, f_end, f_on, Q0, night_mask_full, Pmax0, time_curr



def adjustedStaticData(t_res=15. / 60.):
    ### This function sets prices (TOU, Demand Charge), battery and fan param
    # this data should be adjusted once before running the first time

    # TOU charge
    s_peak = 0.31752        # $/kWh
    s_offpeak = 0.16888     # $/kWh
    prices = np.hstack((s_offpeak * np.ones((1, 12 * 4)), s_peak * np.ones((1, 6 * 4)), s_offpeak * np.ones((1, 6 * 4)))) / 4 / 2
    prices_full = np.reshape(np.tile(prices, (1, 31)), (31 * 24 * 4, 1)).T
    prices_full = prices_full * t_res  # scale prices to reflect hours instead of true time resolution

    # demand charge
    # d_price = 18.26

    # battery info
    # Qmax = 17 * 24 * 0.2
    # print('Battery energy capacity (kWh)', Qmax)
    # cmax = Qmax / 3.  # max charging rate
    # print('Battery power capacity (kW)', cmax)
    # dmax = cmax  # max discharging rate
    # fmax = 1. / 8. * cmax  # max power consumed by a single fan
    # print('maximum fan power for a single fan', fmax)
    # print('shape of uncontrollable demand', power.shape)

    # n_f = 8 # the number of fans

    d_price = 10.77     # demand charge $/kW

    # batt info
    Qmin = 0            # min battery energy
    Qmax = 10           # max battery energy
    cmax = 8            # max battery charging rate kW
    dmax = 8            # max battery discharging rate kW

    # fan info
    fmax = 1.7  # max power consumed by a single fan kW
    n_f = 15 # number of fans


    return prices_full, d_price, Qmin, Qmax, cmax, dmax, fmax, n_f

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
    load_data.fillna(0, inplace=True)



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

    st = time.time()

    # loading the dynamic data to be input to the main function
    power, solar_full, start_idx, f_start, f_end, f_on, Q0, night_mask_full, Pmax0, time_curr = \
        dynamicData('synthFarmData_15minJuly.csv', solar_data)



