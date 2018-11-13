# Main script to run in the BBB
import HardwareClass
# import StorageClass
import logging

from threading import Thread
from Queue import Queue
from logging.handlers import RotatingFileHandler
from raven import Client
from google.cloud import pubsub_v1

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
    h_id = raw_input("Enter house id: ")

    # Initializing variables for queue and threads
    rpi = HardwareClass.HardwareRPi(house_id = int(h_id), gpio_map=None)
    # batt = StorageClass.Storage()
    buffer_size = 8
    q_ai = Queue(buffer_size)

    # Initialize threads

    producer_ai_thread = Thread(name='Producer', target=rpi.producer_ai, args=(q_ai,))
    producer_ai_thread.start()

    consumer_ai_thread = Thread(name='Consumer', target=rpi.consumer_ai, args=(q_ai,))
    consumer_ai_thread.start()

    devices_thread = Thread(name='Device', target=rpi.devices_th)
    devices_thread.start()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logging.exception(exc)
        client.captureException()
        logger.info("Re-starting main program")
        main()
