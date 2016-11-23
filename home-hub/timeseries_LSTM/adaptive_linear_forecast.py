import numpy as np
import pandas as pd
import sys, os
from os.path import join
from skimage.util.shape import view_as_windows

# ===============================================
# methods
import AdaptiveLinear as al
# ===============================================
np.set_printoptions(precision=3)
print('starting...')

class runModels:
    """
    A wrapper to evaluate different forecasting methods
    """

    def __init__(self, datetime, path, typeModel, windowSize):
        """
        Initialization function
        :param datetime:
        :param path:
        :param typeModel:
        :param windowSize:
        """
        self.dates = pd.DatetimeIndex(datetime.to_pydatetime())
        self.path = path
        self.typeModel = typeModel
        self.windowSize = windowSize

    def joinAllResults(self, path, nUsers, stepAhead):
        user = 0
        key = str(user) + '_' + str(stepAhead) + 'h'
        df_train_main = pd.read_csv((path + str(stepAhead) + 'h_user' + str(user) + '_train.csv'), index_col=0)
        df_test_main = pd.read_csv((path + str(stepAhead) + 'h_user' + str(user) + '_test.csv'), index_col=0)

        for user in xrange(1, nUsers):
            key = str(user) + '_' + str(stepAhead) + 'h'

            df_test = pd.read_csv((path + str(stepAhead) + 'h_user' + str(user) + '_test.csv'), index_col=0)
            df_test_main[key] = df_test[key]
            os.remove((path + str(stepAhead) + 'h_user' + str(user) + '_test.csv'))

            df_train = pd.read_csv((path + str(stepAhead) + 'h_user' + str(user) + '_train.csv'), index_col=0)
            df_train_main[key] = df_train[key]
            os.remove((path + str(stepAhead) + 'h_user' + str(user) + '_train.csv'))
        df_test_main.to_csv(self.path + '/prediction_' + str((stepAhead)) + 'h_test.csv', float_format='%.3f')
        df_train_main.to_csv(self.path + '/prediction_' + str((stepAhead)) + 'h_train.csv', float_format='%.3f')
        os.remove((path + str(stepAhead) + 'h_user0_test.csv'))
        os.remove((path + str(stepAhead) + 'h_user0_train.csv'))

    def createExportFileUser(self, yTrain_idxs, user, hour, y_forecast_te, y_forecast_tr, path,dates):
        key = str(user) + '_' + str(hour) + 'h'
        df_ = pd.DataFrame(index=dates[yTrain_idxs==0], columns=[key])
        df_[key] = y_forecast_te
        df_.to_csv(path + '_test.csv', float_format='%.3f')

        df_ = pd.DataFrame(index=dates[yTrain_idxs==1], columns=[key])
        df_[key] = y_forecast_tr
        df_.to_csv(path + '_train.csv', float_format='%.3f')

    def exportTrainTest(self, dates, y_actual,path,train_idxs):
        listCol = []
        print 'train_idxs=',train_idxs.sum()
        y_actual_tr = y_actual[train_idxs==1, :]
        y_actual_te = y_actual[train_idxs==0, :]
        nUsers = y_actual_te.shape[1]
        for user in xrange(nUsers):
            listCol.append(user)
        df_train = pd.DataFrame(data=y_actual_tr,index=dates[train_idxs==1], columns=listCol)
        df_test = pd.DataFrame(data=y_actual_te,index=dates[train_idxs==0], columns=listCol)
        print 'saving train'
        df_train.to_csv(path + '/real_train.csv', float_format='%.3f')
        print 'saving test'
        df_test.to_csv(path + '/real_test.csv', float_format='%.3f')

    def runHourUser(self, user, load, idx_tr,idx_te, stepAhead, dates, xTemp, path):
        """
        Load forecasting for one user
        :param user:
        :param load: load for one user
        :param nTrain:
        :param stepAhead:
        :param dates:
        :param xTemp:
        :param path:
        :return:
        """
        # The path for storing testing loads
        pathTest = path + str((stepAhead)) + 'h_user' + str(user) + '_test.csv'

        if not os.path.exists(pathTest):
            window_shape = (self.windowSize,)
            xLoad = (view_as_windows(load.copy(), window_shape))[:-stepAhead, :]
            yLoad = load[(self.windowSize + stepAhead - 1):]
            y = yLoad.ravel()
            lag = int(self.typeModel.split('_')[-1])
            model = al.AdaptiveLinear(y,lag)
            X=xLoad[:,-lag:]
            y_train = model.fit(X[idx_tr, :], y[idx_tr])
            y_test = model.predict(X[idx_te, :], y[idx_te])
            return y_train, y_test
        else:
            key = str(user) + '_' + str(stepAhead) + 'h'
            df_test = pd.read_csv(pathTest, index_col=0)
            print 'user already calculated.'
            return 0, df_test[key] #ignore saving train
        print 'finished user', user

    def checkAllPred(self, nUsers, setT, path):
        for user in xrange(nUsers):
            if not os.path.exists(path + str(user) + '_' + setT + '.csv'):
                print 'missing user=' + str(user) + ' ' + setT
                return True
        return False

    def runPredictionHour(self, load, user2zip, stepAhead, xTemp, train_idxs):
        """
        A wrapper for load forecasting for multi users
        :param load: a numpy array, size(length of all training and testing, number of users)
        :param user2zip: a numpy array, size (number of users, 1), the zip5 of each user
        :param stepAhead: an int, forecasting horizon
        :param xTemp: a dict, keys are zips (int), values are associated numpy array,
                      size(window size, length of training and testing)
        :param sizeLastMonth: an int, the total data points for last hour
        :return: None
        """
        path_prefix = self.path + '/prediction_'

        # Date time range for training and testing
        dates = self.dates[self.windowSize + (stepAhead - 1):]
        yTrain_idxs = train_idxs[(self.windowSize + stepAhead - 1):]
        nUsers = load.shape[1]
        user = 0
        if os.path.exists((path_prefix + str(stepAhead) + 'h_user0_test.csv')):
            os.remove((path_prefix + str(stepAhead) + 'h_user0_test.csv'))
            os.remove((path_prefix + str(stepAhead) + 'h_user0_train.csv'))
        idx_tr = yTrain_idxs == 1
        idx_te = yTrain_idxs == 0
        y_train,y_test=self.runHourUser(user, load[:, user], idx_tr,idx_te, stepAhead, dates, xTemp[user2zip[user]], path_prefix)

        y_tests=np.empty((y_test.size,nUsers))
        y_tests[:,0]=y_test[:,0]

        cols=[]
        cols.append(0)
        print 'predicting users - hour=',stepAhead
        for user in xrange(1, nUsers):
            cols.append(user)
            key = str(user) + '_' + str(stepAhead) + 'h'
            y_train, y_test = self.runHourUser(user, load[:, user], idx_tr,idx_te, stepAhead, dates, xTemp[user2zip[user]],path_prefix)
            y_tests[:,user]=y_test[:,0]
            if user%100==0:
                print 'hour=' + str(stepAhead) + ' user=' + str(user)

        df_test_main = pd.DataFrame(data=y_tests,index=dates[yTrain_idxs == 0], columns=cols)
        df_test_main.to_csv(self.path + '/prediction_' + str((stepAhead)) + 'h_test.csv', float_format='%.3f')

if __name__ == '__main__':
    data_dir = '..'
    working_dir = join(data_dir, 'predictions')

    hours = np.arange(1,25)
    # each hour to predict

    typeModels = np.array(['AdaptiveLinear_all_168'])#,'AdaptiveLinear_4','AdaptiveLinear_8','AdaptiveLinear_24'])

    sizeData=8760#744#2208
    dates = pd.date_range('08/01/2011', periods=sizeData, freq='H')  # this is the date-time of data.

    tempPath = join(data_dir, 'temp_by_zip.csv')
    df_tempByZip = pd.read_csv(tempPath, index_col=0)
    windowSize = 168
    window_shape = (windowSize,)
    discretization = 24
    pathZip = join(data_dir, 'zip5.csv')
    loadFile = np.loadtxt(pathZip, delimiter=',', dtype=np.str)
    user_to_zip = loadFile[1:, 1].astype('int')
    num_users_per_grp = 2000#100#2000

    # getting the number of days for each month
    month_end_dates = (dates[dates.is_month_end])[::24]
    numberDaysMonth = np.array(month_end_dates.day)
    # For the case that the last day of the data is not the last day of the month,
    # for example: if data has 8760 time stamps and it is leap year, then last day is 7/30
    if month_end_dates[-1].month != dates[-1].month:
        numberDaysMonth = np.concatenate([numberDaysMonth, (np.array([dates[-1].day]))])

    train_idxs = np.zeros(dates.size)
    months_test = np.array([2, 5, 6, 8, 11])
    aux = 0
    for m in xrange(12):
        if not (m in months_test):
            train_idxs[aux:aux + numberDaysMonth[m] * discretization] = 1
        aux += numberDaysMonth[m] * discretization
    # --------------------------

    # Generate 2D arrays representing each training months (Last one does not have test data)
    #xMonths = view_as_windows(np.arange(numberDaysMonth.size), (sizeFrameMonth,))
    numProcess = 6
    # Iterate 59 groups
    for group_idx in xrange(1,60):
        print 'Starting group ', group_idx
        # Read load file for one group
        #loadPath = data_dir + '/user_grp_' + str(group_idx) + '.csv'
        loadPath = data_dir + '/norm_group' + str(group_idx) + '.csv'
        loadFile = np.loadtxt(loadPath, delimiter=',', dtype=np.str)
        load = loadFile[:sizeData, :].astype('float')
        # Remove empty data
        idx = np.logical_or(np.isnan(load), np.isinf(load))
        load[idx] = 0.0
        idx = load < 0.0
        load[idx] = 0.0

        # Get zip for each user in the group
        zipcodes = user_to_zip[num_users_per_grp * (group_idx - 1):num_users_per_grp * (group_idx)]

        print 'calculating xTemp for all zipcodes.'
        xTemp_by_hour = {}
        for h in hours:
            xTemp_by_hour[h] = {}
        for zipcode in df_tempByZip.keys():
            serie = np.array(df_tempByZip[zipcode][:])
            matrixTemp = view_as_windows(serie, window_shape)

            for h in hours:
                xTemp_by_hour[h][int(zipcode)] = matrixTemp[:-h, :]
        print 'finished all xTemp'

        for typeModel in typeModels:
            pathForecast = join(working_dir,
                                typeModel,
                                str(dates[-1].month) + '_' + str(dates[-1].year),
                                'user_grp_' + str(group_idx))

            if not os.path.exists(pathForecast):
                os.makedirs(pathForecast)

            truePath = join(working_dir,
                                'True',
                                str(dates[-1].month) + '_' + str(dates[-1].year),
                                'user_grp_' + str(group_idx))
            if not os.path.exists(truePath):
                os.makedirs(truePath)
            # Initialize a class instance
            forecast = runModels(dates[:], pathForecast, typeModel, windowSize)

            for hour in hours:
                print 'Hour=',hour
                fileForecast = 'prediction_' + str(hour) + 'h_test.csv'
                if not os.path.exists(join(pathForecast, fileForecast)):
                    forecast.runPredictionHour(load, zipcodes, hour, xTemp_by_hour[hour],train_idxs)
                    '''
                    Process(target=forecast.runPredictionHour,args=(load, zipcodes, hour, xTemp_by_hour[hour],train_idxs)).start()
                    while (len(multiprocessing.active_children()) > numProcess):
                        time.sleep(1)
                    if psutil.virtual_memory()[2] > 80.0:
                        print 'waiting because of memory...'
                        print 'memory = ', psutil.virtual_memory()[2]
                        while (psutil.virtual_memory()[2]) > 50.0:
                            time.sleep(5)
                        print 'restarting.'
                    #'''

                print 'Finish hour ', hour
    print 'Finished group ', group_idx

print 'finished script'