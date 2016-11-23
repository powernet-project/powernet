# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import math
import os
import random
import zipfile

import numpy as np
from six.moves import urllib
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf
from os.path import join

import pandas as pd

#dataPath='/media/mateus/My Passport/Benchmark/normalized'
#dataPath='/media/mateus/hd2/tensorflow/normalized'
dataPath='/mnt/normalized'
#dates = pd.date_range('08/01/2011', periods=8760, freq='H')

sizeData=8760 # all // #2208 ->3months #744 ->1 month
dates = pd.date_range('08/01/2011', periods=sizeData, freq='H')
n_bins_raw=2000
n_bins=250
usersPerGroup=2000
words=None
nr=''# '' or '_raw'

#===========================================================
# loading data
mtx_path = join(dataPath, 'bin_group59'+nr+'.csv')
mtx = np.loadtxt(mtx_path, delimiter=',').astype(dtype=np.int16)[:sizeData,:]
print('mtx=',mtx.shape)
words=np.empty(((58*usersPerGroup)+mtx.shape[1],sizeData),dtype=np.int16)
print('words=',words.shape)
words[-mtx.shape[1]:,:]=mtx.T

for group_idx in xrange(1,59):
  print('group=',group_idx)
  mtx_path = join(dataPath, 'bin_group'+str(group_idx)+nr+'.csv')
  idx=group_idx-1
  words[(idx*usersPerGroup):((idx+1)*usersPerGroup),:]=np.loadtxt(mtx_path, delimiter=',').astype(dtype=np.int16)[:sizeData,:].T
#===========================================================

# Step 2: Build the dictionary and replace rare words with UNK token.
vocabulary_size = n_bins
def build_dataset(words):
  print('counting frequency of words...')
  count = [['UNK', -1]]
  listFreq=collections.Counter(words.ravel()).most_common(vocabulary_size - 1)
  count.extend(listFreq)
  print('creating dictionary...')
  dictionary = dict()
  for word, _ in count:
    dictionary[word] = len(dictionary)
  print('creating data...')
  data=np.empty(words.shape,dtype=np.int16)
  unk_count = 0
  for i in xrange(words.shape[0]):
    if(i%10000==0):
        print('meter=',i)
    for j in xrange(words.shape[1]):
        word=words[i,j]
        if word in dictionary:
          index = dictionary[word]
        else:
          index = 0  # dictionary['UNK']
          unk_count += 1
        data[i,j]=index
  count[0][1] = unk_count
  print('reverting dictionary...')
  reverse_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
  return data, count, dictionary, reverse_dictionary

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

data, count, dictionary, reverse_dictionary = build_dataset(words[:,train_idxs==1])
#del words  # Hint to reduce memory.

# Step 3: Function to generate a training batch for the skip-gram model.
meter_index=0
data_index = 0
print_m=2000

#--------
skip_train=np.array([1463,2927,3671])# break time on train |Aug+sep|+|Nov+Dec|+|Mar|+|May+Jun|
#--------

def generate_batch(batch_size, num_skips, skip_window):
  global data_index
  global meter_index
  assert batch_size % num_skips == 0
  assert num_skips <= 2 * skip_window
  batch = np.ndarray(shape=(batch_size), dtype=np.int32)
  labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
  span = 2 * skip_window + 1 # [ skip_window target skip_window ]
  buffer = collections.deque(maxlen=span)
  for _ in range(span):
    buffer.append(data[meter_index,data_index])
    data_index = (data_index + 1) % data.shape[1]
    if(data_index==0):
        meter_index= (meter_index+1) % data.shape[0]
        if(meter_index%print_m==0):
            print('meter=',meter_index)
    if((data_index+skip_window) in skip_train):
      data_index+=2*skip_window
  for i in range(batch_size // num_skips):
    target = skip_window  # target label at the center of the buffer
    targets_to_avoid = [ skip_window ]
    for j in range(num_skips):
      while target in targets_to_avoid:
        target = random.randint(0, span - 1)
      targets_to_avoid.append(target)
      batch[i * num_skips + j] = buffer[skip_window]
      labels[i * num_skips + j, 0] = buffer[target]
    buffer.append(data[meter_index,data_index])
    data_index = (data_index + 1) % data.shape[1]
    if(data_index==0):
        meter_index= (meter_index+1) % data.shape[0]
        if(meter_index%print_m==0):
            print('meter=',meter_index)
    if ((data_index + skip_window) in skip_train):
      data_index += 2 * skip_window
  return batch, labels

batch, labels = generate_batch(batch_size=8, num_skips=2, skip_window=1)
for i in range(8):
  print(batch[i], reverse_dictionary[batch[i]],
      '->', labels[i, 0], reverse_dictionary[labels[i, 0]])

# Step 4: Build and train a skip-gram model.
batch_size = 186#128
embedding_size = 128  # Dimension of the embedding vector.
skip_window = 24 #1      # How many words to consider left and right.
num_skips = 6#2         # How many times to reuse an input to generate a label.

# We pick a random validation set to sample nearest neighbors. Here we limit the
# validation samples to the words that have a low numeric ID, which by
# construction are also the most frequent.
valid_size = 16     # Random set of words to evaluate similarity on.
valid_window = 100  # Only pick dev samples in the head of the distribution.
valid_examples = np.random.choice(valid_window, valid_size, replace=False)
num_sampled = 64    # Number of negative examples to sample.

graph = tf.Graph()

with graph.as_default():

  # Input data.
  train_inputs = tf.placeholder(tf.int32, shape=[batch_size])
  train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])
  valid_dataset = tf.constant(valid_examples, dtype=tf.int32)

  # Ops and variables pinned to the CPU because of missing GPU implementation
  #with tf.device('/cpu:0'):

  #with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)):
  with tf.Session(config=tf.ConfigProto(log_device_placement=True)):
    # Look up embeddings for inputs.
    embeddings = tf.Variable(
        tf.random_uniform([vocabulary_size, embedding_size], -1.0, 1.0))
    embed = tf.nn.embedding_lookup(embeddings, train_inputs)

    # Construct the variables for the NCE loss
    nce_weights = tf.Variable(
        tf.truncated_normal([vocabulary_size, embedding_size],
                            stddev=1.0 / math.sqrt(embedding_size)))
    nce_biases = tf.Variable(tf.zeros([vocabulary_size]))

  # Compute the average NCE loss for the batch.
  # tf.nce_loss automatically draws a new sample of the negative labels each
  # time we evaluate the loss.
  loss = tf.reduce_mean(
      tf.nn.nce_loss(nce_weights, nce_biases, embed, train_labels,
                     num_sampled, vocabulary_size))

  # Construct the SGD optimizer using a learning rate of 1.0.
  optimizer = tf.train.GradientDescentOptimizer(0.01).minimize(loss)

  # Compute the cosine similarity between minibatch examples and all embeddings.
  norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
  normalized_embeddings = embeddings / norm
  valid_embeddings = tf.nn.embedding_lookup(
      normalized_embeddings, valid_dataset)
  similarity = tf.matmul(
      valid_embeddings, normalized_embeddings, transpose_b=True)

  # Add variable initializer.
  init = tf.initialize_all_variables()

# Step 5: Begin training.
num_steps = 8000001 #10 milions epochs.
meter_index=0
data_index = 0
#with tf.Session(graph=graph) as session:
config = tf.ConfigProto(device_count={"GPU": 0,"GPU": 1,"GPU": 2,"GPU": 3, "CPU": 0})
session = tf.Session(config=config,graph=graph)
if True:
  # We must initialize all variables before we use them.
  init.run()
  print("Initialized")

  average_loss = 0
  for step in xrange(num_steps):
    batch_inputs, batch_labels = generate_batch(
        batch_size, num_skips, skip_window)
    #print('batch_inputs=',batch_inputs)
    #print('batch_labels=',batch_labels)
    #aa/bb
    feed_dict = {train_inputs : batch_inputs, train_labels : batch_labels}

    # We perform one update step by evaluating the optimizer op (including it
    # in the list of returned values for session.run()
    _, loss_val = session.run([optimizer, loss], feed_dict=feed_dict)
    average_loss += loss_val

    if step % 10000 == 0:
      if step > 0:
        average_loss /= 10000
      # The average loss is an estimate of the loss over the last 2000 batches.
      print("Average loss at step ", step, ": ", average_loss)
      average_loss = 0

    # Note that this is expensive (~20% slowdown if computed every 500 steps)
    '''
    if step % 10000 == 0:
      sim = similarity.eval()
      for i in xrange(valid_size):
        valid_word = reverse_dictionary[valid_examples[i]]
        top_k = 8 # number of nearest neighbors
        nearest = (-sim[i, :]).argsort()[1:top_k+1]
        #print('nearest=',nearest)
        log_str = "Nearest to %s:" % valid_word
        for k in xrange(top_k):
          #print('nearest[k]=',nearest[k])
          close_word = reverse_dictionary[nearest[k]]
          log_str = "%s %s," % (log_str, close_word)
        print('Epoch = '+str(step)+' '+log_str)
    #'''
  final_embeddings = normalized_embeddings.eval()

# saving final_embeddings
#dataPath = '/media/mateus/hd2/tensorflow/normalized'
dataPath='/mnt/normalized'
np.savetxt(join(dataPath, 'final_embeddings_'+str(sizeData)+nr+'.csv'), final_embeddings, delimiter=',')

import json
with open(join(dataPath, 'reverse_dictionary_'+str(sizeData)+nr+'.json'), 'w') as fp:
    json.dump(reverse_dictionary, fp)

with open(join(dataPath, 'dictionary_'+str(sizeData)+nr+'.json'), 'w') as fp:
  json.dump(dictionary, fp)
#np.savetxt(join(dataPath, 'final_embeddings_'+str(sizeData)+nr+'.csv'), final_embeddings, delimiter=',')
#np.savetxt(join(dataPath, 'reverse_dictionary_'+str(sizeData)+nr+'.csv'), reverse_dictionary, delimiter=',')