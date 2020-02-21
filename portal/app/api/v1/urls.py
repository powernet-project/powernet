from django.conf.urls import include, url
from rest_framework import routers

from app.api.v1.endpoint.utility_energy_price import UtilityEnergyPriceViewSet
from app.api.v1.endpoint.device import DeviceViewSet, DeviceStateViewSet
from app.api.v1.endpoint.farm_device import FarmDeviceViewSet, FarmDataViewSet
from app.api.v1.endpoint.lora_device import LoraDeviceViewSet
from app.api.v1.endpoint.hue_states import HueStatesViewSet
from app.api.v1.endpoint.powernet_user import PowernetUserViewSet
from app.api.v1.endpoint.home import HomeViewSet, HomeDataViewSet
from app.api.v1.endpoint.appliance_data import ApplianceJsonDataViewSet
from app.api.v1.endpoint.ecobee_data import ecobee_data, ecobee_set_mode, ecobee_set_temperature
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Powernet API')

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
router.register(r'farm_device', FarmDeviceViewSet, base_name='Farm Device')
router.register(r'farm_device_data', FarmDataViewSet, base_name='Farm Data')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^$', schema_view),
    url(r'lora_device', LoraDeviceViewSet.as_view()),
    url(r'ecobee/data', ecobee_data),
    url(r'ecobee/temperature/(?P<temp>.+)', ecobee_set_temperature),
    url(r'ecobee/mode/(?P<mode>.+)', ecobee_set_mode)
]
