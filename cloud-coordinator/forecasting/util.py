import datetime

from sklearn.model_selection import KFold
import numpy as np

# Generate test and training set
def generate_sets(x, y, train_index,):
    training = int(len(x) * split)

    x_training = x[:training]
    y_training = y[:training]

    x_test = x[training:]
    y_test = y[training:]

    return (x_training, y_training), (x_test, y_test)

# Generate input and output data
def generate_data(lookback_days, load, weather):
    x = list()
    y = list()

    for sp_id, sp_load in load.iteritems():
        for i, contiguous_block in enumerate(sp_load):
            #filter out contiguous_blocks without enough data (lookback_days + 1)
            if len(contiguous_block) > lookback_days + 1:
                for j in xrange(len(contiguous_block) - lookback_days):
                    x.append(sum(contiguous_block[j: j + lookback_days], []))
                    y.append(contiguous_block[j + lookback_days][0:24])

    return np.array(x), np.array(y)
