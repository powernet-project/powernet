from django.apps import AppConfig
from app.farm_updater import updater


class FarmConfig(AppConfig):
    name = 'app.farm_api'

    def ready(self):
        updater.start()
