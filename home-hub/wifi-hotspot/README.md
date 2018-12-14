# WiFi portal

WiFI portal is a webapplication for users to configure wifi SSID and password. The WiFi portal will be available at port 8000.

Python 2.7 and Django 1.11 is used for this portal.

### how to run WiFi portal on startup
This service should be run on startup. 

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
ExecStart=/usr/bin/python2 /home/pi/powernet/home-hub/wifi-hotspot/manage.py runserver

[Install]
WantedBy=multi-user.target
```
3. sudo systemctl enable wifi-portal@pi.service


### how to run standalone for development purpose
```
virtualenv venv
source venv/bin/activate
sudo pip2 install -r requirements.txt
python2 manage.py migrate
python2 manage.py runserver
```

