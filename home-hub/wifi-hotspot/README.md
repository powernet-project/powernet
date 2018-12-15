# WiFi portal

WiFI portal is a webapplication for users to configure wifi SSID and password. The WiFi portal will be available at port 8000.

Python 2.7 and Django 1.11 is used for this portal.

There are two parts
1. check wifi service, this service should be run on startup to check if raspberryPi is connected to wifi.

If wifi is connected, this service quit itself

Else wifi portal will be started, and hot spot mode will be active, users can connect to the hot spot and access 192.168.4.1:8000, 
in the website, users can input SSID and password, if they input the correct ones, raspberry pi will connect to the wifi and shift to normal mode.

# setup

### how to configure check-wifi service
1. add file /etc/systemd/system/check-wifi@pi.service
```
[Unit]
Description=CheckWifiConnection

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python2 /home/pi/powernet/home-hub/wifi-hotspot/check_wifi_connection.py
[Install]
WantedBy=multi-user.target
```
2. sudo systemctl enable check-wifi@pi.service


### how to configure WiFi portal service
"check wifi" service need WiFiPortal configured as a service to control it on and off

Steps:
1. install requirements
```
sudo pip2 install -r requirements.txt
```
2. add file /etc/systemd/system/wifi-portal@pi.service
```
[Unit]
Description=WifiPortal

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python2 /home/pi/powernet/home-hub/wifi-hotspot/manage.py runserver 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

### how to run Wifi Portal standalone for development purpose
```
virtualenv venv
source venv/bin/activate
sudo pip2 install -r requirements.txt
python2 manage.py migrate
python2 manage.py runserver 0.0.0.0:8000
```
