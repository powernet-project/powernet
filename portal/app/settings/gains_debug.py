from app.settings.base import *

# DEV
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'powernet',
        'USER': 'postgres',
        'PASSWORD': '1qaz@WSX3e',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

CELERY_BROKER_URL = 'redis://localhost:6379'