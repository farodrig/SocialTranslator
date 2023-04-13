from .default import *

BASE_URL = "http://localhost:8000"
DEBUG = True
ALLOWED_HOSTS = ['*']
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testingDB'
    }
}