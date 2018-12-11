"""
Initialize the Home Hub to begin collecting sensor data
"""
from __future__ import print_function

__author__ = 'Gustavo C. & Jonathan G. '
__copyright__ = 'Stanford University'
__version__ = '0.2'
__email__ = 'gcezar@stanford.edu, jongon@stanford.edu'
__status__ = 'Beta'

import os
import sys
import getopt
import logging
import requests

from Queue import Queue
from raven import Client
from threading import Thread
from main.api_hardware import HardwareInterface
from logging.handlers import RotatingFileHandler


error_reporter = None
logger = logging.getLogger('HOME_HUB_APPLICATION_LOGGER')
HOME_ID = None
DEBUG = False # by default we run the HH with DEBUG off

FILE_USAGE_EXPLANATAION = """
    Usage:
    python init.py -h           # displays this help message
    python init.py -i <int>     # supply a home ID - this is REQUIRED
    python init.py -i <int> -d  # run the Home Hub in debug (prints to console as well as file)
"""


def init_error_reporting():
    """
    Simple error reporting wrapper - will allow us to plug in
    different error reporting backend(s) in the future
    """
    global error_reporter
    SENTRY_DSN = 'https://e3b3b7139bc64177b9694b836c1c5bd6:fbd8d4def9db41d0abe885a35f034118@sentry.io/230474'
    error_reporter = Client(SENTRY_DSN)

def init_logging():
    """
    Simple logging abstraction. We currently use Rotating File Handler.
    We may, however, in the future, plug in something like Papertrail
    """
    logger.setLevel(logging.DEBUG)
    # set a common log format
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    # setup our rotating file handler and assign our common formatter to it
    rotating_file_handler = RotatingFileHandler('my_log.log', maxBytes=200000, backupCount=10)
    rotating_file_handler.setFormatter(logFormatter)
    logger.addHandler(rotating_file_handler)
    
    if DEBUG:
        # print to stdout if we are debugging
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logFormatter)
        logger.addHandler(stream_handler)

def parse_cmd_line_opts(argv):
    """
    Attempt to use the cmd line options, if any are given
    """
    if argv is None:
        return
    
    try:
        opts, args = getopt.getopt(argv, 'hdi:')
        for opt, arg in opts:
            if opt == '-h':
                print(FILE_USAGE_EXPLANATAION)
                sys.exit()
            elif opt == '-d':
                print('Running HH with DEBUG set to True')
                global DEBUG
                DEBUG = True
            elif opt == '-i':
                global HOME_ID
                HOME_ID = int(arg)
    except getopt.GetoptError:
        print('Unrecognized option; running HH with DEBUG set to False')

def initialize_home_hub(argv):
    """
    Perform the necessary setup before starting to collect sensor data
    """
    parse_cmd_line_opts(argv)
    init_logging()
    init_error_reporting()
    
    # Verify we have a valid home id
    if HOME_ID is None:
        print('Home ID is invalid or missing. Please provide an integer following the -i flag')
        exit()

    # Begin Home Hub Specific Setup
    logger.info('Starting the Home Hub main program for Home: %s', HOME_ID)

    # Get the email and password for this HH's user from the env vars
    powernet_user_email = os.getenv('POWERNET_USER_EMAIL', None)
    powernet_user_password = os.getenv('POWERNET_USER_PASSWORD', None)
    
    if powernet_user_email is None:
        logger.info('Missing the required login email address')
        logger.info('Please set the POWERNET_USER_EMAIL environment variable and try again')
        exit()
    
    if powernet_user_password is None:
        logger.info('Missing the required login password')
        logger.info('Please set the POWERNET_USER_PASSWORD environment variable and try again')
        exit()
    
    # attempt to authenticate against our API
    form_payload = {'email': powernet_user_email, 'password': powernet_user_password}
    response = requests.post('https://pwrnet-158117.appspot.com/api/v1/powernet_user/auth/', data=form_payload)
    auth_token = response.json()['token']

    # Initializing variables for queue and threads
    rpi = HardwareInterface(house_id=HOME_ID, gpio_map=None, auth_token=auth_token)
    buffer_size = 8
    q_ai = Queue(buffer_size)

    # Initialize threads
    producer_ai_thread = Thread(name='Producer', target=rpi.producer_ai, args=(q_ai,))
    producer_ai_thread.start()

    consumer_ai_thread = Thread(name='Consumer', target=rpi.consumer_ai, args=(q_ai,))
    consumer_ai_thread.start()

    devices_thread = Thread(name='Device', target=rpi.devices_th)
    devices_thread.start()

    load_control_thread = Thread(name="LoadControl", target=rpi.local_controller_th)
    load_control_thread.start()

if __name__ == '__main__':
    try:
        initialize_home_hub(sys.argv[1:])
    except Exception as exc:
        logging.exception(exc)
        error_reporter.captureException()
        logger.info("Re-starting main program")
        initialize_home_hub(None)
