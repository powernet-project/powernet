import numpy as np

from sklearn import linear_model
from sklearn.externals import joblib

class LinearRegression:
    def __init__(self):
        self.model = linear_model.LinearRegression()

    def train(self, data):
        X, Y = data
        self.model.fit(X, Y)

        joblib.dump(self.model, 'linear_regression.pkl')

    def test(self, data):
        X, Y = data

        self.model = joblib.load('linear_regression.pkl')

        prediction = self.model.predict(X)
        squared_error = (prediction - Y) ** 2

        return squared_error, prediction

