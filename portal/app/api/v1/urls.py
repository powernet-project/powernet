from django.conf.urls import include, url
from rest_framework import routers

from app.api.v1.endpoint.utility_energy_price import UtilityEnergyPriceViewSet
from app.api.v1.endpoint.home_data import home_data_view

# register the default and nested routes
router = routers.SimpleRouter()
router.register(r'energy_price', UtilityEnergyPriceViewSet, base_name='utility_energy_price')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^home_data/', home_data_view),
]
