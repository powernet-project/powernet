import numpy as np
from sklearn import linear_model
from skimage.util.shape import view_as_windows

class AdaptiveLinear:

    def __init__(self,y,lag):
        np.set_printoptions(precision=5)
        self.model = linear_model.LinearRegression()#n_jobs=-1)
        if len(y.shape) <= 1:
            y = y.reshape([-1, 1])
        self.lag=lag
        self.y = y
        self.y_train = None
        self.x_train = None
        self.firstFit=True

    def getRMSE(self, y, y_predict):
        return np.sqrt((np.power(y_predict - y, 2)).sum() / y_predict.size)

    def generate_x(self, X_in, dates, stepAhead):
        xLoad = X_in[:, 168:]
        return xLoad[:,-self.lag:]

    def fit(self, X, y, val_ratio=0.0):
        self.model.fit(X, y.ravel())
        if self.firstFit:
            self.x_train=X
            if len(y.shape) <= 1:
                y = y.reshape([-1, 1])
            self.y_train=y
            nTrain = y.shape[0]
            self.firstFit=False
        return 0 #ignore the train prediction

    def predict(self, X,y):
        if len(X.shape) <= 1:
            X = X.reshape([1, -1])
        if len(y.shape) <= 1:
            y = y.reshape([-1, 1])
        h_x = np.empty((X.shape[0], self.y.shape[1]))
        step = 24
        count = X.shape[0] / step
        try:
            for i in xrange(count):
                _x = X[i * step:(i + 1) * step, :]
                h_x[i * step:(i + 1) * step, :] = self.model.predict(_x).reshape([-1, 1])
                _y = y[i * step:(i + 1) * step, :]
                self.x_train = np.concatenate([self.x_train[step:, :], _x])
                self.y_train = np.concatenate([self.y_train[step:, :], _y])
                self.model.fit(self.x_train, self.y_train.ravel())
        except:
            self.x_train=self.x_train[-step:,:]
            self.y_train=self.y_train[-step:,:]
            self.model.fit(self.x_train, self.y_train.ravel())
        return h_x
