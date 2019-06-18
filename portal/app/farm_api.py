from django.apps import AppConfig

class FarmConfig(AppConfig):
    name = 'app.farm_api'

    def ready(self):
        from app.farmUpdater import updater
        updater.start()