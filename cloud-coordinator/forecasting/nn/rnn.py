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
    X, Y = data
    indices = np.random.choice(len(X), batch_size, replace=False)
    return X[indices], Y[indices]

class GRU:
    def __init__(self, depth=24):
        self.sess = tf.InteractiveSession()
        self.depth = depth

        self.batch_size = 100
        self.output_size = 24
        self.max_time = 24
        self.unit_size = 2

        self.model_name = "./saved_models/gru.ckpt"
        self.construct_graph()

    # def layer(self, X, num_neuron):
    #     input_shape = X.get_shape()

    #     #layer takes input X, with num_neuron many neurons. Relu is used for activation.
    #     W = tf.get_variable("W", shape=[input_shape[1], num_neuron], initializer=tf.contrib.layers.xavier_initializer())
    #     b = tf.get_variable("b", shape=[num_neuron], initializer=tf.constant_initializer(0))
    #     Y = tf.matmul(X, W) + b
    #     return tf.nn.relu(Y)

    def construct_graph(self):
        self.x = tf.placeholder(tf.float32, [None, self.max_time, self.depth])
        self.y_ = tf.placeholder(tf.float32, [None, self.output_size])

        cell = tf.contrib.rnn.GRUCell(2, self.input_size)
        state = tf.Variable(cell.zero_states(self.unit_size, tf.float32), trainable=False)

        rnn_outputs, rnn_states = tf.nn.dynamic_rnn(cell, self.x, initial_state=initial_state)

        #add projection layer
        with tf.variable_scope("proj_layer"):
            hidden_shape = rnn_outputs.get_shape()
            W = tf.get_variable("W", shape=[hidden_shape[1], self.output_size],
                initializer=tf.contrib.layers.xavier_initializer())

            b = tf.get_variable("b", shape=[self.output_size], initializer=tf.constant_initializer(0))
            y = tf.matmul(h, W) + b

            self.prediction = y

            self.squared_error = tf.reduce_mean(tf.square(self.prediction - self.y_))
            tf.summary.scalar('mean_squared_error', self.squared_error)

            self.train_step = tf.train.RMSPropOptimizer(1e-4) \
                .minimize(self.squared_error)
            self.saver = tf.train.Saver()

    def train(self, data):
        t0 = time.clock()
        x, y = data

        print '{}: training with data: ({})'.format(type(self).__name__, x.shape)

        merged = tf.summary.merge_all()
        writer = tf.summary.FileWriter('./summary', graph=tf.get_default_graph())

        tf.global_variables_initializer().run()

        for i in range(2000):
            batch_xs_train, batch_ys_train = generate_batch(data, self.batch_size)
            batch_ys_train.reshape(self.batch_size, 24)

            summary, error, _ = self.sess.run([merged, self.squared_error, self.train_step],
                feed_dict={
                self.x: batch_xs_train,
                self.y_: batch_ys_train
                })
            writer.add_summary(summary, i)

            if i % 50 == 0:
                print 'iteration ({}): ({}) squared error'.format(i, error)

        save_path = self.saver.save(self.sess, self.model_name)
        print '{}: {} seconds took for training'.format(type(self).__name__, time.clock() - t0)

    def predict(self, data):
        x, y = data

        print '{}: testing with data: ({})'.format(type(self).__name__, x.shape)
        self.saver.restore(self.sess, self.model_name)
        return self.sess.run(self.prediction, feed_dict = {self.x: x, self.y_: y})
