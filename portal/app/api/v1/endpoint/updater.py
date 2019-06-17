from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import sonnen_data

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(sonnen_data.update_battery_status, 'interval', minutes=1)
    scheduler.start()