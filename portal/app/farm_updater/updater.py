import logging
import std_api
import sonnen_api
import egauge_api
from app.algorithms import battery_load_control
from apscheduler.schedulers.background import BackgroundScheduler
from app.algorithms import std_control


logging.basicConfig()


def start():
    scheduler = BackgroundScheduler()

    # scheduler.add_job(sonnen_api.update_battery_status, 'interval', minutes=5)
    # scheduler.add_job(std_api.update_std_device_status, 'interval', minutes=5)
    scheduler.add_job(egauge_api.update_egauge_data, 'interval', seconds=10)
    # scheduler.add_job(battery_load_control.batt_dispatch, 'interval', minutes=5)
    scheduler.start()
