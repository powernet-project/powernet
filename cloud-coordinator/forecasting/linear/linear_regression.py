import numpy as np

from sklearn import linear_model
from sklearn.externals import joblib

class LinearRegression:
    def __init__(self):
        self.model = linear_model.LinearRegression()
        self.model_name = "./lr.pkl"

    def train(self, data):
        X, Y = data
        self.model.fit(X, Y)

        joblib.dump(self.model, self.model_name)

    def predict(self, data):
        X, Y = data

        self.model = joblib.load(self.model_name)
        return self.model.predict(X)

