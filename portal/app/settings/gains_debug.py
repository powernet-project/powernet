from app.settings.base import *

# DEV
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'powernet_local',
        'USER': 'derins',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
