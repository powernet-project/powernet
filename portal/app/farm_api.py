from django.apps import AppConfig
from app.farmUpdater import updater


class FarmConfig(AppConfig):
    name = 'app.farm_api'

    def ready(self):
        updater.start()
