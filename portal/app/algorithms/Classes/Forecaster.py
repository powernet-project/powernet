from statsmodels.tsa.statespace.sarimax import SARIMAX
import numpy as np


class Forecaster:
    def __init__(self, my_order=(3, 0, 3), my_seasonal_order=(3, 0, 3, 24), pos=False, training_mean_p=None, training_mean_s=None):
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
