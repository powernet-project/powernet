import json, datetime, numpy as np
import pandas as pd
from app.farm_updater import sonnen_api
from django.conf import settings
import os
import cvxpy as cvx
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pytz import timezone
import pytz


# all units should be in kW
# Power consumed is positive
# Power generated is negative

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

        f_p[:, start:start + duration] = fan    # Need to define all the cases or set a default state

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

# Still need to implement forecast for the final solution - currently running offline
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


def dynamicData(d_name, s_name, f_on):
    from app.models import FarmDevice, FarmData, DeviceType, FarmMaxDemand

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
    sun_start = 7 * 4  # number of 15 minute intervals after midnight that the sun rises
    sun_stop = 20 * 4
    # creating the solar mask
    night_mask = np.hstack((np.zeros(sun_start, dtype=int), np.ones(sun_stop - sun_start, dtype=int),
                            np.zeros(4 * 4, dtype=int)))
    night_mask_full = np.tile(night_mask, 31)

    # approximate start and end times of the fans to improve predictions
    f_start = 12 * 4
    f_end = 20 * 4

    f_on = f_on

    # Getting sonnen USOC
    sonnen_queryset = FarmDevice.objects.filter(type=DeviceType.SONNEN)
    soc_current = []
    for item in sonnen_queryset:
        batt = FarmData.objects.filter(farm_device=item).order_by('-id')[0]
        try:
            soc_current.append(batt.device_data['USOC'])
        except Exception as exc:
            print('Battery exception: ', exc)
            soc_current.append(98) # set it to 98 as if there's error pulling data from db the system will either do nothing or discharge
    # Get the smallest soc between the two batteries.
    soc_min = np.min(np.asarray(soc_current))
    print('soc_min: ', soc_min)

    # initial battery charge in kWh (battery capacity 10kWh)
    Q0 = soc_min * 10./100
    print('Q0: ', Q0)

    # Getting current month
    month_curr = datetime.datetime.now(tz=pytz.utc).astimezone(timezone('US/Pacific')).month
    queryset_month = FarmMaxDemand.objects.all()

    if queryset_month:
        data_month = queryset_month.order_by('-id')[0]
        if data_month.month_pst != month_curr:
            data_month.max_power = 0.2
            Pmax0 = 0.2 # Cannot set to zero as it triggers problems in the optimization
            data_month.month_pst = month_curr
            data_month.save()
        else:
            Pmax0 = data_month.max_power

    else:
        # Need to fix home_id. Prod is 11 Dev is 1

        max_power = FarmMaxDemand(home_id=11, max_power=0, month_pst=month_curr)
        max_power.save()
        Pmax0 = 0.2


    # current time (number of 15 minute intervals past midnight)
    # Getting current datetime
    hour_day_utc = int(datetime.datetime.today().hour)
    # Converting hours from UTC to local
    if hour_day_utc < 7:
        hour = hour_day_utc + 24 - 7
    else:
        hour = hour_day_utc - 7

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
    l_eff = 1
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

    # Implement for winter months and change prices
    # TOU charge
    s_peak = 0.31752        # $/kWh
    s_offpeak = 0.16888     # $/kWh
    prices = np.hstack((s_offpeak * np.ones((1, 12 * 4)), s_peak * np.ones((1, 6 * 4)), s_offpeak * np.ones((1, 6 * 4))))
    prices_full = np.reshape(np.tile(prices, (1, 31)), (31 * 24 * 4, 1)).T
    prices_full = prices_full * t_res  # scale prices to reflect hours instead of true time resolution

    d_price = 10.77     # demand charge $/kW

    # batt info
    Qmin = 0.5            # min battery energy
    Qmax = 9.8           # max battery energy
    cmax = 7.9            # max battery charging rate kW
    dmax = 7.9            # max battery discharging rate kW

    # fan info
    fmax = 1.6  # max power consumed by a single fan kW
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


def getHistoryforForecast(power, start_idx, offset, t_horizon, i):
    prev_data_p = power[:, start_idx - offset + t_horizon * i:start_idx + t_horizon * i]
    prev_data_p = prev_data_p.reshape((prev_data_p.size, 1))
    return prev_data_p


def net_load():
    from app.models import FarmDevice, FarmData, DeviceType

    try:
        egauge_device = FarmDevice.objects.get(device_uid=settings.EGAUGE_ID)
    except Exception as exc:
        print('Error: ', exc)
        return None

    farmdata = FarmData.objects.filter(farm_device=egauge_device).order_by('-id')[0:3]
    test_pen_power = []

    # Getting egauge info
    for data in farmdata:
        egauge_data = json.loads(data.device_data)
        test_pen_power.append(egauge_data['processed']['POWER_TEST_PEN'])
    print('egauge_load: ', test_pen_power) ###########################
    return np.average(np.asarray(test_pen_power))/1000


def realTimeUpdate(p_net, pmax, u_curr):
    # takes the most current readings and makes real time adjustments
    # purpose is to compensate for forecaster errors

    if p_net > pmax:
        u_new = u_curr + pmax - p_net
    elif p_net < 0:
        u_new = u_curr - p_net
    else:
        u_new = u_curr

    return u_new


def batt_act(mode='charge', val=0):
    from app.models import FarmDevice, DeviceType
    batt_instance = sonnen_api.SonnenApiInterface()
    sonnen_queryset = FarmDevice.objects.filter(type=DeviceType.SONNEN)
    for item in sonnen_queryset:
        batt_serial = item.device_uid
        print('Battery Serial: ', batt_serial) ###########################
        print('mode: ', mode)
        print('value: ', val)
        batt_instance.manual_mode_control(serial=batt_serial, mode=mode, value=str(val))



def batt_opt():
    from app.models import FarmDevice, FarmData, FarmMaxDemand
    # from app.algorithms.Classes import Forecaster, Controller

    ### Dynamic inputs
    try:
        blender_device = FarmDevice.objects.get(device_uid='100000')
    except Exception as exc:
        print('Error: ', exc)
        return

    start_date = datetime.datetime.today()-datetime.timedelta(days=4)
    end_date = datetime.datetime.today()
    solar_data = FarmData.objects.filter(farm_device=blender_device, timestamp__range=[start_date, end_date]).order_by(
        'timestamp')
    blender_solar_power = []
    blender_data = None
    # Getting solar power info
    for data in solar_data:
        blender_data = data.device_data
        blender_solar_power.append([blender_data[0]['pv_power'], data.timestamp])
    blender_pd = pd.DataFrame(blender_solar_power, columns=['PV_Power', 'Time'])
    blender_pd.set_index('Time', inplace=True)
    blender_pd.index = blender_pd.index.tz_convert('America/Los_Angeles')
    blender_pd = blender_pd.sort_index()
    solar_data = blender_pd['PV_Power'].resample('15min').mean()
    solar_data.fillna(0, inplace=True)
    solar_full = np.array([solar_data.to_numpy()])

    # Converting solar values to kW
    solar_full = solar_full / 1000

    # Getting the last value from solar_data - which corresponds to most recent date/time - to get the frequency
    if blender_data is not None:
        f_on = blender_data[0]['frq']
    else:
        f_on = 0

    # Power data: all zeros as we are assuming there are no other significant loads besides the fans
    # power = np.array(np.zeros(solar_full.size))
    power = np.zeros(solar_full.size)
    power = power.reshape(1, power.size)

    # loading the dynamic data to be input to the main function
    power, solar_full, start_idx, f_start, f_end, f_on, Q0, night_mask_full, Pmax0, time_curr = \
        dynamicData(power, solar_full, f_on)
    print('Pmax0_dynamic output: ', Pmax0) ###########################

    # Define all the needed static info
    ### This function sets the prices
    prices_full, d_price, Qmin, Qmax, cmax, dmax, fmax, n_f = adjustedStaticData()

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

    p_curr = np.zeros(solar_curr.size)
    p_curr = p_curr.reshape(1,p_curr.size)

    # get prices for current time
    prices_curr = prices_full[:, time_curr:time_curr + t_lookahead]

    # simplified fan prediction that only uses current time and indicator if fan is on
    f_p = contr.fanPredictionSimple(f_on, time_curr, f_start, f_end)

    c_s, d_s, Q_s, prob_s, Pmax_ex = contr.optimize(p_curr, solar_curr, prices_curr, Q0, Pmax0, f_p)


    if prob_s != 'optimal':
        print('optimization status', prob_s)

    print('Old max power', Pmax0, 'new expected maximum power', Pmax_ex) ###########################

    # input real time values for net power, battery power (u_curr = charge - discharge power), price
    real_time_data_point_for_net_power = -net_load()
    p_net = real_time_data_point_for_net_power

    # Updating db for max_power:
    queryset_month = FarmMaxDemand.objects.all()
    if queryset_month:
        data_month = queryset_month.order_by('-id')[0]
        if data_month.max_power < p_net:
            data_month.max_power = p_net
            data_month.save()
            print('Saving new max_power: ', p_net)

    print('net_load: ', p_net) ###########################
    u_curr = c_s[:, 0] - d_s[:, 0]

    u_new = realTimeUpdate(p_net, Pmax_ex, u_curr)
    if u_new != u_curr:
        print('value of u changed from', u_curr)
        print('to', u_new)
        if u_new < 0:
            d_s[0][0] = -u_new
            c_s[0][0] = 0
        else:
            c_s[0][0] = u_new
            d_s[0][0] = 0

    c_s = c_s.astype(int)
    d_s = d_s.astype(int)

    c_curr = c_s[0][0]
    d_curr = d_s[0][0]

    # Actuating in the battery:
    if c_curr != 0 and d_curr == 0:
        batt_act(mode='charge', val=c_curr*1000)
        print('Charge: ', c_curr)
    elif c_curr == 0 and d_curr != 0:
        batt_act(mode='discharge', val=d_curr*1000)
        print('Discharge: ', d_curr)
    elif c_curr == 0 and d_curr == 0:
        # Stop dis/charging
        batt_act(mode='charge', val=0)
        print('Battery idle')
    else:
        print('Inconsistent results: Either c_curr or d_curr needs to be zero')
