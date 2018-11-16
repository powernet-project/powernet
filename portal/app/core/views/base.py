import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from app.models import Home, Device
from app.api.v1.endpoint.device import DeviceSerializer


@login_required
def index(request):
    return render(request, 'partials/main.html')


@login_required
def weather(request):
    if request.user.id == 1:
        return render(request, 'partials/weather.html')
    return render(request, 'partials/404.html')


@login_required
def electricity(request):
    if request.user.id == 1:
        return render(request, 'partials/electricity.html')
    return render(request, 'partials/404.html')


@login_required
def home_one(request):
    if request.user.id == 1:
        return render(request, 'visualization/Demo3/index.html')
    return render(request, 'partials/404.html')


@login_required
def home_two(request):
    if request.user.id == 1:
        return render(request, 'visualization/Demo3/index.html')
    return render(request, 'partials/404.html')


@login_required
def opf(request):
    if request.user.id != 1:
        return render(request, 'partials/404.html')

    # get the homes this user has
    homes = Home.objects.filter(owner=request.user.powernetuser)

    # for now, even the user has multiple homes, we'll just assume they want the first one
    devices = Device.objects.filter(home=homes[0])

    # serialize the device list and return it in the context
    ser_devices = json.dumps(DeviceSerializer(devices, many=True).data)

    return render(request, 'visualization/Demo2/index.html', {"devices": ser_devices, "userId": request.user.id})


@login_required
def pv(request):
    if request.user.id == 1:
        return render(request, 'partials/pv.html')
    return render(request, 'partials/404.html')


@login_required
def charts(request):
    if request.user.id == 1:
        return render(request, 'partials/chart_plots.html')
    return render(request, 'partials/404.html')


@login_required
def charts_no_control(request):
    if request.user.id == 1:
        return render(request, 'partials/chart_plots_no_control.html')
    return render(request, 'partials/404.html')
