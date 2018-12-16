from subprocess import check_output, call
from set_to_hotspot import set_to_hotspot
from time import sleep
import re
import time
"""
This service should be run on startup, check wifi connection in a period of time
if wifi is conencted, stop wifi port web page, then quit
else start wifi port web page and set raspberryPi to hot spot mode
"""
f = open("/home/pi/log.txt", "a")
f.write(str(time.time()) + '  ')


max_try = 12
is_connected = False
while max_try != 0:  # check 10 times

    output = check_output(["iwconfig", "wlan0"])
    result = re.findall("ESSID:\"(\w*)\"", output)

    if len(result) != 0:  # connect to wifi
        f.write("connected to wifi, break   ")
        call(["systemctl", "stop", "wifi-portal@pi"])  # stop wifi port web page
        is_connected = True
        break

    max_try -= 1
    sleep(1)

if not is_connected:  # if not connected to wifi after 10 seconds, set to hot spot mode
    f.write("start to set hot spot")
    call(["systemctl", "start", "wifi-portal@pi"])
    set_to_hotspot()

f.write("\n")
f.close()

