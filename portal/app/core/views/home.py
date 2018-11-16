import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from app.models import Home, Device
from app.api.v1.endpoint.device import DeviceSerializer


@login_required
def index(request):
    return render(request, 'partials/main.html')