import json, datetime, numpy as np
import pandas as pd
from app.farm_updater import sonnen_api
from django.conf import settings
import os
import cvxpy as cvx
from statsmodels.tsa.statespace.sarimax import SARIMAX



class Controller(object):

    def __init__(self, d_price, b_price, h_price, Qmin, Qmax, cmax, dmax, fmax, hmax, l_eff, c_eff, d_eff, coeff_f,
                 coeff_x, coeff_h, coeff_b, n_f, n_t, n_b, T, t_res=15. / 60):
        # coeffs are fan model coefficients
        # self.prices = prices entered when solving
        self.d_price = d_price
        self.b_price = b_price
        self.h_price = h_price  # cost of deviating above THI
        self.Qmin = Qmin
        self.Qmax = Qmax
        self.cmax = cmax
        self.dmax = dmax
        self.fmax = fmax
        self.hmax = hmax
        self.l_eff = l_eff
        self.c_eff = c_eff
        self.d_eff = d_eff
        self.t_res = t_res  # data time resolution in hours
        self.coeff_f = coeff_f
        self.coeff_x = coeff_x
        self.coeff_h = coeff_h
        self.coeff_b = coeff_b.flatten()
        self.n_f = n_f  # number of fans
        self.n_t = n_t  # number of temperature sensors
        self.n_b = n_b  # number of batteries
        self.T = T  # length of optimization horizon

    def fanPrediction(self, h0, f_exo):
        # f_exo are the fan exogenous inputs for the fan model, such as outdoor temperature
        # make fan prediction

        N, T = f_exo.shape
        h = np.zeros((self.n_t, T + 1))
        f_p = np.zeros((self.n_f, T))

        h[:, 0] = h0.flatten()

        for t in range(T):
            if np.max(h[:, t]) >= self.hmax:
                f_p[:, t] = self.fmax * np.ones(self.n_f)
            else:
                f_p[:, t] = np.zeros(self.n_f)

            h[:, t + 1] = np.dot(self.coeff_h, h[:, t]) + np.dot(self.coeff_x, f_exo[:, t]) \
                          + np.dot(self.coeff_f, f_p[:, t]) + self.coeff_b

        return f_p, h

    def fanPredictionSimple(self, f_on, time_curr, f_start=8 * 4, f_end=21 * 4):
        # f_on is binary indicating if the fans are currently on or not
        # time_curr is the number of 15 minute time steps past midnight it is now
        # default assume the fans start at 8am and end at 9pm

        f_p = np.zeros((self.n_f, self.T))
        if f_on and time_curr < f_end:
            # fan is currently running -> predict will run until end
            duration = f_end - time_curr
            fan = self.fmax * np.ones((self.n_f, duration))
            start = 0
        elif f_on and time_curr >= f_end:
            # fan is on after expected time -> fan will remain on one more period
            duration = 1
            fan = self.fmax * np.ones((self.n_f, duration))
            start = 0
        elif time_curr <= f_start:
            # no fan before start -> predict fan on at start until end
            duration = f_end - f_start
            fan = self.fmax * np.ones((self.n_f, duration))
            start = f_start - time_curr
        elif time_curr >= f_start and time_curr < f_end:
            # no fan after expected time -> predict fan will run next period
            duration = f_end - time_curr - 1
            fan = self.fmax * np.ones((self.n_f, duration))
            start = 1
        elif time_curr >= f_end:
            # no fan after end time -> fan will stay off until tomorrow
            start = self.T - time_curr + f_start
            duration = self.T - start
            if duration > f_end - f_start:
                duration = f_end - f_start
            fan = self.fmax * np.ones((self.n_f, duration))
            start = self.T - time_curr + f_start

        f_p[:, start:start + duration] = fan

        return f_p

    def optimize(self, power, solar, prices, Q0, Pmax0, f_p):
        # f_p is predicted fan power consumption
        n, T = power.shape

        cmax = np.tile(self.cmax, (self.n_b, T))
        dmax = np.tile(self.dmax, (self.n_b, T))
        Qmin = np.tile(self.Qmin, (self.n_b, T + 1))
        Qmax = np.tile(self.Qmax, (self.n_b, T + 1))
        # fmax = np.tile(self.fmax, (self.n_f, T))
        # hmax = np.tile(self.hmax, (self.n_t, T + 1))
        solar = np.tile(solar, (self.n_f, 1))

        # print(solar.shape)
        # print(solar)

        c = cvx.Variable((self.n_b, T))
        d = cvx.Variable((self.n_b, T))
        # f = cvx.Variable((self.n_f, T))
        Q = cvx.Variable((self.n_b, T + 1))
        # h = cvx.Variable((self.n_t, T + 1))

        # Battery, fan, THI, Constraints
        constraints = [c <= cmax,
                       c >= 0,
                       d <= dmax,
                       d >= 0,
                       # f >= 0,
                       # f <= fmax,
                       Q[:, 0] == Q0,
                       Q[:, 1:T + 1] == self.l_eff * Q[:, 0:T]
                       + self.c_eff * c * self.t_res - self.d_eff * d * self.t_res,
                       Q >= Qmin,
                       Q <= Qmax,
                       # h[:, 0] == h0.flatten()
                       ]

        # THI vs fan power model
        # for t in range(0, T):
        #    constraints.append(
        #        h[:, t + 1] == self.coeff_h * h[:, t] + np.dot(self.coeff_x, f_exo[:, t])
        #        + self.coeff_f * f[:, t] + self.coeff_b)

        # not a constraint, just a definition
        net = cvx.hstack([power.reshape((1, power.size)) + c - d
                          + cvx.reshape(cvx.sum(cvx.pos(f_p - solar), axis=0), (1, T)) - Pmax0, np.zeros((1, 1))])

        obj = cvx.Minimize(
            cvx.sum(cvx.multiply(prices, cvx.pos(power.reshape((1, power.size))
                                                 + c - d + cvx.reshape(cvx.sum(cvx.pos(f_p - solar), axis=0),
                                                                       (1, T)))))  # cost min
            + self.d_price * cvx.max(net)  # demand charge
            + self.b_price * cvx.sum(c + d)  # battery degradation
            # attempt to make battery charge at night * doesnt do anything
            # + 0.0001 * cvx.sum_squares((power.reshape((1, power.size))
            #                            + c - d + cvx.reshape(cvx.sum(cvx.pos(f_p - solar), axis=0), (1, T)))/np.max(power))
            #   + self.h_price * cvx.sum_squares(cvx.pos(h - hmax))  # THI penalty
        )

        prob = cvx.Problem(obj, constraints)

        prob.solve(solver=cvx.ECOS)

        # calculate expected max power
        net = power + c.value - d.value + np.sum(np.clip(f_p, 0, None), axis=0) - Pmax0
        Pmax_new = np.max(net) + Pmax0
        if Pmax_new < Pmax0:
            Pmax_new = Pmax0

        return c.value, d.value, Q.value, prob.status, Pmax_new

class Forecaster:
    def __init__(self, my_order=(3, 0, 3), my_seasonal_order=(3, 0, 3, 24), pos=False, training_mean_p=None,
                 training_mean_s=None):
        self.pos = pos  # boolean indicating whether or not the forecast should always be positive
        self.my_order = my_order
        self.my_seasonal_order = my_seasonal_order
        self.model_params_p = np.nan
        self.model_params_r = np.nan
        self.model_params_s = np.nan
        self.training_mean_p = training_mean_p
        self.training_mean_s = training_mean_s

    def input_training_mean(self, training_mean, model_name='p'):
        if model_name == 'p':
            self.training_mean_p = training_mean
        else:
            self.training_mean_s = training_mean
        return True

    def scenarioGen(self, pForecast, scens, battnodes):
        """
        Inputs: battnodes - nodes with storage
            pForecast - real power forecast for only storage nodes
            pMeans/Covs - dictionaries of real power mean vector and covariance matrices
                            keys are ''b'+node#' values are arrays
            scens - number of scenarios to generate
        Outputs: sScenarios - dictionary with keys scens and vals (nS X time)
        """

        nS, T = pForecast.shape
        sScenarios = {}
        for j in range(scens):
            counter = 0
            tmpArray = np.zeros((nS, T))
            if nS == 1:
                sScenarios[j] = pForecast  # no noise
            else:
                for i in battnodes:
                    # resi = np.random.multivariate_normal(self.pMeans['b'+str(i+1)],self.pCovs['b'+str(i+1)])
                    # tmpArray[counter,:] = pForecast[counter,:] + resi[0:T]
                    tmpArray[counter, :] = pForecast[counter, :]  # no noise
                    counter += 1
                sScenarios[j] = tmpArray

        return sScenarios

    def netPredict(self, prev_data_p, time):
        # just use random noise function predict
        pForecast = self.predict(prev_data_p, time, model_name='p')
        return pForecast

    def rPredict(self, prev_data_r, time):
        # just use random noise function predict
        rForecast = self.predict(prev_data_r, time, model_name='r')
        return rForecast

    def train(self, data, model_name='p'):
        model = SARIMAX(data, order=self.my_order, seasonal_order=self.my_seasonal_order, enforce_stationarity=False,
                        enforce_invertibility=False)
        if model_name == 'r':
            model_fitted_r = model.fit(disp=False)  # maxiter=50 as argument
            self.model_params_r = model_fitted_r.params
        elif model_name == 's':
            model_fitted_s = model.fit(disp=False)  # maxiter=50 as argument
            self.model_params_s = model_fitted_s.params
        else:
            model_fitted_p = model.fit(disp=False)  # maxiter=50 as argument
            self.model_params_p = model_fitted_p.params

    def saveModels(self, fname):
        np.savez(fname, model_fitted_p=self.model_fitted_p, model_fitted_r=self.model_fitted_r,
                 model_fitted_s=self.model_fitted_s)

    def loadModels(self, model_params_p=None, model_params_r=None, model_params_s=None):
        """
        self.model = SARIMAX(data, order=self.my_order, seasonal_order=self.my_seasonal_order,
                        enforce_stationarity=False, enforce_invertibility=False)
        self.model_fit = self.model.filter(model_fitted.params)
        """

        if model_params_p is not None:
            self.model_params_p = model_params_p
        if model_params_r is not None:
            self.model_params_r = model_params_r
        if model_params_s is not None:
            self.model_params_s = model_params_s

    def predict(self, prev_data, period, model_name='p'):

        # stime = time.time()

        model = SARIMAX(prev_data, order=self.my_order, seasonal_order=self.my_seasonal_order,
                        enforce_stationarity=False, enforce_invertibility=False)
        if model_name == 'r':
            model_fit = model.filter(self.model_params_r)
        elif model_name == 's':
            model_fit = model.filter(self.model_params_s)
        else:
            model_fit = model.filter(self.model_params_p)

        yhat = model_fit.forecast(period)

        if self.pos:
            yhat = yhat.clip(min=0)  # do not allow it to predict negative values for demand or solar

        # print 'pred time', time.time()-stime

        return yhat

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

# def prepareSolarForecaster(n_samples, training_data=None):
#     if training_data is not None:
#         # train SARIMA forecaster
#         print('no solar forecaster data found, so training new forecaster')
#         forecaster_s, training_mean_s = trainForecaster(training_data, n_samples, 'SARIMA_SolarModel_params')
#         forecaster_s.input_training_mean(training_mean_s, model_name='s')
#     else:
#         # load SARIMA forecaster
#         print('Loading solar forecaster parameters from',
#               'forecast_models/SARIMA_SolarModel_params' + str(n_samples) + '.npz')
#         model_data = np.load('forecast_models/SARIMA_SolarModel_params' + str(n_samples) + '.npz')
#         forecaster_params = model_data['forecaster_params']
#         training_mean_s = model_data['training_mean']
#         forecaster_s = Forecaster(my_order=(3, 0, 3), my_seasonal_order=(3, 0, 3, 24), pos=False)
#         model_fitted_p = forecaster_params
#         forecaster_s.loadModels(model_params_p=model_fitted_p)
#         forecaster_s.input_training_mean(training_mean_s, model_name='s')
#
#     return forecaster_s


def dynamicData(d_name, s_name, f_on):
    from app.models import FarmDevice, FarmData, DeviceType

    # this data should changed and input each time

    # load simulation power data
    power = d_name

    # s_name will be solar_data
    solar_full = s_name

    # Where in the dataset are we starting the simulation
    # for a standard run, the dataset should consist of at least 3 days of historical data (4 * 24 * 3 points)
    # This is so the forecaster can use the historical data to make a prediction
    # when training the forecaster, the dataset should be at least 7 days of history so start_idx = 4 * 24 * 7 points
    start_idx = 4 * 24 * 3

    # keep track of night to improve solar forecast. (ex. night time from 6am to 8pm in July)
    # data can be found at https://www.timeanddate.com/sun/usa/palo-alto
    sun_start = 6 * 4  # number of 15 minute intervals after midnight that the sun rises
    sun_stop = 20 * 4
    # creating the solar mask
    night_mask = np.hstack((np.zeros(sun_start, dtype=int), np.ones(sun_stop - sun_start, dtype=int),
                            np.zeros(4 * 4, dtype=int)))
    night_mask_full = np.tile(night_mask, 31)

    # approximate start and end times of the fans to improve predictions
    f_start = 7 * 4
    f_end = 20 * 4

    f_on = f_on

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

    # initial battery charge in kWh (battery capacity 10kWh)
    Q0 = soc_min * 10

    # last peak power consumption in billing period
    Pmax0 = 1.5

    # current time (number of 15 minute intervals past midnight)
    # Getting current datetime
    hour = int(datetime.datetime.today().hour)
    minute = int(datetime.datetime.today().minute)
    time_curr = hour * 4 + int(minute / 15)

    return power, solar_full, start_idx, f_start, f_end, f_on, Q0, night_mask_full, Pmax0, time_curr


def staticData(n_f):
    # This data should be kept the same

    h_price = None
    b_price = 0.001  # make price of battery degradation low for now

    t_res = 15 / 60.  # 15 minutes is 15/60 of an hour

    period = 4 * 24  # number of time steps in optimization
    offset = 4 * 24 * 3  # amount of data points needed for forecaster predictions

    t_horizon = 1  # 4*12 # how many 15 minute periods between each run (should be 1 in practice)
    t_lookahead = 24 * 4  # how many 15 minute periods to look ahead in optimization

    hmax = 1

    # leakage < 1 encourages the optimization to charge immediately before it is needed which can be risky
    # l_eff = 0.9995  # 15 minute battery leakage efficiency = 94.4% daily leakage
    l_eff = 1.0001
    c_eff = 0.975  # charging efficiency
    d_eff = 1 / 0.975  # round trip efficiency = 0.95

    n_t = 8
    n_b = 1
    coeff_f = -np.eye(n_f)
    coeff_x = 0.2 * 3.4 * np.eye(n_f)  # not necessarily square
    coeff_h = np.eye(n_t)  # not necessarily square
    coeff_b = np.zeros((n_f, 1))

    n_samples = 4 * 24 * 7 # 1 week of training data for forecasters

    return h_price, b_price, t_res, period, offset, hmax, l_eff, c_eff, d_eff, n_t, n_b, \
           coeff_f, coeff_x, coeff_h, coeff_b, n_samples, t_horizon, t_lookahead


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


def prepareSolarForecaster(n_samples, training_data=None):
    if training_data is not None:
        # train SARIMA forecaster
        print('no solar forecaster data found, so training new forecaster')
        forecaster_s, training_mean_s = trainForecaster(training_data, n_samples, 'SARIMA_SolarModel_params')
        forecaster_s.input_training_mean(training_mean_s, model_name='s')
    else:
        # load SARIMA forecaster: Issues reading model2
        # print('Loading solar forecaster parameters from',
        #       'SARIMA_SolarModel_params' + str(n_samples) + '.npz')
        path = 'algorithms/SARIMA_SolarModel_params' + str(n_samples) + '.npz'
        model_data = np.load(os.path.join(settings.BASE_DIR, path))
        forecaster_params = model_data['forecaster_params']
        training_mean_s = model_data['training_mean']
        forecaster_s = Forecaster(my_order=(3, 0, 3), my_seasonal_order=(3, 0, 3, 24), pos=False)
        model_fitted_p = forecaster_params
        forecaster_s.loadModels(model_params_p=model_fitted_p)
        forecaster_s.input_training_mean(training_mean_s, model_name='s')

    return forecaster_s

# Will not use
def preparePowerForecaster(n_samples, training_data=None):
    # SARIMA forecaster for power
    if training_data is not None:
        # train SARIMA forecaster
        print('no forecaster data found, so training new forecaster')
        forecaster, training_mean = trainForecaster(training_data, n_samples, 'SARIMA_model_params')
        forecaster.input_training_mean(training_mean, model_name='p')
    else:
        # load SARIMA forecaster
        print('Loading forecaster parameters from', 'forecast_models/SARIMA_model_params' + str(n_samples) + '.npz')
        model_data = np.load('forecast_models/SARIMA_model_params' + str(n_samples) + '.npz')
        forecaster_params = model_data['forecaster_params']
        training_mean = model_data['training_mean']
        forecaster = Forecaster(my_order=(3, 0, 3), my_seasonal_order=(3, 0, 3, 24), pos=False)
        model_fitted_p = forecaster_params
        forecaster.loadModels(model_params_p=model_fitted_p)
        forecaster.input_training_mean(training_mean, model_name='p')

    return forecaster

def getHistoryforForecast(power, start_idx, offset, t_horizon, i):
    prev_data_p = power[:, start_idx - offset + t_horizon * i:start_idx + t_horizon * i]
    prev_data_p = prev_data_p.reshape((prev_data_p.size, 1))
    return prev_data_p

def batt_opt():
    from app.models import FarmDevice, FarmData, DeviceType
    # from app.algorithms.Classes import Forecaster, Controller

    ### Dynamic inputs
    try:
        egauge_device = FarmDevice.objects.get(device_uid=settings.EGAUGE_ID)
        blender_device = FarmDevice.objects.get(device_uid='100000')
    except Exception as exc:
        print('Error: ', exc)
        return

    start_date = datetime.datetime.today()-datetime.timedelta(days=3)
    end_date = datetime.datetime.today()
    solar_data = FarmData.objects.filter(farm_device=blender_device, timestamp__range=[start_date, end_date]).order_by(
        'timestamp')
    blender_solar_power = []
    blender_data = None
    # Getting solar power info
    for data in solar_data:
        blender_data = data.device_data
        # print(blender_data[0]['pv_power'])
        blender_solar_power.append([blender_data[0]['pv_power'], data.timestamp])
    blender_pd = pd.DataFrame(blender_solar_power, columns=['PV_Power', 'Time'])
    blender_pd.set_index('Time', inplace=True)
    blender_pd.index = blender_pd.index.tz_convert('America/Los_Angeles')
    blender_pd = blender_pd.sort_index()
    solar_data = blender_pd['PV_Power'].resample('15min').mean()
    solar_data.fillna(0, inplace=True)
    solar_full = solar_data.to_numpy()

    # Getting the last value from solar_data - which corresponds to most recent date/time - to get the frequency
    if blender_data is not None:
        f_on = blender_data[0]['frq']
    else:
        f_on = 0

    # Power data: all zeros as we are assuming there are no other significant loads besides the fans
    power = np.zeros(len(solar_full))

    # # Getting egauge info
    # for data in power_data:
    #     egauge_data = json.loads(data.device_data)
    #     test_pen_power.append([egauge_data['processed']['POWER_CIRCUIT1'] + egauge_data['processed']['POWER_CIRCUIT2'], data.timestamp])
    #     # print('Egauge_data: ',test_pen_power)
    # egauge_pd = pd.DataFrame(test_pen_power, columns=['Power','Time'])
    # egauge_pd.set_index('Time', inplace=True)
    # load_data = egauge_pd['Power'].resample('15min').mean()
    # load_data.fillna(0, inplace=True)

    # loading the dynamic data to be input to the main function
    power, solar_full, start_idx, f_start, f_end, f_on, Q0, night_mask_full, Pmax0, time_curr = \
        dynamicData(power, solar_full, f_on)

    # This is where main starts:
    # Define all the needed static info
    ### This function sets the prices
    prices_full, d_price, Qmin, Qmax, cmax, dmax, fmax, n_f = adjustedStaticData()

    ### Change n_f to the real number of fans = 15
    h_price, b_price, t_res, period, offset, hmax, l_eff, c_eff, d_eff, n_t, n_b, \
    coeff_f, coeff_x, coeff_h, coeff_b, n_samples, t_horizon, t_lookahead = staticData(n_f)

    # initialize controller
    contr = Controller(d_price, b_price, h_price, Qmin, Qmax, cmax, dmax, fmax, hmax, l_eff, c_eff, d_eff, coeff_f,
                       coeff_x, coeff_h, coeff_b, n_f, n_t, n_b, period, t_res)

    # ~~~~~~~ Uncomment these when training the forecaster
    # for training the forecaster input at least 1 week of historical data
    # if it gives a ConvergenceWarning when training, just ignore it.
    # forecaster = preparePowerForecaster(n_samples, training_data=power)
    # forecaster_s = prepareSolarForecaster(n_samples, training_data=solar_full)

    # ~~~~~~~~~~~ Uncomment these when running the forecaster without training
    # forecaster = preparePowerForecaster(n_samples)
    forecaster_s = prepareSolarForecaster(960)

    # get solar power forecast
    prev_data_s = getHistoryforForecast(solar_full, start_idx, offset, t_horizon, 0)
    solar_curr = forecaster_s.predict(prev_data_s, period, model_name='p')  # no difference in model name
    solar_curr = solar_curr.reshape((1, solar_curr.size)) + forecaster_s.training_mean_s
    night_mask = night_mask_full[time_curr:time_curr + t_lookahead]
    solar_curr = solar_curr * night_mask

    # get prices for current time
    prices_curr = prices_full[:, time_curr:time_curr + t_lookahead]




