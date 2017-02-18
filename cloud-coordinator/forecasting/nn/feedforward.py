#!/usr/bin/env python
"""FeedForward network Developed using Tensorflow"""

import math
import numpy as np
import os
import random
import time
import tensorflow as tf

__author__ = "Edward Ng"
__email__ = "edjng@stanford.edu"

def generate_batch(data, batch_size=100):
  x, y = data
  indices = np.random.choice(len(x), batch_size, replace=False)
  return x[indices], y[indices]

class FeedForward:
  def __init__(self, num_layer=3, num_neuron=300, input_size=409):
    self.num_layer = num_layer
    self.num_neuron = num_neuron
    self.sess = tf.InteractiveSession()
    self.input_size = input_size
    self.output_size = 24

    self.construct_graph()

  def layer(self, x, num_neuron):
    input_shape = x.get_shape()
    #layer takes input x, with num_neuron many neurons. Relu is used for activation.
    W = tf.get_variable("W", shape=[input_shape[1], num_neuron], initializer=tf.contrib.layers.xavier_initializer())
    b = tf.get_variable("b", shape=[num_neuron], initializer=tf.constant_initializer(0))
    y = tf.matmul(x, W) + b
    return tf.nn.relu(y)

  def construct_graph(self):
    self.x = tf.placeholder(tf.float32, [None, self.input_size])
    self.y_ = tf.placeholder(tf.float32, [None, self.output_size])

    h = self.x
    for layer_idx in range(self.num_layer):
      #add intermediate layers
      with tf.variable_scope("layer{}".format(layer_idx)):
        h = self.layer(h, self.num_neuron)

    #add projection layer
    with tf.variable_scope("proj_layer"):
      hidden_shape = h.get_shape()
      W = tf.get_variable("W", shape=[hidden_shape[1], self.output_size],
        initializer=tf.contrib.layers.xavier_initializer())

      b = tf.get_variable("b", shape=[self.output_size], initializer=tf.constant_initializer(0))
      y = tf.matmul(h, W) + b

    self.prediction = y

    self.squared_error = tf.square(self.prediction - self.y_)
    tf.summary.scalar('mean_squared_error', tf.reduce_mean(self.squared_error))

    self.train_step = tf.train.AdamOptimizer(1e-4) \
                        .minimize(tf.reduce_mean(self.squared_error))
    self.saver = tf.train.Saver()

  def train(self, data):
    t0 = time.clock()
    x, y = data

    print '{}: training with data: ({})'.format(type(self).__name__, x.shape)

    merged = tf.summary.merge_all()
    writer = tf.summary.FileWriter('./train')

    tf.global_variables_initializer().run()
    batch_size = 100
    for i in range(4000):
      batch_xs_train, batch_ys_train = generate_batch(data, batch_size)
      batch_ys_train.reshape(batch_size, 24)

      summary, _ = self.sess.run([merged, self.train_step],
        feed_dict={
          self.x: batch_xs_train,
          self.y_: batch_ys_train
        })
      writer.add_summary(summary, i)

    save_path = self.saver.save(self.sess, "./model.ff.ckpt")

    print '{}: {} seconds took for training'.format(type(self).__name__, time.clock() - t0)

  def test(self, data):
    x, y = data

    print '{}: testing with data: ({})'.format(type(self).__name__, x.shape)
    self.saver.restore(self.sess, "./model.ff.ckpt")
    return self.sess.run([self.squared_error, self.prediction], feed_dict = {self.x: x, self.y_: y})
