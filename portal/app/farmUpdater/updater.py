from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import sonnen_api
import logging

logging.basicConfig()

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(sonnen_api.update_battery_status, 'interval', minutes=1)
    scheduler.start()