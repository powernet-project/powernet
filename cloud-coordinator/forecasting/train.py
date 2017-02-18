#!/usr/bin/env python
"""Entry point for Testing Learning Models"""

import argparse
import datetime
import math

from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

from nn.feedforward import FeedForward
from nn.rnn import Recurrent
from sql.models import ResInterval60, LocalWeather
from sql.sqlclient import SqlClient

from util import generate_data
from sklearn.model_selection import KFold

__author__ = "Edward Ng"
__email__ = "edjng@stanford.edu"

sqlClient = SqlClient()

FLAGS = None
LOOKBACK = 7 #days

load, earliest_date, latest_date = ResInterval60.get_batch(sqlClient)
weather = LocalWeather.get_weather(sqlClient, earliest_date, latest_date)

X, Y = generate_data(LOOKBACK, load, weather)

print 'total dataset size X:{},Y:{}'.format(X.shape, Y.shape)

parser = argparse.ArgumentParser(description='Run ML models for load forecasting.')
parser.add_argument('--model', default='ff', help='Pick a model to use for estimation.')
parser.add_argument('-t', '--train', action='store_true')

FLAGS, unparsed = parser.parse_known_args()

print 'running with arguments: ({})'.format(FLAGS)

nrmsd = []
prediction = None
kf = KFold(n_splits=3)

for train, test in kf.split(X):
    if FLAGS.model == 'ff':
        feedForward = FeedForward(num_layer=3, num_neuron=300,input_size=X.shape[1])
        if FLAGS.train == True:
            feedForward.train((X[train], Y[train]))
        squared_error, prediction = feedForward.test((X[test], Y[test]))
        nrmsd.append(math.sqrt(np.mean(squared_error)) / (np.max(Y[test]) - np.min(Y[test])))
        feedForward.sess.close()
        tf.reset_default_graph()

    elif FLAGS.model == 'lstm':
        recurrent = Recurrent()
        x=np.reshape(x, (x.shape[0], x.shape[1], 1))
        recurrent.train(training)
        print recurrent.test(test)
    else:
        print '{} is an invalid model. Pick from (ff), (lstm).'.format(FLAGS.model)
        break

print 'nrmsd mean: ({}), nrsmd std:({})'.format(np.mean(nrmsd), np.std(nrmsd))

# if prediction is not None:
#     plt.plot(test[1][-15:-1].flatten())
#     plt.plot(prediction[-15:-1].flatten())
#     plt.show()
