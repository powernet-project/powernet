import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from app.models import Home, Device
from app.api.v1.endpoint.device import DeviceSerializer


@login_required
def settings(request):
    return render(request, 'home/settings.html')


@login_required
def devices(request):
    return render(request, 'home/devices.html')


@login_required
def consumption(request):
    return render(request, 'home/consumption.html')