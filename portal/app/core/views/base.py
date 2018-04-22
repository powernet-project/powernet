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
    return render(request, 'partials/chart_plots_no_control.html')


def run_gc_algo(request):
    from global_controller.gc_main import *
    arb = run_gc()

    return render(request, 'partials/gc_algo.html', {'arb_total': arb})
