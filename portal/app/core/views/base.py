import json
import requests
from django.shortcuts import render


def index(request):
    return render(request, 'partials/main.html')


def weather(request):
    return render(request, 'partials/weather.html')


def electricity(request):
    return render(request, 'partials/electricity.html')


def home_one(request):
    return render(request, 'visualization/Demo3/index.html')


def home_two(request):
    return render(request, 'visualization/Demo3/index.html')


def opf(request):
    return render(request, 'visualization/Demo2/index.html')


def pv(request):
    return render(request, 'partials/pv.html')


def charts(request):
    return render(request, 'partials/chart_plots.html')


def charts_no_control(request):
    import mosek
    import numpy as np 
    a = np.array([60, 2, 3])
    return render(request, 'partials/chart_plots_no_control.html', {"my_numpy_var": a[0]})