from django.apps import AppConfig
from app.home_updater import updater


class HomeDeviceConfig(AppConfig):
    name = 'app.home_device_api'

    def ready(self):
        updater.start()
