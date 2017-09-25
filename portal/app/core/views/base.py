import json
import requests
from django.shortcuts import render


def index(request):
    from app.models import UtilityEnergyPrice
    from app.api.v1.endpoint.utility_energy_price import UtilityEnergyPriceSerializer
    prices = UtilityEnergyPrice.objects.all()[:1]
    return render(request, 'partials/main.html', {
        'price': UtilityEnergyPriceSerializer(prices)
    })


def weather(request):
    return render(request, 'partials/weather.html')


def electricity(request):
    try:
        r = requests.get('https://hourlypricing.comed.com/api?type=currenthouraverage&format=json')
        price = r.json()[0]['price']
    except requests.exceptions.ChunkedEncodingError as e:
        price = 'Could not retrieve price from the ComedAPI'
        print e

    return render(request, 'partials/electricity.html', {
        'utility_price': price
    })
