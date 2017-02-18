#!/usr/bin/env python
"""Entry point for Testing Learning Models"""

import argparse
import datetime
import math

from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

from linear.linear_regression import LinearRegression
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
parser.add_argument('-t', '--train', action='store_true', help='Explicitly train.')
parser.add_argument('-p', '--plot', action='store_true', help='Explicitly plot.')

FLAGS, unparsed = parser.parse_known_args()

print 'running with arguments: ({})'.format(FLAGS)

nrmsd = []
prediction = None
kf = KFold(shuffle=True, n_splits=3, random_state=0)

for train, test in kf.split(X):
    model = None

    if FLAGS.model == 'ff':
        model = FeedForward(num_layer=3, num_neuron=300,input_size=X.shape[1])
    elif FLAGS.model == 'linear':
        model = LinearRegression()
    else:
        print '{} is an invalid model. Pick from (ff),(linear).'.format(FLAGS.model)

    if FLAGS.train == True:
        model.train((X[train], Y[train]))

    squared_error, prediction = model.test((X[test], Y[test]))

    if FLAGS.model == 'ff':
        model.sess.close()
        tf.reset_default_graph()

    nrmsd.append(math.sqrt(np.mean(squared_error)) / (np.max(Y[test]) - np.min(Y[test])))

    if prediction is not None:
        plt.plot(Y[test][-15:-1].flatten())
        plt.plot(prediction[-15:-1].flatten())
        plt.show()

    # elif FLAGS.model == 'lstm':
    #     recurrent = Recurrent()
    #     x=np.reshape(x, (x.shape[0], x.shape[1], 1))
    #     recurrent.train(training)
    #     print recurrent.test(test)

print 'nrmsd mean: ({}), nrsmd std:({})'.format(np.mean(nrmsd), np.std(nrmsd))
