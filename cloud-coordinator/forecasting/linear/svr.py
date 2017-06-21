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
            joblib.dump(model, 'saved_models/svr.{}.pkl'.format(i))

    def predict(self, data):
        X, Y = data

        Y = np.split(Y, 24, axis=1)
        predictions=[]

        self.models = [joblib.load('saved_models/svr.{}.pkl'.format(i)) for i in xrange(24)]

        for model in self.models:
            prediction = model.predict(X)

            predictions.append(prediction)

        return np.array(predictions).transpose()
