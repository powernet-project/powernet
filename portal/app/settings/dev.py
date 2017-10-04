from base import *

# DEV
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'powernet',
#         'USER': 'postgres',
#         'PASSWORD': '1qaz@WSX3e',
#         'HOST': 'localhost',
#         'PORT': '5432'
#     }
# }

# PROD via local tunnel
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'jongon',
        'PASSWORD': '1qaz@WSX3e',
        'HOST': '35.184.255.34',
        'PORT': '5432'
    }
}
