#!/usr/bin/env python
"""Decoder-Encoder network Developed using Tensorflow"""

import math
import numpy as np
import os
import random
import time
import tensorflow as tf
import pdb

def generate_batch(data, batch_size=100):
  X, Y = data
  indices = np.random.choice(len(X), batch_size, replace=False)
  return X[indices], Y[indices]

class Base:
  def layer(self, X, num_neuron):
    input_shape = X.get_shape()
    return tf.layers.dense(X,
      num_neuron,
      activation=tf.nn.relu,
      kernel_initializer=tf.contrib.layers.xavier_initializer())

  def train(self, data, batch_size=100, num_epochs=4):
    t0 = time.clock()
    X, y = data

    print '{}: training with data: ({})'.format(type(self).__name__, X.shape)

    merged = tf.summary.merge_all()
    writer = tf.summary.FileWriter('./summary', graph=tf.get_default_graph())

    tf.global_variables_initializer().run()

    for i in range(num_epochs):
        print 'starting epoch ({})'.format(i)
        idx = np.random.choice(np.arange(len(X)), len(X), replace=False)

        X = X[idx]
        y = y[idx]

        for j in range(len(X) / batch_size):
            batch_xs_train, batch_ys_train = X[j * batch_size:(j+1) * batch_size], y[j * batch_size:(j+1) * batch_size]
            batch_ys_train.reshape(batch_size, 24)

            summary, error, _ = self.sess.run([merged, self.squared_error, self.train_step],
                feed_dict={
                self.x: batch_xs_train,
                self.y_: batch_ys_train
                })
            writer.add_summary(summary, i)

            if j % 50 == 0:
                print 'iteration ({}): ({}) squared error'.format(j, error)

    save_path = self.saver.save(self.sess, self.model_name)
    print '{}: {} seconds took for training'.format(type(self).__name__, time.clock() - t0)

    def predict(self, data):
      x, y = data

      print '{}: testing with data: ({})'.format(type(self).__name__, x.shape)
      self.saver.restore(self.sess, self.model_name)
      return self.sess.run(self.prediction, feed_dict = {self.x: x, self.y_: y})