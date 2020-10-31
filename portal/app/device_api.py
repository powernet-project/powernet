from django.apps import AppConfig
from app import device_updater


class DeviceConfig(AppConfig):
    name = 'app.device_api'

    def ready(self):
        device_updater.add_farm_updater()
        device_updater.add_home_updater()
        device_updater.start()
