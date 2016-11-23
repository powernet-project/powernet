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

# simplest way to create an embedding representaion

def calculate_c_mtx(group_idx,y,y_raw,data_dir,dir_save,train_idxs,window_size):
    if not os.path.exists(dir_save):
        os.makedirs(dir_save)
    # Read load file for one group
    binPath = join(data_dir, 'bin_group' + str(group_idx) + '.csv')
    bins = np.loadtxt(binPath, delimiter=',', dtype=np.float).astype(np.int)

    binPath = join(data_dir, 'bin_group' + str(group_idx) + '_raw.csv')
    bins_raw = np.loadtxt(binPath, delimiter=',', dtype=np.float).astype(np.int)

    nUsers = bins.shape[1]
    size_series = bins.shape[0]

    #co-occurrence matrix
    c_mtx = np.zeros((y.size,y.size))
    c_mtx_raw = np.zeros((y_raw.size,y_raw.size))

    #window_size=24 # looking only for left
    idx=window_size
    while(idx<size_series):
        #print 'idx=',idx
        if(train_idxs[idx]==1):
            for u in xrange(nUsers):
                # --------- norm ----------
                lin=bins[idx,u]
                cols=bins[idx-window_size:idx,u]
                for c in cols:
                    c_mtx[lin,c]+=1
                #--------- raw ----------
                lin = bins_raw[idx, u]
                cols = bins_raw[idx - window_size:idx, u]
                for c in cols:
                    c_mtx_raw[lin, c] += 1
            idx+=1
        else:
            while(idx<size_series and train_idxs[idx]!=1):
                idx+=1
            idx+=window_size

    np.savetxt(join(dir_save, 'co_occurrence_mtx_group' + str(group_idx) + '.csv'), c_mtx, delimiter=',')
    np.savetxt(join(dir_save, 'co_occurrence_mtx_group' + str(group_idx) + '_raw.csv'), c_mtx_raw, delimiter=',')
    print 'Finished group ', group_idx

if __name__ == '__main__':
    data_dir = '.'
    dir_save='./SVD'
    dates = pd.date_range('08/01/2011', periods=8760, freq='H')  # this is the date-time of data.
    num_users_per_grp = 2000

    # getting the number of days for each month
    month_end_dates = (dates[dates.is_month_end])[::24]
    numberDaysMonth = np.array(month_end_dates.day)
    # For the case that the last day of the data is not the last day of the month,
    # for example: if data has 8760 time stamps and it is leap year, then last day is 7/30
    if month_end_dates[-1].month != dates[-1].month:
        numberDaysMonth = np.concatenate([numberDaysMonth, (np.array([dates[-1].day]))])

    # nTrain=dates.size-np.sum(numberDaysMonth[-4:])
    train_idxs = np.zeros(dates.size)
    months_test = np.array([2, 5, 6, 8, 11])
    aux = 0
    discretization=24
    for m in xrange(12):
        if not (m in months_test):
            train_idxs[aux:aux + numberDaysMonth[m]*discretization] = 1
        aux += numberDaysMonth[m]*discretization

    print 'train_idxs=',train_idxs.shape
    print 'sum train_idxs=', train_idxs.sum()

    n_bins = 250
    y = np.arange(n_bins)
    n_bins_raw = 100
    y_raw = np.arange(20 * n_bins_raw)

    windows=np.array([6,14])#2,4,68,10,12,14,16,18,20,22,24
    numProcess = 14
    for ws in windows:
        '''
        # Iterate 59 groups
        #calculate_c_mtx(1, y, y_raw, data_dir, dir_save, train_idxs)
        for group_idx in xrange(3,4):# 60):
            print 'Starting group ', group_idx
            Process(target=calculate_c_mtx, args=(group_idx, y, y_raw, data_dir, dir_save+'_'+str(ws), train_idxs,ws)).start()
            while (len(multiprocessing.active_children()) > numProcess):
                time.sleep(1)
            if psutil.virtual_memory()[2] > 80.0:
                print 'waiting because of memory...'
                print 'memory = ', psutil.virtual_memory()[2]
                while (psutil.virtual_memory()[2]) > 50.0:
                    time.sleep(5)
                print 'restarting.'


        #for group_idx in xrange(1, 60):
        #    cPath = join(dir_save+'_'+str(ws), 'co_occurrence_mtx_group' + str(group_idx) + '.csv')
        #    cPath2 = join(dir_save+'_'+str(ws), 'co_occurrence_mtx_group' + str(group_idx) + '_raw.csv')
        #    while (not os.path.exists(cPath)) and (not os.path.exists(cPath2)):
        #        time.sleep(1)
        '''

        print 'starting sum all c-mtx'
        # co-occurrence matrix
        c_mtx = np.zeros((y.size, y.size))
        c_mtx_raw = np.zeros((y_raw.size, y_raw.size))
        for group_idx in xrange(1, 60):
            cPath = join(dir_save+'_'+str(ws), 'co_occurrence_mtx_group' + str(group_idx) + '.csv')
            c_mtx += np.loadtxt(cPath, delimiter=',', dtype=np.float)
            cPath = join(dir_save+'_'+str(ws), 'co_occurrence_mtx_group' + str(group_idx) + '_raw.csv')
            c_mtx_raw += np.loadtxt(cPath, delimiter=',', dtype=np.float)
            print 'Finished group ', group_idx
        idx=np.logical_or(np.isnan(c_mtx),np.isinf(c_mtx))
        idx_raw=np.logical_or(np.isnan(c_mtx_raw),np.isinf(c_mtx_raw))
        if idx.sum()>1 or idx_raw.sum()>1:
            print 'idx=',idx.sum()
            print 'idx_raw=',idx_raw.sum()
            print 'There is a problem.'
        else:
            print 'fine.'
        np.savetxt(join(dir_save+'_'+str(ws), 'co_occurrence_mtx_total.csv'), c_mtx, delimiter=',')
        np.savetxt(join(dir_save+'_'+str(ws), 'co_occurrence_mtx_total_raw.csv'), c_mtx_raw, delimiter=',')

        print 'calculating SVD'
        U, s, V = np.linalg.svd(c_mtx, full_matrices=True)
        np.savetxt(join(dir_save+'_'+str(ws), 'U_mtx.csv'), U, delimiter=',')
        np.savetxt(join(dir_save+'_'+str(ws), 's_mtx.csv'), s, delimiter=',')
        np.savetxt(join(dir_save+'_'+str(ws), 'V_mtx.csv'), V, delimiter=',')

        U, s, V = np.linalg.svd(c_mtx_raw, full_matrices=True)
        np.savetxt(join(dir_save+'_'+str(ws), 'U_mtx_raw.csv'), U, delimiter=',')
        np.savetxt(join(dir_save+'_'+str(ws), 's_mtx_raw.csv'), s, delimiter=',')
        np.savetxt(join(dir_save+'_'+str(ws), 'V_mtx_raw.csv'), V, delimiter=',')
        #'''
    print 'finished script'

