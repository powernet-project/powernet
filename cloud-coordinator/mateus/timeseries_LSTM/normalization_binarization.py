import numpy as np
import pandas as pd
import sys, os
from os.path import join
from multiprocessing import Process, Lock, Event
import multiprocessing
import time
import psutil
import pickle
from skimage.util.shape import view_as_windows
import datetime
from sklearn import neighbors
# ===============================================
np.set_printoptions(precision=3)
SEASON = {
    11: 'Winter',
    12: 'Winter',
    1: 'Winter',
    2: 'Spring',
    3: 'Spring',
    4: 'Spring',
    5: 'Summer',
    6: 'Summer',
    7: 'Summer',
    8: 'Autumn',
    9: 'Autumn',
    10: 'Autumn'
}

def process_group(group_idx,X,y,X_raw,y_raw,data_dir,dir_save,train_idxs):
    # Read load file for one group
    loadPath = join(data_dir, 'user_grp_' + str(group_idx) + '.csv')
    loadFile = np.loadtxt(loadPath, delimiter=',', dtype=np.str)
    load = loadFile[1:, 1:].astype('float')
    # Remove empty data
    idx = np.logical_or(np.isnan(load), np.isinf(load))
    load[idx] = 0.0
    idxs=train_idxs==1
    # value to bin.
    load_norm = np.empty_like(load)
    nUsers = load.shape[1]
    user_max = np.empty(nUsers)
    user_min = np.empty(nUsers)
    for u in xrange(nUsers):
        user_max[u] = np.max(load[idxs,u])
        user_min[u] = np.min(load[idxs,u])
        load_norm[:,u] = (load[:,u] - user_min[u]) / (user_max[u] - user_min[u])
        load_norm[load_norm[:,u] > 1.0,u] = 1.0
        load_norm[load_norm[:,u] < 0.0,u] = 0.0

    load_norm[np.isnan(load_norm)] = 0.0
    load_norm[np.isinf(load_norm)] = 1.0

    max_min = np.concatenate([user_max.reshape([-1, 1]), user_min.reshape([-1, 1])], axis=1)
    np.savetxt(join(dir_save, 'max_min_group' + str(group_idx) + '.csv'), max_min, delimiter=',')
    np.savetxt(join(dir_save, 'norm_group' + str(group_idx) + '.csv'), load_norm, delimiter=',')

    load_bin=np.zeros_like(load_norm,dtype=np.int)
    for i in xrange(load_norm.shape[0]):
        for j in xrange(load_norm.shape[1]):
            load_bin[i, j] = (np.abs(load_norm[i, j] - X)).argmin()
    np.savetxt(join(dir_save, 'bin_group' + str(group_idx) + '.csv'), load_bin, delimiter=',')

    load_bin_raw = np.zeros_like(load, dtype=np.int)
    for i in xrange(load.shape[0]):
        for j in xrange(load.shape[1]):
            load_bin_raw[i, j] = (np.abs(load[i, j] - X_raw)).argmin()
    np.savetxt(join(dir_save, 'bin_group' + str(group_idx) + '_raw.csv'), load_bin_raw, delimiter=',')
    print 'Finished group ', group_idx

if __name__ == '__main__':
    data_dir = '..'
    dir_save='.'
    dates = pd.date_range('08/01/2011', periods=8760, freq='H')  # this is the date-time of data.
    num_users_per_grp = 2000

    # getting the number of days for each month
    month_end_dates = (dates[dates.is_month_end])[::24]
    numberDaysMonth = np.array(month_end_dates.day)
    # For the case that the last day of the data is not the last day of the month,
    # for example: if data has 8760 time stamps and it is leap year, then last day is 7/30
    if month_end_dates[-1].month != dates[-1].month:
        numberDaysMonth = np.concatenate([numberDaysMonth, (np.array([dates[-1].day]))])

    train_idxs=np.zeros(dates.size)
    months_test=np.array([2,5,6,8,11])
    aux = 0
    discretization = 24
    for m in xrange(12):
        if not (m in months_test):
            train_idxs[aux:aux + numberDaysMonth[m] * discretization] = 1
        aux += numberDaysMonth[m] * discretization

    print 'train_idxs=', train_idxs.shape
    print 'sum train_idxs=', train_idxs.sum()

    n_bins = 250
    X = np.linspace(0.0, 1.0, num=n_bins).reshape([-1, 1])
    y = np.arange(n_bins)
    x_y=np.concatenate([X.reshape([-1, 1]), y.reshape([-1, 1])], axis=1)
    np.savetxt(join(dir_save, 'X_y_scale.csv'), x_y, delimiter=',')

    n_bins_raw = 100
    X_raw = np.linspace(0.0, 20.0, num=20*n_bins_raw).reshape([-1, 1])
    y_raw = np.arange(20*n_bins_raw)
    x_y_raw = np.concatenate([X_raw.reshape([-1, 1]), y_raw.reshape([-1, 1])], axis=1)
    np.savetxt(join(dir_save, 'X_y_raw_scale.csv'), x_y_raw, delimiter=',')

    numProcess = 14 # parallel processing
    # Iterate 59 groups
    for group_idx in xrange(1,60):
        print 'Starting group ', group_idx
        Process(target=process_group,args=(group_idx,X,y,X_raw,y_raw,data_dir,dir_save,train_idxs)).start()
        while (len(multiprocessing.active_children()) > numProcess):
            time.sleep(1)
        if psutil.virtual_memory()[2] > 80.0:
            print 'waiting because of memory...'
            print 'memory = ', psutil.virtual_memory()[2]
            while (psutil.virtual_memory()[2]) > 50.0:
                time.sleep(5)
            print 'restarting.'
print 'finished script'