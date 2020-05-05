import json
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from app.api.v1.endpoint.home import HomeSerializer
from app.models import Home, Device, PowernetUserType
from app.api.v1.endpoint.device import DeviceSerializer
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    if Token.objects.filter(user=request.user).count() > 0:
        token = Token.objects.get(user=request.user)
    else:
        token = Token.objects.create(user=request.user)

    # get the list of homes for this user
    home_lst = Home.objects.filter(owner=request.user.powernetuser)
    serialized_homes = json.dumps(HomeSerializer(home_lst, many=True).data)

    # get all the devices in all the homes for this user
    device_lst = Device.objects.filter(home__owner=request.user.powernetuser)
    serialized_devices = json.dumps(DeviceSerializer(device_lst, many=True).data)

    if request.user.powernetuser.type == PowernetUserType.LAB:
        template = 'partials/main_lab.html'
    elif request.user.powernetuser.type == PowernetUserType.FARM:
        template = 'partials/main_farm.html'
    else:
        template = 'partials/main_home.html'

    return render(request, template, {
        'token': token,
        'homes': serialized_homes,
        'devices': serialized_devices
    })


@login_required
def settings(request):
    return render(request, 'partials/settings.html')


@login_required
def devices(request):
    return render(request, 'partials/devices.html')


@login_required
def consumption(request):
    return render(request, 'partials/consumption.html')


@login_required
def loads(request):
    return render(request, 'partials/loads.html', {'resource': 'loads'})


@login_required
def battery(request):
    return render(request, 'partials/battery.html', {'resource': 'battery'})


@login_required
def solar(request):
    return render(request, 'partials/solar.html', {'resource': 'solar'})


@login_required
def hvac(request):
    return render(request, 'partials/hvac.html', {'resource': 'hvac'})


@login_required
def ev(request):
    return render(request, 'partials/ev.html', {'resource': 'ev'})

#########################################################
# Actual error page handlers
#########################################################


def handler404(request, *args, **kwargs):
    return render(request, 'partials/404.html', {'hide_header': True})

#########################################################
# These views are to be used by the demo/lab account only.
# They are not relevant to regular Powernet users.
#########################################################


@login_required
def weather(request):
    if request.user.powernetuser.type == PowernetUserType.LAB:
        return render(request, 'partials/weather.html')
    return render(request, 'partials/404.html')


@login_required
def electricity(request):
    if request.user.powernetuser.type == PowernetUserType.LAB:
        return render(request, 'partials/electricity.html')
    return render(request, 'partials/404.html')


@login_required
def home_one(request):
    if request.user.powernetuser.type == PowernetUserType.LAB:
        return render(request, 'visualization/Demo3/index.html')
    return render(request, 'partials/404.html')


@login_required
def home_two(request):
    if request.user.powernetuser.type == PowernetUserType.LAB:
        return render(request, 'visualization/Demo3/index.html')
    return render(request, 'partials/404.html')


@login_required
def opf(request):
    if request.user.powernetuser.type != PowernetUserType.LAB:
        return render(request, 'partials/404.html')

    # get the homes this user has
    homes = Home.objects.filter(owner=request.user.powernetuser)

    # for now, even the user has multiple homes, we'll just assume they want the first one
    devices = Device.objects.filter(home=homes[0])

    # serialize the device list and return it in the context
    ser_devices = json.dumps(DeviceSerializer(devices, many=True).data)

    return render(request, 'visualization/Demo2/index.html', {'devices': ser_devices, 'userId': request.user.id})


@login_required
def pv(request):
    if request.user.powernetuser.type == PowernetUserType.LAB:
        return render(request, 'partials/pv.html')
    return render(request, 'partials/404.html')


@login_required
def charts(request):
    if request.user.powernetuser.type == PowernetUserType.LAB:
        return render(request, 'partials/chart_plots.html')
    return render(request, 'partials/404.html')


@login_required
def charts_no_control(request):
    if request.user.powernetuser.type == PowernetUserType.LAB:
        return render(request, 'partials/chart_plots_no_control.html')
    return render(request, 'partials/404.html')


@login_required
def local_fan_info(request):
    if request.user.powernetuser.type == PowernetUserType.FARM:
        return render(request, 'partials/local_fan.html')
    else:
        return render(request, 'partials/404.html')
