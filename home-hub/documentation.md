#Documentation
This is documentaiton from Rongpeng Zheng, it is about how to integrate Z-wave device and 
how wifi configuration system works


## Z-wave integration

+ install home-assistant

home-assistant is a framework that we used to control Z-wave devices

```bash
sudo pip3 install homeassistant
```

+ modify ~/.homeassistant/configuration.yaml

```yaml
homeassistant:
  # Name of the location where Home Assistant is running
  name: Home
  # Location required to calculate the time the sun rises and sets
  latitude: 0
  longitude: 0
  # Impacts weather/sunrise data (altitude above sea level in meters)
  elevation: 0
  # metric for Metric, imperial for Imperial
  unit_system: metric
  # Pick yours from here: http://en.wikipedia.org/wiki/List_of_tz_database_time_zones
  time_zone: UTC
  # Customization file
  customize: !include customize.yaml

# Show links to resources in log and frontend
introduction:

# Enables the frontend
frontend:

# Enables configuration UI
config:

# Uncomment this if you are using SSL/TLS, running in Docker container, etc.
# http:
#   base_url: example.duckdns.org:8123

# Checks for available updates
# Note: This component will send some information about your system to
# the developers to assist with development of Home Assistant.
# For more information, please see:
# https://home-assistant.io/blog/2016/10/25/explaining-the-updater/
updater:
  # Optional, allows Home Assistant developers to focus on popular components.
  # include_used_components: true

# Discover some devices automatically
#discovery:

# Allows you to issue voice commands from the frontend in enabled browsers
conversation:

# Enables support for tracking state changes over time
history:

# View all events in a logbook
logbook:

# Enables a map showing the location of tracked devices
map:

# Track the sun
sun:

# Weather prediction
sensor:
  - platform: yr

# Text to speech
tts:
  - platform: google

# Cloud
cloud:

group: !include groups.yaml
automation: !include automations.yaml
script: !include scripts.yaml

# Z-stick configuration
# ttyACM0 is the usb port which z-stick connects to
zwave:
  usb_path: /dev/ttyACM0
 
# Z-wave api password
# this password is used to control the Z-wave devices
# it is used in codes 
http:
  api_password: homeRP
```

+ run service on startup

create file /etc/systemd/system/home-assistant@YOUR_USER.service
```text
[Unit]
Description=HomeAssistant
After=network-online.target

[Service]
Type=simple
User=%i
ExecStart=/usr/local/bin/hass

[Install]
WantedBy=multi-user.target
```

Reference: <https://www.home-assistant.io/docs/autostart/systemd/>

Notes on running codes:

+ install RPi.GPIO: if program goes wrong because cannot find RPI.GPIO:
https://www.raspberrypi-spy.co.uk/2012/05/install-rpi-gpio-python-library/

## Wifi configuration system
### Pre configuration
```bash
sudo apt-get install dnsmasq hostapd
sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
sudo reboot
```

#### configuring DHCP server(dnsmasq)
DHCP server is used to assign IP address to connected device when raspberryPi is served as a hot spot.
+ save original file
```bash
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig  
```
+ modify /etc/dnsmasq.conf to
```text
interface=wlan0      # Use the require wireless interface - usually wlan0
  dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
```
#### Configuring the access point host software (hostapd)
+ add this to /etc/hostapd/hostapd.conf
```text
interface=wlan0
driver=nl80211
ssid=NameOfNetwork  #ssid
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=12345678 #should more than 8 characters
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```
+ tell the system the default configuration, modify /etc/default/hostapd 
```bash
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```
#### configuring a static IP
+ append snippets to the end of /etc/dhcpcd.conf including comments, they are used to locate configs in future use
```text
# create hot spot
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
sudo service dhcpcd restart  #now cannot connect to wifi
# create hot spot end
```

After all the above configuration is done, you can run wifi configuration system, 
details are in wifi-hotspot/README.md.

## Notes
Following are some notes, which can help you understand how the wifi configutaion system works.

### Relevant services

+ dhcpcd
 
dhcp client, it communicates with dhcp server so that wifi or ethernet can provide a ip address to 
this machine, then it can connects to internet.
 
This service should be always enable (run on startup), if configure /etc/dhcpcd.conf to static ip (wlan0), cannot connect to wifi 
because ip address is static.
+ dnsmasq

dhcp server and dns cache, when raspberryPi is a hot spot, only when this service is on, raspberruPi 
are able to provide ip address to deivces trying to connect to it.
+ hostapd

hostapd service is used to change raspberryPi to a hot spot, when this service is active, raspberryPi 
cannot connect to Wi-FI.


### normal mode to hotspot mode
1. add static IP configuration to /etc/dhcpcd.conf
2. sudo systemctl start hostapd
3. sudo systemctl start dnsmasq
4. sudo systemctl restart dhcpcd

### hotspot mode to normal mode and connect to wifi
1. add wifi configuration to /etc/wpa_supplicant/wpa_supplicant.conf
2. stop hostapd service
3. remove static ip setting in /etc/dhcpcd.conf, then restart dhcpcd service



Reference: <https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md>
