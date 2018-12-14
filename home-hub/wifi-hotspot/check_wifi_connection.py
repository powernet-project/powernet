from subprocess import check_output
from set_to_hotspot import set_to_hotspot
from time import sleep
import re

max_try = 10
is_connected = False
while max_try != 0:  # check 10 times

    output = check_output(["iwconfig", "wlan0"])
    result = re.findall("ESSID:\"(\w*)\"", output)

    if len(result) != 0:  # connect to wifi
        is_connected = True
        break

    max_try -= 1
    sleep(1)

if not is_connected:  # if not connected to wifi after 10 seconds, set to hot spot mode
    set_to_hotspot()
