from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='/login/')
def index(request):
    return render(request, 'partials/main.html')


@login_required(login_url='/login/')
def weather(request):
    return render(request, 'partials/weather.html')


@login_required(login_url='/login/')
def electricity(request):
    return render(request, 'partials/electricity.html')


@login_required(login_url='/login/')
def home_one(request):
    return render(request, 'visualization/Demo3/index.html')


@login_required(login_url='/login/')
def home_two(request):
    return render(request, 'visualization/Demo3/index.html')


@login_required(login_url='/login/')
def opf(request):
    return render(request, 'visualization/Demo2/index.html')


@login_required(login_url='/login/')
def pv(request):
    return render(request, 'partials/pv.html')


@login_required(login_url='/login/')
def charts(request):
    return render(request, 'partials/chart_plots.html')


@login_required(login_url='/login/')
def charts_no_control(request):
    return render(request, 'partials/chart_plots_no_control.html')