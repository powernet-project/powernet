from django.conf.urls import include, url
from rest_framework import routers

from app.api.v1.endpoint.utility_energy_price import UtilityEnergyPriceViewSet
from app.api.v1.endpoint.device import DeviceViewSet, DeviceStateViewSet
from app.api.v1.endpoint.hue_states import HueStatesViewSet
from app.api.v1.endpoint.powernet_user import PowernetUserViewSet
from app.api.v1.endpoint.home import HomeViewSet, HomeDataViewSet
from app.api.v1.endpoint.appliance_data import ApplianceJsonDataViewSet

# register the default and nested routes
router = routers.SimpleRouter()
router.register(r'energy_price', UtilityEnergyPriceViewSet, base_name='utility_energy_price')
router.register(r'device', DeviceViewSet, base_name='device')
router.register(r'device_state', DeviceStateViewSet, base_name='device_state')
router.register(r'rms', ApplianceJsonDataViewSet, base_name='appliance_data')
router.register(r'hue_states', HueStatesViewSet, base_name='Philips Hue State to Set')
router.register(r'home', HomeViewSet, base_name='Home')
router.register(r'home_data', HomeDataViewSet, base_name='Home Data')
router.register(r'powernet_user', PowernetUserViewSet, base_name='Powernet User')

urlpatterns = [
    url(r'^', include(router.urls))
]
