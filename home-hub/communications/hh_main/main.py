# Main script to run in the BBB
import HardwareClass
import StorageClass
import logging

from threading import Thread
from Queue import Queue
from logging.handlers import RotatingFileHandler
from raven import Client

# Sentry setup for additional error reporting via 3rd party cloud service
SENTRY_DSN = 'https://e3b3b7139bc64177b9694b836c1c5bd6:fbd8d4def9db41d0abe885a35f034118@sentry.io/230474'
client = Client(SENTRY_DSN)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('my_log.log', maxBytes=2000, backupCount=10)
logger.addHandler(handler)

def main():
    # Logger setup for a rotating file handler


    logger.info("Starting main program")

    # Initializing variables for queue and threads
    #gpioMap = {"CW1": "P8_9", "DW1": "P8_10", "AC1": "P8_15", "RF1": "P8_14", "SE1": "P8_11"}
    gpioMap = {"CW1": 29, "DW1": 31, "AC1": 33, "RF1": 35, "SE1": 37, "WM1": 38}
    rpi = HardwareClass.HardwareRPi(gpio_map=gpioMap)
    batt = StorageClass.Storage()
    buffer_size = 8
    q_ai = Queue(buffer_size)
    q_batt = Queue(3)

    # FIXME: Number of analog inputs -> Needs to be automated
    n_ai = 8
    format_ai = [i * 4 for i in range(n_ai)]

    # Initialize threads
    #producer_ai_thread = Thread(name='Producer', target=rpi.producer_ai, args=(format_ai, q_ai)) # This is for BBB
    producer_ai_thread = Thread(name='Producer', target=rpi.producer_ai, args=(q_ai,))
    producer_ai_thread.start()

    consumer_ai_thread = Thread(name='Consumer', target=rpi.consumer_ai, args=(q_ai,))
    consumer_ai_thread.start()

    # devices_thread = Thread(name='Device', target=rpi.devices_th, args=(q_batt,))
    # devices_thread.start()

    # battery_thread = Thread(name='Battery', target=batt.battery_thread, args=(q_batt,))
    # battery_thread.start()

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logging.exception(exc)
        client.captureException()
        logger.info("Re-starting main program")
        main()
