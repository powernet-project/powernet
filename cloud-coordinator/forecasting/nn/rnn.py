#!/usr/bin/env python
"""LSTM Neural Network using Kera"""

from keras.models import Sequential
from keras.layers import Dense
from keras.layers.recurrent import LSTM

import numpy as np

__author__ = "Edward Ng"
__email__ = "edjng@stanford.edu"

class Recurrent:
  def __init__(self, input_size=(7*24), output_size=24):
    self.input_size=input_size
    self.output_size=output_size

    self.construct_graph()

  def construct_graph(self):
    self.model = Sequential()
    self.model.add(LSTM(self.output_size, activation='relu', input_dim=self.input_size))
    self.model.compile(loss='mean_squared_error', optimizer='adam')

  def train(self, data):
    x, y = data
    history = self.model.fit(x, y, validation_split=0.3, nb_epoch=100, batch_size=100, verbose=0)
    self.model.save_weights("./model.ckpt")
    return history

  def test(self, data):
    x, y = data
    self.model.load_weights("./model.ckpt")

    y_ = self.model.predict(x)

    return np.mean(np.ma.masked_invalid(np.abs(y - y_) / y))
