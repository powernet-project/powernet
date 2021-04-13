from app.settings.base import *

# DEV
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'powernet_local',
        'USER': 'postgres',
        'PASSWORD': '1qaz@WSX3e',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
