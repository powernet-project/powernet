import logging
import std_api
import sonnen_api
from apscheduler.schedulers.background import BackgroundScheduler


logging.basicConfig()


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(sonnen_api.update_battery_status, 'interval', minutes=15)
    scheduler.add_job(std_api.update_std_device_status, 'interval', minutes=15)
    scheduler.start()
