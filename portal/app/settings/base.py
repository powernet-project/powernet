import os
import mimetypes


mimetypes.add_type("image/svg+xml", ".svg", True)
mimetypes.add_type("image/svg+xml", ".svgz", True)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# setup for local env use
INTERNAL_IPS = ('192.168.134.1', '127.0.0.1', '0.0.0.0')

# SECURITY WARNING: keep the secret key used in production secret! # FIXME: put in envar
# TODO
SECRET_KEY = 's$#@4*=sz+tvjhcufeijpch-&9&gseo1hn1(vbv+0=8_l+8+_p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (os.environ.get('DEBUG', 'True').lower() == 'true')
ALLOWED_HOSTS = [
    '.pwrnet-158117.appspot.com'
    'localhost',  # just so we can run debug false locally if needed
    '127.0.0.1',
    '*'
]
ROOT_URLCONF = 'app.urls'
WSGI_APPLICATION = 'app.wsgi.application'


if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'app',
    'app.api',
    'app.core',
    'app.device_api.DeviceConfig',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# If the user isn't logged, send them to the login page
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/' if DEBUG else 'https://storage.googleapis.com/powernet-app-assets/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'core/assets'),)
STATICFILES_FINDERS = ('django.contrib.staticfiles.finders.FileSystemFinder',
                       'django.contrib.staticfiles.finders.AppDirectoriesFinder')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'core/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database
# PROD - Config for when this runs on GCPs AppEngine
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'jongon',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': '/cloudsql/pwrnet-158117:us-central1:pwrnet-dev-store',
        'PORT': '5432'
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

SUN_TECH_DRIVE_URL = ''
SONNEN_BATT1 = '67682'
SONNEN_BATT2 = '67670'
SONNEN_URL = 'https://core-api.sonnenbatterie.de/proxy/'
SUN_TECH_DRIVE_TEST_URL = 'https://test.suntechdrive.com'
EGAUGE_URL = 'https://egauge46613.egaug.es/cgi-bin/egauge'
EGAUGE_ID = '46613'

# DO NOT MANUALLY EDIT THESE!!!!! THEY ARE INJECTED IN OUR BUILD PIPELINE
# AND THEREFORE WILL BE OVERWRITTEN ANYWAYS
EGAUGE_USER=''
SONNEN_TOKEN=''
EGAUGE_PASSWORD=''
SUN_TECH_DRIVE_PASSWORD=''
SUN_TECH_DRIVE_USERNAME=''
