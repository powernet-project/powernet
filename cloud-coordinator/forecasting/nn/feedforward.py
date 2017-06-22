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

class FeedForward:
    def __init__(self, num_layer=3, num_neuron=300, input_size=24):
        self.num_layer = num_layer
        self.num_neuron = num_neuron
        self.sess = tf.InteractiveSession()
        self.input_size = input_size
        self.output_size = 24

        self.model_name = "./saved_models/ff.ckpt"
        self.construct_graph()

    def layer(self, X, num_neuron):
        input_shape = X.get_shape()
        return tf.layers.dense(X, num_neuron,
            activation=tf.nn.relu,
            kernel_initializer=tf.contrib.layers.xavier_initializer())

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
            self.prediction = tf.layers.dense(h, self.output_size,
                kernel_initializer=tf.contrib.layers.xavier_initializer())

        with tf.variable_scope("optimization"):
            self.squared_error = tf.reduce_mean(tf.square(self.prediction - self.y_))
            tf.summary.scalar('mean_squared_error', self.squared_error)

            global_step = tf.Variable(0, trainable=False)
            starter_learning_rate = 1e-3
            learning_rate = tf.train.exponential_decay(
                starter_learning_rate,
                global_step,
                100000,
                0.98,
                staircase=True)

            self.train_step = tf.train.AdamOptimizer(learning_rate) \
                .minimize(self.squared_error, global_step=global_step)
            self.saver = tf.train.Saver()

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
                writer.add_summary(summary, j)

                if j % 50 == 0:
                    print 'iteration ({}): ({}) squared error'.format(j, error)

        save_path = self.saver.save(self.sess, self.model_name)
        print '{}: {} seconds took for training'.format(type(self).__name__, time.clock() - t0)

    def predict(self, data):
        x, y = data

        print '{}: testing with data: ({})'.format(type(self).__name__, x.shape)
        self.saver.restore(self.sess, self.model_name)
        return self.sess.run(self.prediction, feed_dict = {self.x: x, self.y_: y})
