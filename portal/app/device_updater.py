import logging
from app.algorithms import battery_load_control, battery_optimizer
from apscheduler.schedulers.background import BackgroundScheduler


logging.basicConfig()
scheduler = BackgroundScheduler()

# Add jobs for updating farm data
def add_farm_updater():
    import app.farm_updater.std_api as std_api
    import app.farm_updater.sonnen_api as sonnen_api
    import app.farm_updater.egauge_api as egauge_api
    scheduler.add_job(sonnen_api.update_battery_status, 'interval', minutes=5)
    scheduler.add_job(std_api.update_std_device_status, 'interval', minutes=5)
    scheduler.add_job(egauge_api.update_egauge_data, 'interval', minutes=5)
    # scheduler.add_job(battery_optimizer.batt_opt, 'interval', minutes=5)
    scheduler.add_job(battery_load_control.batt_dispatch, 'interval', minutes=5)

# Add jobs for updating home device data
def add_home_updater():
    import app.home_updater.sonnen_api as sonnen_api
    import app.home_updater.egauge_api as egauge_api
    import app.home_updater.home_battery_optimizer as home
   # scheduler.add_job(sonnen_api.update_battery_status, 'interval', minutes=5)
   # scheduler.add_job(egauge_api.update_egauge_data, 'interval', minutes=5)
    scheduler.add_job(home.optimize_home_battery, 'interval' , seconds = 10)


# Start background tasks for farm_updater and home_updater
def start():
    scheduler.start()
