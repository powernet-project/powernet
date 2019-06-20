import sonnen_api
import egauge_api
import logging
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig()


def start():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(sonnen_api.update_battery_status, 'interval', minutes=5)
    scheduler.add_job(egauge_api.updater_egauge_status(), 'interval', minutes=5)
    scheduler.start()
