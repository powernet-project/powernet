import json
import requests
from django.shortcuts import render


def index(request):
    return render(request, 'partials/main.html')


def weather(request):
    return render(request, 'partials/weather.html')


def electricity(request):
    r = requests.get('https://hourlypricing.comed.com/api?type=currenthouraverage&format=json')

    return render(request, 'partials/electricity.html', {
        'utility_price': json.dumps(r.json()[0]['price'])
    })
