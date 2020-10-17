import logging
import app.home_updater.std_api as std_api
import app.home_updater.sonnen_api as sonnen_api
import app.home_updater.egauge_api as egauge_api
from app.algorithms import battery_load_control, battery_optimizer
from apscheduler.schedulers.background import BackgroundScheduler


logging.basicConfig()


def start():
    scheduler = BackgroundScheduler()

    scheduler.add_job(sonnen_api.update_battery_status, 'interval', minutes=5)
    scheduler.add_job(std_api.update_std_device_status, 'interval', minutes=5)
    scheduler.add_job(egauge_api.update_egauge_data, 'interval', seconds=5)
    # scheduler.add_job(battery_optimizer.batt_opt, 'interval', minutes=5)
    # scheduler.add_job(battery_load_control.batt_dispatch, 'interval', minutes=5)
    scheduler.start()
