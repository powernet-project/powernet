# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from forms import *
from django.http import HttpResponse, Http404

from wifi_control import add_dhcpcd_conf, delete_dhcpcd_conf, stop_hostapd, disable_hostapd, add_wifi_conf, \
    restart_dhcpcd


# Create your views here.

def wifi_connect(request):
    context = dict()

    return render(request, 'wificonnector/credential.html', context)


def process_ssid_pwd(request):
    context = dict()

    if not request.POST:
        raise Http404
    else:
        msg = 'We are trying to connect to your network, ' \
              'please wait for a while'
        context['messages'] = [msg]

        # to normal mode and connect to wifi
        add_wifi_conf(request.POST['ssid'], request.POST['pass'])
        stop_hostapd()
        disable_hostapd()
        delete_dhcpcd_conf()
        restart_dhcpcd()

    # going back to the wifi page
    return render(request, 'wificonnector/credential.html', context)
