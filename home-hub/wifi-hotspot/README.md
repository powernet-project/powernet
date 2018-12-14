# How to run WiFi portal

Python 2.7 and Django 1.11 is used for this portal.

```
virtualenv venv
source venv/bin/activate
sudo pip2 install -r requirements.txt
python2 manage.py migrate
python2 manage.py runserver
```
The WiFi portal will be available at port 8000.
