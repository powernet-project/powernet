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
from linear.svr import SVR
from nn.feedforward import FeedForward
from nn.rnn import Recurrent
from sql.models import ResInterval60, LocalWeather
from sql.sqlclient import SqlClient

from util import generate_data, get_error
from sklearn.model_selection import KFold

__author__ = "Edward Ng"
__email__ = "edjng@stanford.edu"

sqlClient = SqlClient()

FLAGS = None
LOOKBACK = 7 #days

load, earliest_date, latest_date = ResInterval60.get_batch(sqlClient, batch_size=200000)
weather = LocalWeather.get_weather(sqlClient, earliest_date, latest_date)

X, Y = generate_data(LOOKBACK, load, weather)

print 'total dataset size X:{},Y:{}'.format(X.shape, Y.shape)

parser = argparse.ArgumentParser(description='Run ML models for load forecasting.')
parser.add_argument('--model', default='ff', help='Pick a model to use for estimation.')
parser.add_argument('-t', '--train', action='store_true', help='Explicitly train.')
parser.add_argument('-p', '--plot', action='store_true', help='Explicitly plot.')

FLAGS, unparsed = parser.parse_known_args()

print 'running with arguments: ({})'.format(FLAGS)

errors = []
kf = KFold(shuffle=True, n_splits=2, random_state=0)

for train, test in kf.split(X):
    model = None

    if FLAGS.model == 'ff':
        tf.logging.set_verbosity(tf.logging.INFO)
        model = FeedForward(num_layer=4, num_neuron=300,input_size=X.shape[1])
        tf.logging.set_verbosity(tf.logging.WARN)
    elif FLAGS.model == 'linear':
        model = LinearRegression()
    elif FLAGS.model == 'svr':
        model = SVR()
    else:
        print '{} is an invalid model. Pick from (ff),(linear),(svr).'.format(FLAGS.model)

    if FLAGS.train == True:
        model.train((X[train], Y[train]))

    prediction = model.predict((X[test], Y[test]))

    if FLAGS.model == 'ff':
        model.sess.close()
        tf.reset_default_graph()

    error = get_error(Y[test], prediction)
    print """=================
nrsmd per hour: {}
nrsmd mean: {}""".format(error, np.mean(error))

    errors.append(error)

    if FLAGS.plot == True:
        plt.plot(Y[test][-15:-1].flatten())
        plt.plot(prediction[-15:-1].flatten())
        plt.show()

    # elif FLAGS.model == 'lstm':
    #     recurrent = Recurrent()
    #     x=np.reshape(x, (x.shape[0], x.shape[1], 1))
    #     recurrent.train(training)
    #     print recurrent.test(test)
errors = np.array(errors)

print """=======
SUMMARY
=======
nrmsd per hour: {}
nsrmd mean: {}""".format(np.mean(errors, axis=0), np.mean(errors))
