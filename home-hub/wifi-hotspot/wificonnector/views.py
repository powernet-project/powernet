# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from forms import *
from django.http import HttpResponse, Http404


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


        # TODO: add action on WIFI connection
        print("------> HERE are WIFI INFO <------")
        print(request.POST['ssid'])
        print(request.POST['pass'])


    # going back to the wifi page
    return render(request, 'wificonnector/credential.html', context)