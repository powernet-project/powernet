import logging
import app.home_updater.sonnen_api as sonnen_api
import app.home_updater.egauge_api as egauge_api
from apscheduler.schedulers.background import BackgroundScheduler


logging.basicConfig()


def start():
    scheduler = BackgroundScheduler()

    scheduler.add_job(sonnen_api.update_battery_status, 'interval', minutes=5)
    scheduler.add_job(egauge_api.update_egauge_data, 'interval', minutes=5)
    scheduler.start()
