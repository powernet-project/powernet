import calendar
import pytz
from datetime import datetime, timedelta

from django.shortcuts import render
from django.http import HttpResponse
from django_ajax.decorators import ajax
import numpy as np

from .models import ResInterval60, LocalWeather
from ml.models import FeedForward, LinearRegression, SVR

def index(request):
    service_point_list = ResInterval60.objects.values('sp_id').distinct()
    context = {
        'sp_list' : service_point_list
    }
    return render(request, 'viz/index.html', context)

@ajax
def show(request, sp_id):
    res_intervals = ResInterval60.objects.filter(sp_id=sp_id).order_by('date').all()[:7]

    model_input = list()

    start_date = calendar.timegm(res_intervals[0].date.timetuple())
    end_date = calendar.timegm(res_intervals[len(res_intervals) - 1].date.timetuple())
    forecast_date = res_intervals[len(res_intervals) - 1].date + timedelta(days=1)
    forecast_datetime = pytz.utc.localize(datetime.combine(forecast_date, datetime.min.time()))

    for res_interval in res_intervals:
        date_info = [0] * 8
        date_info[res_interval.date.weekday()] = 1

        # weekend
        if res_interval.date.weekday() >= 5:
            date_info[7] = 1

        model_input.extend([
            res_interval.q1,
            res_interval.q2,
            res_interval.q3,
            res_interval.q4,
            res_interval.q5,
            res_interval.q6,
            res_interval.q7,
            res_interval.q8,
            res_interval.q9,
            res_interval.q10,
            res_interval.q11,
            res_interval.q12,
            res_interval.q13,
            res_interval.q14,
            res_interval.q15,
            res_interval.q16,
            res_interval.q17,
            res_interval.q18,
            res_interval.q19,
            res_interval.q20,
            res_interval.q21,
            res_interval.q22,
            res_interval.q23,
            res_interval.q24
        ] + date_info)

    local_weathers = LocalWeather.objects.order_by('date').all()

    temperature_max = -float("inf")
    temperature_min = float("inf")
    humidity_max = -float("inf")
    humidity_min = float("inf")

    for local_weather in local_weathers:
        if local_weather.date >= forecast_datetime and local_weather.date < (forecast_datetime + timedelta(days=1)) :
            if local_weather.TemperatureF > temperature_max:
                temperature_max = local_weather.TemperatureF

            if local_weather.TemperatureF < temperature_min:
                temperature_min = local_weather.TemperatureF

            if local_weather.Humidity > humidity_max:
                humidity_max = local_weather.Humidity

            if local_weather.Humidity < humidity_min:
                humidity_min = local_weather.Humidity

    model_input.extend([
        temperature_max,
        temperature_min,
        humidity_max,
        humidity_min]
        )

    model_input = np.reshape(np.array(model_input), (1, -1))

    forecast_date_load = ResInterval60.objects.filter(sp_id=sp_id, date=forecast_date).order_by('date').get()
    load = [
        forecast_date_load.q1,
        forecast_date_load.q2,
        forecast_date_load.q3,
        forecast_date_load.q4,
        forecast_date_load.q5,
        forecast_date_load.q6,
        forecast_date_load.q7,
        forecast_date_load.q8,
        forecast_date_load.q9,
        forecast_date_load.q10,
        forecast_date_load.q11,
        forecast_date_load.q12,
        forecast_date_load.q13,
        forecast_date_load.q14,
        forecast_date_load.q15,
        forecast_date_load.q16,
        forecast_date_load.q17,
        forecast_date_load.q18,
        forecast_date_load.q19,
        forecast_date_load.q20,
        forecast_date_load.q21,
        forecast_date_load.q22,
        forecast_date_load.q23,
        forecast_date_load.q24
    ]

    data = (model_input, np.reshape(np.array([0] * 24), (1, 24)))

    linear_regression = LinearRegression().predict(data)
    # ffnn = FeedForward().predict(data)
    dates = [forecast_datetime]

    for i in xrange(23):
        dates.append(dates[-1] + timedelta(hours=1))

    for i, date in enumerate(dates):
        dates[i] = calendar.timegm(date.timetuple()) * 1000

    return {
        'forecast_date': calendar.timegm(forecast_date.timetuple()),
        'weather': {
            'temperature': temperature_max,
            'humidity': temperature_min
        },
        'nrsmd': {
            'lr': np.sqrt(np.mean(np.square(np.subtract(load, linear_regression[0])))) / (np.max(load) - np.min(load))
        },
        'chart': {
            'data': {
                'dates': dates,
                'load': load,
                'lr': linear_regression[0]
            }
        }
    }
