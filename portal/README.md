# Powernet Portal

User facing application to allow an end user to access his data and perform a variety of controls.

This is a multi tier application, containing client code > HTML/CSS/JS, a middle tier reliant on Python 2.7 & Django 1.11, and a DB tier running PostgreSQL.

To run the project locally, begin by installing all the dependencies. 
Highly recommended to do so via a virtual env (venv or conda), or Vagrant or Docker (the existing Dockerfile is used by GCP to build/run our project).

- Install Redis: simply follow the install instructions here: https://redis.io/topics/quickstart
Redis is used as a message broker for celery and async task processing.

- Install Python dependencies (assuming you are using pip, if not install pip):
```
pip install -r requirements.txt
```

- Make sure you have postgresql installed
- Boot the DB (you can use pgadmin and connect to the DB.) Look in the gains_debug settings file to view expected params. 
Also, once you connect to *your local* db for the very first time, run:
```
python manage.py migrate  #please don't run this against the prod DB config
```

- Lastly, run the django server:
```
export DJANGO_SETTINGS_MODULE=app.settings.gains_debug
django-admin runserver
```

# PENDING TO-DOs:
- Forgot password link isn't hooked up to anything
- Login flow and the rest of the application use diff bootstrap versions. Consolidate!
- Fix static assets setup and deploy - afff.....whatever else that is needed



