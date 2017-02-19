import numpy as np

from sklearn import svm
from sklearn.externals import joblib

# SVR implementation. Does not scale.
class SVR:
    def __init__(self):
        self.models = [svm.SVR()] * 24

    def train(self, data):
        X, Y = data

        Y = np.split(Y, 24, axis=1)
        for i, model in enumerate(self.models):
            print 'svr: fitting ({})'.format(i)
            model.fit(X, Y[i])
            joblib.dump(model, 'svr.{}.pkl'.format(i))

    def test(self, data):
        X, Y = data

        Y = np.split(Y, 24, axis=1)
        predictions=[]

        self.models = [joblib.load('svr.{}.pkl'.format(i)) for i in xrange(24)]

        for model in self.models:
            prediction = model.predict(X)

            predictions.append(prediction)

        predictions = np.array(predictions).transpose()

        return (predictions - Y) ** 2, predictions
