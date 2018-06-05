import json
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return render(request, 'partials/main.html')


@login_required
def weather(request):
    return render(request, 'partials/weather.html')


@login_required
def electricity(request):
    return render(request, 'partials/electricity.html')


@login_required
def home_one(request):
    return render(request, 'visualization/Demo3/index.html')


@login_required
def home_two(request):
    return render(request, 'visualization/Demo3/index.html')


@login_required
def opf(request):
    return render(request, 'visualization/Demo2/index.html')


@login_required
def pv(request):
    return render(request, 'partials/pv.html')


@login_required
def charts(request):
    return render(request, 'partials/chart_plots.html')


@login_required
def charts_no_control(request):
    return render(request, 'partials/chart_plots_no_control.html')


@login_required
def run_gc_algo(request):
    from global_controller.gc_main import *
    arb = run_gc()

    return render(request, 'partials/gc_algo.html', {'arb_total': arb})
