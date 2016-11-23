import os
os.environ['KERAS_BACKEND']='tensorflow'#'tensorflow' 'theano'
from keras.models import Sequential
import numpy as np
from os.path import join
import pandas as pd
import json
from skimage.util.shape import view_as_windows
from models import SimpleSeq2seq
from keras.models import model_from_json

#-----------------------------
# loading data
print('loading data')
dataPath='/media/mateus/hd2/tensorflow/normalized'
#dataPath='/mnt/normalized'
sizeData=8760#744
dates = pd.date_range('08/01/2011', periods=sizeData, freq='H')
#n_bins_raw=2000
n_bins=250
nr=''# _raw
if 'raw' in nr:
    n_bins=2000
mtx_path = join(dataPath, 'bin_group59'+nr+'.csv')
mtx = np.loadtxt(mtx_path, delimiter=',').astype(dtype=np.int16)[:sizeData,:]
print('mtx=',mtx.shape)
usersPerGroup=2000
words=np.empty(((58*usersPerGroup)+mtx.shape[1],sizeData),dtype=np.int16)
print('words=',words.shape)
words[-mtx.shape[1]:,:]=mtx.T
for group_idx in xrange(1,59):
    print('group=',group_idx)
    mtx_path = join(dataPath, 'bin_group'+str(group_idx)+nr+'.csv')
    idx=group_idx-1
    words[(idx*usersPerGroup):((idx+1)*usersPerGroup),:]=np.loadtxt(mtx_path, delimiter=',').astype(dtype=np.int16)[:sizeData,:].T
#-----------------------------

# -----------------------------
# dictionary
final_embeddings = np.loadtxt(join(dataPath, 'final_embeddings_'+str(sizeData)+nr+'.csv'), delimiter=',').astype(dtype=np.float16)
# Reading data back

with open(join(dataPath, 'reverse_dictionary_'+str(sizeData)+nr+'.json'), 'r') as f:
    _reverse_dictionary = json.load(f)
with open(join(dataPath, 'dictionary_'+str(sizeData)+nr+'.json'), 'r') as f:
    _dictionary = json.load(f)

dictionary = {}
reverse_dictionary = {}
checkBin = np.zeros(n_bins)
for k in _dictionary.keys()[1:]:
    if ('UNK' in k):
        dictionary[k] = _dictionary[k]
    else:
        dictionary[int(k)] = _dictionary[k]
        checkBin[int(k)] = 1
for i in np.where(checkBin == 0)[0]:
    dictionary[i] = _dictionary['UNK']

checkBin = np.zeros(n_bins)
for k in _reverse_dictionary.keys():
    if ('UNK' in k):
        reverse_dictionary[k] = _reverse_dictionary[k]
    else:
        reverse_dictionary[int(k)] = _reverse_dictionary[k]
        checkBin[int(k)] = 1
for i in np.where(checkBin == 0)[0]:
    reverse_dictionary[i] = _reverse_dictionary['UNK']
# -----------------------------

#-----------------------------
# data input and output
print('creating data input and output')
window_size=168
size_pred=24
#sizeTest=144
#nTrain=744-(sizeTest+size_pred+window_size-1)
intToBinary=np.eye(n_bins,n_bins,dtype=np.bool)

nUsers = words.shape[0]
window_shape = (window_size,)
stepAhead = 24

#--------------------------
# filtering train and test

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
#--------------------------
yTrain_idx=train_idxs[(window_size + stepAhead - 1):]
#--------------------------

sizeSerie = words.shape[1] - (window_size + stepAhead - 1)
#meterToXTrain = np.empty((nUsers, sizeSerie - sizeTest, window_size), dtype=np.int16)
num_train=int(yTrain_idx.sum())
sizeTest=int((yTrain_idx==0).sum())
print('num_train=',num_train)
print('num_test=',sizeTest)
meterToXTrain = np.empty((nUsers, num_train, window_size), dtype=np.int16)
meterToXTest = np.empty((nUsers, sizeTest, window_size), dtype=np.int16)

#meterToYTrain = np.empty((nUsers, sizeSerie - sizeTest, stepAhead), dtype=np.int16)
meterToYTrain = np.empty((nUsers, num_train, stepAhead), dtype=np.int16)
meterToYTest = np.empty((nUsers, sizeTest, stepAhead), dtype=np.int16)

for u in xrange(nUsers):
    serie = words[u, :]
    xLoad = (view_as_windows(serie, window_shape))[:-stepAhead, :]
    yLoad24 = np.empty((serie.size - (window_size + stepAhead - 1), stepAhead), dtype=np.int16)
    yLoad24[:, -1] = serie[(window_size + stepAhead - 1):]
    for i in xrange(stepAhead - 1):
        yLoad24[:, i] = serie[(window_size + i):-(stepAhead - (i + 1))]
    meterToXTrain[u] = xLoad[yTrain_idx==1, :]
    meterToYTrain[u] = yLoad24[yTrain_idx==1, :]

    meterToXTest[u] = xLoad[yTrain_idx==0, :]
    meterToYTest[u] = yLoad24[yTrain_idx==0, :]
'''
    meterToXTrain[u] = xLoad[:-sizeTest, :]
    meterToYTrain[u] = yLoad24[:-sizeTest, :]
    meterToXTest[u] = xLoad[-sizeTest:, :]
    meterToYTest[u] = yLoad24[-sizeTest:, :]
'''
#-----------------------------

#-----------------------------
# batch generation
print('defining batch')
meter_index=0
data_index = 0
print_m=10000
batch_size=num_train#409
train_pos=np.where(yTrain_idx==1)[0]
def generate_batch():
  global data_index
  global meter_index
  X = np.zeros((batch_size, window_size, 128), dtype=np.float)
  Y = np.zeros((batch_size, size_pred, n_bins), dtype=np.int16)
  for b in range(batch_size):
    vecX=meterToXTrain[meter_index,data_index,:]
    for i in xrange(window_size):
        X[b,i,:]=final_embeddings[dictionary[vecX[i]]]
    vecY=meterToYTrain[meter_index,data_index,:]
    for i in xrange(size_pred):
        Y[b,i,:]=intToBinary[vecY[i],:]
    data_index = (data_index + 1) % num_train
    if(data_index==0):
        meter_index=(meter_index+1) % nUsers
        if(meter_index%print_m==0):
            print('meter=',meter_index)
  return X,Y
#-----------------------------

#-----------------------------
# model
model = SimpleSeq2seq(input_dim=128, input_length=window_size, hidden_dim=40, output_length=size_pred,output_dim=n_bins,depth=2)
model.compile(loss='mse', optimizer='rmsprop')
#-----------------------------

#-----------------------------
# save models functions
def save_model(k_model,name_file='seq2seq'):
    model.save_weights(name_file+'Weights.h5')

def load_model(name_file='seq2seq'):
    loaded_model = SimpleSeq2seq(input_dim=128, input_length=window_size, hidden_dim=20, output_length=size_pred,output_dim=n_bins, depth=1)
    loaded_model.compile(loss='mse', optimizer='rmsprop')
    loaded_model.load_weights(name_file+'Weights.h5')
    return loaded_model
#-----------------------------

#-----------------------------
# train
print('starting train')
meter_index=0
#data_index = 0
num_steps = 6000001
save_model_idx= 50000
for step in xrange(num_steps):
    if step % 10000 == 0:
        print('step=', step)
    X_train,Y_train=generate_batch()
    model.fit(X_train, Y_train, batch_size=batch_size, nb_epoch=1, verbose=1)
    if step % save_model_idx==0:
        model.fit(X_train, Y_train, batch_size=batch_size, nb_epoch=1, show_accuracy=True, verbose=1)
        print('saving model epoch ',str(step))
        save_model(model,name_file='seq2seq_ep'+str(step)+'_')
#-----------------------------
save_model(model,name_file='seq2seq_final_')