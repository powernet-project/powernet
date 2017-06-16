#!/usr/bin/env python
"""Decoder-Encoder network Developed using Tensorflow"""

import math
import numpy as np
import os
import random
import time
import tensorflow as tf
import pdb

__author__ = "Edward Ng"
__email__ = "edjng@stanford.edu"

def generate_batch(data, batch_size=100):
    X, Y = data
    indices = np.random.choice(len(X), batch_size, replace=False)
    return X[indices], Y[indices]

class GRU:
    def __init__(self):
        self.sess = tf.InteractiveSession()

        self.batch_size = 1000
        self.output_size = 24
        self.max_time = 24 * 7

        self.num_layer = 3
        self.num_neuron = 50

        self.model_name = "./saved_models/gru.ckpt"
        self.construct_graph()

    def layer(self, X, num_neuron):
        input_shape = X.get_shape()

        #layer takes input X, with num_neuron many neurons. Relu is used for activation.
        W = tf.get_variable("W", shape=[input_shape[1], num_neuron], initializer=tf.contrib.layers.xavier_initializer())
        b = tf.get_variable("b", shape=[num_neuron], initializer=tf.constant_initializer(0))
        Y = tf.matmul(X, W) + b
        return tf.nn.relu(Y)

    def construct_graph(self):
        self.hourly_data = tf.placeholder(tf.float32, [None, self.max_time, 1])
        self.weather = tf.placeholder(tf.float32, [None, 4])
        self.y_ = tf.placeholder(tf.float32, [None, self.output_size])

        with tf.variable_scope("encoder"):
            encoder_fwd_cell = tf.contrib.rnn.GRUCell(24)
            encoder_bwd_cell = tf.contrib.rnn.GRUCell(24)
            _, encoder_final_state = tf.nn.bidirectional_dynamic_rnn(
                encoder_fwd_cell,
                encoder_bwd_cell,
                self.hourly_data,
                sequence_length=[24 * 7] * self.hourly_data.get_shape()[1],
                dtype=tf.float32)

        U = tf.reshape(tf.concat(encoder_final_state, 1), (-1, 24, 2))

        with tf.variable_scope("decoder"):
            decoder_cell = tf.contrib.rnn.GRUCell(1)
            decoder_output, _ = tf.nn.dynamic_rnn(decoder_cell, U, dtype=tf.float32)

        decoder_output = tf.squeeze(decoder_output, squeeze_dims=[2])
        print(decoder_output.get_shape())
        h = tf.concat([decoder_output, self.weather], 1)

        for layer_idx in range(self.num_layer):
        #add intermediate layers
            with tf.variable_scope("layer{}".format(layer_idx)):
                h = self.layer(h, self.num_neuron)

        #add projection layer
        with tf.variable_scope("proj_layer"):
            hidden_shape = h.get_shape()
            W = tf.get_variable("W", shape=[hidden_shape[1], self.output_size],
                initializer=tf.contrib.layers.xavier_initializer())

            b = tf.get_variable("b",
                shape=[self.output_size],
                initializer=tf.constant_initializer(0))

            y = tf.matmul(h, W) + b

            self.prediction = y

            self.loss = tf.reduce_mean(tf.square(self.prediction - self.y_))
            tf.summary.scalar('mean_squared_error', self.loss)

        with tf.variable_scope("train_step"):
            optimizer = tf.train.AdamOptimizer(1e-4)
            grads_and_vars = optimizer.compute_gradients(self.loss)
            gradients = [grads_and_var[0] for grads_and_var in grads_and_vars]

            gradients, _ = tf.clip_by_global_norm(gradients, 10)
            grads_and_vars = [(gradient, grads_and_vars[i][1]) for i, gradient in enumerate(gradients)]

            self.grad_norm = tf.global_norm(gradients)
            self.train_step = optimizer.apply_gradients(grads_and_vars)

        self.saver = tf.train.Saver()

    def train(self, data):
        t0 = time.clock()
        x, y = data

        print '{}: training with data: ({})'.format(type(self).__name__, x.shape)

        merged = tf.summary.merge_all()
        writer = tf.summary.FileWriter('./summary', graph=tf.get_default_graph())

        tf.global_variables_initializer().run()

        for i in range(10000):
            batch_xs_train, batch_ys_train = generate_batch(data, self.batch_size)
            batch_ys_train.reshape(self.batch_size, 24)

            summary, error, _ = self.sess.run([merged, self.loss, self.train_step],
                feed_dict={
                self.hourly_data: np.expand_dims(batch_xs_train[:, 0:24 * 7], 2),
                self.weather: batch_xs_train[:, 24*7:],
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
