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

def generate_set(x, y, split=0.9):
  training = -1 #int(len(x) * split)

  x_training = x[:training]
  y_training = y[:training]

  x_test = x[training:]
  y_test = y[training:]

  return (x_training, y_training), (x_test, y_test)

# metadata
load = list()
weather = list()
date = list()

earliest_date = None

for idx, resInterval60 in enumerate(sqlClient.session.query(ResInterval60)
    .filter(ResInterval60.sp_id==7171561005)
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

    date.append([
        resInterval60.date.isoweekday()
        ])

for idx, localWeather in enumerate(sqlClient.session.query(LocalWeather) \
    .from_statement(text("SELECT * FROM local_weather WHERE date>=:date ORDER BY date")) \
    .params(date=earliest_date.isoformat()).all()):

    if idx != 0 and idx % 24 != 0:
        weather_curr.append(localWeather.TemperatureF)
    else:
        if idx > 0:
            weather.append(weather_curr)

        weather_curr = [localWeather.TemperatureF]

x=list()
y=list()

load_scaler=MinMaxScaler(feature_range=(0, 1))
load=load_scaler.fit_transform(load)

weather_scaler=MinMaxScaler(feature_range=(0, 1))
weather=weather_scaler.fit_transform(weather)

for i in xrange(len(load) - 7):
  x.append(np.concatenate([load[i:i + 8].ravel(), weather[i:i+9].ravel(), date[i + 7]]))
  y.append(load[i + 7])

x = np.array(x)
y = np.array(y)

print 'dataset is ({})'.format(x.shape)

training, test = generate_set(x, y)

parser = argparse.ArgumentParser(description='Run ML models for load forecasting.')
parser.add_argument('--model', default='ff', help='Pick a model to use for estimation.')
parser.add_argument('-t', '--train', action='store_true')

FLAGS, unparsed = parser.parse_known_args()

print 'running with arguments: ({})'.format(FLAGS)

rmse = None
prediction = None

if FLAGS.model == 'ff':
    feedForward = FeedForward(4, 700)
    if FLAGS.train is not None:
        feedForward.train(training)
    squared_error, prediction = feedForward.test(test)
    rmse = math.sqrt(np.mean(squared_error)) / np.mean(test[1])
elif FLAGS.model == 'lstm':
    recurrent = Recurrent()
    x=np.reshape(x, (x.shape[0], x.shape[1], 1))
    recurrent.train(training)
    print recurrent.test(test)
else:
    print '{} is an invalid model. Pick from (ff), (lstm), (linear)'.format(FLAGS.model)

if rmse is not None:
    print 'rmse: ({})'.format(rmse)

if prediction is not None:
    raise NotImplementedError # plot the damn prediction
