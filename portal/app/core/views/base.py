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
