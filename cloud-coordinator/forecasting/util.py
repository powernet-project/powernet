from datetime import timedelta

from sklearn.model_selection import KFold
import numpy as np
import pdb

# Generate test and training set
def generate_sets(x, y, train_index,):
    training = int(len(x) * split)

    x_training = x[:training]
    y_training = y[:training]

    x_test = x[training:]
    y_test = y[training:]

    return (x_training, y_training), (x_test, y_test)

# Generate input and output data
def generate_data(lookback_days, load_dict, weather_dict, intervals=24):
    x = list()
    y = list()

    for sp_id, sp_load in load_dict.iteritems():
        for i, contiguous_block in enumerate(sp_load):
            #filter out contiguous_blocks without enough data (lookback_days + 1 + 2 (sentinel dates))
            if len(contiguous_block) > lookback_days + 1 + 2:
                start_date = contiguous_block[0]
                # we don't really need this, but for symmetry
                end_date = contiguous_block[-1]

                for j in xrange(1, len(contiguous_block) - lookback_days - 2):
                    weather_forecast = weather_dict[(start_date + timedelta(days=lookback_days + j - 1)).strftime('%Y-%m-%d')]

                    temperature = weather_forecast[0::2]
                    humidity = weather_forecast[1::2]

                    weather_forecast_stats = [
                        np.max(temperature),
                        np.min(temperature),
                        np.max(humidity),
                        np.min(humidity)]

                    datum = sum(contiguous_block[j: j + lookback_days], []) + weather_forecast_stats

                    x.append(datum)
                    y.append(contiguous_block[j + lookback_days][0:intervals])

    return np.array(x), np.array(y)

def get_error(Y, Y_predict):
    rmsd = np.sqrt(np.mean(np.square(np.subtract(Y, Y_predict)), axis=0))
    return rmsd / (np.max(Y, axis=0) - np.min(Y, axis=0))
