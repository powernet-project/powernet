#!/usr/bin/env python
"""Entry point for Testing Learning Models"""

import argparse
import datetime
import math

from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np

from nn.feedforward import FeedForward
from nn.rnn import Recurrent
from sql.models import ResInterval60, LocalWeather
from sql.sqlclient import SqlClient

from util import generate_sets, generate_data

__author__ = "Edward Ng"
__email__ = "edjng@stanford.edu"

sqlClient = SqlClient()

FLAGS = None

LOOKBACK = 7

# metadata
load, earliest_date, latest_date = ResInterval60.get_batch(sqlClient)
weather = LocalWeather.get_weather(sqlClient, earliest_date, latest_date)

x, y = generate_data(LOOKBACK, load, weather)

print 'total dataset size x:{},y:{}'.format(x.shape, y.shape)
training, test = generate_sets(x, y)

parser = argparse.ArgumentParser(description='Run ML models for load forecasting.')
parser.add_argument('--model', default='ff', help='Pick a model to use for estimation.')
parser.add_argument('-t', '--train', action='store_true')

FLAGS, unparsed = parser.parse_known_args()

print 'running with arguments: ({})'.format(FLAGS)

nrmsd = None
prediction = None

if FLAGS.model == 'ff':
    feedForward = FeedForward(num_layer=3, num_neuron=500,input_size=x.shape[1])
    if FLAGS.train == True:
        feedForward.train(training)
    squared_error, prediction = feedForward.test(test)
    nrmsd = math.sqrt(np.mean(squared_error)) / (np.max(test[1]) - np.min(test[1]))
elif FLAGS.model == 'lstm':
    recurrent = Recurrent()
    x=np.reshape(x, (x.shape[0], x.shape[1], 1))
    recurrent.train(training)
    print recurrent.test(test)
else:
    print '{} is an invalid model. Pick from (ff), (lstm).'.format(FLAGS.model)

if nrmsd is not None:
    print 'nrmsd: ({})'.format(nrmsd)

if prediction is not None:
    plt.plot(test[1][-15:-1].flatten())
    plt.plot(prediction[-15:-1].flatten())
    plt.show()
