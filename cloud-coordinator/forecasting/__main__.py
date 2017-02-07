#!/usr/bin/env python
"""Entry point for Testing Learning Models"""

from sklearn.preprocessing import MinMaxScaler
from sql.models import ResInterval60
from sql.sqlclient import SqlClient
from nn.feedforward import FeedForward
from nn.rnn import Recurrent

import numpy as np

__author__ = "Edward Ng"
__email__ = "edjng@stanford.edu"

sqlClient = SqlClient()

dataset = list()

for entry in sqlClient.session.query(ResInterval60).order_by(ResInterval60.date):
  dataset.extend([
    entry.q1,
    entry.q2,
    entry.q3,
    entry.q4,
    entry.q5,
    entry.q6,
    entry.q7,
    entry.q8,
    entry.q9,
    entry.q10,
    entry.q11,
    entry.q12,
    entry.q13,
    entry.q14,
    entry.q15,
    entry.q16,
    entry.q17,
    entry.q18,
    entry.q19,
    entry.q20,
    entry.q21,
    entry.q22,
    entry.q23,
    entry.q24
    ])

x=list()
y=list()

scaler=MinMaxScaler(feature_range=(0, 1))
dataset=scaler.fit_transform(dataset)

for i in xrange(len(dataset) / 24 - 7):
  curr = i * 24
  x.append(dataset[curr : curr + 24 * 7])
  y.append(dataset[curr + 24 * 7 : curr + 24 * 8])

x = np.array(x)
y = np.array(y)

feedForward = FeedForward()
feedForward.train((x, y))
print feedForward.test((x, y))

x=np.reshape(x, (x.shape[0], 1, x.shape[1]))
y=np.array(y)

recurrent = Recurrent()
recurrent.train((x, y))
print recurrent.test((x, y))