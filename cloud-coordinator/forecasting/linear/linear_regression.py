import numpy as np

from sklearn import linear_model

class LinearRegression:
    def __init__(self):
        self.model = linear_model.LinearRegression()

    def train(self, data):
        X, Y = data
        self.model.fit(X, Y)

    def test(self, data):
        X, Y = data
        prediction = self.model.predict(X)
        squared_error = (prediction - Y) ** 2

        return squared_error, prediction

