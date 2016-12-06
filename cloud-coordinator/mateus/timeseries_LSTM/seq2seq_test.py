import os
os.environ['KERAS_BACKEND']='tensorflow'#'tensorflow' 'theano'
from keras.models import Sequential
import numpy as np
from os.path import join
import pandas as pd
import json
from skimage.util.shape import view_as_windows
from models import SimpleSeq2seq
import sys

print('calculating test...!!!')
#-----------------------------
# loading data
#dataPath='/media/mateus/dados2/Stanford/normalized'
dataPath='.'
sizeData=8760
dates = pd.date_range('08/01/2011', periods=sizeData, freq='H')
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
print words.shape
#-----------------------------
window_size=168
n_bins=250
size_pred=24
def load_model(name_file):
    loaded_model = SimpleSeq2seq(input_dim=128, input_length=window_size, hidden_dim=20, output_length=size_pred,output_dim=n_bins, depth=2)
    loaded_model.compile(loss='mse', optimizer='rmsprop')
    loaded_model.load_weights(name_file+'.h5')
    return loaded_model

print('creating model!.!')
model=load_model('seq2seq_ep1_user40000_Weights')

# -----------------------------
# dictionary
final_embeddings = np.loadtxt(join(dataPath, 'final_embeddings_'+str(sizeData)+'.csv'), delimiter=',').astype(dtype=np.float16)
# Reading data back

with open(join(dataPath, 'reverse_dictionary_'+str(sizeData)+'.json'), 'r') as f:
    _reverse_dictionary = json.load(f)
with open(join(dataPath, 'dictionary_'+str(sizeData)+'.json'), 'r') as f:
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
sizeTest=int(train_idxs.size-train_idxs.sum())
print 'sizeTest=',sizeTest
#--------------------------

#-----------------------------
# data input and output
intToBinary=np.eye(n_bins,n_bins,dtype=np.bool)

nUsers = words.shape[0]
window_shape = (window_size,)
stepAhead = 24

ini_users=int(sys.argv[1])
end_users = int(sys.argv[2])

sizeSerie = words.shape[1] - (window_size + stepAhead - 1)

# in order to run it in many instances
#meterToXTest = np.empty((nUsers, sizeTest, window_size), dtype=np.int16)
meterToXTest = np.empty((end_users-ini_users, sizeTest, window_size), dtype=np.int16)

for u in xrange(ini_users,end_users):
    serie = words[u, :]
    xLoad = (view_as_windows(serie, window_shape))[:-stepAhead, :]
    yLoad24 = np.empty((serie.size - (window_size + stepAhead - 1), stepAhead), dtype=np.int16)
    yLoad24[:, -1] = serie[(window_size + stepAhead - 1):]
    for i in xrange(stepAhead - 1):
        yLoad24[:, i] = serie[(window_size + i):-(stepAhead - (i + 1))]
    #meterToXTest[u] = xLoad[yTrain_idx == 0, :]
    meterToXTest[u-ini_users] = xLoad[yTrain_idx==0, :]
#-----------------------------
print('removing words from memory')
del words
#-----------------------------
# test
print('starting test...')
#shapeYtest=(nUsers, sizeTest, stepAhead)
shapeYtest=(end_users-ini_users, sizeTest, stepAhead)
meterToYTest_pred=np.empty(shapeYtest,dtype=np.int16)
print('meterToYTest_pred=',meterToYTest_pred.shape)
aux=0
for u in xrange(end_users-ini_users):
  print('user=', u)
  X = np.zeros((sizeTest, window_size, 128), dtype=np.float)
  for b in range(sizeTest):
    vecX=meterToXTest[u,b,:]
    for i in xrange(window_size):
        X[b,i,:]=final_embeddings[dictionary[vecX[i]]]
  predictions = model.predict(X, verbose=0)
  #print('predictions=',predictions.shape)
  for t_idx in xrange(sizeTest):
    for t in xrange(size_pred):
        meterToYTest_pred[u,t_idx,t]= np.argmax(predictions[t_idx,t,:])
  if u % 500 == 0:
    print('saving user=', u)
    for h in xrange(size_pred):
        print('saving hour='+ str(h)+' user='+str(u))
        #pathForecast = join('.', 'results', 'meterToYTest_pred_user_'+str(aux)+'_'+ str(u) + '_'+str(h)+'h.csv')
        pathForecast = join('.', 'result_test','_meterToYTest_pred_user_' + str(aux+ini_users) + '_' + str(u+ini_users) + '_' + str(h) + 'h.csv')
        np.savetxt(pathForecast, meterToYTest_pred[aux:u, :, h], delimiter=',')
    aux=u
#-----------------------------
for h in xrange(size_pred):
    print('saving hour=' + str(h) + ' user=' + str(u))
    #pathForecast = join('.', 'results', 'meterToYTest_pred_user_' + str(aux) + '_' + str(nUsers) + '_' + str(h) + 'h.csv')
    pathForecast = join('.', 'result_test','_meterToYTest_pred_user_' + str(aux) + '_' + str(end_users-1) + '_' + str(h) + 'h.csv')
    #np.savetxt(pathForecast, meterToYTest_pred[aux:nUsers, :, h], delimiter=',')
    np.savetxt(pathForecast, meterToYTest_pred[aux:end_users, :, h], delimiter=',')
#-----------------------------
# saving results
print('saving results')
for h in xrange(size_pred):
    print('saving hour=',str(h))
    #/media/mateus/dados2/Stanford/normalized/seq2seq/results
    np.savetxt(join('.', 'result_test','_0_meterToYTest_pred_'+str(h)+'h_user_'+str(ini_users)+'_'+str(end_users)+'.csv'), meterToYTest_pred[:,:,h],delimiter=',')
#-----------------------------