#!/usr/bin/env python
"""Entry point for Testing Learning Models"""

from sklearn.preprocessing import MinMaxScaler
from sql.models import ResInterval60, LocalWeather
from sql.sqlclient import SqlClient
from nn.feedforward import FeedForward
from nn.rnn import Recurrent

from sqlalchemy import text

import argparse
import datetime
import math

import matplotlib.pyplot as plt
import numpy as np

__author__ = "Edward Ng"
__email__ = "edjng@stanford.edu"

sqlClient = SqlClient()

FLAGS = None

LOOKBACK = 7

def generate_set(x, y, split=0.7):
    training = int(len(x) * split)

    x_training = x[:training]
    y_training = y[:training]

    x_test = x[training:]
    y_test = y[training:]

    return (x_training, y_training), (x_test, y_test)

def format_weather(data):
    data=data[:(len(data) / 24) * 24]
    data_scaler=MinMaxScaler(feature_range=(0, 1))
    data=data_scaler.fit_transform(data)
    return data.reshape(-1, 24)

# metadata
load = list()
temperature = list()
humidity = list()
date = list()

earliest_date = None

for idx, resInterval60 in enumerate(sqlClient.session.query(ResInterval60)
    .filter(ResInterval60.sp_id==6238323)
    .order_by(ResInterval60.date)):
    if idx == 0:
        earliest_date = resInterval60.date

    load.append([
        resInterval60.q1,
        resInterval60.q2,
        resInterval60.q3,
        resInterval60.q4,
        resInterval60.q5,
        resInterval60.q6,
        resInterval60.q7,
        resInterval60.q8,
        resInterval60.q9,
        resInterval60.q10,
        resInterval60.q11,
        resInterval60.q12,
        resInterval60.q13,
        resInterval60.q14,
        resInterval60.q15,
        resInterval60.q16,
        resInterval60.q17,
        resInterval60.q18,
        resInterval60.q19,
        resInterval60.q20,
        resInterval60.q21,
        resInterval60.q22,
        resInterval60.q23,
        resInterval60.q24
        ])

    day_of_week = [0] * 7
    day_of_week[resInterval60.date.weekday()] = 1

    date.append(day_of_week)

for idx, localWeather in enumerate(sqlClient.session.query(LocalWeather) \
    .from_statement(text("SELECT * FROM local_weather WHERE date>=:date ORDER BY date")) \
    .params(date=earliest_date.isoformat()).all()):

    temperature.append(localWeather.TemperatureF)
    humidity.append(localWeather.Humidity)

x=list()
y=list()

load_scaler=MinMaxScaler(feature_range=(0, 1))
load=load_scaler.fit_transform(load)

temperature = format_weather(temperature)
humidity = format_weather(humidity)

for i in xrange(len(load) - LOOKBACK):
  x.append(np.concatenate([load[i:i + LOOKBACK].ravel(), temperature[i + LOOKBACK].ravel(), humidity[i:i + LOOKBACK].ravel(), date[i + LOOKBACK]]))
  y.append(load[i + LOOKBACK])

x = np.array(x)
y = np.array(y)

print 'dataset is ({})'.format(x.shape)

training, test = generate_set(x, y)

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
    print '{} is an invalid model. Pick from (ff), (lstm), (linear)'.format(FLAGS.model)

if nrmsd is not None:
    print 'nrmsd: ({})'.format(nrmsd)

if prediction is not None:
    plt.plot(test[1][-8:-1].flatten())
    plt.plot(prediction[-8:-1].flatten())
    plt.show()
