from django.conf.urls import include, url
from rest_framework import routers

from app.api.v1.endpoint.utility_energy_price import UtilityEnergyPriceViewSet
from app.api.v1.endpoint.device import DeviceViewSet, DeviceStateViewSet
from app.api.v1.endpoint.home_data import home_data_view
from app.api.v1.endpoint.appliance_data import ApplianceJsonDataViewSet

# register the default and nested routes
router = routers.SimpleRouter()
router.register(r'energy_price', UtilityEnergyPriceViewSet, base_name='utility_energy_price')
router.register(r'device', DeviceViewSet, base_name='device')
router.register(r'device_state', DeviceStateViewSet, base_name='device_state')
router.register(r'rms', ApplianceJsonDataViewSet, base_name='appliance_data')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^home_data/', home_data_view),
]
