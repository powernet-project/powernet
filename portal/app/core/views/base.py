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
    # get the homes this user has
    homes = Home.objects.filter(owner=request.user.powernetuser)

    # for now, even the user has multiple homes, we'll just assume they want the first one
    devices = Device.objects.filter(home=homes[0])

    # serialize the device list and return it in the context
    ser_devices = json.dumps(DeviceSerializer(devices, many=True).data)

    return render(request, 'visualization/Demo2/index.html', {"devices": ser_devices, "userId": request.user.id})


@login_required
def pv(request):
    return render(request, 'partials/pv.html')


@login_required
def charts(request):
    return render(request, 'partials/chart_plots.html')


@login_required
def charts_no_control(request):
    return render(request, 'partials/chart_plots_no_control.html')
